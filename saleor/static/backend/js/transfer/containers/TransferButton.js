import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
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

  handleSubmit = (e) => {
    e.preventDefault();
    console.log('we submit data');
    // console.warn(this.props.counter);
    // console.warn(this.props.cart);
    // console.warn(this.props.totalQty);
    // validate
    if (!this.props.counter) {
      toast.error('Counter not selected !');
      return;
    }

    if (this.props.cart.length < 1) {
      toast.error('Transfer Cart can not be empty');
      return;
    }

    // submit
    var formData = new FormData();

    formData.append('counter', this.props.counter);
    formData.append('counter_transfer_items', JSON.stringify(this.props.cart));

    api.create('/counter/transfer/api/create/', formData)
    .then((data) => {
      console.log(data);
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
  totalQty: PropTypes.number.isRequired,
  totalWth: PropTypes.number.isRequired
};
function mapStateToProps(state) {
  return {};
}

function matchActionsToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchActionsToProps)(TransferButton);
