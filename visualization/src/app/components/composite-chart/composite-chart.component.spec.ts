import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CompositeChartComponent } from './composite-chart.component';

describe('CompositeChartComponent', () => {
  let component: CompositeChartComponent;
  let fixture: ComponentFixture<CompositeChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CompositeChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CompositeChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
