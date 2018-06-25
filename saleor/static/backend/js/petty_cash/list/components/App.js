import React, { Component } from 'react';
import PropTypes from 'prop-types';
import FilterBlock from '../containers/FilterBlock';
import ItemList from '../containers/ItemList';
import CompareItemList from '../containers/CompareItemList';
import PaginationBlock from '../containers/PaginateBlock';
import '../css/style.scss';

export default class App extends Component {
  static propTypes = {
    prop: PropTypes
  }

  render() {
    return (
      <div className="row">
      {/* remember to to uncomment for the comparison functionality */}
       { /* <div className="col-md-12">
          <div className="col-md-6">
            <div className="panel panel-body">
              <CompareItemList />
            </div>
          </div>
          <div className="col-md-6">
            <div className="panel panel-body">
              <CompareItemList />
            </div>
          </div>
          
        </div> */ }
        <div className="col-md-12">
          <FilterBlock />
          <div className="panel panel-body">
            <ItemList />
            <PaginationBlock />
          </div>
        </div>
      </div>
    );
  }
}
