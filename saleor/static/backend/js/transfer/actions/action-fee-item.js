export const SET_FEE_ITEM  = 'SET_FEE_ITEM'
export const ADD_FEE_ITEM = 'ADD_FEE_ITEM'
export const FEE_ITEM_DELETED  = 'FEE_ITEM_DELETED'
export const FEE_ITEM_UPDATED = 'FEE_ITEM_UPDATED'

export const addFeeItem = (payload) => ({
  type: ADD_FEE_ITEM,
  payload
})

export const deleteFeeItem = (Id) => ({
  type: FEE_ITEM_DELETED,
  Id
})

export const updateFeeItem = (payload) => ({
  type: FEE_ITEM_UPDATED,
  payload
})
