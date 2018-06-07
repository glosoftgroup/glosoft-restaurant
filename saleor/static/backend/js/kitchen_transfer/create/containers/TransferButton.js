import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import { ToastContainer, toast } from 'react-toastify';
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
    if (!this.props.counter) {
      $.jGrowl('Please select Kitchen !. Did you forget to close kitchen transfer?', {
        header: 'Kitchen required',
        theme: 'bg-danger'
      });
      return;
    }
    // find seleted counter in closded counters
    var found = props.closedCouters.find(function(element) {
      return element.id === parseInt(props.counter.id);
    });
    if (found) {
      if (moment(transferDate).isAfter(moment(found.last_open))) {
        // You must close later date which is probably todays transfer
        var msg = 'Please close ' + found.last_open + ' kitchen transfer for ' + found.name + '.';
        $.jGrowl(msg, {
          header: '',
          theme: 'bg-danger'
        });
        return;
      }
    } else {
      console.warn('not found');
    }
    // submit
    var formData = new FormData();
    // validate
    formData.append('date', transferDate);

    if (!this.cartValidate()) {
      $.jGrowl('All transfer cart items quantity should be a valid integer', {
        header: '',
        theme: 'bg-danger'
      });
      return;
    }

    if (this.props.cart.length < 1) {
      $.jGrowl('Transfer Cart can not be empty', {
        header: '',
        theme: 'bg-danger'
      });
      toast.error('Transfer Cart can not be empty', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }
    formData.append('counter', this.props.counter.id);
    formData.append('kitchen_transfer_items', JSON.stringify(this.props.cart));

    api.create('/kitchen/transfer/api/create/', formData)
    .then((data) => {
      window.location.href = '/kitchen/transfer/';
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
  closedCouters: PropTypes.array.isRequired,
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
