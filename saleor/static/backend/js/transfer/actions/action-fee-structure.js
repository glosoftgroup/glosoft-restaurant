export const SET_STRUCTURE  = 'SET_STRUCTURE'
export const ADD_STRUCTURE  = 'ADD_STRUCTURE'
export const STRUCTURE_DELETED  = 'STRUCTURE_DELETED'
export const ADD_FEE_ITEM = 'ADD_FEE_ITEM'

export const selectStructure = (payload) => {    
    return {
        type: SET_STRUCTURE,
        payload
    }
};

export const addStructure = (payload) => {    
    return {
        type: ADD_STRUCTURE,
        payload
    }
};

export function deleteStructure(item) {
    return {
      type: STRUCTURE_DELETED,
      item
    }
}