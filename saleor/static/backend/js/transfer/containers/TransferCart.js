import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Quantity } from './Quantity';
import { updateCartItem, deleteCartItem } from '../actions/action-cart';

class TransferCart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      totalQty: 0,
      totalWorth: 0
    };
  }
  // componentWillUpdate(nextProps, nextState) {
  //   // compute total products/worth
  //   var totalWorth = 0;
  //   var totalQty = 0;
  //   // nextProps.cart.map((value, index) => {
  //   //   totalQty += parseInt(value.qty);
  //   //   totalWorth += parseInt(value.price) * parseInt(value.qty);
  //   // });
  //   this.setState({
  //     totalQty: totalQty,
  //     totalWorth: totalWorth
  //   });
  // }
  deleteItem = id => {
    this.props.deleteCartItem(id);
  }
  render() {
    return (
      <div className="product-cart-panel">
        {this.props.cart.length !== 0 &&
        <div >
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
                          <td>{obj.productName}</td>
                          <td>{obj.sku}</td>
                          <td>
                            <Quantity
                            updateCartItem={(obj) => this.props.updateCartItem(obj) }
                            instance={obj}
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
                </div>
            </div>
            <div className="col-md-6">
              <i className="icon-circle-right2 icon-3x cursor-pointer"></i>
              <br />
              <span className="text-bold text-large">
                Transfer
              </span>
            </div>
          </div>
        </div>
        }
        {this.props.cart.length === 0 &&
        <div className="order-empty text-center">
            <i className="animated shake icon-cart icon-3x"></i>
            <br />
            <h1 className="mt-15">
                Your transfer cart is empty
            </h1>
        </div>
        }
      </div>
    );
  }
}

TransferCart.propTypes = {
  cart: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  deleteCartItem: PropTypes.func.isRequired
};
function mapStateToProps(state) {
  return {
    cart: state.cart
  };
}

function matchActionsToProps(dispatch) {
  return bindActionCreators({
    updateCartItem, deleteCartItem
  }, dispatch);
}

export default connect(mapStateToProps, matchActionsToProps)(TransferCart);
