/**** Market Component ****/
export class Products {
  market: string;  //시장 구분
  codes: string[]; //종목 코드 리스트
  selectedProduct: string; //선택된 종목
  list: Object; //상품목록 세부 정보
  constructor(market: string=''){
    this.market = market;
    this.codes = [];
  }   
}


export class Product {

  // 종목 기본정보
  code: string; //종목코드
  name: string; //종목이름
  month: string; //월물
  isActive: boolean; //액티브 월물?
  isRecent: boolean; //최근 월물?
  market: string;  //상품군
  groupname: string; //그룹네임 ex)CUR6A
  currency: string; //결재통화
  margin: string; //증거금
  expirate: string; //만기일
  remained: string; //잔존 만기
  openDate: string; //영업일
  tickValue: string; //틱 가치
  tickUnit: string; //틱 단위
  openTime: string; //장시작시간
  closeTime: string; //장종료시간
  
  //가격 정보
  price: string; //가격
  diff: string; //전일대비
  volumn: string; //거래량
  
  //데이터
  size: number;
  
  constructor(code: string, name: string, month: string, groupname:string, market:string) {
    this.code = code;
    this.name = name;
    this.month = month;
    this.groupname = groupname;
    this.market = market;
    this.size = 20; // 기본 매매 사이즈 --> 최적 매매 사이즈를 결정하도록 추후 변경
  }
}


/***** RecordComponent *****/

export class Record {

    //1. 기초 데이터
    public index: number; //넘버
    public product: string; //상품명
    public entryDate: string; //진입 날짜
    public exitDate: string; //청산 날짜
    public contracts: number; //계약수
    public position: number; //매매 포지션 - 1: long, -1:short
    public priceOpen: number; //진입 가격
    public priceClose: number; //청산 가격
    //public priceHigh: number; //보유중 최고가
    //public priceLow: number; //보유중 최저가

    //2. 결과 데이터
    public commission: number; //수수료
    public profit: number; //손익
    public ticks: number; //수익(틱)
    //public profitHigh: number;
    //public profitLow: number;
    //public ticksHigh: number;
    //public ticksLow: number;
    public duration: string; //포지션 보유 기간
    public tradingType: string; //타임 프레임
    
    //3. 매매전략
    //public reasonBuy: string; //진입 사유
    //public reasonSell: string; //청산 사유
    public strategy: string; //매매전략
    public lossCut: string; //손절 가격
    public description: string; //one-note 매매 설명 페이지로 링크
    //public isPlanned: boolean; //매매를 계획대로 했는지 여부

    constructor() {
      this.index = 0;
      this.contracts = 1;
     }

}

export class RecordInfo {
  public product: string;
  public tickPrice: string;
  public tickValue: string;
  public commission: number;
  public notation: number;
}


/***** Account Component *****/
export class Balance {
  public date: string;
  public deposit: number;
  public withdraw: number;
  public description: string;

  constructor(date:string){
    this.date = date;
  }
}