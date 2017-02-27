#-*-coding: utf-8 -*-
# pylint: disable=E1101,E0611
import logging
import sqlite3 as lite
from datetime import datetime
import pandas as pd
import numpy as np

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
    """
        record.db에 저장된 매매기록으로부터 매매 통계를 작성한다

    """
    @pyqtSlot(result=QVariant)
    def getAllData(self):

        items = "entryDate, profit, ticks, commission"
        rawData = pd.read_sql_query("SELECT {0} FROM Records".format(items), self.con)
        deposit = util.load("private")['deposit']

        #가공된 data용 Data frame
        cols = ['date', 'profitOpen', 'profitHigh', 'profitLow', 'profitClose',
                'ticksOpen', 'ticksClose', 'commission']
        data = pd.DataFrame(columns=cols)
        data.date = pd.to_datetime(rawData.entryDate)

        #profit OHLC
        data.profitClose = rawData.profit.cumsum() + deposit
        data.profitOpen = data.profitClose.shift(1)
        data.ix[0, 'profitOpen'] = deposit
        data.profitOpen = data.profitOpen - rawData.commission
        data.profitHigh = np.where(data.profitOpen > data.profitClose, data.profitOpen, data.profitClose)
        data.profitLow = np.where(data.profitOpen > data.profitClose, data.profitClose, data.profitOpen)

        #ticks
        data.ticksClose = rawData.ticks.cumsum()
        data.ticksOpen = data.ticksClose.shift(1)
        data.ix[0, 'ticksOpen'] = 0

        #convert date to unix epoch time
        #data['timestamp'] = data.date.map(lambda x: pd.Timestamp(x).timestamp()*1000)
        data['timestamp'] = data.date.astype("int64")/1000000

        #commission
        data.commission = rawData.commission.cumsum()

        #volume
        data['volume'] = 1

        #normalized data
        data['profit_norm'] = (data.profitClose-data.profitClose.min())/(data.profitClose.max()-data.profitClose.min())*100
        data['ticks_norm'] =(data.ticksClose-data.ticksClose.min())/(data.ticksClose.max()-data.ticksClose.min())*100

        #result (win:1, lose:0)
        data['result'] = np.where(rawData.ticks > 0, 1, 0)

        #cumulative winrate
        data['winrate'] = (data.result.cumsum()/(data.index+1))*100

        #frequncy data
        freqTable = pd.DataFrame()
        ticks_min = rawData.ticks.min() - (rawData.ticks.min()%5)-2.5
        ticks_max = rawData.ticks.max() + (rawData.ticks.min()%5)+2.5
        ticks_rng = np.arange(ticks_min, ticks_max, 5) #data range
        freqTable['ticks_rng'] = ticks_rng[:-1]+2.5
        freqTable['ticks_freq'] = rawData.ticks.groupby(pd.cut(rawData.ticks, ticks_rng)).count().values
        freqTable['ticks_freqP'] = (freqTable['ticks_freq']/freqTable['ticks_freq'].sum())*100

        #web에 전달할 dictionary object 생성
        dataDict = {}
        dataDict['profitOHLC'] = data[['timestamp', 'profitOpen', 'profitHigh', 'profitLow', 'profitClose']].values.tolist() 
        dataDict['tickOHLC'] = data[['timestamp', 'ticksOpen','ticksClose']].values.tolist() 
        dataDict['volume'] = data[['timestamp', 'volume']].values.tolist()
        dataDict['commission'] = data[['timestamp', 'commission']].values.tolist()
        dataDict['result'] = data[['timestamp', 'result']].values.tolist()
        dataDict['winrate'] = data[['timestamp', 'winrate']].values.tolist()
        dataDict['profit'] = data[['timestamp', 'profit_norm']].values.tolist()
        dataDict['ticks'] = data[['timestamp', 'ticks_norm']].values.tolist()
        dataDict['freq_ticks'] = freqTable[['ticks_rng', 'ticks_freqP']].values.tolist()

        return dataDict

    @pyqtSlot(float)
    def saveDeposit(self, dep):
        data = util.load('private')
        data['deposit'] = round(data['deposit'] + dep,2)
        util.toFile('private', data)


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

        if ('strategy' in newRecord) and newRecord['strategy']:
            newRecord['strategy'] = newRecord['strategy'].lower()

        if ('description' in newRecord) and newRecord['description']:
            link = newRecord['description']
            ind = link.find('onenote')
            if ind is not -1:
                newRecord['description'] = link[ind:]

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
    
    @pyqtSlot(int, result=QVariant)
    def getRecordsList(self, page):
        """매매 기록을 DB로부터 로드 """
        recordsList = []
        with self.con:
            cur = self.con.cursor()
            items = "id, entryDate, product, contracts, position, profit, ticks, tradingType \
                     , strategy, description"
            
            #전체 데이터 갯수를 구함
            cur.execute("SELECT seq FROM sqlite_sequence WHERE name = ?",("Records",))
            lastIndex = cur.fetchall()[0][0]-20*page
            
            #레코드를 20개씩 불러옴
            cur.execute("SELECT {0} FROM Records LIMIT 20 OFFSET {1}".format(items,lastIndex))
            rows = cur.fetchmany(20)
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
                record['strategy'] = row[8]
                record['description'] = row[9]
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
                #priceHigh=data[8],
                #priceLow=data[9],
                commission=data[10],
                profit=data[11],
                ticks=data[12],
                duration=data[13],
                tradingType=data[14],
                #reasonBuy=data[15],
                #reasonSell=data[16],
                lossCut=data[17],
                description=data[18],
                #isPlanned=data[19],
                strategy=data[20],
                #profitHigh=data[21],
                #profitLow=data[22],
                #ticksHigh=data[23],
                #ticksLow=data[24]
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