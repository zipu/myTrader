import { Routes, RouterModule } from '@angular/router';

import { OverviewComponent }   from './overview.component';
import { TradingComponent }   from './trading.component';
import { HistoryComponent }   from './history.component';

export const routes: Routes = [
  { path: 'overview', component: OverviewComponent },
  { path: 'trading', component: TradingComponent },
  { path: 'history', component: HistoryComponent },
  { path: '', redirectTo:'overview', pathMatch: 'full' }
];

export const routing = RouterModule.forRoot(routes);
