import sqlite3 as lite
import sys

con = lite.connect('./data/history.db')

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE Statements(\
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
        date_in TEXT NOT NULL,\
        date_out TEXT,\
        product  TEXT NOT NULL,\
        contracts INGETER NOT NULL,\
        position TEXT NOT NULL,\
        tick_diff TEXT,\
        emotion TEXT,\
        weather TEXT,\
        plan TEXT,\
        reason_in TEXT,\
        reason_out TEXT,\
        imgurls TEXT,\
        discussion TEXT,\
        isPlanned INTEGER,\
        orderType TEXT,\
        slippage INTEGER,\
        result TEXT,\
        type TEXT)")
    