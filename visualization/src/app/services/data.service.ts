import {Injectable} from '@angular/core';
import {ReplaySubject} from "rxjs/ReplaySubject";
import {HttpClient} from '@angular/common/http';
import {Indicator} from "../indicator";
import {DataPoint} from "../datapoint";
import {Subject} from "rxjs/Subject";
import 'rxjs/add/operator/map';

@Injectable()
export class DataService {

  private dataUrl = 'assets/data/visualization_data.json';
  private settingsUrl = 'assets/data/settings.json';

  // Observable source
  private weightChange = new Subject<boolean>();
  private impacts = new Subject<any[]>();

  // Observable stream
  weightChange$ = this.weightChange.asObservable();
  impacts$ = this.impacts.asObservable();

  private data: Indicator[];
  private data$ = new ReplaySubject(1);

  constructor(private http: HttpClient){}

  /**
   *
   * @param {boolean} forceRefresh
   * @returns {any}
   */
  getDaten(forceRefresh?: boolean): any {
    if (!this.data$.observers.length || forceRefresh) {
      this.http.get(this.dataUrl).subscribe(((d) => {
        this.http.get(this.settingsUrl).subscribe((s) => {
          let keys = Object.keys(d);
          let indicators = new Array<Indicator>();
          keys.map(key => {
            let dataPoints: DataPoint[];
            dataPoints = d[key]['data'].map(obj => {
              return {date: obj.date, m: obj.m, value: obj.value.toFixed(1)} as DataPoint;
            });
            if (s[key] && d[key] && !/non_normalized_*/.test(key) ) {
                indicators.push({
                    code: key,
                    title: d[key]["title"],
                    url: d[key]["url"],
                    description: d[key]['description'],
                    impact_percentage: null,
                    weight: (s[key]['weight'] || 0),
                    threshold: s[key]['threshold'],
                    data: dataPoints
                } as Indicator);
            }
          });
          indicators.push({code: "COMP", threshold: s["COMP"]["threshold"]} as Indicator);
          this.data = indicators;
          this.data$.next(this.data);
        });
      }));
    }
    return this.data$;
  }

  /**
   * FirstTime calculation
   * @param data
   * @returns {any}
   */
  calculateImpactWeight(data: Indicator[]){
    let impacts = [];
    let calculated_weight_sum: number = 0;

    var sire = new RegExp("^S.*$");
    var core = new RegExp("^CI.*$");

    // calculate calculated_weight for each indicator & calculated_weight_sum
    data.forEach((d)=>{
      if ( sire.test(d.title) || core.test(d.title) ) {
        let w = d.weight / 100;
        let cw = Math.pow(2, ((0.99 * w) / (1 - 0.99 * w)) ) - 1 ;
        d.calculated_weight = cw;
        calculated_weight_sum += cw;
      } else {
        d.weight = null;
        d.calculated_weight = null;
      }
    });
    data.forEach((d)=>{
      if ( sire.test(d.title) || core.test(d.title) ) {
        var impact:number = ((d.calculated_weight/calculated_weight_sum) * 100);
        d.impact_percentage = impact;
        impacts.push({code:d.code,impact:impact});
      }
    });
    this.impacts.next(impacts);
    return data;
  }

  // calc trigger
  weightChanged(weightChanged: boolean) {
    this.weightChange.next(weightChanged);
  }

  // indicator weight - slider value
  setWeight(dat: {code: string, weight: number}){
    this.data.map((d)=>{
      if(d.code === dat.code) {
        d.weight = dat.weight;
      }
    });
  }

  // indicator threshold - slider value
  setThreshold(dat: {code: string, threshold: number}){
    this.data.map((d)=>{
      if(d.code === dat.code)
        d.threshold = dat.threshold;
    });
  }

}
