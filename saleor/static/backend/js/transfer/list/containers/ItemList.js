import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

class ItemList extends Component {
  addCart = (obj) => {
  }
  render() {
    return (
      <div className="table-responsive">
        <table className="table table-xs table-hover">
            <thead>
                <tr className="bg-primary">
                    <th>Counter</th>
                    <th>Date</th>
                    <th>Quantity</th>
                    <th>Worth</th>
                </tr>
            </thead>
            <tbody>
            {this.props.items.results.map(obj => {
              return (
                <tr key={obj.id}>
                    <td>{obj.counter.name}</td>
                    <td>{obj.created}</td>
                    <td>{obj.quantity}</td>
                    <td>{obj.worth}</td>
                </tr>
              );
            })
            }
            {this.props.items.results.length === 0 &&
            <tr>
                <td colSpan='5' className="text-center">
                    <h4>No data Found</h4>
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
