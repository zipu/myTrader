import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule }              from './app/app.module';
//import { AppModuleNgFactory } from './app.module.ngfactory';

platformBrowserDynamic().bootstrapModule(AppModule);
//platformBrowser().bootstrapModuleFactory(AppModuleNgFactory);
