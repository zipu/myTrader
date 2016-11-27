import { Component } from '@angular/core';
import { CommonService } from './app.service';
//import { NgForm } from '@angular/common';
import { Statement } from './prototypes';
//var QWebChannel:any = require('../../public/js/qwebchannel.js').QWebChannel;

@Component({
  selector: 'my-history',
  template: require('./history.component.html'),
  styles: [require('./history.component.css')],
})


export class HistoryComponent{ 
  modalOn: boolean = false;
  isReadOnly: boolean = false;
  curIndex: number = 0;
  
  products = ['AUD/USD', 'EUR/USD' , 'Natural Gas'];
  positions = ['Long', 'Short'];
  orderType = ['Market', 'Limit'];
  //types = ['Real', 'Simul']

  statement: Statement;
  historyDB: any;
  historyList:any[];

  constructor(
    private commonService: CommonService
  ){}

  ngOnInit(){
    //historyDB object 로드 끝날때까지 기다림
    if ( (<any>window).historyDB == undefined ) {
      setTimeout(()=>{
        this.ngOnInit();
      },100);
    } else {
      this.historyDB = (<any>window).historyDB;
      this.getDBList();
    }
  }

  reset(){
    this.getDBList();
    this.modalOn = false;
    this.isReadOnly = false;
    this.curIndex = 0;
  }
  
  //매매 기록창에서 submit 버튼과 연동
  onSubmit() {
    let statement = JSON.stringify(this.statement);
    if (this.statement.product && this.statement.position) {
       if (this.curIndex == 0) {
             this.historyDB.save(statement);
       } else {
         this.historyDB.update(this.curIndex,  statement);
       }
       this.reset();
    }
  }

  modify() {
    this.isReadOnly = false;
    if (!this.statement.date_out) {
      let now = this.commonService.now();
      this.statement.date_out = now.datetime;
    }
  }

  delete() {
    if (confirm('Do you really want to delete?')) {
      this.historyDB.delete(this.curIndex);
      this.reset();
    }
  }
  

  //매매기록창 오픈
  openModal() {
    this.modalOn = true; //modal 화면 on
    this.statement = new Statement();
    let now = this.commonService.now();
    this.statement.date_in = now.datetime;
  }
  
  getStatement(index:number) {
    this.curIndex = index;
    this.historyDB.getStatement(index).then( (data:any) => {
      this.statement = Object.assign(new Statement(), data);
      this.modalOn = true;
      this.isReadOnly = true;
      console.log(this.statement);
    });
    
  }

  //db로부터 데이터 리스트를 불러옴
  getDBList() {
    this.historyDB.getDBList().then( (data:any)=> { 
      this.historyList = data;
    });
  }
  
  //image 파일명 저장 
  addImage(imgs:any) {
    for (let i=0; i<imgs.length; i++){
      if ( this.statement.imgurls.indexOf(imgs[i].name) < 0 ) {
        this.statement.imgurls.push(imgs[i].name);
      }
    };
  }

  //한글 타이핑시 두번씩 입력 되는거 삭제
  deleteKorean(event:any){
      let lastChar =  event.target.value.substr(-1);
      if (lastChar.match('[^\u0000-\u007F]+') && event.keyCode != 8 && event.keyCode != 16 ) {
        event.target.value = event.target.value.slice(0,-1);
      }
  }
  
}