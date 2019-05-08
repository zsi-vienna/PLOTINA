import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {HttpClientModule} from '@angular/common/http';
import {AppComponent} from './app.component';
import {SliderModule} from 'primeng/primeng';
import {DataService} from "./services/data.service";
import {SharedService} from "./services/shared.service";
import {RouterModule, Routes} from "@angular/router";
import {FormsModule} from "@angular/forms";
import {HelpComponent} from './components/help/help.component';
import {SettingsComponent} from './components/settings/settings.component';
import {IndicatorChartComponent} from './components/indicator-chart/indicator-chart.component';
import {CoreIndicatorsComponent} from './components/core-indicators/core-indicators.component';
import {CompositeChartComponent} from './components/composite-chart/composite-chart.component';
import {SpecificIndicatorsComponent} from './components/specific-indicators/specific-indicators.component';

const appRoutes: Routes = [
  { path: 'help', component: HelpComponent },
  { path: '', component: CoreIndicatorsComponent },
  { path: 'settings', component: SettingsComponent },
  { path: 'specific-indicators', component: SpecificIndicatorsComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    HelpComponent,
    SettingsComponent,
    IndicatorChartComponent,
    CoreIndicatorsComponent,
    CompositeChartComponent,
    SpecificIndicatorsComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    RouterModule.forRoot(appRoutes),
    SliderModule,
    HttpClientModule
  ],
  providers: [
    DataService,
    SharedService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
