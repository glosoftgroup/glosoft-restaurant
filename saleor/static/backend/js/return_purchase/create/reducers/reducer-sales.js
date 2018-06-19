import { SET_SALES } from '../actions/action-sales';

const initialState = {
  'links': {
    'next': null,
    'previous': null
  },
  'count': 7,
  'total_pages': 1,
  'loading': true,
  'results': []
};
export default (state = initialState, action) => {
  switch (action.type) {
    case SET_SALES:
      return action.payload;
    default:
      return state;
  }
};
