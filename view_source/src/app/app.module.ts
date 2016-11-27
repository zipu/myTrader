import { NgModule }       from '@angular/core';
import { BrowserModule  } from '@angular/platform-browser';
import { FormsModule }    from '@angular/forms';
import { LocationStrategy, HashLocationStrategy} from '@angular/common';
//import { Router, ROUTER_DIRECTIVES} from '@angular/router';
import { Router } from '@angular/router';
//components
import { AppComponent }   from './app.component';
import { OverviewComponent }   from './overview.component';
import { TradingComponent }   from './trading.component';
import { ChartComponent }   from './chart.component';
import { HistoryComponent }   from './history.component';

//services
import { KiwoomService, CommonService }  from './app.service';

//routing
import { routing } from './app.routing';

@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        routing
    ],
    providers: [
        {provide: LocationStrategy, useClass: HashLocationStrategy},
        KiwoomService,
        CommonService,
    ],
    declarations: [
        //ROUTER_DIRECTIVES,
        AppComponent,
        OverviewComponent,
        TradingComponent,
        ChartComponent,
        HistoryComponent
    ],
    
    bootstrap:    [AppComponent],
})
export class AppModule {}
