import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Quantity } from './Quantity';
import FilterDate from './FilterDate';
import { TransferButton } from './TransferButton';
import { updateCartItem, deleteCartItem } from '../actions/action-cart';
import { getTotalQty, getTotalWorth } from '../reducers';
import { setCounter } from '../actions/action-counter';

class TransferCart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      totalQty: 0,
      totalWorth: 0,
      counter: '',
      closedCouters: '',
      openCounters: '',
      allCounters: [{fake: 'counter'}]
    };
  }
  deleteItem = id => {
    this.props.deleteCartItem(id);
  }
  render() {
    return (
      <div className="product-cart-panel">
        {this.props.cart.length !== 0 &&
        <div >
          <div className="panel panel-body counter-panel">
            <div className="col-md-2 transfer-to-padding">
             <span className="text-bold">
               Date:
             </span>
            </div>
            <div className="col-md-4">
              <FilterDate/>
            </div>
          </div>
          <div className="table-responsive">
              <table className="table table-xs table-hover">
                  <thead>
                      <tr className="bg-primary">
                        <th>Product</th>
                        <th>SKU</th>
                        <th>Quantity</th>
                        <th>Remove</th>
                      </tr>
                  </thead>
                  <tbody>
                  {this.props.cart.map(obj => {
                    return (
                      <tr key={obj.id}>
                          <td>{obj.product_name}</td>
                          <td>{obj.sku}</td>
                          <td>
                            <Quantity
                            updateCartItem={(obj) => this.props.updateCartItem(obj) }
                            instance={obj}
                            cart={this.props.cart}
                            />
                          </td>
                          <td onClick={ () => this.deleteItem(obj.id)}>
                            <i className="animated shake icon-trash cursor-pointer"></i>
                          </td>
                      </tr>
                    );
                  })
                  }
                  </tbody>
              </table>

          </div>
          <div className="row transfer-section text-center mt-25">
            <div className="col-md-6">
                <div className="transfer-details">
                  <table className="table table-hover table-xm">
                    <thead>
                      <tr>
                        <th>Quantity</th>
                        <th>Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{this.props.totalQty}</td>
                        <td>{this.props.totalWth}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
            </div>
            <div className="col-md-6">
              <TransferButton closedCouters={this.state.closedCouters} date={this.props.date} cart={this.props.cart} sale={this.props.sale} counter={this.props.counter} />
            </div>
          </div>
        </div>
        }
        {this.props.cart.length === 0 &&
        <div className="order-empty text-center">
            <i className="animated shake icon-cart icon-3x"></i>
            <br />
            <h1 className="mt-15">
                Your returning cart is empty
            </h1>
        </div>
        }
      </div>
    );
  }
}

TransferCart.propTypes = {
  cart: PropTypes.array.isRequired,
  sale: PropTypes.object,
  counter: PropTypes.object,
  date: PropTypes.string.isRequired,
  totalQty: PropTypes.number.isRequired,
  totalWth: PropTypes.number.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  setCounter: PropTypes.func.isRequired,
  deleteCartItem: PropTypes.func.isRequired
};
function mapStateToProps(state) {
  return {
    cart: state.cart,
    sale: state.sale,
    counter: state.counter,
    date: state.date,
    totalQty: getTotalQty(state),
    totalWth: getTotalWorth(state)
  };
}

function matchActionsToProps(dispatch) {
  return bindActionCreators({
    setCounter,
    updateCartItem,
    deleteCartItem
  }, dispatch);
}

export default connect(mapStateToProps, matchActionsToProps)(TransferCart);
