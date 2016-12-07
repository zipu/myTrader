import { Component} from '@angular/core';
import { CommonService } from './app.service';


@Component({
  selector: 'my-overview',
  template: require('./overview.component.html'),
})

export class OverviewComponent{
  private test:any = 'hi';
}

