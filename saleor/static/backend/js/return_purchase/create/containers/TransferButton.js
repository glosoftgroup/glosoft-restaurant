import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from '../api/Api';
import jGrowl from 'jgrowl';

export class TransferButton extends Component {
  constructor(props) {
    super(props);
    this.state = {
      totalQty: 0,
      totalWorth: 0,
      counter: ''
    };
  }
  componentDidMount() {
    try { jGrowl; } catch (error) {};
  }
  cartValidate = () => {
    var valid = true;
    this.props.cart.map((value, index) => {
      if (!value.qty) {
        valid = false;
      }
    });
    return valid;
  }

  handleSubmit = (e) => {
    e.preventDefault();
    var props = { ...this.props };
    var transferDate = props.date ? props.date.date : moment().format('YYYY-MM-DD');
    // submit
    var formData = new FormData();
    // validate
    formData.append('date', transferDate);
    if (!this.cartValidate()) {
      $.jGrowl('All returned items quantity in the cart should be a valid integer', {
        header: 'Invalid item quantity detected',
        theme: 'bg-danger'
      });
      return;
    }

    if (this.props.cart.length < 1) {
      $.jGrowl('Returning Cart can not be empty', {
        header: 'Your cart is empty',
        theme: 'bg-danger'
      });
      return;
    }
    formData.append('invoice_number', this.props.sale.invoice_number);
    formData.append('return_purchase_items', JSON.stringify(this.props.cart));

    api.create('/return/purchase/api/create/', formData)
    .then((data) => {
      window.location.href = '/return/purchase/';
    })
    .catch((error) => {
      console.log(error);
    });
  }

  render() {
    return (
        <div onClick={this.handleSubmit} className="btn bg-slate-800 btn-raised legitRipple">
          <ToastContainer />
          <i className="icon-circle-right2 icon-3x cursor-pointer"></i>
          <br />
          <span className="text-bold text-large">
            Return
          </span>
        </div>
    );
  }
}

TransferButton.propTypes = {
  cart: PropTypes.array.isRequired,
  closedCouters: PropTypes.array.isRequired,
  counter: PropTypes.object,
  sale: PropTypes.object,
  date: PropTypes.string.isRequired,
  totalQty: PropTypes.number.isRequired,
  totalWth: PropTypes.number.isRequired
};
function mapStateToProps(state) {
  return {
    date: state.date
  };
}

function matchActionsToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchActionsToProps)(TransferButton);
