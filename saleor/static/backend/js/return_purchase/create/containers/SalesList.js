import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { selectSale } from '../actions/action-selected-sale';
import { fetchItems } from '../actions/action-items';

class SalesList extends Component {
  selectSale = (obj) => {
    var payload = { ...obj };
    this.props.fetchItems({}, obj.id);
    this.props.selectSale(payload);
    this.props.closeModal();
  }
  render() {
    return (
      <div className="table-responsive">
        <table className="table table-xs table-hover">
            <thead>
                <tr className="bg-primary">
                    <th>Select</th>
                    <th>Invoice Number</th>
                    <th>Date</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
            {this.props.items.results.map(obj => {
              return (
                <tr key={obj.id}>
                    <td onClick={() => { this.selectSale(obj); } }>
                      <span title="Click to select" className="cursor-pointer btn btn-primary btn-sm">
                        <i className="icon-select2"></i>Select
                      </span>
                    </td>
                    <td>{obj.invoice_number}</td>
                    <td>{obj.created}</td>
                    <td>{obj.total_net}</td>
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
  selectSale: PropTypes.func,
  closeModal: PropTypes.func,
  fetchItems: PropTypes.func
};
function mapStateToProps(state) {
  return {
    items: state.sales
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({
    selectSale, fetchItems
  }, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(SalesList);
