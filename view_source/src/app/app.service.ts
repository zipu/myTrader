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
    
    quit() {
        this.kiwoom.quit();
    }
    
    disconnect(scrno:string) {
        this.kiwoom.disconnect(scrno);
    }
    
    connectState():Promise<any> {
        return this.kiwoom.connectState();
    }
    
    getProducts():any {
        return this.kiwoom.getProducts()
                .then((data:Object) => {
                   return data;
                });           
    }

    getFavorits():any {
        return this.kiwoom.getFavList()
                .then((data:Object) => {
                    return data;
                });
    }
    
    addToFav(fav:string[]) {
        this.kiwoom.addToFav(fav);
    }
    
    getProductsReal(scrNo:string, inputValue:string[]) {
        this.kiwoom.requestProductsReal(scrNo, inputValue);
    }
    
    getProductInfo(code:string) {
        this.kiwoom.getProductInfo(code);
    }

    getChartData(code:string){
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
          yyyymmdd: yyyy+mm+dd,
          datetime: yyyy+'-'+mm+'-'+dd+'T'+hours+':'+minutes,
      }
    }

}
