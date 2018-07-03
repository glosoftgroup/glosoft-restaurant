import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import charts from './reducer-charts';

const allReducers = combineReducers({
  items: ItemReducer,
  search: ItemSearch,
  date: ItemDate,
  charts
});

export default allReducers;
