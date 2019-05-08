import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SpecificIndicatorsComponent } from './specific-indicators.component';

describe('SpecificIndicatorsComponent', () => {
  let component: SpecificIndicatorsComponent;
  let fixture: ComponentFixture<SpecificIndicatorsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SpecificIndicatorsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SpecificIndicatorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
