import React from 'react';
import { Modal, Button } from 'react-bootstrap';

import SaleSearch from './SaleSearch';

import '../css/styles.scss';

class TransferModal extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.handleShow = this.handleShow.bind(this);
    this.handleClose = this.handleClose.bind(this);

    this.state = {
      show: true
    };
  }

  handleClose() {
    this.setState({ show: false });
  }

  handleShow() {
    this.setState({ show: true });
  }

  render() {
    return (
      <div>
        <Button bsStyle="primary" bsSize="large" onClick={this.handleShow}>
          Select Sale
        </Button>

        <Modal bsSize="large" show={this.state.show} onHide={this.handleClose}>
          <Modal.Header closeButton className="bg-slate-800">
            <Modal.Title className="text-center">Select Sale</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="col-md-12">
              <SaleSearch closeModal={this.handleClose} />
            </div>
          </Modal.Body>
          <Modal.Footer >
            <Button className="mt-15" onClick={this.handleClose}>Close</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

export default TransferModal;
