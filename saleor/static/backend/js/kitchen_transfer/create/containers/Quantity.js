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
      qty: 1,
      maxQty: 0
    };
  }

  componentDidMount = () => {
    this.setState({
      qty: this.props.instance.qty,
      maxQty: this.props.instance.quantity
    });
  }
  // componentDidUpdate(prevProps, prevState, snapshot) {
  //   console.log('inside update compoent');
  //   this.props.cart.map(value => {
  //     console.log(value.qty)
  //     console.warn(value.id);
  //     if (value.id === this.props.instance.id) {
  //       this.setState({qty: value.qty});
  //     }
  //   })
  // }
  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }
  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;
    if (value === '') {
      // pass
    } else if (!this.isNumeric(value)) {
      toast.error('Quantity must be a digit!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    } else if (value < 1) {
      toast.error('Each transferred item quantity must more than one!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }
    if (value > this.state.maxQty) {
      toast.error(this.props.instance.sku + ' has ' + this.state.maxQty + ' items remaining! You can not transfer more that.', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }

    this.setState({
      [e.target.name]: value
    });
    var payload = Object.assign(this.props.instance);
    payload.qty = value;
    this.props.updateCartItem(payload);
  }

  render() {
    return (
      <div>
        <ToastContainer />
        <input value={this.state.qty} onChange={this.handleChange}
          type="number" name="qty" className="form-control"
        />
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  cart: PropTypes.array.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
