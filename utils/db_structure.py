"""
 pytables 라이브러리용 DB에 저장될 데이터 구조선언 클래스
 last update: 2017.02.25

 File
    - _v_attrs: 종목 기본정보 (상품군, 상품명, 코드, 틱 가치 등)
    - 그룹: Market - Products - (OHLC, densityRaw, dateRaw, Density as vector, Gradient as vector)
    - Market._v_attrs : 
    - OHLC.attrs: 평균, 표준편차, 상품간 상관도
    - 
    -
    -
    
"""
import tables as tb

class Distribution(tb.IsDescription):
    """
    kind of volume distribution
    Table structure:
        - date : POSIX 시간(초)을 Integer 형태로 저장
        - value : 거래량 / (고가 - 저가)
        - price : 각 value의 column index
    """
    dates = tb.Time32Col(pos=0)
    price = tb.Float64Col(pos=1)
    value = tb.UInt16Col(pos=2)

class OHLC(tb.IsDescription):
    """
    일봉데이터
    Table structure:
        - date : POSIX 시간(초)을 Integer 형태로 저장
        - open : 시가
        - high: 고가
        - low: 저가
        - close: 종가
        - volume: 거래량
    """
    date = tb.Time32Col(pos=0)
    open = tb.Float32Col(pos=1)
    high = tb.Float32Col(pos=2)
    low = tb.Float32Col(pos=3)
    close = tb.Float32Col(pos=4)
    volume = tb.UInt32Col(pos=5)
