
var canvases = {};
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