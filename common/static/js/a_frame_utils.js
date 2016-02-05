// will be used for utility js functions

// removes non alpha numeric and compacts whitespace to single space
function clean_string_no_special(input_object) {
    var input_string = input_object.value;

    //  remove all non alpha numeric
    var first_pass = input_string.replace(/[^a-zA-Z0-9_\ \.\\\#\-_\/]/g, "");

    input_object.value = first_pass;
}

// cleans the string and leaves no white space at all
function clean_string_no_space(input_object) {
    var input_string = input_object.value;

    //  remove all non alpha numeric
    var first_pass = input_string.replace(/[^a-zA-Z0-9_\ ]/g, "");
    var second_pass = first_pass.replace(/\s+/g, "_");
    var third_pass = second_pass.replace(/\s+$/, "");
    input_object.value = third_pass;
}

function embed_template() {

    var template_name = $('#template_autocomplete').val();

    var doc = jQuery(document.documentElement);
    doc.css('cursor', 'progress');

    var params = {
        "template_name" : template_name
    }

    var url = "/tools/embedTemplate/"

    var post = jQuery.post(url, params, function(response) {
        load_overlay(response);
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}


function load_overlay(content) {

    var doc = $(document);
    var overlay = $("<div/>").attr("id", "overlay").addClass("overlay");
    $("body").append(overlay);

    overlay.append(content);

}

function close_overlay() {
    var overlay = $("#overlay");
    overlay.empty();
    overlay.removeClass("help-overlay");
    overlay.remove();
}