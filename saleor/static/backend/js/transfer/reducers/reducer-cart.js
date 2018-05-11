import { ADD_ITEM, DELETE_ITEM, UPDATE_ITEM } from '../actions/action-cart';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case ADD_ITEM:
      return [...state, action.payload];
    case DELETE_ITEM:
      return state.filter(item => item._id !== action.itemId);
    case UPDATE_ITEM:
      return state.map(item => {
        if (item.id === action.payload.id) return action.payload;
        return item;
      });
    default:
      return state;
  }
};
