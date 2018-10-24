import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import ToggleFormStatus from './reducer-toggle-form';

const allReducers = combineReducers({
  items: ItemReducer,
  search: ItemSearch,
  date: ItemDate,
  toggle: ToggleFormStatus
});

export default allReducers;
