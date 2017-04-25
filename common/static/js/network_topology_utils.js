
if (canvases == undefined) {
    var canvases = {};
}
var canvas_layout = {};

function get_layout_for_icon(widget_config_id) {

    var wrap_limit = 5;
    var icon_offset = 110;

    if (canvas_layout == undefined) {
        canvas_layout = {};
    }

    if (canvas_layout[widget_config_id] == undefined) {
        var config = {
            'num_instances': 0,
            'left': -50,
            'top': 50,
            'total_offset': 100
        };
        canvas_layout[widget_config_id] = config;
    }

    var c = canvas_layout[widget_config_id];

    console.log('adding one');
    c['num_instances'] += 1;
    c['left'] += 100;
    c['top'] += 0;

    if (c['num_instances'] > wrap_limit) {
        c['left'] = 50;
        c['top'] += icon_offset;
        c['num_instances'] = 1;
        c['total_offset'] += 110;
    }

    return c;
}

function clear_layout(widget_config_id) {
    if (canvas_layout == undefined) {
        canvas_layout = {};
    }
    var config = {
            'num_instances': 0,
            'left': -50,
            'top': 50,
            'total_offset': 100
        };
    canvas_layout[widget_config_id] = config;
}

function add_network_device(widget_config_id) {

    if (canvases == undefined) {
        console.log('uh oh');
        return;
    }

    if (canvases[widget_config_id] == undefined) {
        console.log(' now what? ');
        return;
    }

    canvas = canvases[widget_config_id];

    var name = $('#add_network_device_name_' + widget_config_id).val();
    var ip = $('#add_network_device_ip_' + widget_config_id).val();
    var icon_val = $('#add_network_device_icon_' + widget_config_id).val();

    var icon_array = icon_val.split(':');
    var icon_name = icon_array[0];
    var icon_width = icon_array[1];
    var icon_height = icon_array[2];

    console.log(icon_name, icon_width, icon_height);
    var icon = new draw2d.shape.node.topologyIcon({ path: icon_name, width: icon_width, height: icon_height });
    //var icon = new draw2d.shape.node.topologyIcon();

    icon.setup(name, ip);

    var c = get_layout_for_icon(widget_config_id);
    canvas.add(icon, c['left'], c['top']);

}

function create_new_topology(widget_config_id) {
    var canvas = window.canvases[widget_config_id];
    canvas.clear();

    var name_field = $('#topology_name_' + widget_config_id);
    name_field.val('n/a');
}

function debug_topology(widget_config_id) {

    var canvas = window.canvases[widget_config_id];
    var writer = new draw2d.io.json.Writer();

    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        var data = JSON.stringify(json, null, 2);
        console.log(data);
    });
}

function save_network_topology(widget_config_id) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/createWidgetData";

    var canvas = window.canvases[widget_config_id];

    var writer = new draw2d.io.json.Writer();

    var data = "";
    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        data = JSON.stringify(json, null, 2);
    });

    console.log(data);
    console.log(layout['widgets'][widget_config_id]);

    var widget_name = $('#save_network_topology_name_' + widget_config_id).val();
    var widget_type = layout['widgets'][widget_config_id]['widget_id'];

    var params = {
        "name": widget_name,
        "widget_type": widget_type,
        "data": data
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            alert('Saved OK');
            reveal('save_topology_dialogue_' + widget_config_id);
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

function update_network_topology(widget_config_id) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/updateWidgetData";

    var canvas = window.canvases[widget_config_id];

    var writer = new draw2d.io.json.Writer();

    var data = "";
    writer.marshal(canvas, function(json) {
        // convert the json object into string representation
        data = JSON.stringify(json, null, 2);
    });

    console.log(data);
    console.log(layout['widgets'][widget_config_id]);

    var widget_name = $('#topology_name_' + widget_config_id).val();

    console.log(widget_name);
    var widget_type = layout['widgets'][widget_config_id]['widget_id'];

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

function load_network_topology(widget_config_id, widget_data_name) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/getWidgetData";

    var canvas = window.canvases[widget_config_id];
    canvas.clear();

    clear_layout(widget_config_id);

    var writer = new draw2d.io.json.Writer();

    if (widget_data_name == undefined) {
        widget_data_name = $('#load_network_topology_name_' + widget_config_id).val();
    }

    var widget_type = layout['widgets'][widget_config_id]['widget_id'];

    var params = {
        "name": widget_data_name,
        "widget_type": widget_type
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            var json = eval(response['data']);
            reader = new draw2d.io.json.Reader();
            reader.unmarshal(canvas, json);

            if ($('#load_topology_dialogue_' + widget_config_id).css('display') != 'none') {
                reveal('load_topology_dialogue_' + widget_config_id);
            }

            var name_field = $('#topology_name_' + widget_config_id);
            name_field.val(widget_data_name);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function delete_network_topology(widget_config_id, widget_data_name) {

    var doc = $(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/deleteWidgetData";

    var canvas = window.canvases[widget_config_id];

    if (widget_data_name == undefined) {
        widget_data_name = $('#load_network_topology_name_' + widget_config_id).val();
    }

    var widget_type = layout['widgets'][widget_config_id]['widget_id'];

    var params = {
        "name": widget_data_name,
        "widget_type": widget_type
    }
    console.log(params);

    var post = $.post(url, params, function(response) {
        if(response['status'] == true) {
            list_network_topologies(widget_config_id);
        }
    });

    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}

function list_network_topologies(widget_config_id) {

    var doc = jQuery(document.documentElement);
    doc.css('cursor', 'progress');

    var url = "/screens/listWidgetData"

    var widget_type = layout['widgets'][widget_config_id]['widget_id'];

    var canvas = window.canvases[widget_config_id];
    canvas.clear();

    clear_layout(widget_config_id);

    var params = {
        "widget_type": widget_type
    }

    var post = $.post(url, params, function(response) {
        console.log(response);
        var widget_list = $.parseJSON(response['list']);
        $.each(widget_list, function(i, o) {
            var name = o["name"]
            var cloud = new draw2d.shape.node.TopologyLinkCloud(name);
            cloud.width = 100;
            cloud.height = 100;
            var c = get_layout_for_icon(widget_config_id);
            canvas.add(cloud, c['left'], c['top']);
        });
    });

    if ($('#load_topology_dialogue_' + widget_config_id).css('display') != 'none') {
        reveal('load_topology_dialogue_' + widget_config_id);
    }


    post.fail(function() {
        alert('Could not perform request!');
    });

    post.always(function() {
        doc.css('cursor', '');
    });
}
