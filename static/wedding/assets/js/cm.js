var currentHousehold = {};

function saveHousehold() {

    currentHousehold.sddSent = null;
    currentHousehold.inviteSent = null;

	$.ajax({
		type : "POST",
		url  : "/wedding/household/",
		datatype : "json",
		data : JSON.stringify(currentHousehold),

		success : function(data) {

		    currentHousehold = data;
		    $('#rsvpPersonContainer').empty();

		    html = ' <div id="saveSuccess" class="row">';
		    html += '<div class="col-md-12 text-center">';
		    html += '<p class="h2 secondary-font"><i class="fa fa-check" style="color:green"></i>&nbsp\;Your RSVP has been received.</p>';
		    html += '<p class="h2 secondary-font">You will receive an email confirmation shortly.</p>';
		    html += '</div>';
		    html += '</div>';

            $('#rsvpPersonContainer').append(html);

            $('#myModal').modal('hide');

            toggleMessageControl();

		},
		error : function(xhr, textStatus, errorThrown) {

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

function getUrlParameter(key) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === key) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}

function detectUser() {
    var uuid = getUrlParameter("household");
    if(typeof uuid != "undefined") {
        getHousehold(uuid);
    }
}

function getHousehold(uuid) {
    $.get( "/wedding/household/" + uuid, function(data) {
        currentHousehold = data;

        if(typeof data.persons != "undefined") {

            $('#knownRsvp').removeClass('hidden');
            $('#unknownRsvp').addClass('hidden');
            $('#welcomeHousehold').html('Welcome ' + data.name + '!');

            $.each(currentHousehold.persons, function (i, item) {
                if(item.going == null) {
                    item.going = false;
                }
            });

            renderRsvp(currentHousehold);
        }

        toggleMessageControl();
    });
}

function toggleMessageControl() {
    if(typeof currentHousehold.comments != "undefined" && currentHousehold.comments.length == 0) {
        $('#wellWishesControl').html('<a href="#" data-toggle="modal" data-target="#myModal"><i class="fa fa-pencil-square-o"  style="color:green" aria-hidden="true"></i>&nbsp;Add a Message</a>')
    }
    else if(typeof currentHousehold.comments != "undefined" && currentHousehold.comments.length > 0) {
        $('#wellWishesControl').html('<i class="fa fa-check" style="color:green"></i>&nbsp;Thank you for leaving us a message!')
    }
}

function toggleButton(number) {
    var button = $('#rsvp' + number);
    var diet = $('#diet' + number);
    var person = currentHousehold.persons[number];

    if(person.going) {
        person.going = false;
        button.removeClass('btn-success');
        button.addClass('btn-danger');
        diet.addClass('hidden');
        button.val("Not Going");
    }
    else {
        person.going = true;
        button.removeClass('btn-danger');
        button.addClass('btn-success');
        diet.removeClass('hidden');
        button.val("Going");
    }
}


function updateDiet(event, i) {
    currentHousehold.persons[i].diet = event.currentTarget.value;
}

function updateComment(event, i) {
    if(currentHousehold.comments.length == 0) {
        currentHousehold.comments[0] = {};
    }
    currentHousehold.comments[0].id = null;
    currentHousehold.comments[0].commentText = event.currentTarget.value;
    currentHousehold.comments[0].commentFrom = currentHousehold.name;
}

function renderRsvp(household) {

    //invite has been sent, so show rsvp content
    if(household.inviteSent != null) {
        var html = "";

        $.each(household.persons, function (i, item) {
            var firstCol = (i%2 == 0);
            if(firstCol) {
                html += '<div class="row">';
                html += '<div class="col-md-2"></div>';
            }
            html += '<div class="col-md-4 text-center">';
            html += '<h3 class="section-subheading secondary-font">' + item.firstName + ' ' + item.lastName + '</h3>';
            html += '<input id="rsvp' + i + '" type="button" value="Not Going"  class="btn btn-danger" onClick="toggleButton(' + i + ')">';
            html += '<input id="diet' + i + '" type="text" onkeyup="updateDiet(event, ' + i + ')" class="form-control col-md-6 hidden" placeholder="Dietary Restrictions" value="' + item.diet + '"/>';
            html += '</div>';
            if(!firstCol) {
                html += '<div class="col-md-2"></div>';
                html += '</div>';
            }
        });

        if(household.persons.length%2 == 1) {
            html += '<div class="col-md-4"></div>';
            html += '<div class="col-md-2"></div>';
            html += '</div>';
        }

        html += '<div class="row">';
        html += '<div class="col-md-3"></div>';
        html += '<div class="col-md-6">';
        html += '<input type="button" value="Send RSVP"  class="btn btn-primary mt30" onClick="saveHousehold()"/>';
        html += '</div>';
        html += '<div class="col-md-3"></div>';
        html += '</div>';

        $('#rsvpPersonContainer').append(html);

        //toggle button for each rendered rsvp
        $.each(household.persons, function (i, item) {
            if(item.going) {
                item.going = false;
                toggleButton(i);
            }
        });
    }
    //Save the date has been sent out
    else {

        html = '';
        if(household.emailVerified) {
            html += '<p class="h2 secondary-font"><i class="fa fa-check" style="color:green"></i>&nbsp\;Thank you for verifying your email.  Invitations will be sent out soon.</p>';
        }
        else {
            html += '<p class="h2 secondary-font"><i class="fa fa-check" style="color:green"></i>&nbsp\;Invitations will be sent out soon.</p>';
        }


        $('#rsvpPersonContainer').append(html);
    }
}


