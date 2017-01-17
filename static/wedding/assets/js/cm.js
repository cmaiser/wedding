function resolveLocation(lat, lon) {

	$.ajax({
		type : "POST",
		url : window.location.hostname + "/smtp/",
		success : function(data) {

			// convert response string to object
			var responseJSON = jQuery.parseJSON(data);

			var city = responseJSON["city"];
			var state = responseJSON["state"];
			;
			var country = responseJSON["country"];
			;

			// only global until I figure out jquery scope (c'mon, it's just
			// javascript!)
			locationString = city + ",&nbsp;" + state + ",&nbsp;" + country;

			$("#location").find("span").fadeOut(
					function() {
						$(this).html(
								"Your&nbsp;location:&nbsp;&nbsp;"
										+ locationString).fadeIn(1000,
								getExcuses(lat, lon, city, state));
					});
		},
		error : function(xhr, textStatus, errorThrown) {

			$("#location").find("span").fadeOut(
					function() {
						$(this).html(
								"Could&nbsp;not&nbsp;resolve&nbsp;location:&nbsp;"
										+ textStatus).fadeIn(1000);
					});

		}
	});
}