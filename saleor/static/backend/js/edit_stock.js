/* ------------------------------------------------------------------------------
*
*  # edit variant scripts
*
*  Specific JS code additions for ps254 backend pages
*
*  Version: 1.0
*  Latest update: Sept 15, 2017
*
* ---------------------------------------------------------------------------- */

$(function(){
  var editStockRefreshDiv = $('#div-edit-stock');
  var editStockForm = $('#edit-product-stock');
  var editStockBtn = $('#editStockBtn');
  var cancelStockBtn = $('#cancelStockBtn');
  var url = '#';
  var invoice_number = $("#id_invoice_number");
  var variant = $('#id_variant');
  var cost_price = $('#id_cost_price');
  var wholesale_override = editStockForm.find('#id_wholesale_override');
  var minimum_price = editStockForm.find('#id_minimum_price');
  var price_override = editStockForm.find('#id_price_override');
  var location = $('#id_location');
  var quantity = $('#id_quantity');
  var low_stock_threshold = $('#reorder-threshold');  

  cancelStockBtn.on('click', function(){
    $('html, body').find('#div-edit-stock').html('');
  });

  editStockBtn.on('click',function(e){
    var url = $(this).data('contenturl');
    var refreshUrl = $(this).data('refreshstockurl')+"?tab=stock";
    
    dynamicData = {};
    dynamicData['location'] = location.val();
    if(cost_price.val()){
      dynamicData['cost_price'] = cost_price.val();
    }
    if(!variant.val()){
      alertUser('Variant field required','bg-warning','Variant required!');
      return false;
    }else{
      dynamicData['variant'] = variant.val();
    }
    if(!quantity.val()){
      alertUser('quantity field required','bg-warning','Quantity required!');
      return false;
    }else{
      dynamicData['quantity'] = quantity.val();
    }       
    if(low_stock_threshold.val()){
      dynamicData['low_stock_threshold'] = low_stock_threshold.val();
    }   
    if(!wholesale_override.val()){
//      alertUser('Invoice number field required','bg-warning','Invoice Number!');
//      return false;
    }else{
      dynamicData['wholesale_override'] = wholesale_override.val();
    }

    if(!minimum_price.val()){
//      alertUser('Invoice number field required','bg-warning','Invoice Number!');
//      return false;
    }else{
      dynamicData['minimum_price'] = minimum_price.val();
    }

    if(!price_override.val()){
//      alertUser('Invoice number field required','bg-warning','Invoice Number!');
//      return false;
    }else{
      dynamicData['price_override'] = price_override.val();
    }


    dynamicData['status'] = 'fully-paid';
    dynamicData['template'] = 'edit_stock';

    addProductDetails(dynamicData, url, 'post')
    .done(function(data){
      alertUser('Product Stock updated successfully');
      $('#div-edit-variant').slideUp();      
      window.location.href = refreshUrl;
    })
    .fail(function(data){
      alertUser('update failed','bg-danger','Ooops!');
    });    
  
  });

});

