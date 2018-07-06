import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import charts from './reducer-charts';
import pie from './reducer-pie';
import mode from './reducer-mode';
import openGraph from './reducer-toggle-graph';

const allReducers = combineReducers({
  items: ItemReducer,
  search: ItemSearch,
  date: ItemDate,
  charts: charts,
  mode,
  pie,
  openGraph
});

export default allReducers;
