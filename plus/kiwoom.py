# -*- coding: utf-8 -*-

import os, json, logging, re, datetime, time
from collections import defaultdict
from .kiwoomAPI import KiwoomAPI
from .util import util
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QVariant

class Kiwoom(KiwoomAPI):
    """
     Event Handler Usage:
        Any method that decorated with @KiwoomAPI.on("<some_event>") will act as
        a event handler for "some_event". There could be optional keyword argument
        'screen' for 'OnReceiveTrData' and 'realType' for 'OnReceiveTrData'
        ex) @KiwoomAPI.on("OnReceiveTrData", screen='0001')
            def any_method(self, *args):
                //Do something
    """
    bridge = pyqtSignal(str, QVariant)
    loginEvent = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @pyqtSlot()
    def testbed(self):
        self.CommConnect(0)

    @pyqtSlot()
    def quit(self):
        self.CommTerminate()
        super().__init__()

    @pyqtSlot(result=QVariant)
    def login(self):
        state = self.CommConnect(0)
        if state == 0:
            return {'succeed' : True}
        else:
            self.logger.warning("<Send request> %s",util.parseErrorCode(state))
            return {'succeed' : False}

    @pyqtSlot(result=QVariant)
    def connectState(self):
        state = self.GetConnectState()
        if state == 1:
            return {'succeed' : True}
        else:
            return {'succeed' : False}


    @pyqtSlot(str)
    def disconnect(self, scrNo):
        self.DisconnectRealData(scrNo)


    def sendRequest(self, rqName, trCode, scrNo, inputValue, preNext=""):
        """Send Rquest to the server.
        Args:
            rQname (str) : request name  ex) "기본정보"
            trCode (str) : trcode ex) "opt10001"
            scrNo (str) : Four digit string number  ex) "0001"
            inputValue (dict) : input values ex) "{ "종목코드": "6AM16"}"
            preNext (str) : code for continuous request ( default= "" )
        """
        for key, val in inputValue.items():
            self.SetInputValue(key, val)
        ret = self.CommRqData(rqName, trCode, preNext, scrNo)
        if str(ret) in KiwoomAPI.ERROR_MESSAGES:
            self.logger.info("Send request - %s, %s, %s, %s",util.parseErrorCode(ret),\
                              rqName, trCode, scrNo)

    ######################################################################
    ##                                                                  ##
    ##                          Products List Screen                    ##
    ##                            (Screen : 0001)                       ##
    ######################################################################
    @pyqtSlot(result=QVariant)
    def getProducts(self):
        """
            전체종목의  리스트를 불러온다.
        """
        allProducts = dict()
        typelist = util.toList(self.GetGlobalFutureItemTypelist())
        for types in typelist:
            allProducts[types] = dict()
            productslist = util.toList(self.GetGlobalFutureItemlistByType(types))
            for product in productslist:
                allProducts[types][product] = dict()
                codelist = util.toList(self.GetGlobalFutureCodelist(product))
                for code in codelist:
                    allProducts[types][product][code] = dict()
                    codeinfo = self.GetGlobalFutOpCodeInfoByCode(code)
                    name = re.sub(r'\(.*\).*$', '', codeinfo[18:58]).strip()
                    month = codeinfo[150:158].strip()
                    isActive = True if codeinfo[-1] == '1' else False
                    isRecent = True if codeinfo[-2] == '1' else False
                    allProducts[types][product][code] = {
                        "name":name, "month":month, "isActive":isActive, "isRecent":isRecent
                    }
        return allProducts
    
    @pyqtSlot(result=QVariant)
    def getFavList(self):
        """
            Load Favorite list from the file favorites.json
        """
        data = {}
        flist = list(util.load('favorite'))
        for code in flist:
            codeinfo = self.GetGlobalFutOpCodeInfoByCode(code)
            if not codeinfo:
                print("%s 종목의 만기일이 만료되었습니다"%code)
                flist.remove(code)
                self.addToFav(flist)
                continue
                
            name = re.sub(r'\(.*\).*$', '', codeinfo[18:58]).strip()
            month = codeinfo[150:158].strip()
            month = month[2:4]+'/'+month[4:6]+'/'+month[6:8]
            isActive = True if codeinfo[-1] == '1' else False
            isRecent = True if codeinfo[-2] == '1' else False
            data[code] = {"name":name, "month":month, "isActive":isActive, "isRecent":isRecent}
        
        return data

    @pyqtSlot(QVariant)
    def addToFav(self, codes):
        """ 
            관심종목 등록 
            codes: string[]
        """
        util.toFile('favorite', codes)


    @pyqtSlot(str, QVariant)
    def requestProductsReal(self, scrNo, inputValue):
        """
        inputValue(list) : ["6AM16","CLN16","ZFM16","ZWN16"]
        """
        inputValue = {"종목코드" : util.toString(set(inputValue))}
        #inspect input value
        #if (len(inputValue) != 1) \
        #  or not isinstance(inputValue['종목코드'], list):
        #    self.logger.warning("inputValue is wrong: %s", inputValue)
        #else:
        self.sendRequest("관심종목", "opt10005", scrNo, inputValue)

    @KiwoomAPI.on('OnReceiveTrData', screen='0001')
    def _onTrProducts(self, scrNo, rqName, trCode, fieldName, preNext):
        """
        관심종목 조회 결과 처리
        """
        data = defaultdict(list)
        cnt = self.GetRepeatCnt(trCode, rqName)
        for i in range(cnt):
            code = self.GetCommData(trCode, rqName, i, "종목코드")
            data[code].append(self.GetCommData(trCode, rqName, i, "현재가"))
            data[code].append(self.GetCommData(trCode, rqName, i, "전일대비"))
            volumn = self.GetCommData(trCode, rqName, i, "누적거래량")
            data[code].append(format(int(volumn), ',d'))

        self.bridge.emit("_onProducts", dict(data))



    ######################################################################
    ##                                                                  ##
    ##                          Products Info Screen                    ##
    ##                            (Screen : 0002)                       ##
    ######################################################################
    @pyqtSlot(str)
    def getProductInfo(self, code):
        inputValue = {"종목코드" : code}
        self.sendRequest("종목정보", "opt10001", "0002", inputValue)

        inputValue = {
            "조회일자" : datetime.datetime.now().strftime("%Y%m%d"),
            "종목코드" : code
        }
        self.sendRequest("증거금", "opw30008", "0002", inputValue)

    @KiwoomAPI.on('OnReceiveTrData', screen='0002')
    def _onProductInfo(self, scrNo, rqName, trCode, fieldName, preNext):
        """
         조회 결과 처리
        """
        if trCode == 'opt10001':
            expirate = self.GetCommData(trCode, rqName, 0, "최종거래")
            expirate = expirate[0:4]+'/'+expirate[4:6]+'/'+expirate[6:8]
            openDate = self.GetCommData(trCode, rqName, 0, "영업일자")
            openDate = openDate[0:4]+'/'+openDate[4:6]+'/'+openDate[6:8]
            data = {
                'market' : self.GetCommData(trCode, rqName, 0, "거래소"),
                'currency' : self.GetCommData(trCode, rqName, 0, "결제통화"),
                'expirate' : expirate,
                'remained' : self.GetCommData(trCode, rqName, 0, "잔존만기"),
                'openDate' : openDate,
                'tickValue' : self.GetCommData(trCode, rqName, 0, "틱가치"),
                'openTime' : self.GetCommData(trCode, rqName, 0, "시작시간"),
                'closeTime' : self.GetCommData(trCode, rqName, 0, "종료시간")
            }
            self.bridge.emit("onProductInfo", data)

        elif trCode == 'opw30008':
            margin = self.GetCommData(trCode, rqName, 0, "위탁증거금")
            margin = format(int(margin[-6:-2]), ',d')
            self.bridge.emit("onProductInfo", {'margin': margin})

    ######################################################################
    ##                                                                  ##
    ##                          Modal Info Screen                       ##
    ##                            (Screen : 0003)                       ##
    ######################################################################
    @KiwoomAPI.on('OnReceiveTrData', screen='0003')
    def _onTrModal(self, scrNo, rqName, trCode, fieldName, preNext):
        """
        Modal 조회 결과 처리
        """
        data = defaultdict(list)
        cnt = self.GetRepeatCnt(trCode, rqName)
        for i in range(cnt):
            code = self.GetCommData(trCode, rqName, i, "종목코드")
            data[code].append(self.GetCommData(trCode, rqName, i, "현재가"))
            data[code].append(self.GetCommData(trCode, rqName, i, "전일대비"))
            volumn = self.GetCommData(trCode, rqName, i, "누적거래량")
            data[code].append(format(int(volumn), ',d'))

        self.bridge.emit("onGoods", dict(data))


    ######################################################################
    ##                                                                  ##
    ##                             Chart Screen                         ##
    ##                            (Screen : 0004)                       ##
    ######################################################################
    @pyqtSlot(str)
    def getChartData(self, code, preNext=""):
        self.selectedProduct = code
        self.preNext = preNext
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        inputValue = {
            "종목코드" : code,
            "조회일자" : today
        }
        self.sendRequest("ChartData", "opc10003", "0004", inputValue, preNext)


    @KiwoomAPI.on('OnReceiveTrData', screen='0004')
    def _onChartData(self, scrNo, rqName, trCode, fieldName, preNext):
        """
         조회 결과 처리
        """
        #self.chartData += self.GetCommFullData(trCode, rqName, 2)
        data = self.GetCommFullData(trCode, rqName, 2)
        #if preNext != self.preNext:
        #    time.sleep(0.1)
        #    self.getChartData(self.selectedProduct, preNext)
        #elif preNext == self.preNext:
        self.bridge.emit("onChartData", data)
        #    self.chartData = ""




    ######################################################################
    ##                                                                  ##
    ##                          이벤트 및 실시간 데이터 처리              ##
    ##                                                                  ##
    ######################################################################
    @KiwoomAPI.on('OnReceiveRealData', realType="해외선물시세")
    def _onRealProducts(self, jongmokCode, realType, realData):
        """
        실시간 데이터 처리:
        """
        #realData = util.toList(realData)
        #data = [jongmokCode, [realData[1], realData[3], format(int(realData[8]), ',d')]
        data = jongmokCode+';'+realData
        self.bridge.emit("onRealPrice", data)

        if len(util.toList(realData)) != 16:
            self.logger.warning("실시간 데이터 형식이 바뀐것 같습니다")

    #errCode: 0 - 로그인 성공, 음수 - 로그인 실패
    @KiwoomAPI.on('OnEventConnect')
    def _connect(self, errCode):
        self.logger.info('로그인 - ' + util.parseErrorCode(errCode))
        self.loginEvent.emit(errCode)

    @KiwoomAPI.on('OnReceiveMsg')
    def _receiveMsg(self, scrNo, rqName, trCode, msg):
        data = dict(
            scrNo=scrNo, rqName=rqName, trCode=trCode, msg=msg
        )
        self.bridge.emit("onReceiveMsg", data)