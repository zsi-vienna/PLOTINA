import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CoreIndicatorsComponent } from './core-indicators.component';

describe('CoreIndicatorsComponent', () => {
  let component: CoreIndicatorsComponent;
  let fixture: ComponentFixture<CoreIndicatorsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CoreIndicatorsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CoreIndicatorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
