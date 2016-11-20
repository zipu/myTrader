import { Component, ChangeDetectorRef, ViewChild} from '@angular/core';
import { KiwoomService, CommonService } from './app.service';
import { ChartComponent } from './chart.component';
import { Product, ProductInfo } from './prototypes';

@Component({
  selector: 'my-trading',
  template: require('./trading.component.html'),
  styles: [require('./trading.component.css')],
})


export class TradingComponent{ 
  
  isConnected:boolean; //연결상태
  
  typeList:string[]; //타입 리스트 
  selectedType: string; //선택된 타입
  curProducts: string[][]; //선택된 종목군 리스트
  curCodes: string[]; //선택된 종목 코드 리스트
  
  modalProducts: any[][]; //월물별 종목 리스트
  modalCodes: string[]; //월물별 종목 코드
  modalTitle: string; //모달화면 제목

  allProducts:Object; //전체 종목 정보
  favorites:Object; //관심종목 정보
  
  selectedProduct: Product; //선택된 종목
  productInfo: ProductInfo; //선택된 종목 정보

  isModalOn:boolean; //모달화면 flag
  
  /* child component의 change를 detect하기 위해 필요함 */
  @ViewChild(ChartComponent)
  private chartComponent:ChartComponent;
   
  constructor(
    private kiwoomService: KiwoomService,
    private commonService: CommonService,
    private ref: ChangeDetectorRef //mutable object는 변경이 감지가 자동으로 안되서 필요함 
  ) {}

  ngOnInit(){
    /* index.html에 있는 qt object 로드하는 script가 로딩이 다 안끝났으면 에러가 나서 로딩 끝날때까지 기다림 */ 
    if ( (<any>window).kiwoom == undefined ) {
      setTimeout(()=>{
        this.ngOnInit();
      },100);
    } else {
      this.kiwoomService.kiwoom = (<any>window).kiwoom;
      this.kiwoomService.connectState().then( () => {
          this.isConnected = true;
          this.__initKiwoom();
      }, ()=>{});
    }
  }
  
  ngOnDestroy() {
  // 화면 넘어갈때 disconnect 안하면 background에서 계속 data 받고 있음 
   this.kiwoomService.disconnect('0001');
   this.kiwoomService.disconnect('0004');
  }

  __initKiwoom() {
    this.kiwoomService.disconnect('0004'); //refresh 용
    /** 종목정보 받아오기
     * fav list 로딩 --> 전체 종목 정보 로딩 --> 받아온 타입 리스트를 탭으로 만듬 -->
     * 선택된 타입으로 FAV 선택 */
    this.kiwoomService.getFavorits()
      .then( (fav:Object) => this.favorites = fav)
      .then ( () => {
        this.kiwoomService.getProducts().then((data:Object) => {
            this.allProducts = data;
            this.typeList = ['FAV'].concat(Object.keys(data));
            this.selectType('FAV');
            this.ref.detectChanges(); 
        });
      })
    //이벤트 핸들러
    this.kiwoomService.kiwoom.bridge.connect((event:string, data:any) => {
       console.info('< ' + event + ' > received from the server...');
       this[event](data);
    });   
  }  
  
  connect() {
    if (!this.isConnected) {
      this.kiwoomService.login()
        .then( () => {
            this.commonService.pop_alert('로그인 성공');
            this.__initKiwoom();
            this.isConnected = true;
        }, () => {
            this.commonService.pop_alert('로그인 실패');
        })
    } else {
      this.kiwoomService.disconnect('0001');
      delete this.curProducts;
      delete this.typeList;
      this.kiwoomService.quit();
      this.isConnected=false;
    }
  }

  
  /******************************************************************
  *                       관심종목 화면 처리(0001)                    *
  ******************************************************************/
  selectType(type:string){
    this.kiwoomService.disconnect('0001');
    let scrNo = '0001';
    this.selectedType = type;
    this.curProducts = [];
    this.curCodes = [];
    if (type == 'FAV') {
        this.curCodes = Object.keys(this.favorites);
        for (let code of this.curCodes) {
          let info:string[] = [];
          info[0] = code;
          info[1] = this.favorites[code].name;
          info[2] = this.favorites[code].month;
          this.curProducts.push(info);
        }

    } else {
      for (let goods in this.allProducts[type]){
        for (let good in this.allProducts[type][goods]){
          if (this.allProducts[type][goods][good].isActive) this.curCodes.push(good);
        }
      }
      for (let i=0 ; i < this.curCodes.length; i++){
        let info:string[] = [];
        info[0] = this.curCodes[i];
        info[1] = this.allProducts[type][info[0].slice(0,-3)][info[0]].name;
        let month = this.allProducts[type][info[0].slice(0,-3)][info[0]].month;
        info[2] = month.slice(2,4)+'/'+month.slice(4,6)+'/'+month.slice(6,8);
        this.curProducts.push(info);
      }
    }
    this.ref.detectChanges();
    let inputvalue = this.curCodes;
    this.kiwoomService.getProductsReal(scrNo, inputvalue);
  }
  
  addToFav(product:string[]) {
    let code:string = product[0];
    if (this.selectedType == 'FAV' && !this.isModalOn) {
      delete this.favorites[code];
      this.curProducts.splice(this.curCodes.indexOf(code),1);
      this.curCodes.splice(this.curCodes.indexOf(code),1);
    } else if (this.selectedType == 'FAV' && this.isModalOn) {
      this.favorites[code] = new Product(code, product[1], product[2]);
      this.selectType(this.selectedType);
    } else {
      this.favorites[code] = new Product(code, product[1], product[2]);
    }
    
    let favlist = Object.keys(this.favorites);
    this.ref.detectChanges()
    this.kiwoomService.addToFav(favlist); 
  }

  onProducts(data:Object) {
    for (let code in data){
      if (this.curCodes.indexOf(code) > -1) {
        this.curProducts[this.curCodes.indexOf(code)][3] = data[code][0];
        this.curProducts[this.curCodes.indexOf(code)][4] = data[code][1];
        this.curProducts[this.curCodes.indexOf(code)][5] = data[code][2];
        this.ref.detectChanges();
      }
    }
  }




  /******************************************************************
  *                       modal 화면 처리(0003)                      *
  ******************************************************************/
  selectMonth(product:any){
    let scrNo = '0003';
    this.isModalOn = true;
    this.modalTitle = product[1];
    this.modalProducts = [];
    this.modalCodes = [];

    let goods = product[0].slice(0,-3)
    let type:string;
    for (let typename in this.allProducts){
      if (this.allProducts[typename][goods]){
        type = typename;
      }
    }

    for (let code in this.allProducts[type][goods]){
        let info:string[] = [];
        info[0] = code;
        info[1] = this.allProducts[type][goods][code].name;
        info[2] = this.allProducts[type][goods][code].month;
        this.modalProducts.push(info);
      }

    this.modalProducts = this.modalProducts.sort((a,b)=> {return a[2]-b[2]}).slice(0,10);
    this.modalProducts.forEach((a)=> {
      this.modalCodes.push(a[0]);
      a[2] = a[2].slice(2,4)+'/'+a[2].slice(4,6)+'/'+a[2].slice(6,8);
    });
    this.ref.detectChanges();
    let inputvalue = this.modalCodes;
    this.kiwoomService.getProductsReal(scrNo, inputvalue);
  }
  modalClose(){
    this.kiwoomService.disconnect('0003');
    this.isModalOn = false;
    delete this.modalProducts;
    delete this.modalCodes;

  }
  onGoods(data:Object) {
    for (let code in data){
      if (this.modalCodes.indexOf(code) > -1) {
        this.modalProducts[this.modalCodes.indexOf(code)][3] = data[code][0];
        this.modalProducts[this.modalCodes.indexOf(code)][5] = data[code][2];
        this.ref.detectChanges();
      }
    }
  }

  /******************************************************************
  *                       종목정보 화면 처리                         *
  ******************************************************************/
  selectProduct(product:string[]){
    this.selectedProduct = new Product(product[0], product[1], product[2]);
    this.productInfo = new ProductInfo();
    this.kiwoomService.getProductInfo(product[0]);
    this.setChart(this.selectedProduct);
  }
  
  onProductInfo(data:Object) {
    for (let item in data){
      this.productInfo[item] = data[item];
    }
    this.ref.detectChanges();
  }
  
  
  /******************************************************************
  *                        차트 데이터 처리                          *
  ******************************************************************/
  setChart(product:Product){
    let code = product.code.slice(0,-3)+'000';
    this.kiwoomService.getChartData(code);
  }

  onChartData(dataString:any) {
    let data = dataString.match(/\S+/g);
    let chart_data:number[][] = [];
    for (let i=0; i< data.length/7; i++) {
      let temp:number[] = [];
      let date:any = data[4+i*7];

      temp[0] = +data[i*7];
      temp[1] = +data[i*7+1];
      temp[2] = +data[i*7+2];
      temp[3] = +data[i*7+3];
      temp[4] = new Date(date.slice(0,4),date.slice(4,6),date.slice(6,8)).getTime();
      temp[5] = +data[i*7+5];
      chart_data.push(temp);
    };
    this.selectedProduct.chart = chart_data;
    this.chartComponent.updateChart()
  }
  
  /******************************************************************
  *                       실시간 데이터 처리                         *
  ******************************************************************/  
  onRealPrice(data:string) {
      let realdata = data.split(';');
      let code = realdata[0];
      realdata = [code, realdata[2], realdata[4], Number(realdata[9]).toLocaleString()]
      if (this.curCodes.indexOf(code) > -1) {
        this.curProducts[this.curCodes.indexOf(code)][3] = realdata[1];
        this.curProducts[this.curCodes.indexOf(code)][4] = realdata[2];
        this.curProducts[this.curCodes.indexOf(code)][5] = realdata[3];
        this.ref.detectChanges();
      } 
  }
  
  onReceiveMsg(msg:any) {
    console.info("message: "+ msg.msg + " (rqName:" + msg.rqName + ", trCode: " 
                        + msg.scrNo + ", trCode: " + msg.trCode + ")");
  }

}

