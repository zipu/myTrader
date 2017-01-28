import { Component, ChangeDetectorRef, ViewChild} from '@angular/core';
import { KiwoomService, CommonService } from './app.service';
import { ChartComponent } from './chart.component';
import { Products, Product, ProductInfo } from './prototypes';

@Component({
  selector: 'my-market',
  template: require('./market.component.html'),
  styles: [require('./market.component.css')],
})


export class MarketComponent{ 
  
  /** 접속 관련 **/
  isConnected:boolean; //연결상태
  
  /** 상품 리스트 관련 정보 **/
  allProducts:Object; //전체 종목 정보
  markets:string[]; //시장 목록(상품 구분)
  favorites:Object; //관심종목 정보
  

  productInfo: ProductInfo; //선택된 종목 정보 --> deprecated
  
  /** 상품 관련  */
  products: Products = new Products();

  selectedProduct: Product; //선택된 종목
  

  /** 상품의 월물 리스트 관련 */
  modalProducts: Products; //월물별 종목 리스트
  modalTitle: string; //모달화면 제목
  isModalOn:boolean; //모달화면 flag

  

  /* Constants */
  readonly _pListScr = '0001'; // product list screen
  readonly _pInfoScr = '0002'; // product info screen
  readonly _modalScr = '0003'; // modal info screen
  readonly _chartScr = '0004'; // chart screen

  
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
   //this.kiwoomService.disconnect(this._pListScr);
   this.kiwoomService.disconnect(this._chartScr);
  }


  /*****************************************************************************
   Initialization:
   1) 수신중인 ReaData Disconnect
   2) data/favrorite.json에 저장된 관심종목 불러오기 --> DB로 변경 예정
   3) 시장 전체 종목 정보 불러와 allProducts에 저장함
   4) 이벤트 핸들러 생성
  *****************************************************************************/
  __initKiwoom() {
    this.kiwoomService.disconnect(this._chartScr); //refresh 용
    // 종목정보 받아오기
    // 관심종목 로딩 --> 전체 종목 정보 로딩 --> 마켓 리스트 생성
    this.kiwoomService.getFavorits()
      .then( (fav:Object) => this.favorites = fav)
      .then ( () => {
        this.kiwoomService.getProducts().then((data:Object) => {
            this.allProducts = data;
            this.markets = ['FAV'].concat(Object.keys(data)); //마켓 리스트 
            this.selectMarket('FAV');
            this.ref.detectChanges(); 

            this.commonService.logging("All products", data);
        });
      })

    //이벤트 핸들러
    //수신받은 이벤트명과 동일한 이름의 메소드에 수신받은 데이터를 전달
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
      this.kiwoomService.quit();
      this.isConnected=false;
    }
  }

  
  /******************************************************************
  *                       관심종목 화면 처리(_pListScr)              *
  ******************************************************************/
  selectMarket(market:string){
    /* html 관심종목 창에서 탭을 클릭하면 실행된다
       마켓별로 액티브 월물의 종목 정보를 Products 클래스에 정리한다.
     */
    
    this.products = new Products(market);
    let pList = {};
    let codes:string[] = [];
    
    if (market == 'FAV') {
        codes = Object.keys(this.favorites);
        for (let code of codes) {
          let name = this.favorites[code].name;
          let month = this.favorites[code].month;
          pList[code] = new Product(code, name, month);
      }

    } else {
        for (let goods in this.allProducts[market]){
          for (let good in this.allProducts[market][goods]){
            if (this.allProducts[market][goods][good].isActive) {
              codes.push(good); //액티브 월물의 코드 수집
            } 
          }
        }
        for (let code of codes){
          let item = this.allProducts[market][code.slice(0,-3)][code]
          let name = item.name
          let month = item.month.slice(2,4)+'/'+item.month.slice(4,6)+'/'+item.month.slice(6,8);
          pList[code] = new Product(code, name, month);
        }
    }

    this.products.codes = codes;
    this.products.list = pList;
    this.ref.detectChanges();

    this.commonService.logging("Current Products", this.products);
  }

  /*
    관심종목 편집
  */
  addToFav(code:any) {
    if (code in this.favorites) {
      delete this.favorites[code];
    } else if (this.isModalOn) {
      let item = this.modalProducts.list[code];
      this.favorites[code] = new Product(code, item.name, item.month);
    } else {
      let item = this.products.list[code];
      this.favorites[code] = new Product(code, item.name, item.month);
    }
    
    this.selectMarket(this.products.market);

    let favlist = Object.keys(this.favorites);
    this.ref.detectChanges()
    this.kiwoomService.addToFav(favlist); 

    this.commonService.logging("Current Favorites", this.favorites);
  }

  //OnProducts 이름으로 Real Data 들어왔을때 이벤트 핸들러 --> deprecated
 // _onProducts(data:Object) {
 //   for (let code in data){
 //     if (this.curCodes.indexOf(code) > -1) {
 //       this.curProducts[this.curCodes.indexOf(code)][3] = data[code][0];
 //       this.curProducts[this.curCodes.indexOf(code)][4] = data[code][1];
 //       this.curProducts[this.curCodes.indexOf(code)][5] = data[code][2];
 //       this.ref.detectChanges();
 //     }
 //   }
 // }

  //종목이 즐겨찾기 목록에 있는지 확인 
  checkFav(product:string){
    return (product in this.favorites)? true : false ;
  }




  /******************************************************************
  *                       modal 화면 처리(_modalScr)                      *
  ******************************************************************/
  selectMonth(code:any){
    this.isModalOn = true;
    this.modalTitle = this.products.list[code].name;
    this.modalProducts = new Products();

    let mList = {};
    let goods = code.slice(0,-3)
    let market:string;

    //마켓 이름 찾기
    for (let marketname in this.allProducts){
      if (this.allProducts[marketname][goods]){
        this.modalProducts.market = market = marketname;
      }
    }

    for (let code in this.allProducts[market][goods]){
        let item = this.allProducts[market][goods][code];
        mList[code] = new Product(code, item.name, item.month);
    }

    this.modalProducts.list = mList;
    this.modalProducts.codes = Object.keys(this.allProducts[market][goods]).sort((a,b) => {
        return this.modalProducts.list[a].month-this.modalProducts.list[b].month
    }).slice(0,10);

    Object.keys(this.modalProducts.list).forEach( (key) => {
      let mon = this.modalProducts.list[key].month;
      this.modalProducts.list[key].month = mon.slice(2,4)+'/'+mon.slice(4,6)+'/'+mon.slice(6,8);
    });

    this.ref.detectChanges();
  }

  modalClose(){
    this.isModalOn = false;
    delete this.modalProducts;
  }

//  onGoods(data:Object) {
//    for (let code in data){
//      if (this.modalCodes.indexOf(code) > -1) {
//        this.modalProducts[this.modalCodes.indexOf(code)][3] = data[code][0];
//        this.modalProducts[this.modalCodes.indexOf(code)][5] = data[code][2];
//        this.ref.detectChanges();
//      }
//    }
//  }

  /******************************************************************
  *                       종목정보 화면 처리                         *
  ******************************************************************/
  selectProduct(code:string){
    //this.selectedProduct = new Product(product[0], product[1], product[2]);
    this.productInfo = new ProductInfo();
    this.products.selectedProduct = this.products.list[code].name;
    this.kiwoomService.getProductInfo(code);
    //this.setChart(this.selectedProduct);
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
      if (this.products.codes.indexOf(code) > -1) {
        //this.products.list[code][''] = realdata[1];
        //this.curProducts[this.curCodes.indexOf(code)][4] = realdata[2];
        //this.curProducts[this.curCodes.indexOf(code)][5] = realdata[3];
        this.ref.detectChanges();
      } 
  }
  
  onReceiveMsg(msg:any) {
    console.info("message: "+ msg.msg + " (rqName:" + msg.rqName + ", trCode: " 
                        + msg.scrNo + ", trCode: " + msg.trCode + ")");
  }

}

