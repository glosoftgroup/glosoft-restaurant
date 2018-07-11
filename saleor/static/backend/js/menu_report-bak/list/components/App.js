import React, { Component } from 'react';
import PropTypes from 'prop-types';
import FilterBlock from '../containers/FilterBlock';
import ItemList from '../containers/ItemList';
import GraphList from '../containers/GraphList';
import PaginationBlock from '../containers/PaginateBlock';
import '../css/style.scss';
import '../css/tooltip.scss';
import '../../../common/css/print.scss';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <FilterBlock />
          <div className="panel panel-body">
            <ItemList />
            <PaginationBlock />
          </div>
          <div className="panel panel-body">
            <GraphList />
          </div>
        </div>
      </div>
    );
  }
}
