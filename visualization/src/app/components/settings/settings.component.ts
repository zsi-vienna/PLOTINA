import {Component, OnInit} from '@angular/core';
import {DataService} from "../../services/data.service";
import {Indicator} from "../../indicator";
import * as FileSaver from 'file-saver';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {

  data: Indicator[];

  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.dataService.getDaten().subscribe((d)=>{this.data = d;});
  }

  downloadWeights(){
    let str = {};
    this.data.map((d)=>{
      str[d.code] = {"weight":d.weight, "threshold":d.threshold};
    });
    let blob = new Blob([JSON.stringify(str)], { type: 'application/json;charset=utf-8' });
    FileSaver.saveAs(blob, 'settings.json');
  }
}
