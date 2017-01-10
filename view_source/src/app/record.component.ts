import { Component } from '@angular/core';
import { CommonService } from './app.service';
import { Record, RecordInfo } from './prototypes';

@Component({
  selector: 'my-record',
  template: require('./record.component.html'),
  styles: [require('./record.component.css')],
})


export class RecordComponent {
  recordDB: any;

  //레코드 기록 폼
  isInfoForm: boolean;
  isRecordForm: boolean;

  //매매기록
  record: Record = new Record();
  recordsList: any[];
  page: number;

  //종목 정보
  recordInfo: RecordInfo;
  infoList: any[];

  //for 자동완성
  filteredList: string[] = [];
  products: string[];
  strategies: string[];
  filteringField:string;

  constructor(
    private commonService: CommonService
  ) {}

  ngOnInit() {
    //historyDB object 로드 끝날때까지 기다림
    if (( < any > window).recordDB == undefined) {
      setTimeout(() => {
        this.ngOnInit();
      }, 100);
    } else {
      this.recordDB = (<any>window).recordDB;
      this.myInit();
    }
  }


  /** refresh all **/
  myInit(){
    this.record = new Record();
    this.isInfoForm = false;
    this.isRecordForm = false;
    this.filteringField = "";
    this.page = 1;
    this.getRecordsList(this.page);
    this.getInfo();
    this.getStrategy();
  }



  /** Methods for Record table */
    //DB로부터 레코드 불러옴
  getRecordsList(page:number) {
    this.recordDB.getRecordsList(page).then ( (data:any) => {
      this.recordsList = data;
    });
  }

  //pagination
  paging(flag:number) {
    if ((this.recordsList[this.recordsList.length-1].index == 1 && flag == 1)
        || this.page+flag == 0 ){
    } else {
      this.page += flag;
      this.getRecordsList(this.page)
    }
  }

  /** Methods for Record Form */
  openRecordForm() {
    //this.record = new Record();
    this.isRecordForm = !this.isRecordForm; //매매기록창 열기 
    this.isInfoForm = false; //종목정보창 닫기
    if (this.isRecordForm == true){ //새로 작성할때 
      this.record.entryDate = this.commonService.now().datetime;
    } else { //저장하거나 record form 끌때
      this.myInit();
    }
  }

  saveRecord() {
    if (this.record.product && this.record.position && this.record.priceOpen) {
      let checkProduct = this.infoList.filter( function(obj:any){
        return obj.product == this.record.product;
      }.bind(this)); 
      if (!checkProduct.length) { //product가 종목 정보 리스트에 있는지 확인
        this.commonService.pop_alert('Not valid product');
      } else {

          let newRecord = JSON.stringify(this.record);
          this.recordDB.saveRecord(newRecord);
          if (this.record.reasonBuy != null && this.strategies.indexOf(this.record.reasonBuy.toLowerCase()) == -1){
            this.recordDB.addStrategy(this.record.reasonBuy);
          }

          this.myInit();
      }
    } else {
      this.commonService.pop_alert('Fill fields');
    }
  }

  //리스트에서 레코드 클릭하면 수정창 열림
  getRecord(index:number) {
    this.isRecordForm = true;
    this.recordDB.getRecord(index).then ( (data:any) => {
      this.record = Object.assign(new Record(), data);
      if (!this.record.exitDate) {
        this.record.exitDate = this.commonService.now().datetime;
      }
    });
  }

  //레코드 삭제
  deleteRecord() {
    if (confirm('정말 삭제하시겠습니까?')){
      this.recordDB.deleteRecord(this.record.index);
      this.myInit();
    }
  }

  /** Methods for product Information */
  openInfoForm() {
    if (this.isInfoForm == false) {
      this.isInfoForm = true;
      this.isRecordForm = false;
      this.recordInfo = new RecordInfo();

    } else {
      this.isInfoForm = false;
      this.myInit();
    }
  }

  //파이썬 recordDB에서 종목정보 불러옴
  getInfo() {
    this.products = [];
    this.recordDB.getInfo().then( (info:any) => {
        this.infoList = info;
        this.infoList.forEach ( (obj:any) => {
          this.products.push(obj.product);
        })
    });
  }

  addInfo() {
    if (Object.keys(this.recordInfo).length > 0 ) { //필드가 하날도 채워있어야 함
      let newInfo = JSON.stringify(this.recordInfo);
      this.recordDB.addInfo(newInfo); //파이썬 record모듈 addInfo 함수 호출
    } 
    this.recordInfo = new RecordInfo(); //종목정보 지움
    this.getInfo();
  }

  removeInfo(index:any) {
    this.recordDB.removeInfo(index);
    this.getInfo();
  }

  gotoOneNote(url:any){ // 원노트 링크
    window.location.href=url;
  }

  /** Methods for Auto completion */
  getStrategy(){
    this.recordDB.getStrategy().then( (el:any) => {
      this.strategies = el;
    })
  }

  filter(name:string) { // 타이핑 된 글자 목록에서 필터링
    let initialList:any[]=[];    //전체 목록 담을 어레이
    this.filteringField = name;

    if (name == 'product') {
      initialList = this.products;
    } else if (name == 'reasonBuy'){
      initialList = this.strategies;
    }

    if (this.record[name] !== "") {
      this.filteredList = initialList.filter(function (el:string) {
        return el.toLowerCase().indexOf(this.record[name].toLowerCase()) > -1;
      }.bind(this));
    } else {
      this.filteredList = [];
    }
  }
  
  select(item:string) { // 자동완성 목록에서 아이템 클릭시
    this.record[this.filteringField] = item;  //쿼리 = 아이템명 
    this.filteredList = []; //필터링 목록은 초기화
  }

    //한글 타이핑시 두번씩 입력 되는거 삭제
  deleteKorean(event:any){
      let lastChar =  event.target.value.substr(-1);
      if (lastChar.match('[^\u0000-\u007F]+') && event.keyCode != 8 && event.keyCode != 16 ) {
        event.target.value = event.target.value.slice(0,-1);
      }
  }

}