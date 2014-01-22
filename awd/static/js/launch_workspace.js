$(function() {
    jQuery("#ws_launch_form").dialog({
	autoOpen: false,
	height: 300,
	width: 300,
	modal: true,
	cache: false,
	open: function() {
	    $("#id_hardware").change(function() {
		$.ajax({
		    url: '/console/',
		    type: 'post',
		    data: $("#ws_launch_form").serialize(),
		    success: function(data) {
			$("#ws_launch_form").load($(data).find("#ws_launch_form"));
			$("#id_os").replaceWith($(data).find("#id_os"));
		    }
		});
	    });
	},
    });
  jQuery("#ws_launch_butt").click(function() {
      jQuery("#ws_launch_form").dialog("open");
  });
  
  
  
    
});

