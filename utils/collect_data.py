# -*- coding: utf-8 -*-
import sys, os, json, logging, re, time
sys.path.append('..')

from collections import defaultdict
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QVariant
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from PyQt5.QtWidgets import QApplication,QMainWindow
from plus.kiwoomAPI import KiwoomAPI
from plus.kiwoom import Kiwoom
from plus.util import util

import sqlite3 as lite
from datetime import datetime


class CollectData(Kiwoom):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.codelist = []
        self.today = datetime.today()

        getattr(self.ocx, 'OnReceiveRealData').disconnect()
        getattr(self.ocx, 'OnReceiveChejanData').disconnect()
        getattr(self.ocx, 'OnReceiveMsg').disconnect()

    
    #1분봉 데이터 받기
    def getMinData(self):
        item = self.codelist.pop()
        self.con = lite.connect("../data/historical data/{0}.db".format(item[0]), detect_types=lite.PARSE_DECLTYPES)
        self.con.execute('create table if not exists Minute (Date timestamp, High real, Low real, Volume integer)')
        self.lastdate = 0
        with self.con:
            cur = self.con.cursor()
            cur.execute("select Date from Minute order by Date desc limit 1")
            ret = cur.fetchone()
            if ret:
                self.lastdate = ret[0]

        #print("last date: ", self.lastdate)
        
        self.preNext = ""
        self.inputValue = {
            "종목코드" : item[1],
            "시간단위" : "1"
        }
        print(item[1])
        self.sendRequest(item[0], "opc10002", "0000", self.inputValue, "")
    
    def getDailyData(self):
        item = self.codelist.pop()
        self.con = lite.connect("../data/historical data/{0}.db".format(item[0]), detect_types=lite.PARSE_DECLTYPES)
        self.con.execute('create table if not exists Daily (Date timestamp, Open real, High real, Low real, Close real, Volume integer)')

        self.ticks = []
        self.preNext = ""
        self.inputValue = {
            "종목코드" : item[1],
            "조회일자" : "20170219"
        }
        print(item[1])
        #self.sendRequest(item[0], "opc10003", "9999", self.inputValue, "")

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

            Date = datetime.strptime(Date, '%Y%m%d')
            item = (Date, Open, High, Low, Close, Volume)
            items.append(item)

        cur = self.con.cursor()
        with self.con:
            cur.executemany("INSERT INTO Daily ({0}) VALUES(?,?,?,?,?,?)".format(keys), items)

        print("reciveing: ",rqName, " ,  ", preNext)
        if not preNext.strip():
            if self.codelist:
                self.getDailyData()
            else:
                QApplication.quit()

        else:
            time.sleep(0.25)
            self.preNext = preNext
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)

    @KiwoomAPI.on("OnReceiveTrData", screen="0000")
    def __receiveMinute(self, scrNo, rqName, trCode, fieldName, preNext):
        data = self.GetCommFullData(trCode, rqName, 2)
        datalist = [data[i:i+140] for i in range(0, len(data), 140)]
        keys = 'Date, High, Low, Volume'
        cond = False
        items = []
        for row in datalist:
            Date = row[40:60].strip() #시간
            High = row[80:100].strip() #고가
            Low = row[100:120].strip() #저가
            Volume = row[20:40].strip() #거래량

            Date = datetime.strptime(Date, '%Y%m%d%H%M%S')
            interval = (self.today - Date).days
            #1년치 1분 데이터면 충분할듯..
            if (interval > 365) or (Date == self.lastdate):
                cond = True
                break

            item = (Date, High, Low, Volume)
            items.append(item)

        cur = self.con.cursor()
        with self.con:
            cur.executemany("INSERT INTO Minute ({0}) VALUES(?,?,?,?)".format(keys), items)

        print("reciveing: ",rqName, " ,  ", preNext)
        if (not preNext.strip()) or cond:
            if self.codelist:
                self.getMinData()
            else:
                QApplication.quit()

        else:
            time.sleep(0.25)
            self.preNext = preNext
            self.sendRequest(rqName, trCode, scrNo, self.inputValue, preNext)


    @KiwoomAPI.on('OnEventConnect')
    def _connect(self, errCode):
        
        if errCode == 0:
            #종목 정보 취합
            itemList = self.GetGlobalFutureItemlist()
            itemList = util.toList(itemList)

            for var in itemList:
                items = self.GetGlobalFutureCodelist(var)
                item = util.toList(items)[0]
                itemInfo = self.GetGlobalFutOpCodeInfoByCode(item)
                name = re.sub(r'\(.*\).*$', '', itemInfo[18:58]).strip()
                if ('Mini' not in name) and ('Micro' not in name) and ('Miny' not in name):
                    self.codelist.append((name, var+'000'))
                
                tickunit = itemInfo[64:79].strip()
                tickvalue = itemInfo[79:94].strip()
                jinbub = itemInfo[124:125].strip()
                calcunit= itemInfo[125:140].strip()
                flo = itemInfo[158:168].strip()
                print(name,' ',tickunit,' ',tickvalue,' ',jinbub,' ',calcunit,' ',flo)

        #일봉 데이터 받기
        #self.getDailyData()

        #분봉 데이터 받기
        #self.getMinData()

        #db 만들기
        #self.create_db()
    def create_db(self):
        import tables as tb
        self.marketInfo = dict()
        
        FILTERS = tb.Filters(complib='blosc', complevel=9)
        h5file = h5file = tb.open_file("../data/market.hdf5", mode="a", title="Market Data Collection",
                      filters=FILTERS)
        h5file.root._v_attrs.productInfo = self.codelist
        
        
        print(h5file.root._v_attrs.productInfo)
        h5file.close()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.view = QWebEnginePage()
    kiwoom = window.view.kiwoom = CollectData()
    kiwoom.CommConnect(0)
    sys.exit(app.exec_())
