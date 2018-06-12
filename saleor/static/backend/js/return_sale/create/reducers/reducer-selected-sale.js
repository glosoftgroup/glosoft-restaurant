import { SELECT_SALE } from '../actions/action-selected-sale';

const initialState = {};
export default (state = initialState, action) => {
  switch (action.type) {
    case SELECT_SALE:
      return action.payload;
    default:
      return state;
  }
};
