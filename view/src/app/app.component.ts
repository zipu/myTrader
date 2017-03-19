import { Component} from '@angular/core';
import { CommonService } from './app.service';

import '../../public/css/styles.css';

@Component({
    selector: 'Carpediem',
    template: require('./app.component.html'),
})


export class AppComponent{
    title = 'Carpediem';
    visible:boolean = false;
    alertMsg:string;
    
    constructor(
       // private router: Router,
        private commonService: CommonService
    ) {
        commonService.emitter.subscribe((msg:string) => {
            this.sendAlert(msg);
        });
        
    }

   
    sendAlert(msg:string) {
      this.alertMsg = msg;
      this.visible = true;
      setTimeout( () => this.visible=false ,5000 )
    }
}