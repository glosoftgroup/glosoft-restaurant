import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Select2 from 'react-select2-wrapper';

/**
 * Containers
 */
// import FilterSearch from './FilterSearch';
import FilterDate from './FilterDate';
import FilterMonth from './FilterMonth';
import FilterDateRange from './FilterDateRange';
import FilterMonthRange from './FilterMonthRange';

/**
 * Utilities
 */
import PrintThis from '../../../common/components/PrintThis';
import CsvExport from '../../../common/components/CsvExport';

/**
 * Redux
 */
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

/**
 * Actions
 */
import { toggleGraph } from '../actions/action-toggle-graph';

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
      title: 'Petty Cash Report',
      label: 'Petty Cash',
      exportData: [],
      printCssPaths: [],
      defaultFilterChoice: 1,
      filterChoices: [
        {'text': 'Date', 'id': '1'},
        {'text': 'Month', 'id': '2'},
        {'text': 'Year', 'id': '3'}
      ],
      defaultFilter: 1,
      filters: [
        {'text': 'Filter', 'id': '1'},
        {'text': 'Range Filter', 'id': '3'}
      ],
      rangeStatus: false,
      compareStatus: false,
      checked: false
    };
  }
  componentWillMount() {
    var baseURL = document.location.protocol + '//' + document.location.host;
    var printCssPaths = [];
    printCssPaths.push(baseURL + '/static/backend/css/bootstrap.css');
    printCssPaths.push(baseURL + '/static/backend/css/core.css');
    printCssPaths.push(baseURL + '/static/backend/css/print.css');
    this.setState({printCssPaths});
  }
  toggleCheckBox = () => {
    var checked = (this.state.checked === '') ? 'checked' : '';
    this.setState({checked});
    let open = !this.props.openGraph.open;
    this.props.toggleGraph({open});
  }
  getData = () => {
    var items = [];
    var temp = this.props.items.results.slice();
    temp.map((obj, index) => {
      // delete unneccessary fields
      delete obj['view_url'];
      obj['created'] = obj.created;
      obj['opening'] = obj.opening;
      obj['added'] = obj.added;
      obj['expenses'] = obj.expenses;
      obj['closing'] = obj.closing;
      items.push(obj);
    });
    return items;
  }
  onSelectChange = (e) => {
    var name = e.target.name, value = e.target.value,
        newRangeStatus, newCompareStatus;

    newRangeStatus = value == 1 ? false : true;
    newCompareStatus = value == 1 ? false : true;

    this.setState({
      [name]: value,
      rangeStatus: newRangeStatus,
      compareStatus: newCompareStatus
    });
  }
  
  onSelectPeriod = (e) => {
    var name = e.target.name, value = e.target.value,
        newRangeStatus, newCompareStatus;

    newRangeStatus = (this.state.defaultFilter == 1) ? false : true;

    this.setState({
      [name]: value,
      rangeStatus: newRangeStatus,
    });
  }

  renderDateComponent(){
    var button;
    var periodChoice = this.state.defaultFilterChoice;
        
    button = this.state.rangeStatus ?
            (
              periodChoice == 2 || periodChoice == 3 ? 
              <FilterMonthRange mode={ periodChoice == 2 ? "month" : "year"} /> : 
              <FilterDateRange />
            ) :
            (periodChoice == 2 || periodChoice == 3 ? 
              <FilterMonth mode={ periodChoice == 2 ? "month" : "year"} /> : 
              <FilterDate />        
            );

    return button;
  }

  render() {
    return (
        <div>
            <div className="panel no-print">
                <div className="panel-body">
                    <div className="col-md-1">
                    <label>Action</label>
                    <div className="form-group">
                        <Select2
                          data={this.state.filters}
                          onChange={this.onSelectChange}
                          value={ this.state.defaultFilter }
                          name="defaultFilter"
                          options={{
                            minimumResultsForSearch: -1,
                            placeholder: 'Select Action'
                          }}
                        />
                        </div>
                    </div>
                    <div className="col-md-1">
                        <label>Period</label>
                        <div className="form-group">
                          <Select2
                              data={this.state.filterChoices}
                              onChange={this.onSelectPeriod}
                              value={ this.state.defaultFilterChoice }
                              name="defaultFilterChoice"
                              options={{
                                minimumResultsForSearch: -1,
                                placeholder: 'Select Filter'
                              }}
                          />
                        </div>
                    </div>
                    <div className="col-md-4">
                        <label>Filter</label>
                        <div className="form-group">
                        {this.renderDateComponent()}
                        </div>
                    </div>
                    <div className="col-md-2">
                      <label className="visibility-hidden">&nbsp;</label>
                      <div className="form-group">
                        <PrintThis printCssPaths={this.state.printCssPaths} title={this.state.title} />
                      </div>
                    </div>
                    <div className="col-md-2">
                    <label className="visibility-hidden">&nbsp;</label>
                      <div className="form-group">
                        <CsvExport getData={this.getData} title={this.state.title} label={this.state.label} />
                      </div>
                    </div>
                    <div className="col-md-1">
                      <label> Graph</label>
                      <div className="form-control">
                        <div onClick={this.toggleCheckBox} className="checker">
                          <span className={this.state.checked}>
                            <input className="styleds" type="checkbox" />
                          </span>
                        </div>
                      </div>
                    </div>
                </div>
            </div>

      </div>
    );
  }
}
FilterBlock.propTypes = {
  items: PropTypes.array.isRequired,
  openGraph: PropTypes.object.isRequired,
  toggleGraph: PropTypes.func.isRequired
};
function mapDispatchToProps(dispatch) {
  return bindActionCreators({ toggleGraph }, dispatch);
}

function mapStateToProps(state) {
  return { items: state.items, openGraph: state.openGraph };
}
export default connect(mapStateToProps, mapDispatchToProps)(FilterBlock);
