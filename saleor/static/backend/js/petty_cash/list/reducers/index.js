import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemMode from './reducer-mode';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';

const allReducers = combineReducers({
  items: ItemReducer,
  search: ItemSearch,
  date: ItemDate,
  mode: ItemMode
});

export default allReducers;
