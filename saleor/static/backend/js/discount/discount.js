/* ------------------------------------------------------------------------------
*
*  # Discount js scripts
*
*  Specific JS code additions for G-POS backend pages
*
*  Version: 1.0
*  Latest update: Sep 8, 2017
*
* ---------------------------------------------------------------------------- */
// alertUser
function alertUser(msg,status='bg-success',header='Well done!')
{ $.jGrowl(msg,{header: header,theme: status}); }
//add productDetails
function sendDiscountData(dynamicData,url,method){
  dynamicData["csrfmiddlewaretoken"]  = jQuery("[name=csrfmiddlewaretoken]").val();
  return $.ajax({
      url: url,
      type: method,
      data: dynamicData
    });
}

function refreshTable(){
	var rUrl = $('.pageUrls').data('refreshtable');
	$.ajax({ url:rUrl, type: 'GET',data: {page:1, q:''},success: function(data){
          $('#pagination-div').html(data);
   }});
}

$(function(){    
    // validate
    $('#sale-details').validate({
    rules:{
        name: {
          required:true,
          minlength:3
        },
        start_date: {
          required:true,         
        }, 
        end_date: {
          required:true,          
		},
		quantity:{
			required: true,
			digits: true
		}
    },
    messages:{
      name:{
        required: "Provide a name",
        minlength: "at least 3 characters long"
	  }, 
	  quantity:{
		required: "Provide a quantity",
		digits: "digits only"
	  }    
    },
    
  });
    // end validate
  
});

$(function() {
	var pageUrls = $('.pageUrls');
	var getVariants = $('#variants');
	var getCustomers = $('#customers');
	var url   = pageUrls.data('variants');
	var curl  = pageUrls.data('curl');
	var redirectUrl = pageUrls.data('redirect');
	var name  = $('#id_name');
	var value = $('#id_value');
	var type  = $('#id_type');
	var day = $('#id_day');
	var date = $('#id_date');
	var quantity = $('#id_quantity');
	var id_start_date = $('#id_start_date');
	var id_end_date = $('#id_end_date');
	var id_start_time = $('#id_start_time');
	var id_end_time = $('#id_end_time');
	var deleteBtn = $('.delete-discount');
	var deleteUrl = '#';
	var modalId = $('#modal_instance');
	var toggleDiv = $('#toggle-div');
	var modalContent = $('.results');
	var createDiscountBtn = $('#createDiscountBtn');

	// take care of variants
	getVariants.on('tokenize:select', function(container){
		$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
	   });	 
	getVariants.tokenize2({
	    placeholder: 'Select Product',
	    displayNoResultsMessage:true,	    
	    sortable: true,
	    dataSource: function(search, object){
	        $.ajax(url, {
	            data: { search: search, start: 1, group:'users' },
	            dataType: 'json',
	            success: function(data){
	                var $items = [];
	                $.each(data, function(k, v){
	                    $items.push(v);
	                });
	                object.trigger('tokenize:dropdown:fill', [$items]);
	            }
	        });
	    }
	});
	// take care customer
	getCustomers.on('tokenize:select', function(container){
		$(this).tokenize2().trigger('tokenize:search', [$(this).tokenize2().input.val()]);
	   });	 
	getCustomers.tokenize2({
	    placeholder: 'Select customer',
	    displayNoResultsMessage:true,	    
	    sortable: true,
	    dataSource: function(search, object){
	        $.ajax(curl, {
	            data: { search: search, start: 1, group:'customers',returnId:'true' },
	            dataType: 'json',
	            success: function(data){
	                var $items = [];
	                $.each(data, function(k, v){
	                    $items.push(v);
	                });
	                object.trigger('tokenize:dropdown:fill', [$items]);
	            }
	        });
	    }
	});
	// end tokenization

	// validate and create Discouont
	createDiscountBtn.on('click',function(){
	  var createUrl = $(this).data('createurl');
      var dynamicData = {};
      if(!name.val()){
      	alertUser('Discount name required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['name'] = name.val();
      }
      if(!value.val()){
      	alertUser('Discount Value field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['value'] = value.val();
      }
      if(!type.val()){
      	alertUser('Discount Type field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['type'] = type.val();
      }

      if(!getVariants.val()){
      	alertUser('Product(s) field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['variants'] = JSON.stringify(getVariants.val());
      }

      if(getCustomers.val()){
        dynamicData['customers'] = JSON.stringify(getCustomers.val());
      }
      if(!id_start_date.val() && !id_end_date.val() && !date.val() && (!day.val() || day.val() == "---")){
      	alertUser('Period (day or date or start & end date) field (s) required','bg-danger','Ooops!');
      	return false;
      }

      if(id_start_date.val()){
        dynamicData['start_date'] = id_start_date.val();
        dynamicData['day'] = null;
        dynamicData['date'] = null;
      } 
      if(id_end_date.val()){
        dynamicData['end_date'] = id_end_date.val();
        dynamicData['day'] = null;
        dynamicData['date'] = null;
	  }
      if(!id_start_time.val()){
      	alertUser('Start Time field required','bg-danger','Ooops!');
      	return false;
      }else{
        dynamicData['start_time'] = id_start_time.val();
      }

      if(!id_end_time.val()){
        alertUser('End Time field required','bg-danger','Ooops!');
        return false;
      }else{
        dynamicData['end_time'] = id_end_time.val();
      }

	  if(day.val() && day.val() != "---"){
        dynamicData['day'] = day.val();
        dynamicData['start_date'] = null;
        dynamicData['end_date'] = null;
	  } 
	  if(date.val()){
        dynamicData['date'] = date.val();
        dynamicData['start_date'] = null;
        dynamicData['end_date'] = null;
	  }

     if(!quantity.val()){
      	alertUser('Quantity field required','bg-danger','Ooops!');
      	return false;
     }else{
        dynamicData['quantity'] = quantity.val();
     }

	 sendDiscountData(dynamicData,createUrl,'post')
	 .done(function(response){
	    var response = JSON.parse(response);
	    if(response.status == '200'){
	 	    alertUser(response.message);
	 	}else{
	 	    alertUser(response.message,'bg-danger','Oops!');
	 	}
	 	if(response.type == "create"){
	 	    toggleDiv.slideUp('slow');
	 	    refreshTable();
	 	}else{
	 	    window.location.href = redirectUrl;
	 	}
	 })
	 .fail(function(errRsponse){
	    var response = JSON.parse(errRsponse);
	    alertUser(response.message,'bg-danger','Oops!');
	 });
	});

	// Basic select
    $('.bootstrap-select').selectpicker();
     // Default initialization
    

    $('.pickadate-selectors').pickadate({
        format: 'yyyy-mm-dd',
        editable: true,  
        selectYears: true,
        selectMonths: true,
        formatSubmit: 'yyyy-mm-dd',

    });

    deleteBtn.on('click',function(){
    	deleteUrl = $(this).data('href');    	
    	$('.modal-title').html($(this).data('title'));    	
    	modalId.modal();
    	dynamicData = {};
    	sendDiscountData(dynamicData,deleteUrl,'get')
		 .done(function(data){
		 	//alertUser('Delete content loaded');
		 	modalContent.html(data);
		 })
		 .fail(function(){
		 	//alertUser('Error loading form','bg-danger','Oops!');
		 });
    });
});