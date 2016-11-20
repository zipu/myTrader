angular.module('tradeSystem')
    .factory('KiwoomService', ['$filter', '$q', function($filter, $q) {

        new QWebChannel(qt.webChannelTransport, function(channel) {
            var kiwoom = window.kiwoom = channel.objects.kiwoom;
            kiwoom.bridge.connect(function(event, data) {
                console.info('< ' + event + ' > received from the server...');
                window.test = data;
                if (event=="receiveTrData.kiwoom" && data.trcode == "opt10081"){
                    console.log('hello')
                    chart(data);
                }
                
            });
        });

        var login = function() {
            kiwoom.login()
                .then(function() {
                    kiwoom.loginEvent.connect(function(event, errCode) {
                        kiwoom.parseErrorCode(errCode).then(function(e) {
                            console.info('로그인 :' + e);
                        });
                    });
                }, function() {
                    console.info('이미 연결중입니다');
                });
        };

        var userInfo = function() {
            var deferred = $q.defer();
            kiwoom.userInfo().then(function(info) {
                deferred.resolve(info);
            });
            return deferred.promise;
        };

        var chart = function(data) {
            var ids = Bokeh._.keys(Bokeh.index);
            var plot = Bokeh.index[ids[0]];
            var d = plot.model.document._all_models_by_name._existing('data')[0]
            var source = d.attributes.data;
            source.time = data.time;
            source.open = data.open;
            source.high = data.high;
            source.low = data.low;
            source.close = data.close;
            d.trigger('change');
           // UserInfo().then(function(e) {
           //     console.log(JSON.stringify(e));
           // });
           // kiwoom.setInputValue('종목코드', code);
           // kiwoom.setInputValue('기준일자', $filter('date')(new Date(), 'yyyyMMdd'));
           // kiwoom.setInputValue('수정주가구분 ', 0);
            // rQName과 화면번호는 사용자가 지정하여 구분하는 값
           // kiwoom.commRqData('주식일봉차트조회요청', 'opt10081', 0, '0002');
        };

        var search = function(code) {
            kiwoom.setInputValue('종목코드', code);
            // rQName과 화면번호는 사용자가 지정하여 구분하는 값
            kiwoom.commRqData('주식기본정보', 'opt10001', 0, '0001');

        };
        var eventHandler = (function() {
            return {
                'receiveMsg.kiwoom': function(data) {
                    console.info(data);
                },

                'receiveTrData.kiwoom': function(data) {
                    // kiwoom.getRepeatCnt(data.trCode, data.rQName).then(function(len){
                    //       console.info('rQName : '+data.rQName+', trCode: '+data.trCode+', repeadCnt : '+len);
                    // });
                    //kiwoom.test('opt10001', '주식기본정보').then(function(e) {console.log(e)});
                    switch (data.trCode) {
                        case 'opt10001':
                            for (var i = 0; i < len; i++) {
                                console.log('TR 데이터', {
                                    // "종목명" : kiwoom.commGetData(data.trCode, "", data.rQName, i, "종목명"),
                                    // "시가총액" : kiwoom.commGetData(data.trCode, "", data.rQName, i, "시가총액"),
                                    // "거래량" : kiwoom.commGetData(data.trCode, "", data.rQName, i, "거래량"),
                                    // "현재가" : kiwoom.commGetData(data.trCode, "", data.rQName, i, "현재가")
                                    '종목명': kiwoom.plusGetTrData(data.trCode, data.rQName, i, '종목명'),
                                    '시가총액': kiwoom.plusGetTrData(data.trCode, data.rQName, i, '시가총액'),
                                    '거래량': kiwoom.plusGetTrData(data.trCode, data.rQName, i, '거래량'),
                                    '현재가': kiwoom.plusGetTrData(data.trCode, data.rQName, i, '현재가')
                                });
                            }
                            break;
                        case 'opt10081':
                            console.log('TR 데이터', JSON.parse(kiwoom.getCommDataEx(data.trCode, data.rQName)));
                            break;
                    }
                },

                'receiveRealData.kiwoom': function(data) {
                    console.info('실시간데이터', {
                        'jongmokCode': data.jongmokCode,
                        'realType': data.realType,
                        'realData': data.realData
                    });
                    console.log(kiwoom.plusGetRealData(data.jongmokCode, data.realType, 10));
                }
            };
        })();

        return {
            login: login,
            userInfo: userInfo,
            chart: chart,
            search: search
        };
    }]);