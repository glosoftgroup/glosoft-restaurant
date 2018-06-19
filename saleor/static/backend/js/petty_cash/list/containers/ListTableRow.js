import React, { Component } from 'react';
import PropTypes from 'prop-types';
import api from '../api/Api';

export class ListTableRow extends Component {
  /*
   * This component list stock transfers in rows
   * Props:
   *  instance: (Required) An object with stock transfer details
   *         Array of items to be rendered in transfered item table
   *  Usage: <ListTableRow
   *            instance={object}
   *          />
   * */
  constructor(props) {
    super(props);
    this.state = {
      controlId: 'control',
      collapse: 'collapse',
      showDelete: false
    };
  }
  goTo = (url) => {
    window.location.href = url;
  }
  toggleDelete = () => {
    this.setState({showDelete: true});
    // reset delete confimartion
    setTimeout(() => {
      this.setState({showDelete: false});
    }, 3000);
  }
  deleteInstance = () => {
    api.destroy('/counter/transfer/api/delete/' + this.props.instance.id + '/')
    .then((response) => {
      window.location.reload();
    })
    .catch((error) => {
      console.error(error);
    });
  }
  render() {
    var instance = { ...this.props.instance };
    return (
      <tr>
        <td>{instance.created}</td>
        <td>{instance.opening}</td>
        <td>{instance.added}</td>
        <td>{instance.expenses}</td>
        <td>{instance.closing}</td>
        <td className=" text-center no-print">
          <ul className="icons-list">
            <li className="dropdown">
              <button type="button" onClick={ () => this.goTo(instance.view_url)} 
               className="no-print animated fadeIn btn btn-md bg-slate-700 legitRipple">
              view
              </button>

            </li>
          </ul>
        </td>
    </tr>
    );
  }
}

ListTableRow.propTypes = {
  instance: PropTypes.object.isRequired
};
export default ListTableRow;
