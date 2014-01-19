$(function() {
    jQuery("#testb").dialog({
	autoOpen: false,
	height: 300,
	width: 350,
	modal: true,
	cache: false,
	open: function() {
	    $("#id_hardware").change(function() {
		$.ajax({
		    url: '/console/',
		    type: 'post',
		    data: $("#testb").serialize(),
		    success: function(data) {
			$("#testb").load($(data).find("#testb"));
			$("#id_os").replaceWith($(data).find("#id_os"));
		    }
		});
	    });
	},
    });
  jQuery("#butt").click(function() {
      jQuery("#testb").dialog("open");
  });
  
  
  
    
});

