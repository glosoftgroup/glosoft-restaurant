import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Pagination from 'react-js-pagination';
import Select2 from 'react-select2-wrapper';
import { fetchItems } from '../actions/action-sales';
import SalesList from './SalesList';

class SaleSearch extends Component {
  constructor(props) {
    super(props);
    this.state = {
      search: '',
      page: 5,
      activePage: 1,
      totalPages: 450,
      itemsCountPerPage: 10,
      show: false,
      edit: false,
      deleteUrl: 'url',
      item: {},
      category: '',
      pageSizes: [
        {'text': '5', 'id': '5'},
        {'text': '10', 'id': '10'},
        {'text': '20', 'id': '20'}
      ]
    };
  }
  componentWillMount() {
    // fetch items
    this.props.fetchItems();
  }
  handleChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
    this.filterContent(e.target.value);
  }

  handleSelectChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
    console.log(e.target.value);
    this.filterContent(this.state.search, null, e.target.value);
  }

  handlePageChange = (pageNumber) => {
        // console.log(`active page is ${pageNumber}`);
    this.setState({activePage: pageNumber});
    var search = this.state.search;
    this.filterContent(search, pageNumber);
  }

  onSelectChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
    this.filterContent();
  }

  filterContent= (search, page, category) => {
    if (!page) {
      page = this.state.activePage;
    }
    var params = Object.assign({
      page_size: this.state.itemsCountPerPage,
      page: page
    });
    if (this.state.search) {
      params = Object.assign(params, {'q': search});
    }
    if (category) {
      params = { ...params, 'category': category };
    }
    this.props.fetchItems(params);
  }
  render() {
    return (
      <div>
        <div className="breadcrumb-line breadcrumb-line-component content-group-lg">
          <ul className="breadcrumb">
              <li><a href="javascript:;">
                  <i className="icon-checkbox-partial position-left"></i> </a>
              </li>
          </ul>

          <ul className="breadcrumb-elements">
            <li>&nbsp;&nbsp;&nbsp;</li>
            <li>
              <a href="javascript:;" className="legitRipple text-bold"> Search:</a>
            </li>
            <li>
              <div className="form-grou search-form-group mr-15">
                  <div className="has-feedback has-feedback-right">
                      <input value={this.state.search} name="search" onChange={this.handleChange} className="form-control" placeholder="Invoice number" type="search" />
                      <div className="form-control-feedback">
                          <i className="icon-search4 text-size-large text-muted"></i>
                      </div>
                  </div>
              </div>
            </li>
          </ul>
          <a className="breadcrumb-elements-toggle"><i className="icon-menu-open"></i></a>
        </div>
        <div className="product-list-view panel panel-flat">
            <SalesList closeModal={this.props.closeModal} />
            <div className="row text-center mb-15">
                <div className="col-md-2 page-of mt-15">
                <Select2
                    data={this.state.pageSizes}
                    onChange={this.onSelectChange}
                    value={ this.state.itemsCountPerPage }
                    name="itemsCountPerPage"
                    options={{
                      minimumResultsForSearch: -1,
                      placeholder: 'Select Page size'
                    }}
                />
                </div>
                <div className="col-md-8 page-of mt-15">
                    <Pagination
                        activePage={this.state.activePage}
                        itemsCountPerPage={this.state.itemsCountPerPage}
                        totalItemsCount={this.props.items.count}
                        pageRangeDisplayed={5}
                        onChange={this.handlePageChange}
                    />
                </div>
                <div className="col-md-2 page-of mt-15">Page {this.state.activePage} of {this.props.items.total_pages}</div>
            </div>
        </div>
      </div>
    );
  }
}

SaleSearch.propTypes = {
  fetchItems: PropTypes.func,
  closeModal: PropTypes.func,
  items: PropTypes.array.isRequired
};

function mapStateToProps(state) {
  return {
    items: state.sales
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({
    fetchItems: fetchItems
  }, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(SaleSearch);
