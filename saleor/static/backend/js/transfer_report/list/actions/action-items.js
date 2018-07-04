import api from '../api/Api';
/**
 * Constants
 */
export const SET_ITEMS = 'SET_ITEMS';
export const ADD_ITEM = 'ADD_ITEM';
export const UPDATE_ITEM = 'UPDATE_ITEM';

/**
 * Actions
 */
import { setChartOptions } from '../actions/action-charts';

export const setItems = (payload) => ({
  type: SET_ITEMS,
  payload
});

export const updateItem = (payload) => ({
  type: SET_ITEMS,
  payload
});

export const fetchItems = (params = {}) => {
  return dispatch => {
    // extract url parameters
    var url = '';
    if (typeof params === 'object') {
      if (Object.keys(params).length >= 1) {
        Object.keys(params).forEach(function(key) {
          url += key + '=' + params[key] + '&';
        });
        // remove last &
        url = url.slice(0, -1);
      }
    }
    // listing items
    api.retrieve('/counter/transfer/report/api/list?' + url)
    .then(data => {
      data.loading = false;
      dispatch(setItems(data.data));
    })
    .catch(error => console.error(error));
    // fetch graph data
    api.retrieve(`/counter/transfer/report/api/graph/recharts/?${url}`)
    // Api.retrieve('/counter/transfer/report/api/graph/')
    .then(response => { return response.data; })
    .then(data => {
      // console.error(data);
      dispatch(setChartOptions(data));
    })
    .catch(error => console.error(error));
  };
};
