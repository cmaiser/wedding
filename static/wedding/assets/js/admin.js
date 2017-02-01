var ajaxData = {};
var currentHousehold = {};

$(document).ready(function(){

    $.get( "/wedding/household/", function( data ) {

        ajaxData = data;

        $.each(data.results, function (i, item) {
            renderHousehold(i, item);
        });
    });

    $('#myModal').on('show.bs.modal', function(e) {

        var $modal = $(this);

        $("#modaltitle").html(currentHousehold.name + " Household");
        $("#modalcontainer").empty();
        renderPersonHeader();
        $.each(currentHousehold.addresses, function (i, item) {
            renderPerson(i, item);
        });
    });
});

saveHousehold = function(i) {

    var household = currentHousehold;
    if(i != null) {
        household = ajaxData.results[i];
    }
    else {
        i = currentHousehold.i;
    }

    $.ajax({
		type : "POST",
		url  : "/wedding/household/",
		datatype : "json",
		data : JSON.stringify(household),

		success : function(data) {

		    processSavedHousehold(i, data);

			var $messageDiv = $('#message');
            $messageDiv.show().html('<strong>Save Success:</strong> ' + data.name + ' saved successfully.'); // show and set the message
            setTimeout(function(){ $messageDiv.hide().html('');}, 3000);
		},
		error : function(xhr, textStatus, errorThrown) {
            var $messageDiv = $('#message');
            $messageDiv.show().html('<strong>Save Failed:</strong> ' + errorThrown); // show and set the message
			var bob;
	    }
    });

};

sendSaveTheDateInvite = function(i) {

    uuid = ajaxData.results[i].uuid;

    $.get( "/wedding/sendSaveTheDate/" + uuid, function(data) {
        processSavedHousehold(i, data);
    });
};

sendWeddingInvite = function(uuid) {

};

setCurrentHousehold = function(i) {
    if(ajaxData.results != null) {
        currentHousehold = ajaxData.results[i];
        currentHousehold.i = i;
    }
    else {
        currentHousehold = {};
    }
};

processSavedHousehold = function(i, data) {

    currentHousehold = data;
    ajaxData.results[i] = data;

    $("#maincontainer").empty();
    renderHouseholdHeader();

    $.each(ajaxData.results, function (i, item) {
        renderHousehold(i, item);
    });

	$('#myModal').modal('hide');
};

addHousehold = function() {
    var blankHousehold = {
        id: null,
        name: "",
        uuid: null,
        email: "",
        emailVerified: false,
        inviteSent: null,
        sddSent: null,
        addresses: [],
        messages: []
    };
    ajaxData.results.push(blankHousehold);
    renderHousehold(ajaxData.results.length-1, blankHousehold)
};

addPerson = function() {
    var blankPerson = {
        id: null,
        firstName: "",
        lastName: "",
        going: null,
        diet : ""
    };
    currentHousehold.addresses.push(blankPerson);
    renderPerson(currentHousehold.addresses.length-1, blankPerson);
};

updateHouseholdName = function(e, i) {
    ajaxData.results[i].name = e.currentTarget.value;
};

updateEmail = function(e, i) {
    ajaxData.results[i].email = e.currentTarget.value;
};

updateFirstName = function(e, i) {
    currentHousehold.addresses[i].firstName = e.currentTarget.value;
};

updateLastName = function(e, i) {
    currentHousehold.addresses[i].lastName = e.currentTarget.value;
};

renderHouseholdHeader = function() {
    var html = '<div class="row">';
    html += '<div class="col-md-2"><strong>Name</strong></div>';
    html += '<div class="col-md-1"><strong>UUID</strong></div>';
    html += '<div class="col-md-2"><strong>Email</strong></div>';
    html += '<div class="col-md-1"><strong>Verified</strong></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-1"><strong>Date</strong></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-1"><strong>Date</strong></div>';

    html += '<div id="message" class="alert alert-success"  style="display: none; top: 0px; left: 0px">';
    html += '</div>';
    html += '<div id="message" class="alert alert-danger"  style="display: none; top: 0px; left: 0px">';
    html += '</div>';
    html += '</div>';
    $('#maincontainer').append(html);
};

renderPersonHeader = function() {
    var html = '<div class="row">';
    html += '<div class="col-md-2"><strong>First</strong></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-2"><strong>Last</strong></div>';
    html += '<div class="col-md-1"></div>';
    html += '<div class="col-md-1"><strong>Going</strong></div>';
    html += '<div class="col-md-5"><strong>Diet</strong></div>';
    html += '</div>';

    $('#modalcontainer').append(html);
}

renderHousehold = function(i, item) {
    var html = '<div class="row"';
    if(i%2 == 0) {
        html +=  'style="background: #f1f1f1;padding-top:5px;">';
    }
    else {
        html +=  'style="padding-top:5px;">';
    }

    html += '<div class="col-md-2">';
    html += '<input type="text" value = "' + item.name + '" onkeyup="updateHouseholdName(event, ' + i + ')">';
    html += '</div>';

    html += '<div class="col-md-1">';
    html += '<a href="http://nnagflar.pythonanywhere.com/wedding/?household=' + item.uuid + '" target="_blank">View</a>';
    html += '</div>';

    html += '<div class="col-md-2">';
    html += '<input type="text" value = "' + item.email + '" onkeyup="updateEmail(event, ' + i + ')">';
    html += '</div>';

    html += '<div class="col-md-1">';
    html += (item.emailVerified ? '<i class="fa fa-check fa-2x" style="color:green"></i>' : '');
    html += '</div>';

    html += '<div class="col-md-1">';
    html += '<input type="button" value="Persons" data-toggle="modal" data-target="#myModal" '
    html += 'class="btn btn-primary" onClick="setCurrentHousehold(' + i + ')">';
    html += '</div>';

    html += '<div class="col-md-1">';
    html += '<input type="button" value="Save" class="btn btn-success" onClick="saveHousehold(' + i + ')">';
    html += '</div>';

    //send save the date button
    html += '<div class="col-md-1">';
    html += '<input type="button" value="StD" class="btn btn-danger" onClick="sendSaveTheDateInvite(' + i + ')">';
    html += '</div>';

    //save the date sent date
    html += '<div class="col-md-1">' + formatDate(item.sddSent);
    html += '</div>';

    //wedding invite button
    html += '<div class="col-md-1">';
    html += '<input type="button" value="wedding" class="btn btn-danger" onClick="sendWeddingInvite(' + i + ')" disabled>';
    html += '</div>';

    //wedding invite sent date
    html += '<div class="col-md-1">' + formatDate(item.inviteSent);
    html += '</div>';

    html += '</div>';
    $('#maincontainer').append(html);
};

renderPerson = function(i, item) {
    var html = '<div class="row"';

    if(i%2 == 0) {
        html +=  ' style="background: #f1f1f1; padding-top:10px; padding-bottom:10px;">';
    }
    else {
        html +=  ' style="padding-top:10px; padding-bottom:10px;">';
    }

    html += '<div class="col-md-2">';
    html += '<input type="text" value="' + item.firstName + '" onkeyup="updateFirstName(event, ' + i + ')">';
    html += '</div>';

    html += '<div class="col-md-1">';
    html += '</div>';

    html += '<div class="col-md-2">';
    html += '<input type="text" value="' + item.lastName + '" onkeyup="updateLastName(event, ' + i + ')">';
    html += '</div>';

    html += '<div class="col-md-1">';
    html += '</div>';

    html += '<div class="col-md-1">';

    if(item.going != null) {
        html += (item.going ? '<i class="fa fa-check fa-2x" style="color:green"></i>' : '<i class="fa fa-times fa-2x" style="color:red">');
    }


    html += '</div>';

    html += '<div class="col-md-5">';
    html += item.diet;
    html += '</div>';


    html += '</div>';
    $('#modalcontainer').append(html);
}

formatDate = function(seconds) {

    if(typeof seconds == "undefined"  || seconds == null) {
        return "";
    }

    var date = new Date(seconds*1000);

    var day = date.getDate();
    var month = date.getMonth()+1;
    var year = date.getFullYear();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    return month + '-' + day + '-' + year + ' ' + hours + ':' + minutes + ':' + seconds;
}