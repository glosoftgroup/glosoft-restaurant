import { SET_STRUCTURE, ADD_STRUCTURE, STRUCTURE_DELETED } from '../actions/action-fee-structure';

const initial = {    
        "amount": 7,
        "academic_year": 1,
        "term":'',
        "fee_items": []
}
export default function(state = initial, action = {}) {
  switch(action.type) { 
    case STRUCTURE_DELETED:
      return state.results.filter(item => item !== action.item);
    
    case ADD_STRUCTURE:
      return [
        ...state,
        action.payload
      ];  
    case SET_STRUCTURE:
      return action.payload;
    default: return state;
  }
}