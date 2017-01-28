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
  code: string;
  name: string;
  month: string;
  isActive: boolean;
  isRecent: boolean;
  price: string;
  diff: string;
  volumn: string;
  chart: any[];
  constructor(code: string, name: string, month: string) {
    this.code = code;
    this.name = name;
    this.month = month;
  }
}


// this will be deprecated.. 
export class ProductInfo {
  market: string;
  currency: string;
  margin: string;
  expirate: string;
  remained: string;
  openDate: string;
  tickValue: string;
  openTime: string;
  closeTime: string;
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
    public priceHigh: number; //보유중 최고가
    public priceLow: number; //보유중 최저가

    //2. 결과 데이터
    public commission: number; //수수료
    public profit: number; //손익
    public ticks: number; //수익(틱)
    public profitHigh: number;
    public profitLow: number;
    public ticksHigh: number;
    public ticksLow: number;
    public duration: string; //포지션 보유 기간
    public tradingType: string; //타임 프레임
    
    //3. 매매전략
    public reasonBuy: string; //진입 사유
    public reasonSell: string; //청산 사유
    public lossCut: string; //손절 가격
    public description: string; //one-note 매매 설명 페이지로 링크
    public isPlanned: boolean; //매매를 계획대로 했는지 여부

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

export class Statement {
  public product: string; //상품명
  public contracts: number; //계약수
  public date_in: string; //진입 날짜
  public date_out: string; //청산 날짜
  public position: string; //포지션 (롱,숏)
  public tick_diff: number; //틱 차이
  public emotion: string; //감정상태
  public weather: string; //날씨
  public plan: string; //매매 계획
  public reason_in: string; //진입 사유
  public reason_out: string; //청산 사유
  public imgurls: string[]; //이미지 url
  public discussion: string; //토의
  public isPlanned: boolean;
  public orderType: string; //비고
  public commission: number; //slippage
  public result: string;
  //public type:string; //모의거래 실거래
  public duration: string; //보유기간
  public profit: number; //손익

  constructor() {
    this.imgurls = [];
    this.contracts = 1;
    this.orderType = "Limit";
    this.commission = 3.5;
    //this.type = "Real"
  }
}