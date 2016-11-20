#-*-coding: utf-8 -*-
import logging
import sqlite3 as lite
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QVariant
from .util import util

class History(QObject):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.con = lite.connect("./data/history.db")

    @pyqtSlot(str)
    def save(self, statement):
        """매매기록을 db에 저장"""
        statement = util.toDict(statement)
        statement['imgurls'] = util.toString(statement['imgurls'])
        if ('date_out' in statement) and statement['date_out']:
            start = datetime.strptime(statement['date_in'], '%Y-%m-%dT%H:%M')
            end = datetime.strptime(statement['date_out'], '%Y-%m-%dT%H:%M')
            duration = (end-start).__str__()
            statement['duration'] = duration[0:-6]+'h'+(end-start).__str__()[-5:-3]+'m'

        if 'profit' in statement and statement['profit']:
            if statement['profit'] > 0 :
                statement['result'] = 'Win'
            elif statement['profit'] < 0 : 
                statement['result'] = 'Lose'
            elif statement['profit'] == 0 :
                statement['result'] = 'Draw'

        with self.con:
            cur = self.con.cursor()
            keys = ','.join(statement.keys())
            values = tuple(statement.values())
            questions = ','.join(['?' for i in range(len(statement))])
            cur.execute("INSERT INTO Statements({0}) VALUES({1})".format(keys,questions), values)
    
    @pyqtSlot(int, str)
    def update(self, id, statement):
        """매매기록 수정"""
        statement = util.toDict(statement)
        statement['imgurls'] = util.toString(statement['imgurls'])
        if ('date_out' in statement) and statement['date_out']:
            start = datetime.strptime(statement['date_in'], '%Y-%m-%dT%H:%M')
            end = datetime.strptime(statement['date_out'], '%Y-%m-%dT%H:%M')
            duration = (end-start).__str__()
            statement['duration'] = duration[0:-6]+'h'+(end-start).__str__()[-5:-3]+'m'

        if 'profit' in statement and statement['profit']:
            if statement['profit'] > 0 :
                statement['result'] = 'Win'
            elif statement['profit'] < 0 : 
                statement['result'] = 'Lose'
            elif statement['profit'] == 0 :
                statement['result'] = 'Draw'

        with self.con:
            cur = self.con.cursor()
            keys = '=?,'.join(statement.keys())
            values = tuple(statement.values())+(id,)
            cur.execute("UPDATE Statements SET {0}=? WHERE Id=?".format(keys), values)

    @pyqtSlot(int)
    def delete(self, id):
        """매매 기록 db에서 삭제"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("DELETE from Statements WHERE ID=?", (id,))
            cur.execute("UPDATE Statements SET Id= Id-1 WHERE Id > ?", (id,))
            cur.execute("UPDATE sqlite_sequence SET seq= seq-1 WHERE name='Statements'")

    @pyqtSlot(result=QVariant)
    def getDBList(self):
        """매매기록을 db로부터 로드"""
        historydb = []
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id, date_in, date_out, product, contracts, position, tick_diff, result, duration, profit, commission FROM Statements")
            rows = cur.fetchall()
            for row in rows:
                statement = {}
                statement['index'] = row[0]
                #statement['type'] = row[1]
                statement['date_in'] = row[1][0:-6]
                #statement['date_out'] = row[3]
                statement['product'] = row[3]
                statement['contracts'] = row[4]
                statement['position'] = row[5]
                statement['tick_diff'] = row[6]
                statement['result'] = row[7]
                statement['duration'] = row[8]
                statement['profit'] = row[9]
                statement['commission'] = row[10]

                if row[2]:
                    start = datetime.strptime(row[1], '%Y-%m-%dT%H:%M')
                    end = datetime.strptime(row[2], '%Y-%m-%dT%H:%M')
                    #duration = (end-start).__str__()
                    #statement['duration'] = duration[0:-6]+'h'+(end-start).__str__()[-5:-3]+'m'
                    if (end-start).days == 0:
                        statement['time_frame'] = 'intraday'
                    elif (end-start).days > 0 and (end-start).days < 8:
                        statement['time_frame'] = 'swing'
                    elif  (end-start).days > 7:
                        statement['time_frame'] = 'long term'
                historydb.insert(0, statement)
        return historydb

    @pyqtSlot(int, result=QVariant)
    def getStatement(self, id):
        # id에 해당하는 Statement를 DB에서 불러온다
        statement = {}
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM Statements WHERE Id=:Id", {"Id": id})
            data = cur.fetchone()
            statement['date_in'] = data[1]
            statement['date_out'] = data[2]
            statement['product'] = data[3]
            statement['contracts'] = data[4]
            statement['position'] = data[5]
            statement['tick_diff'] = data[6]
            statement['emotion'] = data[7]
            statement['weather'] = data[8]
            statement['plan'] = data[9]
            statement['reason_in'] = data[10]
            statement['reason_out'] = data[11]
            statement['imgurls'] = data[12]
            statement['discussion'] = data[13]
            statement['isPlanned'] = data[14]
            statement['orderType'] = data[15]
            statement['commission'] = data[16]
            statement['result'] = data[17]
            statement['duration'] = data[18]
            statement['profit'] = data[19]

        return statement
