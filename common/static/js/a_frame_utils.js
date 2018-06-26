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
        "template_name": template_name
    }

    var url = "/tools/embedTemplate/"

    var post = jQuery.post(url, params, function (response) {
        load_overlay(response);
    });

    post.fail(function () {
        alert('Could not perform request!');
    });

    post.always(function () {
        doc.css('cursor', '');
    });
}

function load_widget_configs(w_id) {
    // We will get the select object as the parameter
    // the value represents the choice the user has made
    // let's check the widget definition to see if there
    // is any configuration required and load it if necessary

    if (typeof(widgets) == "undefined") {
        // if the widgets object isn't around, we need to bail out
        console.log("widgets variable is not available");
        return false;
    }
    console.log(widget_config);

    var widget_config = {};
    var obj = $("#" + w_id);
    var config_button = $("#" + obj.prop("id") + "_config_button");

    $(widgets).each(function (i, w) {
        console.log(w.id + " == " + obj.val());
        if (w.id == obj.val()) {
            widget_config = w;
            // break out
            return false;
        }
    });

    if (widget_config.configurable == false) {
        // no need to load a configuration here
        config_button.css("display", "none");
        // overwrite any previous widget parameters
        var config_element = $("#" + obj.prop("id") + "_config");
        var widget_config_text = JSON.stringify({}, null, 0);
        config_element.val(widget_config_text);
        return true;
    }

    config_button.css("display", "");

    console.log('loading widget config for ' + obj.val());

    var doc = jQuery(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/input_forms/loadWidgetConfig/";

    var params = {
        "widget_id": obj.val(),
        "target_id": obj.prop("id")
    }

    var post = jQuery.post(url, params, function (response) {
        load_overlay(response);
    });

    post.fail(function () {
        alert('Could not perform request!');
    });

    post.always(function () {
        doc.css('cursor', '');
    });
}

function load_screen_widget_configs_manual(widget_id, widget_layout_id) {

    let doc = jQuery(document.documentElement);
    doc.css('cursor', 'progress');

    let url = "/screens/load_widget_config";

    let params = {
        "widget_layout_id": widget_layout_id,
        "widget_id": widget_id
    };

    let post = jQuery.post(url, params, function (response) {
        load_overlay(response);
    });

    post.fail(function () {
        alert('Could not perform request!');
    });

    post.always(function () {
        doc.css('cursor', '');
    });
}


function set_preload_list_config(widget_id) {

    var config_element = jQuery('#' + widget_id + '_config');

    var template_name = jQuery('#template_autocomplete').val();
    var preload_list_key_name = jQuery('#preload_list_key_name').val();
    var preload_list_value_name = jQuery('#preload_list_value_name').val();

    var widget_config = {
        "template_name": template_name,
        "key_name": preload_list_key_name,
        "value_name": preload_list_value_name
    }

    var widget_config_text = JSON.stringify(widget_config, null, 0);
    config_element.val(widget_config_text);
    console.log(widget_config_text);
    console.log('all done');
    close_overlay();
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

function reveal(object_id) {
    $('#' + object_id).toggle('blind');
}

// ======================= Widget Validation ======================= //

function check_ipv4_input(obj) {
    ip = obj.value;
    if (!ip.match('^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$')) {
        alert('IP format is not valid!');
        obj.value = '0.0.0.0';
        return true;
    }
}

function sticky_widget(widget_id) {
    let w = $('#widget_container_' + widget_id);
    let o = w.find('[class=overlay_close]');
    o.css("display", "none");
}

function set_global_sticky_widget(widget_id) {
    let w = $('#widget_container_' + widget_id);
    let o = w.find('[class=overlay_close]');
    // allow widgets to be moved and closed during config
    if (show_widget_menu === true) {
        o.css("display", "");
    } else {
        o.css("display", "none");
    }
}

function sticky_all_widgets(toggle) {
    let widgets = $('[id^=widget_container]');
    widgets.each(function (i, w) {
        let widget = $(w);
        let o = widget.find('[class=overlay_close]');
        if (toggle) {
            o.css("display", "none");
        } else {
            o.css("display", "");
        }

        widget.css('height', '');
    });
}
