import React, { Component } from 'react';
import TransferModal from '../containers/TransferModal';

class App extends Component {
  render() {
    return (
        <div className="row">
            <div className="col-md-6">
                <TransferModal buttonLabel='hello' className='modal-xs'/>
            </div>
            <div className="col-md-6">

            </div>
        </div>
    );
  }
}

export default App;
