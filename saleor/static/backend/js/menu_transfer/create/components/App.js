import React, { Component } from 'react';
import TransferCart from '../containers/TransferCart';
import ItemSearch from '../containers/ItemSearch';
import '../css/styles.scss';
import 'react-toastify/dist/ReactToastify.css';
class App extends Component {
  render() {
    return (
        <div className="row">
            <div className="col-md-6 transfer-cart-wrapper">
              <TransferCart />
            </div>
            <div className="col-md-6 transfer-products-wrapper">
              <ItemSearch />
            </div>
        </div>
    );
  }
}

export default App;
