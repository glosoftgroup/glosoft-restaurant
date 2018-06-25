import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { selectSale } from '../actions/action-selected-sale';
import { fetchItems } from '../actions/action-items';
import { clearCart } from '../actions/action-cart';

class SalesList extends Component {
  selectSale = (obj) => {
    var payload = { ...obj };
    this.props.fetchItems({}, obj.id);
    this.props.clearCart();
    this.props.selectSale(payload);
    this.props.closeModal();
  }
  render() {
    return (
      <div className="table-responsive">
       {this.props.cart.length > 0 &&
       <div className="alert alert-warning no-border text-center">
          <button type="button" className="close" data-dismiss="alert"><span>×</span><span className="sr-only">Close</span></button>
          <span>Selecting another purchase will clear your cart items.</span>
        </div>
       }
        <table className="table table-xs table-hover">
            <thead>
                <tr className="bg-primary">
                    <th>Invoice Number</th>
                    <th>Supplier</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th className="text-center">Select</th>
                </tr>
            </thead>
            <tbody>
            {this.props.items.results.map(obj => {
              return (
                <tr key={obj.id}>
                    <td>{obj.invoice_number}</td>
                    <td>{obj.supplier_name}</td>
                    <td>{obj.date}</td>
                    <td>{obj.total_net}</td>
                    <td className="text-center" onClick={() => { this.selectSale(obj); } }>
                      <span title="Click to select" className="cursor-pointer btn btn-primary btn-sm">
                        <i className="icon-select2"></i>Select
                      </span>
                    </td>
                </tr>
              );
            })
            }
            {this.props.items.results.length === 0 &&
            <tr>
                <td colSpan='5' className="text-center">
                {this.props.items.results.length === 0 &&
                <div className="text-center">
                  {this.props.items.loading &&
                    <h4 className="text-bold">Loading...</h4>
                  }
                  {!this.props.items.loading &&
                    <h4 className="text-bold">No data Found</h4>
                  }
                </div>
                }
                </td>
            </tr>
            }
            </tbody>
        </table>
      </div>
    );
  }
}

SalesList.propTypes = {
  items: PropTypes.array.isRequired,
  cart: PropTypes.array.isRequired,
  selectSale: PropTypes.func,
  closeModal: PropTypes.func,
  fetchItems: PropTypes.func,
  clearCart: PropTypes.func
};
function mapStateToProps(state) {
  return {
    items: state.sales,
    cart: state.cart
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({
    selectSale, fetchItems, clearCart
  }, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(SalesList);
