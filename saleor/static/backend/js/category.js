$(function() {
  //add  product category 
  $('#add-new-category').on('click',function(){
  	var url = $(this).data('href');
  	var csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();
  	var title_text = $(this).data('title');
  	$('.modal-title').html(title_text);
  	var modal = $(this).attr('href');
  	$(modal).modal();
  	//get form
  	
  });


  function notify(msg,color='bg-danger') {
          new PNotify({
              text: msg,
              addclass: color
          });
      }
   
  $('#modal_add_category_btn32').on('click',function(){
        var cat_description = $('#categoryDescription').val();
        var cat_name = $('#categoryName').val();
        var sale_point = $('#id_sale_point').val();
        var csrf_toid_sale_pointid_sale_pointken = jQuery("[name=csrfmiddlewaretoken]").val();
        
        var url = $("#newcaturl").val();        
        if(!cat_name){
          notify('Add a valid category');
          return false;
        }
        if(sale_point == 0){
          notify('Sale point required');
          return false;
        }

        // after validating category cat_name        
        var modal = $("#add-new-category").attr('href');
        var posting = $.post( url, {
                              name:cat_name,
                              section:sale_point,
                              description:cat_description,
                              csrfmiddlewaretoken:csrf_token,
                            });
        posting.done(function( data ) {
//        $( "#category_field" ).empty().append( data );
          $( "#category_field" ).replaceWith( data );
          $(modal).modal('hide');
          $('#categoryName').val('');
          $('#categoryDescription').val('');
          notify('New category added successfully','bg-success');
        });
        posting.fail(function() {          
          notify('Category Exists!. Choose a unique name','bg-danger');
        });
  });
  
});