import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
class TransferCart extends Component {
  tableBody = () => {
    this.props.cart.map(obj => {
      return (
          <tr key={obj.id}>
              <td onClick={() => { this.handleShow(obj); } }>
                <span className="cursor-pointer btn btn-primary btn-sm">
                  <i className="icon-cart-add"></i>
                </span>
              </td>
              <td>{obj.productName}</td>
              <td>{obj.sku}</td>
              <td>{obj.quantity}</td>
              <td>{obj.price}</td>
          </tr>
      );
    });
  }
  render() {
    return (
      <div>
        <div className="table-responsive">
            <table className="table table-xs table-hover">
                <thead>
                    <tr className="bg-primary">
                        <th>Add</th>
                        <th>Product</th>
                        <th>SKU</th>
                        <th>Quantity</th>
                        <th>Selling Price</th>
                    </tr>
                </thead>
                {this.tableBody()}
            </table>
        </div>
        <div className="order-empty text-center">
            <i className="animated shake icon-cart icon-3x"></i>
            <br />
            <h1 className="mt-15">
                Your transfer cart is empty
            </h1>
        </div>
      </div>
    );
  }
}

TransferCart.propTypes = {
  cart: PropTypes.array.isRequired
};
function mapStateToProps(state) {
  return {
    cart: state.cart
  };
}

export default connect(mapStateToProps)(TransferCart);
