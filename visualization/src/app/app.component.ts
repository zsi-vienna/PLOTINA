import {Component, Input, OnInit, OnDestroy} from '@angular/core';
import {SharedService} from "./services/shared.service";
import {DataService} from "./services/data.service";
import {Subscription}   from 'rxjs/Subscription';
import {Indicator} from "./indicator";

import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit, OnDestroy {

  @Input() private settings_data: any[];  // << changed weights - from sharedService
  @Input() indicator_data: any[];         // << data for chart [{m:,val:,},{}] create in generateCompositeIndicatorData()

  private selectedIndex: number;
  private weightChanged: boolean;
  private threshold: number;

  public demo: string = "";

  data: Indicator[];
  subscription: Subscription;

  constructor(private sharedService: SharedService, private dataService: DataService) {
    this.subscription = sharedService.selectedIndex$.subscribe(
      selectedIndex => {
        this.selectedIndex = selectedIndex
      });
    this.subscription = dataService.weightChange$.subscribe(
        weightChanged => {
          this.weightChanged = weightChanged;
          this.calculateCompositeIndicatorData();
        });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  ngOnInit() {
    this.dataService.getDaten().subscribe((d)=>{
      this.data = d;
      this.calculateCompositeIndicatorData();
      var comp = this.data.find(x => x.code === "COMP");
      if (comp){
        this.threshold = comp.threshold;
      } else {
        this.threshold = 0;
      }
    });
    if (environment.demo == true)
      this.demo = "--- DEMO SITE ---";
  }

  calculateCompositeIndicatorData(){
    // calculated values for chart
    let indicators = [];
    this.data = this.dataService.calculateImpactWeight(this.data);

    if(this.data){ // orig data
      // get measure points count & indicator count
      var measurePointCount: number = this.data[0].data.length;

      for (var i=1; i <= measurePointCount; i++) {  // for each measurepoint

        var measurePointMatrix = [[]];
        this.data.forEach((k,indicatorIndex)=> { // for each indikator

          //if ( k.code !== 'COMP' && k.impact_percentage >= 0 && k.data[i-1] && k.data[i-1].value >= 0){
          if ( k.code !== 'COMP' ){
            measurePointMatrix[indicatorIndex] =
              [k.data[i-1].value, k.impact_percentage, null, null];

          }
        });
        let calculatedValue = 0;
        measurePointMatrix.map((m)=>{
          calculatedValue += ((m[0]/100) * m[1]);
        });
        indicators.push({ "m": i, "value": calculatedValue.toFixed(2)  });
      }
    }
    this.indicator_data = indicators;
  }

}
