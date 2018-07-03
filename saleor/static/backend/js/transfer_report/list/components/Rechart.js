import React, { Component } from 'react';
import PropTypes from 'prop-types';

import {
    ComposedChart, Area, Line, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';

export class Rechart extends Component {
  render() {
    return (
      <div>
        <ComposedChart width={600} height={400} data={this.props.data}
          margin={{top: 20, right: 80, bottom: 20, left: 20}}>
        <XAxis dataKey="name" label={{ value: 'Dates', position: 'insideBottomRight', offset: 0 }}/>
        <YAxis label={{ value: 'Quantity', angle: -90, position: 'insideLeft' }}/>
        <Tooltip/>
        <Legend/>
        <CartesianGrid stroke='#f5f5f5'/>
        <Area type='monotone' dataKey='sold' fill='#8884d8' stroke='#8884d8'/>
        <Bar dataKey='transferred' barSize={20} fill='#413ea0'/>
        <Line type='monotone' dataKey='deficit' stroke='#ff7300'/>
      </ComposedChart>
      </div>
    );
  }
}

Rechart.propTypes = {
  data: PropTypes.array.isRequired
};

export default Rechart;
