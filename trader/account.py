#-*-coding: utf-8 -*-
# pylint: disable=E1101,E0611
import logging
from datetime import datetime
import tables as tb
import numpy as np

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QVariant
from .util import util


class Account(QObject):
    """ 
    계좌 입출 및 환전 내역 관리
    Table Structure:
      class Deposit(tb.IsDescription):
            date = tb.StringCol(50, pos=0)
            deposit = tb.FloatCol(pos=1)
            withdraw = tb.FloatCol(pos=2)
            description = tb.StringCol(100, pos=3)

      class Exchange(tb.IsDescription):
            date = tb.StringCol(50, pos=0)
            init_currency = tb.StringCol(50, pos=1)
            init_amount = tb.FloatCol(pos=2)
            dest_currency = tb.StringCol(50, pos=3)
            dest_amount = tb.FloatCol(pos=4)
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.filepath = "./data/account.hdf5"


    @pyqtSlot(QVariant)
    def add_deposit(self, statement):

        with tb.open_file(self.filepath, mode="a") as h5file:
            deposit = h5file.root.deposit
            row = deposit.row
            for key in statement.keys():
                row[key] = statement[key]
            row.append()
            deposit.flush()
        self.logger.info("New deposit added!")


    @pyqtSlot(result=QVariant)
    def load_balances(self):
        balance = []
        with tb.open_file(self.filepath, mode="r") as h5file:
            data = h5file.root.deposit
            for datum in data.iterrows():
                deposit = {}
                deposit['date'] = datum['date'].decode('utf-8')
                deposit['deposit'] = datum['deposit']
                deposit['withdraw'] = datum['withdraw']
                balance.append(deposit)

            return balance

    @pyqtSlot(int)
    def remove_item(self, idx):
        with tb.open_file(self.filepath, mode="a") as h5file:
            deposit = h5file.root.deposit
            deposit.remove_row(idx)