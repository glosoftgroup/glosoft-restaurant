import React, { Component } from 'react';
import PropTypes from 'prop-types';
import FilterBlock from '../containers/FilterBlock';
import ItemList from '../containers/ItemList';
import PaginationBlock from '../containers/PaginateBlock';
import '../css/style.scss';
import '../css/tooltip.scss';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
        <div className="col-md-12">
          <FilterBlock />
          <div className="panel panel-bodys inner-z-indexs">
          <h1>testing ....</h1>
          <div className="panel-body test-body">
            <ItemList />
            <PaginationBlock />
            </div>
          </div>
        </div>
      </div>
    );
  }
}
