import React, { Component } from 'react';

class InstanceForm extends Component {
  render() {
    return (
      <div className="col-md12">
        <div className="panel panel-body">
          <table className="table table-hover">
            <thead>
              <tr className="bg-primary">
                <th>Category</th>
                <th>Name</th>
                <th>Price</th>
                <th>Quantity</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Category</td>
                <td>Name</td>
                <td>Price</td>
                <td>Quantity</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

export default InstanceForm;
