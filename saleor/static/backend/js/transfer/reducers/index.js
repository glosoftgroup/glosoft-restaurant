import { combineReducers } from 'redux';

import ItemReducer from './reducer-items';
import reducerCart from './reducer-cart';

const allReducers = combineReducers({
  items: ItemReducer,
  cart: reducerCart
});

export default allReducers;
