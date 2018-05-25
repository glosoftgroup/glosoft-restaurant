import React, { Component } from 'react';
import PropTypes from 'prop-types';
import api from '../api/Api';

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
    api.destroy('/counter/transfer/api/delete/' + this.props.instance.id + '/')
    .then((response) => {
      window.location.reload();
    })
    .catch((error) => {
      console.error(error);
    });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <tr className="cursor-pointer" onClick={ () => this.goTo(instance.closing_items_url)}>
        <td>{instance.date}</td>
        <td>{instance.counter.name}</td>
        <td>{instance.quantity}</td>
        <td>{instance.worth}</td>
        <td>
          {instance.all_item_closed &&
            <span className="text-success">closed</span>
          }
          {!instance.all_item_closed &&
            <span>open</span>
          }
        </td>
    </tr>
    );
  }
}

TransferTableRow.propTypes = {
  instance: PropTypes.object.isRequired
};
export default TransferTableRow;