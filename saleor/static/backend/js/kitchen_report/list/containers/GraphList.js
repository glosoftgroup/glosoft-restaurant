import React, { Component } from 'react';
// import Rechart from '../components/HCharts';
import Rechart from '../components/Rechart';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

/**
 * Actions
 */
import { setChartOptions } from '../actions/action-charts';

/**
 * Utils
 */
// import Api from '../api/Api';

/**
 * Components
 */
// import LineChart from './LineChart';
import PieChart from './PieChart';

export class GraphList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: []
    };
  }
  render() {
    return (
      <div className="row">
        <div className="col-md-6">
          <Rechart data={this.props.charts}/>
        </div>
        <div className="col-md-6">
          <PieChart />
        </div>
      </div>
    );
  }
}
GraphList.propTypes = {
  setChartOptions: PropTypes.func.isRequired,
  charts: PropTypes.array.isRequired
};
const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    setChartOptions
  }, dispatch);
};
const mapStateToProps = (state) => ({
  charts: state.charts
});

export default connect(mapStateToProps, mapDispatchToProps)(GraphList);
