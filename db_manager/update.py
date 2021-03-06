# -*- coding: utf-8 -*-
import sys
import logging
import re
import time
import traceback
from datetime import datetime, timedelta
from decimal import Decimal
import tables as tb
import numpy as np
from PyQt5.QtWidgets import QApplication

sys.path.append('..')
from trader.kiwoomAPI import KiwoomAPI
from trader.util import util


class Update(KiwoomAPI):

    def __init__(self, arg=None):
        super().__init__()
        import os
        print(os.getcwd())
        self.logger = logging.getLogger('DB Manager')
        self.arg = arg

        #open DB
        filters = tb.Filters(complib='blosc', complevel=9)
        self.h5file = tb.open_file("../data/market.hdf5", mode="a",
                                   title="Market Data Collection", filters=filters)

        #global variable declaration
        self.today = datetime.today()

        # (시장구분, 종목명, 코드) tuple list 작성
        self.codelist = []
        try:
            self.marketinfo = self.h5file.root._v_attrs.marketinfo
        except:
            self.marketinfo = dict()

        for typ, code in self.marketinfo.items():
            for code, item in code.items():
                self.codelist.append((typ, code, item['name'], item['code'], item['tick_unit'], item['digit']))
        self.codelength = len(self.codelist)
        
        getattr(self.ocx, 'OnReceiveRealData').disconnect()
        getattr(self.ocx, 'OnReceiveChejanData').disconnect()
        #getattr(self.ocx, 'OnEventConnect').disconnect()
        getattr(self.ocx, 'OnReceiveMsg').disconnect()

    def updateMarketInfo(self):
        """
            kiwoom API로부터 각 종목의 기본정보를 취합하여 db.root._v_attrs에 저장함
        """
        updatedinfo = dict()
        types = util.toList(self.GetGlobalFutureItemTypelist())
        for typ in types:
            updatedinfo[typ] = dict()
            items = util.toList(self.GetGlobalFutureItemlistByType(typ))
            for item in items:
                #self.marketinfo[typ][item] = dict() 
                code = util.toList(self.GetGlobalFutureCodelist(item))[0]
                iteminfo = self.GetGlobalFutOpCodeInfoByCode(code)
                name = re.sub(r'\(.*\).*$', '', iteminfo[18:58]).strip()
                if ('Mini' in name) or ('Micro' in name) or ('Miny' in name):
                    continue
                else:
                    #print(iteminfo)
                    product = typ+item
                    updatedinfo[typ][product] = dict()
                    itemcode = item+'000'
                    tick_unit = iteminfo[64:79].strip()
                    tick_value = iteminfo[79:94].strip()
                    updatedinfo[typ][product]['name'] = name
                    updatedinfo[typ][product]['code'] = itemcode
                    updatedinfo[typ][product]['digit'] = Decimal(tick_unit).as_tuple().exponent *(-1)
                    updatedinfo[typ][product]['tick_unit'] = float(tick_unit)
                    updatedinfo[typ][product]['tick_value'] = float(tick_value)
                    #self.marketinfo[typ][item]['groupname'] = typ+item

        if self.marketinfo:
            if self.marketinfo == updatedinfo:
                print("Market information did NOT changed")
            else:
                del self.h5file.root._v_attrs.marketinfo
                self.h5file.root._v_attrs.marketinfo = updatedinfo
                print("Market information changed")
        else:
            self.h5file.root._v_attrs.marketinfo = updatedinfo

        self.h5file.close()
        print("market information successfully updated")
        sys.exit()


    #Price distribution table 만들기
    def getDistribution(self):
        item = self.codelist.pop()
        self.tickunit = item[4]
        self.digit = item[5]

        group = getattr(getattr(self.h5file.root, item[0]), item[1])
        self.dist = group.Distribution
        self.dates = group.Date
        self.lastdate = max(self.dates.cols.date, default=0)
        self.flag = False

        #self.preNext = ""
        self.inputValue = {
            "종목코드" : item[3],
            "시간단위" : "1"
        }
        self.sendRequest(item[2], "opc10002", "0000", self.inputValue, "")

        #logging
        self.logger.info("*********************product: %s***********************", item[2])
        self.logger.info("last recorded date: %s", np.array(self.lastdate).astype('M8[s]'))

    @KiwoomAPI.on("OnReceiveTrData", screen="0000")
    def __receiveMinute(self, scrNo, rqName, trCode, fieldName, preNext):

        data = self.GetCommFullData(trCode, rqName, 2)
        datalist = [data[i:i+140] for i in range(0, len(data), 140)]

        for row in datalist:
            items = []
            dates = []

            date = row[40:60].strip() #시간
            idx = len(self.dates.cols.date) ##date에 mapping될 row index

            try:
                date = np.datetime64(datetime.strptime(date, '%Y%m%d%H%M%S')).astype('uint64')/1000000
            except:
                self.logger.warning("%s has a missing DATE or something is wrong", rqName)
                self.logger.error(traceback.format_exc())
                continue
            else:
                high = float(row[80:100].strip()) #고가
                low = float(row[100:120].strip()) #저가
                volume = int(row[20:40].strip()) #거래량

                if not int(volume): #거래량이 0이면 버림
                    self.logger.warning("%s with volume %s will be passed at %s", rqName, volume, date.astype('M8[s]'))
                    continue

                elif np.rint(date) <= np.rint(self.lastdate): #최신 날짜와 겹치면 버림
                    self.flag = True
                    self.logger.warning("Last date in DB matched at %s", np.array(date).astype('M8[s]'))
                    break

                else:
                    self.dates.row['date'] = date
                    self.dates.row['index'] = idx

                    if round(low, self.digit) == round(high, self.digit):
                        item = (idx, round(low, self.digit), volume)
                        items.append(item)

                    else:
                        length = (high-low)/self.tickunit + 1
                        value = volume/length
                        if np.isinf(value) or (value < 0.1):  #inf value 가 생김 가끔..
                            self.logger.warning("wrong volume: %s, length: %s at %s", volume, length, np.array(date).astype('M8[s]'))
                            continue
                        for pr in np.arange(round(low, self.digit), high - self.tickunit/2, self.tickunit):
                            item = (idx, pr, value)
                            items.append(item)

                    try:
                        self.dates.row.append()
                        self.dist.append(items)
                    except: 
                        print(items)
                    else:
                        self.dates.flush()
                        self.dist.flush()

        print("reciveing: %s, %s, remained=(%s/%s)"%(rqName, preNext.strip(),
                                                     len(self.codelist), self.codelength))

        if (not preNext.strip()) or self.flag:
            self.logger.info("preNext: %s, rqName: %s, code: %s", preNext, rqName, self.inputValue["종목코드"])
            self.logger.info("reached last date at  %s", np.array(date).astype('M8[s]'))

            if self.codelist:
                time.sleep(0.25)
                self.getDistribution()
            else:
                print("All Minute Data has been successfully updated!!")
                self.h5file.close()
                sys.exit()

        else:
            time.sleep(0.25)
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)




    #일봉 데이터 받기
    def getOHLC(self):
        item = self.codelist.pop()
        group = getattr(getattr(self.h5file.root, item[0]), item[1])

        startday = self.today - timedelta(days=1)
        startday = startday.strftime('%Y%m%d')

        self.ohlc = group.OHLC
        self.lastdate = max(self.ohlc.cols.date, default=0) #중복 날짜 카운트
        self.flag = False #true이면 데이터 받는거 멈추기

        self.inputValue = {
            "종목코드" : item[3],
            "조회일자" : startday
        }
        self.sendRequest(item[2], "opc10003", "9999", self.inputValue, "")

        #logging
        self.logger.info("product: %s", item[2])
        self.logger.info("last recorded date: %s", np.array(self.lastdate).astype('M8[s]'))
        self.logger.info("start date: %s", startday)

    @KiwoomAPI.on("OnReceiveTrData", screen="9999")
    def __receiveDaily(self, scrNo, rqName, trCode, fieldName, preNext):
        data = self.GetCommFullData(trCode, rqName, 2)
        datalist = [data[i:i+140] for i in range(0, len(data), 140)]
        keys = 'Date, Open, High, Low, Close, Volume'
        items = []

        for row in datalist:
            date = row[80:100].strip() #시간

            try:
                date = np.datetime64(datetime.strptime(date, '%Y%m%d')).astype('uint64')/1000000
            except:
                self.logger.warning("%s has a missing DATE or something is wrong", rqName)
                self.logger.error(traceback.format_exc())
                continue
            else:
                open = row[20:40].strip() #시가
                high = row[40:60].strip() #고가
                low = row[60:80].strip() #저가
                close = row[0:20].strip() #종가
                volume = row[100:120].strip() #거래량

                if not int(volume):
                    #거래량이 0이면 버림
                    self.logger.warning("%s with volume %s will be passed at %s", rqName, volume, date.astype('M8[s]'))
                    continue

                elif np.rint(date) <= np.rint(self.lastdate):
                    self.flag = True
                    self.logger.warning("Last date in DB matched at %s", np.array(date).astype('M8[s]'))
                    break

                else:
                    item = (date, open, high, low, close, volume)
                    items.append(item)

        if items:
            self.ohlc.append(items)
            self.ohlc.flush()

        print("reciveing: %s, %s, remained=(%s/%s)"%(rqName, preNext.strip(), len(self.codelist), self.codelength))

        if not preNext.strip() or self.flag:
            self.logger.info("reached last date at %s", np.array(date).astype('M8[s]'))

            if self.codelist:
                time.sleep(0.25)
                self.getOHLC()
            else:
                print("All Daily OHLC Data has been successfully updated!!")
                self.h5file.close()
                sys.exit()

        else:
            time.sleep(0.25)
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)


    @KiwoomAPI.on('OnEventConnect')
    def _connect(self, errCode):
        if errCode == 0:
            if self.arg == 'OHLC':
                self.getOHLC()
            elif self.arg == 'minute':
                self.getDistribution()
            elif self.arg == 'marketinfo':
                self.updateMarketInfo()
            else:
                sys.exit()