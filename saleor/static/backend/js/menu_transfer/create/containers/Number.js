import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { ToastContainer } from 'react-toastify';
import jGrowl from 'jgrowl';

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
    try { jGrowl; } catch (error) {};
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
      $.jGrowl('Price must be a digit!', {
        header: 'Field error',
        theme: 'bg-danger'
      });
      return;
    } else if (value < 1) {
      $.jGrowl('Price must more than one!', {
        header: 'Field error',
        theme: 'bg-danger'
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
