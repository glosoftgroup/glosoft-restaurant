import React, { Component } from 'react';
import PropTypes from 'prop-types';
import api from '../api/Api';

export default class TransferList extends Component {
  /*
   * This component list stock transfered items
   * Props:
   *  items: (Required) An array of option objects
   *         Array of items to be rendered in transfered item table
   *  parent: (Required) A positive integer
   *         Transfer Public Key. Used when deleting all transfers
   * Usage: <TransferList
   *            items={array}
   *            parent={1}
   *          />
   * */
  constructor(props) {
    super(props);
    this.state = {
      showDelete: true,
      showConfirmDelete: false
    };
  }
  componentWillReceiveProps() {
    console.log('sdfsdfsf');
  }
  showConfirm = () => {
    this.setState({showConfirmDelete: true, showDelete: false});
  }
  deleteInstance = () => {
    api.destroy('/counter/transfer/api/delete/' + this.props.parent + '/')
    .then((response) => {
      console.log(response);
      window.location.reload();
    })
    .catch((error) => {
      console.error(error);
    });
  }
  render() {
    return (
      <div className="table-responsive">
        <table className="table table-hover table-xs">
            <thead>
                <tr>
                    <td colSpan={4} className="text-center active">
                        { this.state.showDelete &&
                          <span onClick={this.showConfirm} className="label label-warning cursor-pointer">Delete All</span>
                        }
                        { this.state.showConfirmDelete &&
                          <span onClick={this.deleteInstance} className="label label-danger cursor-pointer">Confirm Delete All</span>
                        }
                    </td>
                </tr>
                <tr className="bg-primary">
                    <th>Product</th>
                    <th>SKU</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
            {this.props.items.map(obj => {
              return (
                <tr key={obj.id}>
                    <td>{obj.productName}</td>
                    <td>{obj.sku}</td>
                    <td>{obj.qty}</td>
                    <td>{obj.price}</td>
                </tr>
              );
            })
            }
            </tbody>
        </table>
      </div>
    );
  }
}

TransferList.propTypes = {
  items: PropTypes.array.isRequired,
  parent: PropTypes.number.isRequired
};
