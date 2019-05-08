import {Injectable} from '@angular/core';
import {Subject}    from 'rxjs/Subject';

@Injectable()
export class SharedService {

  // Observable source
  private selectedIndex = new Subject<number>();
  private indexShown = new Subject<boolean>();

  // Observable stream
  selectedIndex$ = this.selectedIndex.asObservable();
  indexShown$ = this.indexShown.asObservable();

  constructor(){}

  // Service message commands
  selectIndex(selectedIndex: number) {
    this.selectedIndex.next(selectedIndex);
  }

  showIndex(indexShown: boolean) {
    this.indexShown.next(indexShown);
  }
}

