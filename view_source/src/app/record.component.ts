import { Component } from '@angular/core';
import { CommonService } from './app.service';
import { Statement, Record, RecordInfo } from './prototypes';

@Component({
  selector: 'my-record',
  template: require('./record.component.html'),
  styles: [require('./record.component.css')],
})


export class RecordComponent {

  recordDB: any;

  isInfoForm: boolean = false;
  isRecordForm: boolean = false;

  modalOn: boolean = false;
  isReadOnly: boolean = false;
  curIndex: number = 0;

  statement: Statement;
  historyDB: any;
  historyList: any[];
  
  //매매기록
  record: Record = new Record();
  recordsList: any[];

  //종목 정보
  recordInfo: RecordInfo;
  infoList: any[] = [];

  //for 자동완성
  filteredList: any[] = [];
  

  constructor(
    private commonService: CommonService,
  ) {}

  ngOnInit() {
    //historyDB object 로드 끝날때까지 기다림
    if (( < any > window).historyDB == undefined) {
      setTimeout(() => {
        this.ngOnInit();
      }, 100);
    } else {
      this.historyDB = ( < any > window).historyDB;
      this.recordDB = (<any>window).recordDB;
      this.getDBList();

      this.getInfo(); //종목 정보를 db에서 불러옴 
      this.getRecordsList(); //레코드 기록을 db에서 불러옴
    }
  }

  /** Methods for Record table */
  
  //DB로부터 레코드 불러옴
  getRecordsList() {
    this.recordDB.getRecordsList().then ( (data:any) => {
      this.recordsList = data;
    });
  }

  /** Methods for Record Form */
  openRecordForm() {
    this.record = new Record();
    this.isRecordForm = !this.isRecordForm; //매매기록창 열기 
    this.isInfoForm = false; //종목정보창 닫기
    if (this.isRecordForm == true){
      this.record.entryDate = this.commonService.now().datetime;
    } else {
      this.getRecordsList();
    }
  }

  saveRecord() {
    if (this.record.product && this.record.position && this.record.priceOpen) {
      //가격이 잘못 되었는지 확인
      //let tickPrice = this.infoList.filter( function(key:any){
      //                  return key.product == this.record.product 
      //                }.bind(this))[0].tickPrice;  
      //if (this.record.priceOpen < tickPrice || this.record.priceClose < tickPrice){
      //    this.commonService.pop_alert('Wrong Price');
      //} else {
        let newRecord = JSON.stringify(this.record);
        this.recordDB.saveRecord(newRecord);
        this.openRecordForm();
      //}
    } else {
      this.commonService.pop_alert('Fill fields')
    }
  }

  //리스트에서 레코드 클릭하면 수정창 열림
  getRecord(index:number) {
    this.isRecordForm = true;
    this.recordDB.getRecord(index).then ( (data:any) => {
      this.record = Object.assign(new Record(), data);
    })
  }

  //레코드 삭제
  deleteRecord() {
    if (confirm('정말 삭제하시겠습니까?')){
      this.recordDB.deleteRecord(this.record.index);
      this.openRecordForm();
    }
  }



  /** Methods for product Information */
  openInfoForm() {
    this.isInfoForm = !this.isInfoForm; //종목정보창 열기
    this.isRecordForm = false; //매매기록창 닫기
    this.recordInfo = new RecordInfo();
  }

  //파이썬 recordDB에서 종목정보 불러옴
  getInfo() {
    this.recordDB.getInfo().then( (info:any) => {
        this.infoList = info;
    })
  }

  addInfo() {
    if (Object.keys(this.recordInfo).length > 0 ) {
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

  /** Methods for Auto completion */
  filter() { // 타이핑 된 글자 목록에서 필터링
    let initialList:any[]=[];    //전체 목록 담을 어레이
    for (let key of this.infoList){
      initialList.push(key.product); //infoList 에서 product만 불러와서 어레이로 저장
    }
    if (this.record.product !== "") {
      this.filteredList = initialList.filter(function (el:string) {
        return el.toLowerCase().indexOf(this.record.product.toLowerCase()) > -1;
      }.bind(this));
    } else {
      this.filteredList = [];
    }
  }
  
  select(item:string) { // 자동완성 목록에서 아이템 클릭시
    this.record.product = item;  //쿼리 = 아이템명 
    this.filteredList = []; //필터링 목록은 초기화
  }

  reset() {
    this.getDBList();
    this.modalOn = false;
    this.isReadOnly = false;
    this.curIndex = 0;
  }

  delete() {
    if (confirm('Do you really want to delete?')) {
      this.historyDB.delete(this.curIndex);
      this.reset();
    }
  }


  getStatement(index: number) {
    this.curIndex = index;
    this.historyDB.getStatement(index).then((data: any) => {
      this.statement = Object.assign(new Statement(), data);
      this.modalOn = true;
      this.isReadOnly = true;
      console.log(this.statement);
    });

  }

  //db로부터 데이터 리스트를 불러옴
  getDBList() {
    this.historyDB.getDBList().then((data: any) => {
      this.historyList = data;
    });
  }

  //한글 타이핑시 두번씩 입력 되는거 삭제
  deleteKorean(event: any) {
    let lastChar = event.target.value.substr(-1);
    if (lastChar.match('[^\u0000-\u007F]+') && event.keyCode != 8 && event.keyCode != 16) {
      event.target.value = event.target.value.slice(0, -1);
    }
  }

}