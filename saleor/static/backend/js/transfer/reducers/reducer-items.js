import { SET_ITEMS, ADD_ITEM } from '../actions/action-items'

const initialState = []

export default (state = initialState, action) => {
  switch (action.type) {

  case ADD_ITEM:
    return { ...state }
  case SET_ITEMS:
    return action.payload;
  default:
    return state
  }
}
