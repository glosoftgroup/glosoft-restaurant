import React, { Component } from 'react';
import TransferCart from '../containers/TransferCart';
import ItemSearch from '../containers/ItemSearch';
import TransferModal from '../containers/TransferModal';
import '../css/styles.scss';
class App extends Component {
  render() {
    return (
        <div className="rowg">
          <div className="col-md-12 p-15 text-center">
           <TransferModal />
           <hr/>
          </div>
          <div className="col-md-12 text-center">
            <div className="col-md-5 transfer-cart-wrapper">
              <TransferCart />
            </div>
            <div className="col-md-7 transfer-products-wrapper">
              <ItemSearch />
            </div>
          </div>
        </div>
    );
  }
}

export default App;
