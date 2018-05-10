import { ADD_FEE_ITEM, FEE_ITEM_UPDATED, FEE_ITEM_DELETED } from '../actions/action-fee-item'
const initialState = []

export default (state = initialState, action) => {
  switch (action.type) {
    case FEE_ITEM_UPDATED:
      return state.map(item => {
        if (item.id === action.payload.id) return action.payload;
        return item;
      });

    case FEE_ITEM_DELETED:
      return state.filter(item => item.id !== action.Id);

    case ADD_FEE_ITEM:
     var payload = Object.assign({id:false});
     state.map(item => {
      if (item.id === action.payload.id){
        payload = Object.assign({},action.payload)
        payload.id = action.payload.id + Math.random()
        payload.name = action.payload.name+'['+payload.id+']'
        
      }
    })
    console.log(payload)
      if(payload.id){
        state.concat(payload)
        return [ ...state, payload ]
      }else{
        return [ ...state, action.payload ]
      }
     
      

  default:
    return state
  }
}
