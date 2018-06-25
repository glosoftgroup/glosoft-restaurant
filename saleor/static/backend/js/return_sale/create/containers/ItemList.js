import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { addItem } from '../actions/action-cart';

class ItemList extends Component {
  addCart = (obj) => {
    var payload = { ...obj };
    this.props.addItem(payload);
  }
  render() {
    return (
      <div className="table-responsive">
        <table className="table table-xs table-hover">
            <thead>
                <tr className="bg-primary">
                    <th className="text-center">Product</th>
                    <th className="text-center">SKU</th>
                    <th className="text-center">Quantity</th>
                    <th className="text-center">Add</th>
                </tr>
            </thead>
            <tbody>
            {this.props.items.results.map(obj => {
              return (
                <tr key={obj.id}>
                    <td>{obj.product_name}</td>
                    <td>{obj.sku}</td>
                    <td>{obj.quantity}</td>
                    <td title="add to cart" onClick={() => { this.addCart(obj); } }>
                      <span className="cursor-pointer btn btn-primary btn-sm">
                        <i className="icon-cart-add"></i>
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

ItemList.propTypes = {
  items: PropTypes.array.isRequired,
  addItem: PropTypes.func
};
function mapStateToProps(state) {
  return {
    items: state.items
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({
    addItem
  }, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(ItemList);
