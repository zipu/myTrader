import { bootstrap } from '@angular/platform-browser-dynamic';
import { enableProdMode, provide} from '@angular/core';
import { LocationStrategy, HashLocationStrategy } from '@angular/common';
import { ROUTER_PROVIDERS } from '@angular/router-deprecated';
import { disableDeprecatedForms, provideForms } from '@angular/forms';

import { AppComponent } from './app/app.component';

if (process.env.ENV === 'production') {
  enableProdMode();
}


bootstrap(AppComponent, [
  ROUTER_PROVIDERS,
  provide(LocationStrategy, {useClass: HashLocationStrategy}),
  disableDeprecatedForms(),
  provideForms()
])
.catch((err: any) => console.error(err));