import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import api from '../api/Api';

export class TransferButton extends Component {
  constructor(props) {
    super(props);
    this.state = {
      totalQty: 0,
      totalWorth: 0,
      counter: ''
    };
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
    console.log('we submit data');
    // submit
    var formData = new FormData();
    // validate
    if (!this.props.date) {
      formData.append('date', moment().format('YYYY-MM-DD'));
    } else {
      formData.append('date', this.props.date.date);
    }
    if (!this.props.counter) {
      toast.error('Please select Counter !', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }

    if (!this.cartValidate()) {
      toast.error('All transfer cart items quantity should be a valid integer', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }

    if (this.props.cart.length < 1) {
      toast.error('Transfer Cart can not be empty', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }
    formData.append('counter', this.props.counter.id);
    formData.append('counter_transfer_items', JSON.stringify(this.props.cart));

    api.create('/counter/transfer/api/create/', formData)
    .then((data) => {
      window.location.href = '/counter/transfer/';
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
                Transfer
            </span>
        </div>
    );
  }
}

TransferButton.propTypes = {
  cart: PropTypes.array.isRequired,
  counter: PropTypes.object,
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
