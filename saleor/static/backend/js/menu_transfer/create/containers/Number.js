import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { ToastContainer, toast } from 'react-toastify';

export class Number extends Component {
  constructor(props) {
    super(props);
    this.state = {
      number: 1
    };
  }

  componentDidMount = () => {
    this.setState({
      number: this.props.instance.price
    });
  }
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
      toast.error('Quantity must more than one!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }

    this.setState({
      [e.target.name]: value
    });
    var payload = Object.assign(this.props.instance);
    payload.price = value;
    this.props.updateCartItem(payload);
  }

  render() {
    return (
      <div>
        <ToastContainer />
        <input value={this.state.number} onChange={this.handleChange}
          type="number" name="number" className="form-control"
        />
      </div>
    );
  }
}

Number.propTypes = {
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

export default connect(mapStateToProps, matchDispatchToProps)(Number);
