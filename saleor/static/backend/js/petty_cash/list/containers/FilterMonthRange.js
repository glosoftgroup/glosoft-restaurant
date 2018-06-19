import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import { DateUtils } from "react-day-picker";
import DayPickerInput from 'react-day-picker/DayPickerInput';
import { formatDate, parseDate } from 'react-day-picker/moment';
import Datetime from 'react-datetime';
// import 'react-day-picker/lib/style.css';
import { setDate, setDateRange } from '../actions/action-date';
import { fetchItems } from '../actions/action-items';

class FilterMonthRange extends Component {
  /*
   * This component render datepicker input. Items filter based on selected date
   * Props: Listed in FilterDateRange.propTypes below
   *        All props are fetch from redux
   *  Usage: <FilterMonthRange />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: '',
      from:undefined,
      to:undefined,
      month:undefined
    };
  }

  componentWillUnmount() {
    clearTimeout(this.timeout);
  }

  dayMonthFormatter = (num) => {
    return (num < 10) ? '0' + num : num;
  }

  dateFormatter = (date) => {
    date = new Date(date);
    var day = date.getDate();
    var monthIndex = date.getMonth() + 1;
    var year = date.getFullYear();

    return year + '-' + this.dayMonthFormatter(monthIndex) + '-' + this.dayMonthFormatter(day);
  }

  fetchItems = () => {
    var from = this.dateFormatter(this.state.from);
    var to = this.dateFormatter(this.state.to);
    var payload = {};

    if (this.state.from != undefined && this.state.to!=undefined) {
        payload = { date_from: from, date_to:to, mode:this.props.mode };
        this.props.setDateRange(payload);
    }

    if (this.props.search) {
        var search = this.props.search.q;
        payload = { ...payload, q: search };
    }

    this.props.fetchItems(payload);

  }
  
  focusTo() {
    // Focus to `to` field. A timeout is required here because the overlays
    // already set timeouts to work well with input fields
    this.timeout = setTimeout(() => this.to.getInput().focus(), 0);
  }

  handleFromChange = (from) => {
    // Change the from date and focus the 
    this.setState({ from }, () => {
        this.fetchItems();
    });
  }

  handleToChange = (to) => {
    this.setState({ to }, () => {
        this.fetchItems();
    });
  }

  focousOut = (value) =>{
    if(!moment(value).isValid()) {
     this.setState({selectedValue: ''}); 
    }
  }
  
  handleChange = (date) => {
    var newDate = moment(date).format('YYYY-MM-DD');
    console.log("value is "+newDate);
   this.setState({ month: date });
  }

  render() {
    const { from, to, month } = this.state;
    const modifiers = { start: from, end: to };

    return (
        <div className="form-grou search-form-group mr-15">
          <div className="input-group">
              <Datetime
                  dateFormat="YYYY-MM"
                  timeFormat={false}
                  value={from}
                  onChange={this.handleFromChange}
                  onBlur={this.focousOut}
                  locale='en-US'
                  closeOnSelect
              />
              
              <span className="input-group-addon"> to</span>

              <Datetime
                  dateFormat="YYYY-MM"
                  timeFormat={false}
                  value={to}
                  onChange={this.handleToChange}
                  onBlur={this.focousOut}
                  locale='en-US'
                  closeOnSelect
              />
           </div>

        </div>
    );
  }
}

FilterMonthRange.propTypes = {
  setDate: PropTypes.func.isRequired,
  setDateRange: PropTypes.func.isRequired,
  search: PropTypes.array.isRequired,
  fetchItems: PropTypes.func.isRequired
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems,
    setDate: setDate,
    setDateRange: setDateRange
  }, dispatch);
}

function mapStateToProps(state) {
  return { search: state.search };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterMonthRange);
