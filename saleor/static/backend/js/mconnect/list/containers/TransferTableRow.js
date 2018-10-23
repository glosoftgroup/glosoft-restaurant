import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';

export class TransferTableRow extends Component {
  /*
   * This component list stock transfers in rows
   * Props:
   *  instance: (Required) An object with stock transfer details
   *         Array of items to be rendered in transfered item table
   *  Usage: <TransferTableRow
   *            instance={object}
   *          />
   * */
  constructor(props) {
    super(props);
    this.state = {
      controlId: 'control',
      collapse: 'collapse',
      showDelete: false
    };
  }
  goTo = (url) => {
    window.location.href = url;
  }
  toggleDelete = () => {
    this.setState({showDelete: true});
    // reset delete confimartion
    setTimeout(() => {
      this.setState({showDelete: false});
    }, 3000);
  }
  deleteInstance = () => {
    api.destroy('/menu/api/delete/' + this.props.instance.id + '/')
    .then((response) => {
      this.props.fetchItems();
    })
    .catch((error) => {
      console.error(error);
    });
  }
  render() {
    var instance = { ...this.props.instance };

    return (
      <tr>
        <td>
          {instance.trans_id}
        </td>
        <td>
          {instance.first_name} {instance.middle_name} {instance.last_name}
        </td>
        <td>
          {instance.msisdn}
        </td>
        <td>
          {instance.business_short_code}
        </td>
        <td>
          {instance.transaction_type}
        </td>
        <td>
          {instance.trans_amount}
        </td>
    </tr>
    );
  }
}

TransferTableRow.propTypes = {
  instance: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired
};

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    fetchItems
  }, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(TransferTableRow);
