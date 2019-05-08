import {
  Component, OnInit, OnChanges, ViewChild,
  ElementRef, Input, OnDestroy, ViewEncapsulation,
  EventEmitter, Output
} from '@angular/core';
import {SharedService} from '../../services/shared.service';
import {Subscription}   from 'rxjs/Subscription';
import {DataService} from "../../services/data.service";
import {Indicator} from "../../indicator";
import {DataPoint} from "../../datapoint";
import * as d3 from "d3";
import * as _ from 'lodash';

@Component({
  selector: 'indicator-chart',
  templateUrl: './indicator-chart.component.html',
  styleUrls: ['./indicator-chart.component.css' ],
  encapsulation: ViewEncapsulation.None
})

export class IndicatorChartComponent implements OnInit, OnChanges, OnDestroy {

  @ViewChild('indicatorchart') private chartContainer: ElementRef;
  @Input() private indicator_data: Indicator;
  @Input() private selectedIndex: number;
  @Input() private indexShown: boolean;
  @Output() private weight_update: EventEmitter<{code: string, weight:number}> = new EventEmitter<{code: string, weight:number}>();

  description: string;
  weight: number;
  threshold: number;
  impact_percentage: number;
  title: string;
  bcolor: string;
  subscription: Subscription;

  private margin = {top: 30, right: 20, bottom: 40, left: 20 };
  private svg: any;
  private chartArea: any;
  private width: number;
  private height: number;
  private xScale: any;
  private yScale: any;
  private xAxis: any;
  private yAxis: any;
  private area: any;
  private hoverline: any;
  private thresholdline: any;
  private data: DataPoint[];
  private url: string;
  private code:string;

  constructor(private sharedService: SharedService, private dataService: DataService) {
    this.subscription = sharedService.indexShown$.subscribe(
      indexShown => {
        this.indexShown = indexShown;
        this.updateSelectedIndex(this.selectedIndex,this.indexShown);
      });
    this.subscription = dataService.impacts$.subscribe(
      impacts => {
        _.values(impacts).forEach((d)=>{
          if (d.code === this.indicator_data.code )
            this.impact_percentage = d.impact;
          });
      });
  }

  ngOnInit() {
    this.selectedIndex = (this.selectedIndex) ? this.selectedIndex : null;
    this.indexShown = (this.indexShown)? this.indexShown : false;

    if (this.indicator_data) {
      this.data = this.indicator_data.data;
      this.title = this.indicator_data.title;
      this.description = this.indicator_data.description;
      this.url = this.indicator_data.url;
      this.weight = this.indicator_data.weight;
      this.threshold = this.indicator_data.threshold;
      this.impact_percentage = this.indicator_data.impact_percentage;
      this.code = this.indicator_data.code;
      this.bcolor = ( /^S.*$/.test(this.indicator_data.code) ) ? "pear" :
        ( /^C.*$/.test(this.indicator_data.code) ) ? "apple" : "plum";
      this.createChart();
      this.updateChart();
    }
  }

  ngOnChanges(): void {
    if (this.chartArea) {
      this.updateChart();
    }
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  showDescription(){
    window.open(this.url, "_blank");
  }

  handleThresholdChange(e){
    let actualY = this.getTransformation(
      this.thresholdline.select(".threshold-line").attr("transform")).translateY;

    this.thresholdline
      .attr("transform","translate("+(0)+","+(this.yScale(this.threshold/100) - actualY + 0.5)+")");

    this.dataService.setThreshold({code: this.indicator_data.code, threshold: this.threshold});
  }

  handleWeightChange(e) {
    this.dataService.setWeight({code: this.indicator_data.code, weight: this.weight});
    // calc trigger on weight change
    this.dataService.weightChanged(true);
  }

  createChart() {
    let element = this.chartContainer.nativeElement;
    this.width = element.offsetWidth - this.margin.left - this.margin.right;
    this.height = element.offsetHeight - this.margin.top - this.margin.bottom;
    this.svg = d3.select(element).append('svg')
      .attr('width', element.offsetWidth)
      .attr('height', element.offsetHeight);

    // chartArea plot area
    this.chartArea = this.svg.append('g')
      .attr('class', 'chart-area')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

    // define X & Y domains
    let xDomain = this.data.map(function(d) { return d.m + ""; });
    let yDomain = [0, 1];

    // create scales
    this.xScale = d3.scalePoint().domain(xDomain).range([0, this.width]);
    this.yScale = d3.scaleLinear().domain(yDomain).range([this.height, 0]);

    // x & y axis
    this.xAxis = this.svg.append('g')
      .attr('class', 'axis axis-x')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top + this.height})`);

    //this.yAxis = d3.axisLeft(this.yScale);
    this.yAxis = this.svg.append('g')
      .attr('class', 'axis axis-y')
      .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);

    this.svg.selectAll('.axis-y').call(d3.axisLeft(this.yScale).ticks(1));

    // measure point area/chart
    this.area = d3.area<DataPoint>()
      .x((d) => { return this.xScale(d.m) } )
      .y0(this.height) // threshold?
      .y1((d) => {return this.yScale(d.value)});

    this.chartArea.append("path")
      .datum(this.data)
      .attr("class", "chart-path")
      .attr("d", this.area);

    // thresholdline
    this.thresholdline = this.chartArea.append("g")
      .attr("class","line");

    this.thresholdline.append("line")
      .attr("class", "x-threshold-line threshold-line")
      .attr("x1", 0) // x-start
      .attr("x2", this.width) // x-end
      .attr('transform', `translate(${0}, ${this.yScale((this.threshold/100))})`);

    // hover-line
    this.hoverline = this.chartArea.append("g")
      .attr("class", "line")
      .style("display", "none");

    this.hoverline.append("line")
      .attr("class", "x-hover-line hover-line")
      .attr("y1", 0)
      .attr("y2", this.height);

    this.hoverline.append("circle")
      .attr("r", 4.5);

    this.hoverline.append("text")
      .attr("class", "hover-text")
      .attr("x", -12)
      .attr("y", -20)
      .attr("dy", ".31em");

    // instance of your class for mouse stories
    var _instance = this;

    if (this.data.length > 2) {
      // overlay rect > for mouse movement tracking
      this.svg.append("rect")
        .attr("transform", "translate(" + (this.margin.left) + "," + this.margin.top + ")")
        .attr("class", "overlay")
        .attr("width", this.width)
        .attr("height", this.height)
        .on("mouseover", function(d,i){ _instance.hoverline.style("display", null)} )
        .on("mouseout", function(d,i){
          _instance.hoverline.style("display","none")
          _instance.sharedService.showIndex(false);
          _instance.sharedService.selectIndex(null);
        })
        .on('mousemove',  function(d, i) {
          var mouseScale = d3.scaleLinear()
            .domain([0, _instance.width])
            .range([0,_instance.data.length-1]);
          var idx = Math.round(mouseScale(d3.mouse(this)[0]));
          var dp = _instance.data[idx];

          _instance.sharedService.showIndex(true);
          _instance.sharedService.selectIndex(idx);
          _instance.hoverline.attr("transform", "translate(" + _instance.xScale(dp.m) + "," + _instance.yScale(dp.value) + ")");
          _instance.hoverline.select("text").text(function () {
            return dp.value;
          });
          _instance.hoverline.select(".x-hover-line").attr("y2", _instance.height - _instance.yScale(dp.value));
        });
    }
  }

  updateChart() {
    var tickValues = []; // default tickvalues > simple counter
    var dataLength = this.data.length;
    var dataCallback = function(d,idx) {
      d.m = d.m;
      d.value = +d.value;
      //tickValues.push(d.value);
      tickValues.push('T'+idx);
    };

    // Axis - special labeling if one value
    if( dataLength == 1 ) {
      ////////////
      var cloned = JSON.parse(JSON.stringify(this.data));
      var newPoint = { m:  this.data[0].m + 1, value: this.data[0].value };
      cloned.push(newPoint);
      cloned.forEach(dataCallback);

      this.xScale.domain(cloned.map(function(d) { return d.m; }));
      this.yScale.domain([0, 1]);

      var oneScale = d3.scalePoint().domain(d3.range(3).map((d) => d+"")).range([0, this.width]);
      this.svg.selectAll('.axis-x')
        .call(d3.axisBottom(oneScale).tickFormat(function(d, i) {
          if(i==1)
            return "T0";
        }));

        this.svg.selectAll('.axis-y')
            .call(d3.axisLeft(this.yScale).tickValues( [newPoint.value]));

        this.svg.selectAll('.axis-y').select('g.tick text').attr('x','-6');

      this.chartArea.selectAll('path')
        .transition().delay((d, i) => i * 2)
        .attr("d",this.area(cloned));
      ////////////
    } else {

      this.xScale.domain(this.data.map(function(d) { return d.m; }));
      this.yScale.domain([0, 1]);

      this.data.forEach(dataCallback);

      var m = (n: number, m: number) => {
        return ((n % m) + m) % m;
      };

      this.svg.selectAll('.axis-x')
        .call(d3.axisBottom(this.xScale).tickFormat(function(d, i) {
          if (dataLength < 8 ) {
              return tickValues[i];
          } else {
              if(m(i,2)==0)
                  return tickValues[i];
          }
        }));

      this.chartArea.selectAll('path')
        .transition().delay((d, i) => i * 2)
        .attr("d",this.area(this.data));

      //manually show or hide idx
      this.updateSelectedIndex(this.selectedIndex, this.indexShown);
    }
  }

  updateSelectedIndex(selectedIndex: number, indexShown: boolean) {
    if (indexShown === true && selectedIndex !== null) {
      this.hoverline.style("display", null);

      var d = this.data[selectedIndex];

      this.hoverline.attr("transform", "translate(" + this.xScale(d.m) + "," + this.yScale(d.value) + ")");
      this.hoverline.select("text").text(function () {
        return d.value;
      });

      this.hoverline.select(".x-hover-line").attr("y2", this.height - this.yScale(d.value));
      this.hoverline.select(".y-hover-line").attr("x2", this.width + this.width);

    } else {
      this.hoverline.style("display", "none");
    }
  }

  getTransformation(transform) {
    var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttributeNS(null, "transform", transform);
    var matrix = g.transform.baseVal.consolidate().matrix;
    var {a, b, c, d, e, f} = matrix;   // ES6, if this doesn't work, use below assignment
    var scaleX, scaleY, skewX;
    if (scaleX = Math.sqrt(a * a + b * b)) a /= scaleX, b /= scaleX;
    if (skewX = a * c + b * d) c -= a * skewX, d -= b * skewX;
    if (scaleY = Math.sqrt(c * c + d * d)) c /= scaleY, d /= scaleY, skewX /= scaleY;
    if (a * d < b * c) a = -a, b = -b, skewX = -skewX, scaleX = -scaleX;
    return {
      translateX: e,
      translateY: f,
      rotate: Math.atan2(b, a) * 180 / Math.PI,
      skewX: Math.atan(skewX) * 180 / Math.PI,
      scaleX: scaleX,
      scaleY: scaleY
    };
  }

}
