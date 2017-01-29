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

    setCurrentHousehold = function(i) {
        if(ajaxData.results != null) {
            currentHousehold = ajaxData.results[i];
            currentHousehold.i = i;
        }
        else {
            currentHousehold = {};
        }
    };

    addPerson = function() {
        var blankPerson = {
            id: null,
            firstName: "",
            lastName: "",
            email: "",
            invited: false,
            going: false,
            invitedRehersal: false,
            goingRehersal: false
        };
        currentHousehold.addresses.push(blankPerson);
        renderPerson(currentHousehold.addresses.length-1, blankPerson);
    };

    renderPersonHeader = function() {
        var html = '<div class="row">';
        html += '<div class="col-md-1"><strong>Id</strong></div>';
        html += '<div class="col-md-2"><strong>First</strong></div>';
        html += '<div class="col-md-2"><strong>Last</strong></div>';
        html += '<div class="col-md-2"><strong>Email</strong></div>';
        html += '<div class="col-md-1"><strong>Rehersal</strong></div>';
        html += '<div class="col-md-1"><strong>Invite</strong></div>';
        html += '<div class="col-md-1"><strong>Wedding</strong></div>';
        html += '<div class="col-md-1"><strong>Invite</strong></div>';
        html += '</div>';

        $('#modalcontainer').append(html);
    }

    renderPerson = function(i, item) {
        var html = '<div class="row"';

        if(i%2 == 0) {
            html +=  ' style="background: #f1f1f1; padding-top:10px; padding-bottom:10px;">';
        }
        else {
            html +=  ' style="padding-top:10px; padding-bottom:10px;">';
        }

        html += '<div class="col-md-1">';
        html += item.id;
        html += '</div>';
        html += '<div class="col-md-2">';
        html += '<input type="text" value="' + item.firstName + '" onkeyup="updateFirstName(event, ' + i + ')">';
        html += '</div>';
        html += '<div class="col-md-2">';
        html += '<input type="text" value="' + item.lastName + '" onkeyup="updateLastName(event, ' + i + ')">';
        html += '</div>';
        html += '<div class="col-md-2">';
        html += '<input type="text" value = "' + item.email + '" onkeyup="updateEmail(event, ' + i + ')">';
        html += '</div>';
        html += '<div class="col-md-1">';
        html += '<input type="checkbox" checked="' + item.invited + '">';
        html += '</div>';
        html += '<div class="col-md-1">';
        html += item.going;
        html += '</div>';
        html += '<div class="col-md-1">';
        html += '<input type="checkbox" checked="' + item.invitedRehersal + '">';
        html += '</div>';
        html += '<div class="col-md-1">';
        html += item.goingRehersal;
        html += '</div>';

        html += '</div>';
        $('#modalcontainer').append(html);
    }

    addHousehold = function() {
        var blankHousehold = {
            id: null,
            name: "",
            uuid: null,
            addresses: []
        };
        ajaxData.results.push(blankHousehold);
        renderHousehold(ajaxData.results.length-1, blankHousehold)
    };

    renderHouseholdHeader = function() {
        var html = '<div class="row">';
        html += '<div class="col-md-1"><strong>Id</strong></div>';
        html += '<div class="col-md-2"><strong>Name</strong></div>';
        html += '<div class="col-md-3"><strong>UUID</strong></div>';

        html += '<div class="col-md-4"></div>';

        html += '<div id="message" class="alert alert-success"  style="display: none; top: 0px; left: 0px">';
        html += '</div>';
        html += '<div id="message" class="alert alert-danger"  style="display: none; top: 0px; left: 0px">';
        html += '</div>';


        html += '</div>';
        $('#maincontainer').append(html);
    };

    renderHousehold = function(i, item) {
        var html = '<div class="row"';
        if(i%2 == 0) {
            html +=  'style="background: #f1f1f1;padding-top:5px;">';
        }
        else {
            html +=  'style="padding-top:5px;">';
        }

        html += '<div class="col-md-1">';
        html += item.id;
        html += '</div>';
        html += '<div class="col-md-2">';
        html += '<input type="text" value = "' + item.name + '" onkeyup="updateHouseholdName(event, ' + i + ')">';
        html += '</div>';
        html += '<div class="col-md-3">';
        html += item.uuid;
        html += '</div>';
        html += '<div class="col-md-1">';
        html += '<input type="button" value="Persons" data-toggle="modal" data-target="#myModal" '
        html += 'class="btn btn-primary" onClick="setCurrentHousehold(' + i + ')">';
        html += '</div>';
        html += '<div class="col-md-1">';
        html += '<input type="button" value="Save" class="btn btn-success" onClick=saveHousehold(' + i + ')>';
        html += '</div>';

         html += '</div>';
        $('#maincontainer').append(html);
    };

    updateHouseholdName = function(e, i) {
        ajaxData.results[i].name = e.currentTarget.value;
    };

    updateFirstName = function(e, i) {
        currentHousehold.addresses[i].firstName = e.currentTarget.value;
    };

    updateLastName = function(e, i) {
        currentHousehold.addresses[i].lastName = e.currentTarget.value;
    };

    updateEmail = function(e, i) {
        currentHousehold.addresses[i].email = e.currentTarget.value;
    };

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
    		    currentHousehold = data;
    		    ajaxData.results[i] = data;

    		    $("#maincontainer").empty();
    		    renderHouseholdHeader();
    		    $.each(ajaxData.results, function (i, item) {
                    renderHousehold(i, item);
                });

    			$('#myModal').modal('hide');

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