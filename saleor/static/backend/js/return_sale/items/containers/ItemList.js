import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import TransferTableRow from './TransferTableRow';
import ReactTooltip from 'react-tooltip';

class ItemList extends Component {
  /*
   * This component render panel group of accordions
   * Props: Listed in ItemList.propTypes below
   *        All props are fetch from redux
   *  Usage: <ItemList />
   * */
  render() {
    return (
      <div className="animated fadeIn panel-group panel-group-control panel-group-control-right content-group-lg">
        <h6 className="text-bold text-center">
         <span className="text-bold text-primary">DATE: </span>
         {this.props.items.date} &nbsp;
         <span className="text-bold text-primary">INVOICE NUMBER: </span>
         {this.props.items.invoice_number}
        </h6>
        <ReactTooltip place="bottom"/>
        <table className="table table-hover table-xs">
          <thead>
            <tr className="bg-primary">
              <th>Product</th>
              <th>Category</th>
              <th>SKU</th>
              <th>Cost Price</th>
              <th>Returned Qty</th>
              <th>Sold Qty</th>
              <th className="text-center no-print">Actions</th>
            </tr>
          </thead>
          <tbody>
          {this.props.items.results.map(obj => {
            return (
                  <TransferTableRow instance={obj}/>
            );
          })
          }
          <tr>
            <td colSpan={8}>
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
          </tbody>
        </table>
      </div>
    );
  }
}

ItemList.propTypes = {
  items: PropTypes.array.isRequired
};
function mapStateToProps(state) {
  return {
    items: state.items
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(ItemList);
