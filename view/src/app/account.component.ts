import { Component} from '@angular/core';

import { Balance } from './prototypes';
import { CommonService } from './app.service';



@Component({
    selector: 'account',
    template: require('./account.component.html'),
    styles: [require('./account.component.css')],
})

export class AccountComponent{
    _account: any;
    new_balance: Balance;
    account: Balance[];
    total: number;

    constructor(public service: CommonService) {}

    ngOnInit() {
    //historyDB object 로드 끝날때까지 기다림
        if ((<any>window).account == undefined) {
          setTimeout(() => {
            this.ngOnInit();
          }, 100);
        } else {
          this._account = (<any>window).account;
          this.new_balance = new Balance(this.service.now().yyyymmdd('-'));

          this.load_balances();
        }
    } 
    
    load_balances(){ 
        this._account.load_balances()
        .then( (data:Balance[])=> {
            this.account = data;
            this.total = 0;
            for (let i of this.account) {
                this.total = this.total + i.deposit - i.withdraw;
            }
        });
    }

    add_deposit(){
        this._account.add_deposit(this.new_balance);
        this.new_balance = new Balance(this.service.now().yyyymmdd('-'));
        this.load_balances();        
        this.service.logging("Account", "New deposit added")
    }

    removeItem(dep:any) {
        this._account.remove_item(dep)
        .then(()=>{
            this.load_balances();
        });
        this.service.logging("Account", "Item removed")
    }

}