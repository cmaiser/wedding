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


function startTimer() {
    setInterval(function () {

        var htmlString = " days!"

        var weddingDate = new Date(2017, 7, 19, 15, 30, 0, 0);
        var curDate = new Date();
        var diffInMS = weddingDate.getTime() - curDate.getTime();
        var daysUntil = Math.floor(diffInMS/1000/60/60/24);
        if(daysUntil < 0) {
            daysUntil = 0;
        }

        htmlString = daysUntil + htmlString;

        $('#daysUntil').html(htmlString);

    }, 1000);
}

window.onload = function () {
    startTimer();
};