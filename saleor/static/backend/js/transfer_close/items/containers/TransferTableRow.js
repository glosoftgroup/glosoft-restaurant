import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';
import Quantity from './Quantity';
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
      deficit: 0,
      qty: 0,
      showDelete: false
    };
  }
  componentWillMount() {
    this.setState({
      deficit: this.props.instance.deficit,
      qty: this.props.instance.qty
    });
  }
  goTo = (url) => {
    window.location.href = url;
  }
  getDeficit = (actualQuantity) => {
    var instance = { ...this.props.instance };
    var deficit = instance.qty - actualQuantity;
    this.setState({deficit: deficit, qty: actualQuantity});
  }
  handleChange = (event) => {
    this.setState({description: event.target.value});
  }
  closeItem = (flag) => {
    // validate
    var closeDetails = {store: flag};
    var formData = new FormData();
    formData.append('close_details', JSON.stringify(closeDetails));
    formData.append('qty', this.state.qty);
    formData.append('deficit', this.state.deficit);
    formData.append('description', this.state.description);
    formData.append('price', this.props.instance.price);
    api.update('/counter/transfer/api/close/item/' + this.props.instance.id + '/', formData)
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
        <td>
          <span>
          {instance.productName}<br/>{instance.sku}
          </span>
        </td>
        <td>{instance.unit_price}</td>
        <td>{instance.transferred_qty}</td>
        <td>{instance.sold}</td>
        <td>
        {instance.closed &&
         <span>{instance.qty}</span>
        }
        {!instance.closed &&
          <Quantity getDeficit={this.getDeficit} instance={instance}/>
        }
        </td>
        <td>{instance.expected_qty}</td>
        <td>{this.state.deficit}</td>
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
