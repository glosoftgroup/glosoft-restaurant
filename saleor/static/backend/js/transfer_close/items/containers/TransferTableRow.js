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
      description: '',
      showDelete: false
    };
  }
  goTo = (url) => {
    window.location.href = url;
  }
  handleChange = (event) => {
    this.setState({description: event.target.value});
  }
  closeItem = (flag) => {
    // validate
    var closeDetails = {store: flag};
    var formData = new FormData();
    formData.append('close_details', JSON.stringify(closeDetails));
    formData.append('qty', this.props.instance.qty);
    formData.append('description', this.state.description);
    formData.append('price', this.props.instance.price);
    api.update('/counter/transfer/api/update/item/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
      this.props.fetchItems();
    })
    .catch((error) => { console.log(error); });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <tr>
        <td>.</td>
        <td>{instance.productName}</td>
        <td>{instance.sku}</td>
        <td>{instance.unit_price}</td>
        <td>{instance.qty}</td>
        <td>{instance.sold}</td>
        <td>{instance.price}</td>
        <td>
        {instance.closed &&
         <span>{instance.description}</span>
        }
        {!instance.closed &&
         <textarea className="form-control text-field" value={this.state.description} onChange={this.handleChange} />
        }
        </td>
        <td className="text-center">
          {!instance.closed &&
          <span>
          <a onClick={ () => this.closeItem(false)} href="javascript:;" className="label label-primary">Carry forward</a>
          &nbsp;&nbsp;
          <a onClick={ () => this.closeItem(true)} href="javascript:;" className="label label-success">Return to stock</a>
          </span>
          }
          {instance.closed &&
          <span className="text-success">Closed</span>
          }
        </td>
    </tr>
    );
  }
}

TransferTableRow.propTypes = {
  instance: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({fetchItems}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(TransferTableRow);
