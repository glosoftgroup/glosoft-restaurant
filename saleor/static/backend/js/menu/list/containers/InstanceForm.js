import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import api from '../api/Api';
import { fetchItems } from '../actions/action-items';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { css } from 'glamor';

class InstanceForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedOption: '',
      selectOptions: [],
      quantity: 0,
      name: '',
      price: '',
      errors: {}
    };
  }
  componentWillMount() {
    this.getOptions();
  }
  handleChange = (e) => {
    var value = e.target.value;
    let errors = { ...this.state.errors };
    delete errors[e.target.name];
    this.setState({
      [e.target.name]: value,
      errors: errors
    });
  }
  validateData = (e) => {
    let errors = {};
    var state = { ...this.state };

    if (state.selectedOption === '') errors.selectedOption = 'This field is required';
    if (state.name === '') errors.name = 'This field is required';
    if (!state.price) errors.price = 'This field is required and should be numeric';
    // if (!state.quantity) errors.quantity = 'This field is required and should be numeric';

    this.setState({errors: errors});

    const isValid = Object.keys(errors).length === 0;
    if (isValid) {
      return true;
    } else {
      return false;
    }
  }
  handleSubmit = (e) => {
    var formData = new FormData();
    // validate
    if (this.validateData()) {
      // valid create menu
      formData.append('category', this.state.selectedOption.value);
      formData.append('price', this.state.price);
      formData.append('quantity', this.state.quantity);
      formData.append('name', this.state.name);

      api.create('/menu/api/create/', formData)
      .then((response) => {
        console.log(response);
        this.props.fetchItems();
        this.props.toggleForm();
        toast.success('Menu created succefully');
      })
      .catch((error) => {
        let errors = {name: 'Menu name exist. Try another name.'};
        this.setState({errors: errors});
        toast.error('Menu name exist. Try another name.', {
          position: toast.POSITION.TOP_CENTER
        });
        console.error(error);
      });
    } else {
      // invalid alert fields required
      console.warn('invalid');
    }
  }
  handleSelectChange = (selectedOption) => {
    let errors = { ...this.state.errors };
    delete errors['selectedOption'];
    this.setState({ selectedOption, errors });
    console.log(`Selected: ${selectedOption.label}`);
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
  render() {
    const { selectedOption } = this.state;
    const { errors } = this.state;
    return (
      <div className="animated fadeIn">
        <ToastContainer progressClassName={ css({
          marginTop: '100px'
        })} />
        <div className="panel panel-body">
          <table className="table table-hover">
            <thead>
              <tr className="bg-primary">
                <th>Category</th>
                <th>Name</th>
                <th>Price</th>
                <th>Quantity</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div className="form-group">
                    <Select
                    name="selectedOption"
                    placeholder="Select menu category"
                    value={selectedOption}
                    onChange={this.handleSelectChange}
                    options={this.state.selectOptions}
                    />
                    <span className="help-block text-warning">{errors.selectedOption}</span>
                  </div>
                </td>
                <td>
                  <div className="form-group">
                    <input className="form-control"
                    name="name" placeholder="e.g Chicken soup"
                    onChange={this.handleChange} type="text" />
                    <span className="help-block text-warning">{errors.name}</span>
                  </div>
                </td>
                <td>
                  <div className="form-group">
                    <input className="form-control"
                    name="price" placeholder="price"
                    onChange={this.handleChange} type="number" />
                    <span className="help-block text-warning">{errors.price}</span>
                  </div>
                </td>
                <td>
                  <div className="form-group">
                    <input className="form-control"
                    name="quantity" placeholder="Quantity"
                    onChange={this.handleChange} type="number" />
                    <span className="help-block text-warning">{errors.quantity}</span>
                  </div>
                </td>
                <td>
                  <div className="form-group">
                    <button onClick={this.handleSubmit} className="btn bg-primary">Submit</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

InstanceForm.propTypes = {
  fetchItems: PropTypes.func.isRequired,
  toggleForm: PropTypes.func.isRequired
};

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    fetchItems: fetchItems
  }, dispatch);
};
export default connect(mapStateToProps, mapDispatchToProps)(InstanceForm);
