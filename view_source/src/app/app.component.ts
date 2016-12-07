import { Component} from '@angular/core';
//import { Router, RouteConfig, ROUTER_DIRECTIVES} from '@angular/router-deprecated';
import { CommonService } from './app.service';

//import { TradingComponent } from './trading.component';
//import { OverviewComponent } from './overview.component';


import '../../public/css/styles.css';

@Component({
    selector: 'Carpediem',
    template: require('./app.component.html'),
    //directives: [ROUTER_DIRECTIVES],
    //providers: [CommonService, KiwoomService]
})

/*
@RouteConfig([
    {
        path: '/overview',
        name: 'Overview',
        component: OverviewComponent,
        useAsDefault: true
    },
    {
        path: '/trading',
        name: 'Trading',
        component: TradingComponent,
    },
    {
        path: '/history',
        name: 'History',
        component: HistoryComponent,
        
    },
])
*/

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
      setTimeout( () => this.visible=false ,2000 )
    }
}