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

export class Price extends Component {
  constructor(props) {
    super(props);
    this.state = {
      price: 0,
      maxQty: 0,
      isOpen: false,
      edit: false
    };
  }

  componentDidMount = () => {
    this.setState({
      price: this.props.instance.price
    });
  }
  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }

  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;

    if (value === '') {
      this.setState({
        [e.target.name]: value
      });
    } else if (!this.isNumeric(value)) {
      toast.error('Quantity must be a digit!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    } else if (value < 1) {
      toast.error('Quantity must be more than one!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    } else {
      this.setState({
        [e.target.name]: value
      });
    }
  }

  handleSubmit = () => {
    // validate
    if (!this.isNumeric(this.state.price)) {
      toast.error('Quantity must be a digit!', {
        position: toast.POSITION.BOTTOM_CENTER
      });
      return;
    }
    var formData = new FormData();
    formData.append('close_details', JSON.stringify([]));
    formData.append('qty', this.props.instance.qty);
    formData.append('price', (this.state.price));
    api.update('/menu/transfer/api/update/item/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
      this.props.fetchItems();
    })
    .catch((error) => { console.log(error); });
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
          {!this.state.edit &&
          <Tooltip isOpen={this.state.isOpen} content={(
            <div>
              <div className="editableform" >
                <div className="control-group form-group">
                  <div className="editable-input">
                    <input value={this.state.price} onChange={this.handleChange}
                    type="number" name="price" className="form-control"
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
            <span data-tip="Edit price" className="edit-qty text-primary cursor-pointer">
              {this.props.instance.price}
            </span>
        </Tooltip>
          }
        </div>
        <div className="col-md-4 mt-5">
        {this.state.edit &&
         <span onClick={this.editInstance} className="animated zoomIn btn btn-sm btn-primary cursor-pointer">Save</span>
        }
        </div>
      </div>
    );
  }
}

Price.propTypes = {
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

export default connect(mapStateToProps, matchDispatchToProps)(Price);
