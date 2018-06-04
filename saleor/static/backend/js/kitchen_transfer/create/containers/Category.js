import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Tooltip from 'react-tooltip-lite';
import api from '../api/Api';
// import { fetchItems } from '../actions/action-items';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Select from 'react-select';
import 'react-select/dist/react-select.css';

export class Category extends Component {
  constructor(props) {
    super(props);
    this.state = {
      field: '',
      text: 'No', // Yes if category is selected
      isOpen: false,
      edit: false
    };
  }

  componentDidMount = () => {
    this.getOptions();
  }
  getOptions = (input) => {
    api.retrieve('/menucategory/api/list/')
    .then((response) => {
      return response.data.results;
    })
    .then((data) => {
      var arr = [];
      data.map((value, index) => {
        arr.push({value: value.id, label: value.name});
      });
      this.setState({
        selectOptions: arr
      });
    })
    .catch((error) => {
      console.error(error);
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
  handleSelectChange = (field) => {
    var text = field ? 'Yes' : 'No';
    this.setState({ field, text });
    var payload = { ...this.props.instance };
    payload.category = field;
    this.props.updateCartItem(payload);
  }
  handleSubmit = () => {
    // validate
    if (this.state.field === '') {
      toast.error('Menu name is required');
      return;
    }
    this.setState({isOpen: false});
  }

  toggleEdit = () => {
    this.setState({isOpen: !this.state.isOpen});
  }

  render() {
    const { field } = this.state;
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
                  <Select
                    name="field"
                    placeholder="Select menu category"
                    value={field}
                    onChange={this.handleSelectChange}
                    options={this.state.selectOptions}
                    />
                  </div>
                  <div className="editable-buttons">
                    <button data-tip="Close form" onClick={this.toggleEdit} type="button" className="btn btn-default btn-icon editable-cancel">
                      <i className="icon-x"></i>
                    </button>
                  </div>
                  <div className="editable-error-block help-block hidden"></div>
                </div>
              </div>
            </div>
          )}
            className="target" tagName="span" eventToggle="onClick">
            <span data-tip="Select menu category" className="edit-qty text-primary cursor-pointer">
              {this.state.text}
            </span>
        </Tooltip>
        </div>
      </div>
    );
  }
}

Category.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Category);
