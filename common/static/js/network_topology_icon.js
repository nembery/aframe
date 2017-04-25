topologyIconPortLocator = draw2d.layout.locator.PortLocator.extend({
    NAME: "topologyIconPortLocator",
    init: function() {
        this._super();
    },
    relocate: function(index, figure) {
        var node = figure.getParent();
        var x = node.getWidth() / 2;
        var y = node.getHeight() / 2;
        this.applyConsiderRotation(figure, x, y);
    }
});
BottomCenterLocator = draw2d.layout.locator.Locator.extend({
    NAME: "BottomCenterLocator",
    init: function(parent)
    {
        this._super(parent);
    },
    relocate: function(index, target)
    {
        var parent = target.getParent();
        var boundingBox = parent.getBoundingBox();
        var targetBoundingBox = target.getBoundingBox();
        target.setPosition(boundingBox.w / 2 - targetBoundingBox.w / 2, parent.getHeight());
    }
});
IpLabelLocator = draw2d.layout.locator.Locator.extend({
    NAME: "IpLabelLocator",
    init: function(parent)
    {
        this._super(parent);
    },
    relocate: function(index, target)
    {
        var parent = target.getParent();
        var boundingBox = parent.getBoundingBox();
        var targetBoundingBox = target.getBoundingBox();
        target.setPosition(boundingBox.w / 2 - targetBoundingBox.w / 2, parent.getHeight() + 4);
    }
});
BootStateLocator = draw2d.layout.locator.Locator.extend({
    NAME: "BootStateLocator",
    init: function(parent) {
        this._super(parent);
    },
    relocate: function(index, target) {
        var node = target.getParent()
        var x = node.getWidth() - 11;
        var y = 1;
        target.setPosition(x, y);
    }
});
draw2d.shape.node.topologyIcon = draw2d.shape.basic.Image.extend({
    NAME: "draw2d.shape.node.topologyIcon",
    EDIT_POLICY: false,

    init: function(icon, width, height) {
	    this._super(icon, width, height);
    	var tpl = new topologyIconPortLocator();
    	this.createPort("hybrid", tpl);
        this.setBootState("down");
    },
    setup: function(label, ip) {
		this.setUserData({});
		this.setIp(ip);
		this.setLabel(label);
    },
    setBootState: function(state) {
        this.bootState = state;
        if (this.bootStateIcon == undefined) {
            this.bootStateIcon = new draw2d.shape.basic.Circle();
            this.bootStateIcon.setBackgroundColor("#FF0000");
            this.bootStateIcon.setDimension(8, 8);
            this.add(this.bootStateIcon, new BootStateLocator(this));
        }
        if (state == "up") {
            this.bootStateIcon.setBackgroundColor("#00FF00");
        } else {
            this.bootStateIcon.setBackgroundColor("#FF0000");
        }
    },

    getBootState: function() {
        return this.bootState;
    },
    setType: function(type) {
	    var ud = this.getUserData();
	    ud["type"] = type;
    },
    getType: function() {
	    return this.getUserData()["type"];
    },
    setCpu: function(cpu) {
	    var ud = this.getUserData();
	    ud["cpu"] = cpu;
    },
    getCpu: function() {
        if (this.getUserData()["cpu"] != undefined) {
	        return this.getUserData()["cpu"];
        } else {
            // return magic number 2 - all older version of wistar defaulted to 2 vCPU
            return "2";
        }
    },
    setRam: function(ram) {
	    var ud = this.getUserData();
	    ud["ram"] = ram;
    },
    getRam: function() {
        if (this.getUserData()["ram"] != undefined) {
	        return this.getUserData()["ram"];
        } else {
            // return magic number 2 - all older version of wistar defaulted to 2048MB RAM
            return "2048";
        }
    },
    getMgmtInterface: function() {
        var port = this.getPorts().get(0);
        var connections = port.getConnections();
        mgmtInterfaceIndex = connections.size;
        if(this.getType() == "junos_vmx") {
            return "em0";
        } else if(this.getType() == "junos_vmx_p2") {
            return "fxp0";
        } else if(this.getType() == "junos_firefly") {
            return "ge-0/0/" + mgmtInterfaceIndex;
        } else if(this.getType() == "linux") {
            return "eth" + mgmtInterfaceIndex;
        } else {
            return "eth0";
        }
    },
    setIp: function(ip) {
	    var ud = this.getUserData();
	    ud["ip"] = ip;
	    if (this.ipLabel == undefined) {
		    this.ipLabel = new draw2d.shape.basic.Label({text: "\n" + ip });
	        this.ipLabel.setColor("#000");
        	this.ipLabel.setFontColor("#000");
        	this.ipLabel.setFontSize('16');
        	this.ipLabel.setStroke(0);
        	this.add(this.ipLabel, new BottomCenterLocator(this));
	    } else {
            this.ipLabel.text = "\n" + ip;
        }
    },
    getIp: function() {
    	return this.getUserData()["ip"];
    },
    setPassword: function(pw) {
    	var ud = this.getUserData();
    	ud["password"] = pw;
    },
    getPassword: function() {
    	return this.getUserData()["password"];
    },
    setImage: function(im) {
    	var ud = this.getUserData();
    	ud["image"] = im;
    },
    getImage: function() {
    	return this.getUserData()["image"];
    },
    setLabel: function(label) {
    	// console.log("setlabel " + label);
    	var ud = this.getUserData();
    	ud["label"] = label;
        if (this.label == undefined) {
    	    this.label = new draw2d.shape.basic.Label({text: label });
            this.label.setColor("#0d0d0d");
            this.label.setFontColor("#0d0d0d");
            this.label.setFontSize('16');
            this.label.setStroke(0);
            this.add(this.label, new BottomCenterLocator(this));
        } else {
            this.label.text = label;
        }
    },
    getLabel: function() {
    	return this.getUserData()["label"];
    },
    setConfigScriptId: function(id) {
    	var ud = this.getUserData();
    	ud["configScriptId"] = id;
    },
    getConfigScriptId: function() {
    	return this.getUserData()["configScriptId"];
    },
    setConfigScriptParam: function(p) {
    	var ud = this.getUserData();
    	ud["configScriptParam"] = p;
    },
    getConfigScriptParameter: function() {
    	return this.getUserData()["configScriptParam"];
    },
    setPersistentAttributes: function(memento) {
    	this._super(memento);
    	this.setLabel(memento.userData.label);
    	this.setType(memento.userData.type);
    	this.setIp(memento.userData.ip);
    	this.setImage(memento.userData.image);
    },
    getPersistentAttributes: function() {
        // force grabbing the mgnt interface
        var ud = this.getUserData();
        return this._super();
    },
    setupObject: function(type, label, width, height) {
        this.setDimension(width, height);
    	var tpl = new topologyIconPortLocator();
    	this.createPort("hybrid", tpl);
        this.setType(type);
        this.setLabel(label);
    },
    getParentCanvasId: function() {
        var canvas = this.getCanvas();
        var canvasId = canvas.canvasId;
        return canvasId.split('_').slice(-1);
    },
    // override default dc handler
    onDoubleClick: function() {
        return;
    },
    onContextMenu: function(x, y) {
        console.log('on context menu');
        var items = {
            "status": {
                name: "Refresh Status"
            },
            "details": {
                name: "View Details"
            },
            "delete": {
                name: "Delete"
            }
        };
        console.log(this);
        $.contextMenu({
            selector: 'body',
            zIndex: 1000,
            events: {
                hide: function() {
                    $.contextMenu('destroy');
                }
            },
            callback: $.proxy(function(key, options) {
                switch (key) {
                    case "delete":
			            var ports = this.getPorts().asArray();
        		        for (i = 0; i < ports.length; i++) {
        		            var connections = ports[i].getConnections();
        		            for (c = 0; c < connections.length; c++) {
        		                canvas.remove(canvas.getFigure(c));
        		            }
		                    this.removePort(ports[i]);
        		        }
                        $.contextMenu('destroy');
                        var command = new draw2d.command.CommandDelete(this);
			            this.getCanvas().getCommandStack().execute(command);
                        break;
                    case "status":
                        refresh_topology_icon_status(this.getLabel(), this.getParentCanvasId());
                        break;
                    case "details":
                        load_topology_icon_details(this.getLabel(), this.getParentCanvasId());
                        break;
                    default:
                        break;
                    }
                }, this),
            x: x,
            y: y,
            items: items
        });
    }
});
