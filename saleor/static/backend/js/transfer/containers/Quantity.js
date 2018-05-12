import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export class Quantity extends Component {
  constructor(props) {
    super(props);
    this.state = {
      qty: '',
      maxQty: 0
    };
  }
  componentDidMount = () => {
    this.setState({
      qty: this.props.instance.quantity,
      maxQty: this.props.instance.quantity
    });
  }

  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }

  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;

    if (!this.isNumeric(value)) {
      toast.error('Quantity must be a digit!');
      return;
    }
    if (value > this.state.maxQty) {
      toast.error('Transfer Quantity cannot be more than ' + this.state.maxQty + '!');
    } else {
      this.setState({
        [e.target.name]: value
      });

      var payload = Object.assign(this.props.instance);
      payload.qty = value;
      this.props.updateCartItem(payload);
    }
  }

  render() {
    return (
      <div>
        <ToastContainer />
        <input value={this.props.instance.qty} onChange={ () => this.handleChange}
        type="number" name="quantity" className="form-control"
        />
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
