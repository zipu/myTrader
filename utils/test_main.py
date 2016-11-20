# pylint: disable=all
import sys, os, json, logging, pytest
import pywinauto, time
sys.path.append('..')
#os.environ["PYTEST_QT_API"] = "pyqt5"

from PyQt5.QtWidgets import QApplication
from main import Window
from plus.web import MainView
from plus.kiwoom import Kiwoom, util
from plus.kiwoomAPI import KiwoomAPI


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('testlog.md', mode='w', encoding='utf8', delay=False)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = QApplication(sys.argv)
window = Window()
window.view = MainView()
kiwoom = window.view.kiwoom = Kiwoom()


def test_generated_methods_from_json():
    with open("./kiwoomAPI.json", encoding='utf-8') as json_api:
        methods = json.load(json_api)
    methods = methods['METHODS']
    for name, value in methods.items():
        assert hasattr(kiwoom, name)
        

#로그인창 호출 --> 로그인 --> 로그인 Event 수신 --> Error Code 확인
def test_login(qtbot):
    result = kiwoom.login()
    
    #자동 로그인
    pwa_app = pywinauto.application.Application()
    for i in range(10):
        try:
            pwa_app['영웅문w Login'].Wait('ready')
        except:
            time.sleep(1)
            pass
    
    w_handle = pywinauto.findwindows.find_windows(title='영웅문W Login')[0]
    window = pwa_app.window_(handle=w_handle)
    ctrl = window['2']
    ctrl.SetFocus()
    ctrl.TypeKeys('ke840126{TAB}{SPACE}') # password 부분에 본인의 비밀번호 넣기

    with qtbot.waitSignal(kiwoom.ocx.OnEventConnect, timeout=60000, raising=True) as blocker:
        pass
    args = blocker.args[0]
    assert str(args) in KiwoomAPI.ERROR_MESSAGES

#kiwoom.sendRequest로 tr전문을 제대로 받아오는지 테스트
#TrData 요청(kiwoom.sendRequest) --> OnReceiveTrData Event 수신 --> 수신 및 송신 데이터 확인
@pytest.mark.parametrize("rqName, trCode, scrNo, inputValue", [
    ("종목정보", "opt10001", "0001", {"종목코드":"6AM16"}),
    ("관심정보", "opt10005", "0002", {"종목코드":"6AM16;CLN16;6BM16;ZWN16;PLK16"})
])
def test_sendSearch(qtbot, rqName, trCode, scrNo, inputValue):
    logger.info('\n============================================================')
    logger.info('request tr data with trcode %s', rqName)
    logger.info('============================================================')
    
    #조회 요청을 보낸다.
    kiwoom.sendRequest(rqName, trCode, scrNo, inputValue)

    with qtbot.waitSignal(kiwoom.ocx.OnReceiveTrData, timeout=1000, raising=True) as receivedTr:
        #Args:[scrNo, rQName , trCode, fieldName, prevNext]
        pass
    
    kiwoom.disconnect(scrNo)
    logger.info('-sent data: trcode = %s, rqname = %s, input value = %s', trCode, rqName, inputValue)
    logger.info('-recieved data: %s', receivedTr.args)

    assert receivedTr.args[0] == scrNo
    assert receivedTr.args[1] == rqName
    assert receivedTr.args[2] == trCode

#kiwoom.senRequest로 보낸 관심종목 리스트를 제대로 받아오는지 테스트
#sendRequest --> handleProductLists --> bridge signal capture
@pytest.mark.parametrize("inputValue", [
    (["6AM16","CLN16","ZFM16","ZWN16"]),
    (["6AM16","CLN16","6AM16","ZWN16"]),
    ("6AM16;CLN16")
])
def test_productsList(qtbot, inputValue):
    logger.info('\n============================================================')
    logger.info( 'Products List')
    logger.info('=============================================================')
    
    kiwoom.disconnect("0001")
    kiwoom.disconnect("0002")
    kiwoom.getProducts(inputValue)
    cnt = [False, False]
    while True:
        with qtbot.waitSignal(kiwoom.bridge, timeout=2000) as bridge:
            pass
        try:
            if bridge.args[0] == 'onProducts':
                cnt[0] = True
                data = bridge.args[1]
                logger.info('Data passed to bridge: ')
                logger.info(data)
                for code in ["6AM16","CLN16","6AM16","ZWN16"]:
                    assert code in data
                    assert len(data[code]) == 3
                
            elif bridge.args[0] == 'onProducts':
                cnt[1] = True
                data = bridge.args[1]
                logger.info('Received RealData:')
                logger.info(data)
                kiwoom.disconnect('0001')
                for key,value in data.items():
                    assert key in ["6AM16","CLN16","6AM16","ZWN16"]
                    assert len(value) == 3
            if cnt == [True, True]:
                break
        except TypeError:
            logger.info('No data passed to bridge')
            break

def test_getProducts():
    data = kiwoom.getProducts()
    logger.info(data)
    
def test_quit():
    kiwoom.quit()
"""

#kiwoom.request로 opt10081 tr이 전달되어 일봉차트데이터를 잘 받아오는지 테스트
#Tr 요청 --> OnReceiveTrData Event 수신 --> prevNext 확인 --> 반복 tr요청 --> bridge 시그널 capture --> 수신 및 송신 데이터 확인
@pytest.mark.parametrize("trcode, inputvalue, isContinue", [
    ("opt10081", '{"종목코드":"035420", "기준일자" : "20160404", "수정주가구분" : 0}', False)
])
def test_request_trData_opt10081(qtbot, trcode, inputvalue, isContinue):
    logger.info('=======================================================')
    logger.info('request tr data with trcode opt10081 - daily chart data')
    logger.info('=======================================================')
    
    chart_data = dict(
            time=[], open=[], high=[], low=[], close=[], volume=[]
    )
    
    while True:
        scrNo = kiwoom.request(trcode, inputvalue, isContinue)
        with qtbot.waitSignal(kiwoom.ocx.OnReceiveTrData[str, str, str, str, str, int, str, str, str]) as receivedTr:
            #Args:[scrNo, rQName , trCode, recordName, prevNext, dataLength, errorCode, ERROR_MESSAGE, splmMsg]
            with qtbot.waitSignal(kiwoom.bridge) as bridge:
                #Args: [Event Name, return data in dict]
                pass
        
        scrNo_from_Tr = receivedTr.args[0] # this should be '0002'
        prevNext = receivedTr.args[4]
        assert scrNo == scrNo_from_Tr,'screen number should not be changed here'
        
        logger.info('-screen number: %s',scrNo_from_Tr)
        logger.info('-sent data to the server : trcode = %s, input value = %s, isContinue = %s', trcode, inputvalue, isContinue)
        logger.info('-recieved data from the server: %s', receivedTr.args)
        if prevNext == '2':
            isContinue = True
            data_emitted = bridge.args[1]
            for key,val in data_emitted.items():
                chart_data[key].extend(val)
            #chart_data.extend(json.loads(data_emitted['daily_chart']))
        else:
            break
    
    event_name = bridge.args[0] #this should be 'receiveTrData.kiwoom'
    
    logger.info('-emitted data')
    logger.info('   name = %s', event_name)
    for key, val in chart_data.items():
        logger.info('    %s length: %s', key, len(val))
        logger.info('    first data = %s', val[:10]) 
    #logger.info('   last data = %s',  chart_data[-1])
    
    assert event_name == 'receiveTrData.kiwoom'
    assert scrNo == scrNo_from_Tr == "0002"
"""