import { Injectable, EventEmitter } from '@angular/core';

@Injectable()
export class KiwoomService {
    kiwoom:any;
    
    login() {
        return new Promise<any> ( (resolve, reject) => {
            this.kiwoom.login()
            .then( () => {
                this.kiwoom.loginEvent.connect((errCode:any) => {
                    if (errCode == 0) resolve();
                    else reject();
                });
            }, () => reject() )
        });
    }
    
    quit() { //deprecated
        this.kiwoom.quit();
    }
    
    disconnect(scrno:string) { //deprecated
        this.kiwoom.disconnect(scrno);
    }
    
    connectState():Promise<any> {
        return this.kiwoom.connectState();
    }
    
    getProducts():any { //deprecated
        return this.kiwoom.getProducts()
                .then((data:Object) => {
                   return data;
                });           
    }

    getFavorits():any { //deprecated
        return this.kiwoom.getFavList()
                .then((data:Object) => {
                    return data;
                });
    }
    
    addToFav(fav:string[]) { //deprecated
        this.kiwoom.addToFav(fav);
    }

    //관심종목의 실시간 데이터 요청
    requestProductsReal(scrNo:string, inputValue:string[]) {
        this.kiwoom.requestProductsReal(scrNo, inputValue);
    }
    
    getProductInfo(code:string) { //deprecated
        this.kiwoom.getProductInfo(code);
    }

    getChartData(code:string){ //deprecated
        this.kiwoom.getChartData(code);
    }
}

@Injectable()
export class CommonService {
    emitter:EventEmitter<any> = new EventEmitter()
    
    pop_alert(msg:string){
        this.emitter.emit(msg);
    }

    /** 현재 시간을 년, 월, 일 시간, 분, 기타 여러가지 형태로 포함하고 있는 object를 return함 **/
    now(){
        let now = new Date();
        let yyyy = now.getFullYear().toString();
        let mm:any = now.getMonth() + 1; // getMonth() is zero-based
        mm = mm < 10 ? '0'+ mm : mm.toString();
        let dd:any = now.getDate();
        dd = dd < 10 ? '0'+dd : dd.toString();
        let hours:any = now.getHours();
        hours = hours < 10 ? '0'+hours : hours.toString();
        let minutes:any = now.getMinutes();
        minutes = minutes < 10 ? '0'+minutes : minutes.toString();
      
      return {
          year: yyyy,
          month: mm,
          date: dd,
          hours: hours,
          minutes: minutes,
          yyyymmdd: function(gubun='') { 
                        return yyyy+gubun+mm+gubun+dd 
                    },
          datetime: yyyy+'-'+mm+'-'+dd+'T'+hours+':'+minutes,
      }
    }

    logging(title:string, data:any){
        console.info("%c### "+title+": ", "color:blue", data);
    }
}