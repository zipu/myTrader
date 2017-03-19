# -*- coding: utf-8 -*-
import sys
import logging
from datetime import datetime

import tables as tb
import pandas as pd
import numpy as np
import scipy.sparse as sp


class Calc():

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        #open DB
        filters = tb.Filters(complib='blosc', complevel=9)
        self.h5file = tb.open_file("../data/market.hdf5", mode="a",
                                   title="Market Data Collection", filters=filters)
        self.marketinfo = self.h5file.root._v_attrs.marketinfo

    def density(self):
        """
            Getting density distribution
        """
        now = np.datetime64(datetime.now())+np.timedelta64(1,'h')
        cnt = 0
        for typ in self.h5file.iter_nodes('/'):
            for item in self.h5file.iter_nodes(typ):
                if item.Distribution.shape[0]:
                    cnt += 1
                    print(item, ' cnt: %s'%cnt)

                    #환경 변수
                    tick = self.marketinfo[typ._v_name][item._v_name]['tick_unit'] #틱 단위
                    digit = self.marketinfo[typ._v_name][item._v_name]['digit'] #소숫점 자리수

                    #실제 데이터
                    value = item.Distribution.read(field="value") #density
                    value[value == np.inf] = 0 #inf 값은 0으로..
                    price = item.Distribution.read(field="price").round(digit) #가격. 반올림
                    rows = item.Distribution.read(field="row")
                    dates = item.Date.read(field="date")
                    #idx = item.Date.read(field="index")
                    columns = np.rint((price-price.min())/tick)

                    #sparse matrix creation
                    shape = (rows.max()+1, columns.max()+1)
                    matrix = sp.csr_matrix((value, (rows, columns)), shape=shape)

                    #scale factor creation
                    delta = (np.datetime64(now) - dates.astype('M8[s]'))/np.timedelta64(1,'D')+1 
                    scale = sp.diags(1/(np.sqrt(delta)))

                    #normalized density distribution creation
                    density = np.squeeze(np.asarray((scale*matrix).sum(axis=0)))
                    normed_density = density/density.sum()
                    x_ticks = np.arange(price.min(), price.max()+tick/2, tick).round(digit).tolist()
                    array = np.array([x_ticks, normed_density])

                    #save to db
                    if hasattr(item, 'density'):
                        item.density.remove()

                    self.h5file.create_array(item, 'density', array, shape=array.shape)

        print("Density distribution successfully created")
        self.h5file.close()


        