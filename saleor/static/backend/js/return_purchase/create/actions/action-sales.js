import api from '../api/Api';

export const SET_SALES = 'SET_SALES';

export const setSales = (payload) => ({
  type: SET_SALES,
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
    api.retrieve('/api/purchase/variant?' + url)
    .then(data => {
      data.loading = false;
      dispatch(setSales(data.data));
    });
  };
};
