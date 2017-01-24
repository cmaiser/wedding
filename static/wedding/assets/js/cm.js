function saveHousehold(lat, lon) {
	$.ajax({
		type : "POST",
		url  : "/wedding/household/",
		datatype : "json",
		data : JSON.stringify({
		    name : "Maiser",
		    uuid : "BLAHBLAHBLAH",
		    addresses : [
		        {
		            firstName : "Chris",
		            lastName : "Maiser",
		            email : "blah@blah.org",
		            invited : true,
		            going : true,
		            invitedRehersal : true,
		            goingRehersal : true
		        },
		        {
		            firstName : "Dufus",
		            lastName : "Maiser",
		            email : "blah@blah.org",
		            invited : false,
		            going : false,
		            invitedRehersal : false,
		            goingRehersal : false
		        }
		    ]
		}),

		success : function(data) {

			// convert response string to object
			var responseJSON = jQuery.parseJSON(data);
		},
		error : function(xhr, textStatus, errorThrown) {

			var bob;

		}
	});
}