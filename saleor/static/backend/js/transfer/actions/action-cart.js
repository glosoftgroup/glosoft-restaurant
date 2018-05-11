export const ADD_ITEM = 'ADD_ITEM';
export const DELETE_ITEM = 'DELETE_ITEM';
export const UPDATE_ITEM = 'UPDATE_ITEM';

export const addItem = (payload) => ({
  type: ADD_ITEM,
  payload
});

export const deleteItem = (itemId) => ({
  type: DELETE_ITEM,
  itemId
});

export const updateItem = (payload) => ({
  type: UPDATE_ITEM,
  payload
});

