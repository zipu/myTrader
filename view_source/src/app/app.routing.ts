import { Routes, RouterModule } from '@angular/router';

import { OverviewComponent }   from './overview.component';
import { TradingComponent }   from './trading.component';
import { RecordComponent }   from './record.component';

export const routes: Routes = [
  { path: 'overview', component: OverviewComponent },
  { path: 'trading', component: TradingComponent },
  { path: 'record', component: RecordComponent },
  { path: '', redirectTo:'overview', pathMatch: 'full' }
];

export const routing = RouterModule.forRoot(routes);
