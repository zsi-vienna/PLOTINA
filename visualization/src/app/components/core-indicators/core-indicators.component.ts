import { Component, OnDestroy, OnInit } from '@angular/core';
import { SharedService }     from '../../services/shared.service';
import { DataService } from "../../services/data.service";
import { Subscription } from "rxjs/Subscription";
import {Indicator} from "../../indicator";

@Component({
  selector: 'core-indicators',
  templateUrl: './core-indicators.component.html',
  styleUrls: ['./core-indicators.component.css']
})

export class CoreIndicatorsComponent implements OnInit, OnDestroy {

  data: Indicator[];
  subscription: Subscription;

  private selectedIndex: number;

  constructor(private sharedService: SharedService, private dataService: DataService) {
    this.subscription = sharedService.selectedIndex$.subscribe(
      selectedIndex => {
        this.selectedIndex = selectedIndex
      });

    this.subscription = sharedService.selectedIndex$.subscribe(
      selectedIndex => {
        this.selectedIndex = selectedIndex
      });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  ngOnInit() {
    this.dataService.getDaten().subscribe((d)=>{
      this.data = d.map((tmp)=>{
        let re = new RegExp("^CI.*$");
        if ( re.test(tmp.code) )
          return tmp;
      });
    });
  }
}
