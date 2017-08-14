
if (canvases == undefined) {
    var canvases = {};
}
var canvas_layout = {};

function get_layout_for_icon(widget_layout_id) {
    // determine where on the canvas to put this icon
    // i.e. don't overlap them

    var wrap_limit = 8;
    var icon_offset = 120;

    if (canvas_layout == undefined) {
        canvas_layout = {};
    }

    if (canvas_layout[widget_layout_id] == undefined) {
        var config = {
            'num_instances': 0,
            'left': -25,
            'top': 25,
            'total_offset': 100
        };
        canvas_layout[widget_layout_id] = config;
    }

    var c = canvas_layout[widget_layout_id];

    console.log('adding one');
    c['num_instances'] += 1;
    c['left'] += 120;
    c['top'] += 0;

    if (c['num_instances'] > wrap_limit) {
        c['left'] = 25;
        c['top'] += icon_offset;
        c['num_instances'] = 1;
        c['total_offset'] += 110;
    }

    return c;
}

function clear_layout(widget_layout_id) {
    // reset the layout on this canvas
    // if you delete a topology, then we want to start over
    if (canvas_layout == undefined) {
        canvas_layout = {};
    }
    var config = {
            'num_instances': 0,
            'left': -50,
            'top': 50,
            'total_offset': 100
        };
    canvas_layout[widget_layout_id] = config;
}

function add_network_device(widget_layout_id) {
    // add an icon to the canvas

    if (canvases == undefined) {
        console.log('uh oh');
        return;
    }

    if (canvases[widget_layout_id] == undefined) {
        console.log(' now what? ');
        return;
    }

    canvas = canvases[widget_layout_id];

    var name = $('#add_network_device_name_' + widget_layout_id).val();
    var ip = $('#add_network_device_ip_' + widget_layout_id).val();
    var icon_val = $('#add_network_device_icon_' + widget_layout_id).val();

    var icon_array = icon_val.split(':');
    var icon_name = icon_array[0];
    var icon_width = icon_array[1];
    var icon_height = icon_array[2];

    console.log(icon_name, icon_width, icon_height);
    var icon = new draw2d.shape.node.topologyIcon({ path: icon_name, width: icon_width, height: icon_height });

    icon.setup(name, ip);

    var c = get_layout_for_icon(widget_layout_id);
    canvas.add(icon, c['left'], c['top']);

}

function create_new_topology(widget_layout_id) {
    // clear the current canvas of all icons and create a new one

    var canvas = window.canvases[widget_layout_id];
    canvas.clear();

    clear_layout(widget_layout_id)
    layout['widgets'][widget_layout_id]['widget_config'] = {};

    var name_field = $('#topology_name_' + widget_layout_id);
    name_field.val('n/a');
}

function debug_topology(widget_layout_id) {
    // dump the canvas as JSON to the console.log

    var canvas = window.canvases[widget_layout_id];
    var writer = new draw2d.io.json.Writer();

    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        var data = JSON.stringify(json, null, 2);
        console.log(data);
    });
}

function save_network_topology(widget_layout_id) {
    // serialize the canvas to JSON and post to AFrame to store in the db

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/createWidgetData";

    var canvas = window.canvases[widget_layout_id];

    var writer = new draw2d.io.json.Writer();

    var data = "";
    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        data = JSON.stringify(json, null, 2);
    });

    console.log(data);
    console.log(layout['widgets'][widget_layout_id]);

    var widget_name = $('#save_network_topology_name_' + widget_layout_id).val();
    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];

    var params = {
        "name": widget_name,
        "widget_type": widget_type,
        "data": data
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            alert('Saved OK');
            reveal('save_topology_dialogue_' + widget_layout_id);

            // let's save this topology on the layout config
            widget_config = {
                "name": widget_name,
                "widget_type": widget_type,
            }

            layout['widgets'][widget_layout_id]['widget_config'] = widget_config;

        } else{
            alert(response['message']);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function update_network_topology(widget_layout_id) {
    // update current topology and update in the DB

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/updateWidgetData";

    var canvas = window.canvases[widget_layout_id];

    var writer = new draw2d.io.json.Writer();

    var data = "";
    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        data = JSON.stringify(json, null, 2);
    });

    console.log(data);
    console.log(layout['widgets'][widget_layout_id]);

    if (data == []) {
        console.log('found a blank canvas to update!');
        doc.css('cursor', '');
        return;
    }

    var widget_name = $('#topology_name_' + widget_layout_id).val();

    console.log(widget_name);
    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];

    var params = {
        "name": widget_name,
        "widget_type": widget_type,
        "data": data
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            alert('Saved OK');
        } else{
            alert(response['message']);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function load_network_topology(widget_layout_id, widget_data_name) {
    // load a saved canvas from the DB

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/getWidgetData";

    var canvas = window.canvases[widget_layout_id];
    canvas.clear();

    clear_layout(widget_layout_id);

    var writer = new draw2d.io.json.Writer();

    if (widget_data_name == undefined) {
        widget_data_name = $('#load_network_topology_name_' + widget_layout_id).val();
    }

    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];

    var params = {
        "name": widget_data_name,
        "widget_type": widget_type
    }

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            var json = eval(response['data']);
            reader = new draw2d.io.json.Reader();
            reader.unmarshal(canvas, json);

            if ($('#load_topology_dialogue_' + widget_layout_id).css('display') != 'none') {
                reveal('load_topology_dialogue_' + widget_layout_id);
            }

            var name_field = $('#topology_name_' + widget_layout_id);
            name_field.val(widget_data_name);

            // let's save this topology on the layout config
            layout['widgets'][widget_layout_id]['widget_config'] = params;
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function delete_network_topology(widget_layout_id, widget_data_name) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/deleteWidgetData";

    var canvas = window.canvases[widget_layout_id];

    if (widget_data_name == undefined) {
        widget_data_name = $('#load_network_topology_name_' + widget_layout_id).val();
    }

    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];

    var params = {
        "name": widget_data_name,
        "widget_type": widget_type
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            // remove from layout
            layout['widgets'][widget_layout_id]['widget_config'] = {};

            list_network_topologies(widget_layout_id);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function list_network_topologies(widget_layout_id) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/listWidgetData"

    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];

    var canvas = window.canvases[widget_layout_id];
    canvas.clear();

    clear_layout(widget_layout_id);

    var params = {
        "widget_type": widget_type
    }

    var post = $.post(url, params, function(response) {

        // remove stale config from layout
        layout['widgets'][widget_layout_id]['widget_config'] = {};

        var widget_list = $.parseJSON(response['list']);
        $.each(widget_list, function(i, o) {
            var name = o["name"]
            var cloud = new draw2d.shape.node.TopologyLinkCloud(name);
            cloud.width = 100;
            cloud.height = 100;
            var c = get_layout_for_icon(widget_layout_id);
            canvas.add(cloud, c['left'], c['top']);
        });
    });

    if ($('#load_topology_dialogue_' + widget_layout_id).css('display') != 'none') {
        reveal('load_topology_dialogue_' + widget_layout_id);
    }


    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function save_network_topology_config(widget_layout_id) {
    // save global widget config to the db
    // global config is inherited by all widgets of this type

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/saveWidgetConfig";

    var widget_type = layout['widgets'][widget_layout_id]['widget_id'];
    d = {};

    d["detail_widget"] = $('#detail_widget_' + widget_layout_id).val();
    d["detail_identifier_param"] = $('#detail_identifier_param_' + widget_layout_id).val();

    d["config_widget"] = $('#config_widget_' + widget_layout_id).val();
    d["config_identifier_param"] = $('#config_identifier_param_' + widget_layout_id).val();

    d["telemetry_widget"] = $('#telemetry_widget_' + widget_layout_id).val();
    d["telemetry_identifier_param"] = $('#telemetry_identifier_param_' + widget_layout_id).val();

    data = JSON.stringify(d);

    var params = {
        "widget_type": widget_type,
        "data": data
    }

    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            alert('Saved OK');
            reveal('configure_topology_dialogue_' + widget_layout_id);
        } else{
            alert(response['message']);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function load_topology_icon_details(icon_id, global_config) {
    // will load the widget for the specific icon
    if (global_widget_configs['network_topology']["detail_widget"] == undefined) {
        console.log('detail is not configured in the global config!');
        return;
    }
    var desired_widget = global_widget_configs['network_topology']["detail_widget"];
    var icon_param = global_widget_configs['network_topology']["detail_identifier_param"];
    var widget_layout_id = generate_widget_layout_id();
    load_widget(desired_widget, widget_layout_id, { [icon_param]: icon_id});
}

function load_topology_icon_config(icon_id, global_config) {
    // will load the widget for the specific icon
    if (global_widget_configs['network_topology']["config_widget"] == undefined) {
        console.log('config is not configured in the global config!');
        return;
    }
    var desired_widget = global_widget_configs['network_topology']["config_widget"];
    var icon_param = global_widget_configs['network_topology']["config_identifier_param"];
    var widget_layout_id = generate_widget_layout_id();
    load_widget(desired_widget, widget_layout_id, { [icon_param]: icon_id});
}


function load_topology_icon_telemetry(icon_id, global_config) {
    // will load the widget for the specific icon
    if (global_widget_configs['network_topology']["telemetry_widget"] == undefined) {
        console.log('telemetry is not configured in the global config!');
        return;
    }
    var desired_widget = global_widget_configs['network_topology']["telemetry_widget"];
    var icon_param = global_widget_configs['network_topology']["telemetry_identifier_param"];
    var widget_layout_id = generate_widget_layout_id();

    load_widget(desired_widget, widget_layout_id, { [icon_param]: icon_id});
}
