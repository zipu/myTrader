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
    constructor(code:string, name:string, month:string) {
      this.code = code;
      this.name = name;
      this.month = month;
    }
}

export class ProductInfo {
  market: string;
  currency: string;
  margin: string;
  expirate: string;
  remained:string;
  openDate:string;
  tickValue:string;
  openTime:string;
  closeTime:string;
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
    public duration:string; //보유기간
    public profit:number; //손익

    constructor() {
      this.imgurls = [];
      this.contracts = 1;
      this.orderType = "Limit";
      this.commission = 3.5;
      //this.type = "Real"
    }
}