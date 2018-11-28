import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import FilterSearch from './FilterSearch';
import FilterDate from './FilterDate';
import InstanceForm from '../containers/InstanceForm';

class FilterBlock extends Component {
  /*
   * This component render search/datepicker components & transfer button.
   * Props: Listed in FilterBlock.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterBlock />
   * */
  constructor(props) {
    super(props);
    this.state = {
      open: false
    };
  }
  toggleInstanceForm = () => {
//    this.setState({open: !this.state.open});
    console.log("about to open");
  }
  render() {
    const state = { ...this.state };
    return (
      <div >
      <div className="breadcrumb-line breadcrumb-line-component content-group-lg">
        <ul className="breadcrumb">
            <li onClick={this.toggleInstanceForm}>
              <a className="text-white btn btn-primary btn-sm btn-raised legitRipple" href="javascript:;">
              {!state.open &&
              <span className="animated fadeIn">
              <i className="icon-add position-left"></i>
              Add Mpesa Transaction
              </span>
              }
              {state.open &&
              <i className="animated fadeIn icon-cross position-left"></i>
              }
              </a>
            </li>
        </ul>
        <ul className="breadcrumb-elements">
            <li><a href="javascript:;" className="text-bold"> Search:</a></li>
            <li>
              <FilterSearch />
            </li>
            <li><a href="javascript:;" className="text-bold"> Date:</a></li>
            <li>
              <FilterDate />
            </li>
        </ul>
      </div>
      {state.open &&
       <InstanceForm toggleForm={this.toggleInstanceForm}/>
      }
      </div>
    );
  }
}

FilterBlock.propTypes = {};

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({}, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(FilterBlock);
