#-*-coding: utf-8 -*-
import logging
import sqlite3 as lite
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QVariant
from .util import util

class Record(QObject):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.con = lite.connect("./data/record.db")

    @pyqtSlot()
    def test(self):
        print(self.getProductInfo('EUR/USD'))
    
    @pyqtSlot(str)
    def saveRecord(self, record):
        """ 매매기록을 dB에 저장"""
        from decimal import Decimal, getcontext #부동 소숫점 연산
        getcontext().prec = 6
        
        newRecord = util.toDict(record)
        productInfo = self.getProductInfo(newRecord['product']) #종목정보

        if ('exitDate' in newRecord) and newRecord['exitDate']:
            #청산시간 - 진입시간 계산하여 duration에 저장
            start = datetime.strptime(newRecord['entryDate'], '%Y-%m-%dT%H:%M')
            end = datetime.strptime(newRecord['exitDate'], '%Y-%m-%dT%H:%M')
            duration = end-start
            newRecord['duration'] = duration.__str__()[0:-6]+'h'+duration.__str__()[-5:-3]+'m'

            #매매 타임 프레임 결정
            if duration.days > 7:
                newRecord['tradingType'] = 'Long Term'
            elif (duration.days <= 7) and (duration.days > 0):
                newRecord['tradingType'] = 'Swing'
            elif duration.days == 0:
                newRecord['tradingType'] = 'Intraday'

        #수익 계산 -- 일단 10진법만 생각. 나중에 수정필요
        if ('priceClose' in newRecord) and newRecord['priceClose']:
            priceOpen = Decimal(newRecord['priceClose'])
            priceClose = Decimal(newRecord['priceOpen'])
            sign = 1 if newRecord['position']=='Long' else -1
            price_diff = (priceOpen-priceClose) * sign
            ticks = int(price_diff / Decimal(productInfo['tickPrice']))
            profit = float((ticks * Decimal(productInfo['tickValue']) \
                     - Decimal(newRecord['commission'])) * newRecord['contracts'])

            newRecord['ticks'] = ticks
            newRecord['profit'] = profit

        #save to DB
        curId = newRecord.pop('index') #레코드에서 인덱스를 없애야함, id는 검색할때 필요
        #new Record
        with self.con:
            cur = self.con.cursor()
            if curId == 0:
                keys = ','.join(newRecord.keys()) #sqlitet3 쿼리용
                values = tuple(newRecord.values())
                questions = ','.join(['?' for i in range(len(newRecord))])
                cur.execute("INSERT INTO Records({0}) VALUES({1})".format(keys, questions), values)
            elif curId > 0:
                keys = '=?,'.join(newRecord.keys()) #sqlitet3 쿼리용
                values = tuple(newRecord.values()) + (curId,)
                cur.execute("UPDATE Records SET {0}=? WHERE Id=?".format(keys), values)


    @pyqtSlot(result=QVariant)
    def getRecordsList(self):
        """매매 기록을 DB로부터 로드 """
        recordsList = []
        with self.con:
            cur = self.con.cursor()
            items = "id, entryDate, product, contracts, position, profit, ticks, tradingType \
                     , reasonBuy, description, star"
            cur.execute("SELECT {0} FROM Records".format(items))
            rows = cur.fetchall()
            for row in rows:
                record = {}
                record['index'] = row[0]
                record['entryDate'] = row[1][0:-6]
                record['product'] = row[2]
                record['contracts'] = row[3]
                record['position'] = row[4]
                record['profit'] = row[5]
                record['ticks'] = row[6]
                record['tradingType'] = row[7]
                record['reasonBuy'] = row[8]
                record['description'] = row[9]
                record['star'] = row[10]
                recordsList.insert(0, record)
        return recordsList
    
    @pyqtSlot(int, result=QVariant)
    def getRecord(self, id):
        #id에 해당하는 record를 db에서 불러오기
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM Records WHERE Id=:Id", {"Id": id})
            data = cur.fetchone()
            record = dict(
                index=data[0],
                product=data[1],
                entryDate=data[2],
                exitDate=data[3],
                contracts=data[4],
                position=data[5],
                priceOpen=data[6],
                priceClose=data[7],
                priceHigh=data[8],
                priceLow=data[9],
                commission=data[10],
                profit=data[11],
                ticks=data[12],
                duration=data[13],
                tradingType=data[14],
                reasonBuy=data[15],
                reasonSell=data[16],
                lossCut=data[17],
                description=data[18],
                isPlanned=data[19],
                star=data[20],
            )
        return record

    @pyqtSlot(int)
    def deleteRecord(self, index):
        """ DB에서 매매기록 삭제 """
        with self.con:
            cur = self.con.cursor()
            cur.execute("DELETE from Records WHERE ID=?", (index,))
            cur.execute("UPDATE Records SET Id= Id-1 WHERE Id > ?", (index,))
            cur.execute("UPDATE sqlite_sequence SET seq= seq-1 WHERE name='Records'")

    @pyqtSlot(str)
    def addInfo(self, newRecord):
        """ 종목정보를 db에 저장 """
        newRecord = util.toDict(newRecord)
        with self.con:
            cur = self.con.cursor()
            keys = ','.join(newRecord.keys())
            values = tuple(newRecord.values())
            questions = ','.join(['?' for i in range(len(newRecord))])
            cur.execute("INSERT INTO RecordInfo({0}) VALUES({1})".format(keys, questions), values)

    @pyqtSlot(result=QVariant)
    def getInfo(self):
        """ 종목정보를 db에서 불러옴"""
        infoList = []
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT  id, product, tickPrice, tickValue, commission, notation FROM RecordInfo")
            rows = cur.fetchall()
            for row in rows:
                info = {}
                info['index'] = row[0]
                info['product'] = row[1]
                info['tickPrice'] = row[2]
                info['tickValue'] = row[3]
                info['commission'] = row[4]
                info['notation'] = row[5]
                infoList.append(info)
        return infoList

    @pyqtSlot(int)
    def removeInfo(self, id):
        """ 종목정보 삭제"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("DELETE from RecordInfo WHERE ID=?", (id,))
            cur.execute("UPDATE RecordInfo SET Id= Id-1 WHERE Id > ?", (id,))
            cur.execute("UPDATE sqlite_sequence SET seq= seq-1 WHERE name='RecordInfo'")
    
    def getProductInfo(self, product):
        """ 내부적으로 처리할때 종목 정보 불러오기 """
        productInfo = {}
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM RecordInfo WHERE product=:Product", {"Product": product})
            data = cur.fetchone()
            productInfo['product'] = data[1]
            productInfo['tickPrice'] = data[2]
            productInfo['tickValue'] = data[3]
            productInfo['commission'] = data[4]
            productInfo['notation'] = data[5]
        return productInfo


