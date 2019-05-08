import {DataPoint} from "./datapoint";

export interface Indicator {
  code: string;
  title: string;
  url: string;
  description: string;
  weight: number;
  calculated_weight: number;
  impact_percentage: number;
  threshold: number;
  data: DataPoint[];
}
