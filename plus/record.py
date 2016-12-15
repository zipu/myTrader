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

    
    ######################################################################
    #    Overview 화면용 Methods                                          #
    ######################################################################
    @pyqtSlot(result=QVariant)
    def getAllData(self):
        """ 통계용 데이터를 DB에서 부름 """
        data = dict(
            profit=[], ticks=[], commission=[]
        )

        with self.con:
            cumProfit = 0 #누적 수익
            cumTicks = 0 #누적 틱
            cumComm = 0 #누적 수수료

            cur = self.con.cursor()
            items = "entryDate, profit, profitHigh, profitLow, \
                     ticks, ticksHigh, ticksLow, commission"
            cur.execute("SELECT {0} FROM Records".format(items))
            rows = cur.fetchall()
            for row in rows:
                date = int(datetime.strptime(row[0], '%Y-%m-%dT%H:%M').timestamp() * 1000)
                profit_ohlc = [date, cumProfit, cumProfit+float(row[2] or 0), cumProfit+float(row[3] or 0), cumProfit+float(row[1] or 0), 1 ]
                ticks_ohlc = [date, cumTicks, cumTicks+int(row[5] or 0), cumTicks+int(row[6] or 0), cumTicks+float(row[4] or 0), 1]

                data['profit'].append(profit_ohlc)
                data['ticks'].append(ticks_ohlc)
                data['commission'].append(cumComm+float(row[7]))

                cumProfit = cumProfit + float(row[1] or 0)
                cumTicks = cumTicks + float(row[4] or 0)
                cumComm = cumComm + row[7]
        return data

    ######################################################################
    #    Records 화면용 Methods                                          #
    ######################################################################
    @pyqtSlot(str)
    def saveRecord(self, record):
        """ 매매기록을 dB에 저장"""
        
        newRecord = util.toDict(record)
        productInfo = self.getProductInfo(newRecord['product']) #종목정보
        newRecord['commission'] = newRecord['contracts'] * productInfo['commission']

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
            (newRecord['ticks'], newRecord['profit']) \
             = self.calcDiff(productInfo, newRecord['position'], newRecord['contracts'], newRecord['priceOpen'], newRecord['priceClose'])
            if ('priceHigh' not in newRecord) or (not newRecord['priceHigh']):
                newRecord['priceHigh'] = newRecord['priceOpen'] if newRecord['priceOpen'] > newRecord['priceClose'] else newRecord['priceClose']
            if ('priceLow' not in newRecord) or (not newRecord['priceLow']):
                newRecord['priceLow'] = newRecord['priceClose'] if newRecord['priceOpen'] > newRecord['priceClose'] else newRecord['priceOpen']
            (ticksHigh, profitHigh) \
                   = self.calcDiff(productInfo, newRecord['position'], newRecord['contracts'], newRecord['priceOpen'], newRecord['priceHigh'])
            (ticksLow, profitLow) \
                   = self.calcDiff(productInfo, newRecord['position'], newRecord['contracts'], newRecord['priceOpen'], newRecord['priceLow'])
            
            if newRecord['position'] == 'Long':
                newRecord['ticksHigh'] = ticksHigh
                newRecord['profitHigh'] = profitHigh
                newRecord['ticksLow'] = ticksLow
                newRecord['profitLow'] = profitLow
            else:
                newRecord['ticksHigh'] = ticksLow
                newRecord['profitHigh'] = profitLow
                newRecord['ticksLow'] = ticksHigh
                newRecord['profitLow'] = profitHigh
        
        if ('reasonBuy' in newRecord) and newRecord['reasonBuy']:
            newRecord['reasonBuy'] = newRecord['reasonBuy'].lower()
        
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


    def calcDiff(self, info, position, contracts, first, last):
        """ 가격 차이 계산 """
        from decimal import Decimal, getcontext #부동 소숫점 연산
        getcontext().prec = 6
        
        sign = 1 if position == 'Long' else -1
        unit = Decimal(info['tickPrice'])
        value = Decimal(info['tickValue'])
        commission = Decimal(info['commission'])
        contracts = Decimal(contracts)
        first = Decimal(first)
        last = Decimal(last)

        diff = (last - first)* sign
        ticks = int(diff / unit)
        profit = float((ticks * value - commission)*contracts)
        return (ticks, profit)
    
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
                profitHigh=data[21],
                profitLow=data[22],
                ticksHigh=data[23],
                ticksLow=data[24]
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

    @pyqtSlot(result=QVariant)
    def getStrategy(self):
        """ 매매전략 자동완성용 db """
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT  strategy FROM Strategy")
            rows = cur.fetchall()
            strategies = [x[0] for x in rows]
        return strategies

    @pyqtSlot(str)
    def addStrategy(self,newStrat):
        with self.con:
            cur = self.con.cursor()
            cur.execute("INSERT INTO Strategy(strategy) VALUES(?)", (newStrat.lower(),))