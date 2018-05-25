import React, { Component } from 'react';

export default class PrintThis extends Component {
  printCanvas = () => {
    var dataUrl = document.getElementById('anycanvas').toDataURL();  // attempt to save base64 string to server using this var
    var windowContent = '<!DOCTYPE html>';
    windowContent += '<html>';
    windowContent += '<head><title>Print canvas</title></head>';
    windowContent += '<body>';
    windowContent += '<img src="' + dataUrl + '">';
    windowContent += '</body>';
    windowContent += '</html>';
    var printWin = window.open('', '', 'width=340,height=260');
    printWin.document.open();
    printWin.document.write(windowContent);
    printWin.document.close();
    printWin.focus();
    printWin.print();
    printWin.close();
  }
  render() {
    return (
      <div>
        TODO: print using javascript
      </div>
    );
  }
}
