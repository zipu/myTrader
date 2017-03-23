import { Routes, RouterModule } from '@angular/router';

import { OverviewComponent }   from './overview.component';
import { RecordComponent }   from './record.component';
import { MarketComponent }   from './market.component';
import { AccountComponent } from './account.component';

export const routes: Routes = [
  { path: 'overview', component: OverviewComponent },
  { path: 'market', component: MarketComponent},
  { path: 'record', component: RecordComponent },
  { path: 'account', component: AccountComponent },
  { path: '', redirectTo:'overview', pathMatch: 'full' }
];

export const routing = RouterModule.forRoot(routes);
