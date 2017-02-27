# -*- coding: utf-8 -*-
import sys
import logging
import re
import time
from datetime import datetime, timedelta
import tables as tb
import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QVariant
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication,QMainWindow


sys.path.append('..')


from plus.kiwoomAPI import KiwoomAPI
from plus.util import util
from db_structure import Distribution, OHLC


class Manager(KiwoomAPI):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('DB Manager')

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
                self.codelist.append((typ, item['groupname'], item['name'], item['code'], item['tick_unit']))
        self.codelength = len(self.codelist)

    def updateMarketInfo(self):
        """
            kiwoom API로부터 각 종목의 기본정보를 취합하여 db.root._v_attrs에 저장함
        """
        if self.marketinfo:
            del self.h5file.root._v_attrs.marketinfo
        self.marketinfo = dict()
        types = util.toList(self.GetGlobalFutureItemTypelist())
        for typ in types:
            self.marketinfo[typ] = dict()
            items = util.toList(self.GetGlobalFutureItemlistByType(typ))
            for item in items:
                #self.marketinfo[typ][item] = dict() 
                code = util.toList(self.GetGlobalFutureCodelist(item))[0]
                iteminfo = self.GetGlobalFutOpCodeInfoByCode(code)
                name = re.sub(r'\(.*\).*$', '', iteminfo[18:58]).strip()
                if ('Mini' in name) or ('Micro' in name) or ('Miny' in name):
                    continue
                else:
                    self.marketinfo[typ][item] = dict()
                    itemcode = item+'000'
                    tick_unit = iteminfo[64:79].strip()
                    tick_value = iteminfo[79:94].strip()
                    self.marketinfo[typ][item]['name'] = name
                    self.marketinfo[typ][item]['code'] = itemcode
                    self.marketinfo[typ][item]['tick_unit'] = float(tick_unit)
                    self.marketinfo[typ][item]['tick_value'] = float(tick_value)
                    self.marketinfo[typ][item]['groupname'] = typ+item

        self.h5file.root._v_attrs.marketinfo = self.marketinfo
        self.h5file.flush()
        self.logger.info("종목 정보 업데이트 완료")

    def create_db(self):
        """
         market info로부터 계층적 DB 구조 자동생성
         시장구분 - 종목 - OHLC Table
                        - distribution Table
                        - dates Table
                        - density Vector
                        - gradient Vector
        """
        self.marketinfo = self.h5file.root._v_attrs.marketinfo
        for i in self.h5file.iter_nodes('/'):
            self.h5file.remove_node(i, recursive=True)
        self.logger.info("All file nodes were cleared")
        for typ in self.marketinfo:
            market = self.h5file.create_group('/', typ, "Market")
            for item in self.marketinfo[typ]:
                title = self.marketinfo[typ][item]['name']
                product = self.h5file.create_group(market, typ+item, title)
                self.h5file.create_table(product, "OHLC", OHLC, "Daily OHLC")
                self.h5file.create_table(product, "Distribution", Distribution, "price distribution")
                self.logger.info("%s table successfully created", title)
        self.h5file.close()

    #Price distribution table 만들기
    def getDistribution(self):
        item = self.codelist.pop()
        self.tickunit = item[4]

        group = getattr(getattr(self.h5file.root, item[0]), item[1])
        self.dist = group.Distribution
        self.flag = False
        self.lastdate = max(self.dist.cols.dates, default=0) #가장 최근 date

        #self.preNext = ""
        self.inputValue = {
            "종목코드" : item[3],
            "시간단위" : "1000"
        }
        self.sendRequest(item[2], "opc10002", "0000", self.inputValue, "")

        #logging
        self.logger.info("product: %s", item[2])
        self.logger.info("last recorded date: %s", np.array(self.lastdate).astype('M8[s]'))
        #self.logger.info("codelist: %s",self.codelist)

    @KiwoomAPI.on("OnReceiveTrData", screen="0000")
    def __receiveMinute(self, scrNo, rqName, trCode, fieldName, preNext):
        data = self.GetCommFullData(trCode, rqName, 2)
        datalist = [data[i:i+140] for i in range(0, len(data), 140)]
        keys = 'Date, High, Low, Volume'
        items = []

        #tick_unit = self.marketinfo[]
        for row in datalist:
            Date = row[40:60].strip() #시간
            High = float(row[80:100].strip()) #고가
            Low = float(row[100:120].strip()) #저가
            Volume = int(row[20:40].strip()) #거래량
            Date = np.datetime64(datetime.strptime(Date, '%Y%m%d%H%M%S')).astype('uint64')/1000000

            if Date == self.lastdate:
                self.flag = True
                date = np.array(Date).astype('M8[s]')
                self.logger.info("Last date in DB matched at %s", date)
                break

            if High == Low:
                item = (Date, Low, Volume)
                items.append(item)

            else:
                length = (High-Low)/self.tickunit +1
                value = Volume/length
                for pr in np.arange(Low, High, self.tickunit):
                    item = (Date, pr, value)
                    items.append(item)

        if items:
            self.dist.append(items)
            self.dist.flush()

        print("reciveing: %s, %s, remained=(%s/%s)"%(rqName, preNext.strip(),len(self.codelist),self.codelength))

        if (not preNext.strip()) or self.flag:
            if self.codelist:
                self.logger.info("preNext: %s",preNext)
                self.logger.info("reached last date at  %s", Date.astype('M8[s]'))
                time.sleep(0.25)
                self.getDistribution()
            else:
                self.logger.info("All Minute Data has been successfully updated!!")
                sys.exit()

        else:
            time.sleep(0.25)
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)


    #일봉 데이터 받기
    def getOHLC(self):
        #print(self.codelist)

        item = self.codelist.pop()
        group = getattr(getattr(self.h5file.root, item[0]), item[1])

        startday = self.today - timedelta(days=1)
        startday = self.today.strftime('%Y%m%d')

        self.ohlc = group.OHLC
        self.lastdate = max(self.ohlc.cols.date, default=0) #가장 최근 date
        self.flag = False #true이면 데이터 받는거 멈추기

        self.inputValue = {
            "종목코드" : item[3],
            "조회일자" : startday
        }
        self.sendRequest(item[2], "opc10003", "9999", self.inputValue, "")

        #logging
        self.logger.warning("product: %s", item[2])
        self.logger.warning("last recorded date: %s", np.array(self.lastdate).astype('M8[s]'))

    @KiwoomAPI.on("OnReceiveTrData", screen="9999")
    def __receiveDaily(self, scrNo, rqName, trCode, fieldName, preNext):
        data = self.GetCommFullData(trCode, rqName, 2)
        datalist = [data[i:i+140] for i in range(0, len(data), 140)]
        keys = 'Date, Open, High, Low, Close, Volume'
        items = []
        for row in datalist:
            Date = row[80:100].strip() #시간
            Open = row[20:40].strip() #시가
            High = row[40:60].strip() #고가
            Low = row[60:80].strip() #저가
            Close = row[0:20].strip() #종가
            Volume = row[100:120].strip() #거래량

            Date = np.datetime64(datetime.strptime(Date, '%Y%m%d')).astype('uint64')/1000000
            if Date == self.lastdate:
                self.flag = True
                date = np.array(Date).astype('M8[s]')
                self.logger.info("Last date in DB matched at %s", date)
                break
            item = (Date, Open, High, Low, Close, Volume)
            items.append(item)

        if items:
            self.ohlc.append(items)
            self.ohlc.flush()
        self.logger.info("reciveing: %s, %s", rqName, preNext)

        if not preNext.strip() or self.flag:
            if self.codelist:
                time.sleep(0.25)
                self.getOHLC()
            else:
                #QApplication.quit()
                self.logger.info("All Daily OHLC Data has been successfully updated!!")
                sys.exit()

        else:
            time.sleep(0.25)
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)




    @KiwoomAPI.on('OnEventConnect')
    def _connect(self, errCode):
        if errCode == 0:
            pass
            #종목 정보 갱신
            #self.updateMarketInfo()
            
            #일봉 데이터 받기
            #self.getOHLC()

            #분봉 데이터 받기
            self.getDistribution()
                    

        #db 만들기
        #self.create_db()
        #self.h5file.close()
        #sys.exit()


if __name__ == "__main__":

    logging.basicConfig(filename="db_manager.log", format="%(name)s: %(message)s", level=logging.INFO)
    logging.info('====================================================')
    logging.info('  %s', datetime.now())
    logging.info('====================================================')

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.view = QWebEnginePage()
    kiwoom = window.view.kiwoom = Manager()
    kiwoom.CommConnect(0)
    #kiwoom.create_db() #db 새로 만들기...
    sys.exit(app.exec_())
