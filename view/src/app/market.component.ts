import { Component, ChangeDetectorRef, ViewChild} from '@angular/core';
import { KiwoomService, CommonService } from './app.service';
import { ChartComponent } from './chart.component';
import { Products, Product } from './prototypes';

@Component({
  selector: 'my-market',
  template: require('./market.component.html'),
  styles: [require('./market.component.css')],
})


export class MarketComponent{ 

  //파이썬 키움 오브젝트
  kiwoom: any;
  
  /* child component의 change를 detect하기 위해 필요함 */
  @ViewChild(ChartComponent)
  private chartComponent:ChartComponent;

  isConnected: boolean; //연결상태
  
  /** 상품 리스트 관련 정보 **/
  allProducts:Object; //전체 종목 정보
  markets:string[]; //시장 목록(상품 구분)
  favorites:Object; //관심종목 정보
  
  
  /** 상품 관련  */
  products: Products = new Products();
  selectedProduct: Product; //선택된 종목
  

  /** 상품의 월물 리스트 관련 */
  modalProducts: Products; //월물별 종목 리스트
  modalTitle: string; //모달화면 제목
  isModalOn:boolean; //모달화면 flag

  /* Constants */

  //화면 번호
  screens:any = {
    pList: '0001', // product list screen
    pInfo: '0002', // product info screen
    modal: '0003', // modal info screen
    chart: '0004', // chart screen
  }

   
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
      this.kiwoom = (<any>window).kiwoom;
    
      //이벤트 핸들러 연결
      //수신받은 이벤트명과 동일한 이름의 메소드에 수신받은 데이터를 전달
      this.kiwoom.bridge.connect((event:string, data:any) => {
         this.commonService.logging("Event received", event);
         this[event](data);
      });
      this.kiwoom.connectState().then( () => {
            this.isConnected = true;
            this.__initKiwoom();
      }, ()=>{});
    }
  }
  
  ngOnDestroy() {
  // 화면 넘어갈때 disconnect 안하면 background에서 계속 data 받고 있음 
    if (this.isConnected == true)
      this.kiwoom.disconnect(this.screens.pList);
  }


  /*****************************************************************************
   Initialization:
   1) 수신중인 RealData Disconnect
   2) data/favrorite.json에 저장된 관심종목 불러오기 --> DB로 변경 예정
   3) 시장 전체 종목 정보 불러와 allProducts에 저장함
   4) 이벤트 핸들러 생성
  *****************************************************************************/
  __initKiwoom() {
    
    //this.kiwoomService.disconnect(this._chartScr); //refresh 용
    // 종목정보 받아오기
    // 관심종목 로딩 --> 전체 종목 정보 로딩 --> 마켓 리스트 생성
    this.kiwoom.getFavList()
      .then( (fav:Object) => this.favorites = fav)
      .then ( () => {
        this.kiwoom.getProducts().then((data:Object) => {
            this.allProducts = data;
            this.markets = ['FAV'].concat(Object.keys(data)); //마켓 리스트 
            this.selectMarket('FAV');
            this.ref.detectChanges(); 

            this.commonService.logging("All products", data);
        });
      })
  }
  
  connect() {
    if (!this.isConnected) {
      this.kiwoom.login()
      .then( () => this.commonService.logging('Login','프로그램 호출 성공')
      ,()=> this.commonService.logging('Login', '프로그램 호출 실패'));

    } else {
        let dis_pList = this.kiwoom.disconnect(this.screens.pList);
        let dis_pInfo = this.kiwoom.disconnect(this.screens.pInfo);
        Promise.all([dis_pList, dis_pInfo])
        .then(() => this.kiwoom.quit())
        .then( () => { 
           this.isConnected=false;
           //clear variables
           this.markets = [];
           this.products = new Products();
           delete this.selectedProduct;
           //this.ngOnInit();
        });
    }
  }

  
  test() {
    this.kiwoom.get_density('CUR', 'CUR6A')
      .then( (data:any) => {
        console.log(data);
    });
  }

  
  /******************************************************************
  *                       관심종목 화면 처리(pList)                   *
  ******************************************************************/
  selectMarket(market:string){
    /* html 관심종목 창에서 탭을 클릭하면 실행된다
       마켓별로 액티브 월물의 종목 정보를 Products 클래스에 정리한다.
     */
    
    this.products = new Products(market);
    let pList = {}; //products 안에 Products.list <-- 관심종목 product object 담고 있음
    let codes:string[] = [];
    
    if (market == 'FAV') {
        codes = Object.keys(this.favorites);
        for (let code of codes) {
          let name = this.favorites[code].name;
          let month = this.favorites[code].month;
          let groupname = this.favorites[code].groupname;
          let market = this.favorites[code].market;
          pList[code] = new Product(code, name, month, groupname, market);
      }

    } else {
        for (let goods in this.allProducts[market]){
          for (let good in this.allProducts[market][goods]){
            if (this.allProducts[market][goods][good].isActive) {
              codes.push(good); //액티브 월물의 코드 수집
              let name = this.allProducts[market][goods][good].name;
              let month = this.allProducts[market][goods][good].month;
              month = month.slice(2,4)+'/'+month.slice(4,6)+'/'+month.slice(6,8);
              pList[good] = new Product(good, name, month, goods, market);
            } 
          }
        }
        //for (let code of codes){
        //  let item = this.allProducts[market][code.slice(0,-3)][code]
        //  let name = item.name
        //  let month = item.month.slice(2,4)+'/'+item.month.slice(4,6)+'/'+item.month.slice(6,8);
        //  pList[code] = new Product(code, name, month);
        //}
    }

    this.products.codes = codes;
    this.products.list = pList;
    this.ref.detectChanges();

    //실시간시세 요청
    if (this.products.codes.length > 0) {
      this.kiwoom.requestProductsReal(this.screens.pList, this.products.codes);
    }

    this.commonService.logging("Current Products", this.products);
  }

  //관심종목 편집 method
  addToFav(code:any) {
    if (code in this.favorites) {
      delete this.favorites[code];
    } else if (this.isModalOn) {
      let item = this.modalProducts.list[code];
      this.favorites[code] = new Product(code, item.name, item.month, item.groupname, item.market);
    } else {
      let item = this.products.list[code];
      this.favorites[code] = new Product(code, item.name, item.month, item.groupname, item.market);
    }
    
    this.selectMarket(this.products.market);

    let favlist = Object.keys(this.favorites);
    this.ref.detectChanges()
    this.kiwoom.addToFav(favlist); 

    this.commonService.logging("Current Favorites", this.favorites);
  }

  //종목이 즐겨찾기 목록에 있는지 확인 
  checkFav(product:string){
    return (product in this.favorites)? true : false ;
  }

  //OnProducts 이름으로 Real Data 들어왔을때 이벤트 핸들러
  _onProducts(data:Object) {
    for (let code in data){
      if (this.products.codes.indexOf(code) > -1) {
        this.products.list[code].price = data[code][0].slice(1); //진법 변환된 가격
        this.products.list[code].diff = data[code][1]; //전일대비
        this.ref.detectChanges();
      }
    }
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
        mList[code] = new Product(code, item.name, item.month, goods, market);
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
    this.selectedProduct = this.products.list[code];
    this.kiwoom.getProductInfo(code); //onProductInfo에서 receive

    setTimeout(()=>{  
      this.getDensityData(this.selectedProduct);
    },100);
    this.commonService.logging('selected product', this.selectedProduct);
  }
  
  onProductInfo(data:Object) {
    for (let item in data){
      this.selectedProduct[item] = data[item];
    }
    this.ref.detectChanges();
  }
  
  
  /******************************************************************
  *                        차트 데이터 처리(screen = pInfo)          *
  ******************************************************************/
  getDensityData(product:Product){

    let market = product.market;
    let group = product.groupname;
    let size = product.size;
    this.kiwoom.get_density(market, group, size)
      .then( (data:any) => {
        //this.selectedProduct.density = data;
        this.chartComponent.drawDensityChart(data);
    });
  }
  
  /******************************************************************
  *                       실시간 데이터 및 이벤트  처리               *
  ******************************************************************/  
  onRealPrice(data:string) {
      let realdata = data.split(';');
      let code = realdata[0];
      if (this.products.codes.indexOf(code) > -1) {
        this.products.list[code]['price'] = realdata[2].slice(1); //진법 변환된 가격
        this.products.list[code]['diff'] = realdata[4]; //전일대비
        this.ref.detectChanges();
      } 
      console.log(realdata)
      if (typeof this.selectedProduct !== 'undefined' && code == this.selectedProduct.code){
        this.chartComponent.setPriceOnChart();
      }
      
  }
  
  onReceiveMsg(msg:any) {
    this.commonService.logging("Received Msg", msg);
  }

  //로그인 및 연결상태 관련 이벤트
  onEventConnect(errCode:number){

    if (errCode == 0) {
        this.commonService.logging('Login', '로그인 성공');
        this.isConnected = true;
        this.__initKiwoom();

    } else if (errCode == -106) {
        this.commonService.logging('통신 단절', errCode);
        this.isConnected = false;

    } else {
        this.commonService.logging('Login', '로그인 실패');
    }
  }
}

