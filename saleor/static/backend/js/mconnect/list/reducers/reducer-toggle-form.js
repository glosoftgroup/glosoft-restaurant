/*
 * All reducers get two parameters passed in, state and action that occurred
 *       > state isn't entire apps state, only the part of state that this reducer is responsible for
 * */

// "state = null" is set so that we don't throw an error when app first boots up
import { SET_STATUS } from '../actions/action-toggle-form.js';

const initialState = {open: false};

export default function (state = initialState, action) {
  switch (action.type) {
    case SET_STATUS:
      return action.payload;
  }
  return state;
};
