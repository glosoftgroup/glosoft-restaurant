import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Tooltip from 'react-tooltip-lite';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export class Quantity extends Component {
  constructor(props) {
    super(props);
    this.state = {
      field: '',
      isOpen: false,
      edit: false
    };
  }

  componentDidMount = () => {
    this.setState({
      field: this.props.instance.name
    });
  }
  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }

  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;

    this.setState({
      [e.target.name]: value
    });
  }

  handleSubmit = () => {
    // validate
    if (this.state.field === '') {
      toast.error('Menu name is required');
      return;
    }
    var formData = new FormData();
    var instance = {...this.props.instance};
    formData.append('quantity', instance.quantity);
    formData.append('category', instance.category.id);
    formData.append('price', instance.price);
    formData.append('name', this.state.field);
    api.update('/menu/api/update/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
      this.props.fetchItems();
    })
    .catch((error) => {
      console.error(error);
      toast.error('Try a different Menu name!');
    });
  }

  toggleEdit = () => {
    this.setState({isOpen: !this.state.isOpen});
  }

  render() {
    return (
      <div className="row">
        <ToastContainer />
        <ReactTooltip place="bottom"/>
        <div onClick={this.toggleEdit} className="col-md-8">
          <Tooltip isOpen={this.state.isOpen} content={(
            <div>
              <div className="editableform" >
                <div className="control-group form-group">
                  <div className="editable-input">
                    <input value={this.state.field} onChange={this.handleChange}
                    type="text" name="field" className="form-control"
                    />
                  </div>
                  <div className="editable-buttons">
                    <button onClick={this.handleSubmit} type="submit" className="btn btn-primary btn-icon editable-submit">
                      <i className="icon-check"></i>
                    </button>
                    <button onClick={this.toggleEdit} type="button" className="btn btn-default btn-icon editable-cancel">
                      <i className="icon-x"></i>
                    </button>
                  </div>
                  <div className="editable-error-block help-block hidden"></div>
                </div>
              </div>
            </div>
          )}
            className="target" tagName="span" eventToggle="onClick">
            <span data-tip="Edit Name" className="edit-qty text-primary cursor-pointer">
              {this.props.instance.name}
            </span>
        </Tooltip>
        </div>
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({fetchItems}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
