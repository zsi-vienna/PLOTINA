import {Component, OnDestroy, OnInit} from '@angular/core';
import {SharedService}     from '../../services/shared.service';
import {DataService} from "../../services/data.service";
import {Subscription} from "rxjs/Subscription";
import {Indicator} from "../../indicator";

@Component({
  selector: 'specific-indicators',
  templateUrl: './specific-indicators.component.html',
  styleUrls: ['./specific-indicators.component.css']
})

export class SpecificIndicatorsComponent implements OnInit, OnDestroy {

  data: Indicator[];
  subscription: Subscription;

  private selectedIndex: number;

  constructor(private sharedService: SharedService, private dataService: DataService) {
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
        let re = new RegExp("^S.*$");
        if ( re.test(tmp.code) )
          return tmp;
      });
    });
  }
}
