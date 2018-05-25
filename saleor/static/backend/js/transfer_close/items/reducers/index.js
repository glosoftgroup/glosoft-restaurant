import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import ReducerCart from './reducer-cart';

const allReducers = combineReducers({
  cart: ReducerCart,
  date: ItemDate,
  items: ItemReducer,
  search: ItemSearch
});

export default allReducers;
