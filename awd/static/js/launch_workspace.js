$(function() {
    jQuery(".ws_launch").dialog({
	autoOpen: false,
	height: 300,
	width: 300,
	modal: true,
	cache: false,
	open: function() {
	    var my_id = "#"+$(this).data("id")
	    $(my_id+" #id_hardware").change(function() {
		$.ajax({
		    url: '/console/',
		    type: 'post',
		    data: $(my_id).serialize(),
		    success: function(data) {
			$(my_id).load($(data).find(my_id));
			$(my_id+" #id_os").replaceWith($(data).find(my_id+" #id_os"));
		    }
		});
	    });
	},
    });
    
    jQuery(".addbkg").click(function() {
	jQuery("#"+$(this).data("id")).dialog("open");
    });
    
});

