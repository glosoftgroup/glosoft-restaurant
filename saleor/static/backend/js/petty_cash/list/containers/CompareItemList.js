import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import CompareListTableRow from './CompareListTableRow';
import ReactTooltip from 'react-tooltip';

class CompareItemList extends Component {
  /*
   * This component render panel group of accordions
   * Props: Listed in ItemList.propTypes below
   *        All props are fetch from redux
   *  Usage: <ItemList />
   * */
  render() {
    return (
      <div className="table-responsive panel-group panel-group-control panel-group-control-right content-group-lg">
        <h2 className="col-md-12 text-center text-bold yes-print">
        Petty Cash Report
        </h2>
        <ReactTooltip place="bottom"/>
        <table className="table table-hover table-xs">
          <caption>20-12-2018</caption>
          <thead>
            <tr className="bg-primary">
              <th data-tip="Opening cash">Opening</th>
              <th data-tip="Added cash">Added</th>
              <th data-tip="Total expenses">Expenses</th>
              <th data-tip="Closing cash">Closing</th>
              <th className="text-center no-print">Actions</th>
            </tr>
          </thead>
          <tbody>
          {this.props.items.results.map(obj => {
            return (
                  <CompareListTableRow instance={obj}/>
            );
          })
          }
          <tr>
            <td colSpan={6}>
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

CompareItemList.propTypes = {
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
export default connect(mapStateToProps, matchDispatchToProps)(CompareItemList);
