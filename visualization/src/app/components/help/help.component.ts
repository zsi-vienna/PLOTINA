import {Component, OnInit} from '@angular/core';
import {DataService} from "../../services/data.service";
import {Indicator} from "../../indicator";

@Component({
  selector: 'app-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {

  data: Indicator[];

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.dataService.getDaten().subscribe((d)=>{this.data=d;});
  }

}
