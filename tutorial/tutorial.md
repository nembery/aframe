# A-Frame Tutorial

[GIT Hub Repository: https://github.com/nembery/aframe](https://github.com/nembery/aframe)


### Installing package requirements

Note: DJango version must be 1.9

```
root@automation-srv:~#  apt-get install python-netaddr python-pip python-nmap nmap python-lxml python-dev libssl-dev libxslt-dev python-paramiko
Reading package lists... Done
Building dependency tree
Reading state information... Done
Note, selecting 'libxslt1-dev' instead of 'libxslt-dev'
libxslt1-dev is already the newest version (1.1.28-2.1).
nmap is already the newest version (7.01-2).
libssl-dev is already the newest version (1.0.2g-1).
python-dev is already the newest version (2.7.11-1).
python-pip is already the newest version (1.5.6-7).
The following additional packages will be installed:
  ieee-data
Suggested packages:
  python-lxml-dbg python-lxml-doc ipython python-netaddr-docs
The following NEW packages will be installed:
  ieee-data python-netaddr python-nmap
The following packages will be upgraded:
  python-lxml
1 upgraded, 3 newly installed, 0 to remove and 560 not upgraded.
Need to get 1,783 kB of archives.
After this operation, 4,946 kB of additional disk space will be used.
Do you want to continue? [Y/n] y
Get:1 http://ftp.iinet.net.au/debian/debian stretch/main amd64 python-nmap all 0.5.0-1-1 [22.0 kB]
Get:2 http://ftp.iinet.net.au/debian/debian stretch/main amd64 ieee-data all 20150531.1 [830 kB]
Get:3 http://ftp.iinet.net.au/debian/debian stretch/main amd64 python-lxml amd64 3.6.0-1 [744 kB]
Get:4 http://ftp.iinet.net.au/debian/debian stretch/main amd64 python-netaddr all 0.7.18-1 [187 kB]
Fetched 1,783 kB in 4s (385 kB/s)
Reading changelogs... Done
Selecting previously unselected package python-nmap.
(Reading database ... 180867 files and directories currently installed.)
Preparing to unpack .../python-nmap_0.5.0-1-1_all.deb ...
Unpacking python-nmap (0.5.0-1-1) ...
Selecting previously unselected package ieee-data.
Preparing to unpack .../ieee-data_20150531.1_all.deb ...
Unpacking ieee-data (20150531.1) ...
Preparing to unpack .../python-lxml_3.6.0-1_amd64.deb ...
Unpacking python-lxml (3.6.0-1) over (3.5.0-1) ...
Selecting previously unselected package python-netaddr.
Preparing to unpack .../python-netaddr_0.7.18-1_all.deb ...
Unpacking python-netaddr (0.7.18-1) ...
Processing triggers for man-db (2.7.5-1) ...
Setting up python-nmap (0.5.0-1-1) ...
Setting up ieee-data (20150531.1) ...
Setting up python-lxml (3.6.0-1) ...
Setting up python-netaddr (0.7.18-1) ...
root@automation-srv:~#
root@automation-srv:~#
root@automation-srv:~# pip install django junos-eznc
Downloading/unpacking django
  Downloading Django-1.9.6-py2.py3-none-any.whl (6.6MB): 6.6MB downloaded
Requirement already satisfied (use --upgrade to upgrade): junos-eznc in /usr/local/lib/python2.7/dist-packages
Requirement already satisfied (use --upgrade to upgrade): lxml>=3.2.4 in /usr/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): ncclient>=0.4.6 in /usr/local/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): paramiko>=1.15.2 in /usr/local/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): scp>=0.7.0 in /usr/local/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): jinja2>=2.7.1 in /usr/local/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): PyYAML>=3.10 in /usr/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): netaddr in /usr/local/lib/python2.7/dist-packages (from junos-eznc)
Requirement already satisfied (use --upgrade to upgrade): setuptools>0.6 in /usr/lib/python2.7/dist-packages (from ncclient>=0.4.6->junos-eznc)
Installing collected packages: django
Successfully installed django
Cleaning up...
root@automation-srv:~#
```

<br><br>

### Clone the Git Repository

```
root@automation-srv:/opt# git clone https://github.com/nembery/aframe
Cloning into 'aframe'...
remote: Counting objects: 367, done.
remote: Compressing objects: 100% (37/37), done.
remote: Total 367 (delta 12), reused 0 (delta 0), pack-reused 327
Receiving objects: 100% (367/367), 202.20 KiB | 84.00 KiB/s, done.
Resolving deltas: 100% (196/196), done.
Checking connectivity... done.
root@automation-srv:/opt#
```

<br><br>

### Create the DB

```
root@automation-srv:/opt/aframe# python ./manage.py migrate
importing module_name: CSV file connector
loading class
importing module_name: Statically defined List
loading class
importing module_name: nmap network discovery connector
loading class
importing module_name: Junos Space Device List
loading class
Operations to perform:
  Apply all migrations: sessions, auth, contenttypes, input_forms, endpoints, tools
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying endpoints.0001_initial... OK
  Applying tools.0001_initial... OK
  Applying input_forms.0001_initial... OK
  Applying sessions.0001_initial... OK
root@automation-srv:/opt/aframe#
```

<br><br>

### Run the DJango webserver

```
root@automation-srv:/opt/aframe# python ./manage.py runserver 0.0.0.0:8080
Performing system checks...

importing module_name: CSV file connector
loading class
importing module_name: Statically defined List
loading class
importing module_name: nmap network discovery connector
loading class
importing module_name: Junos Space Device List
loading class
System check identified no issues (0 silenced).
June 02, 2016 - 19:43:40
Django version 1.9.6, using settings 'a_frame.settings'
Starting development server at http://0.0.0.0:8080/
Quit the server with CONTROL-C.
```

<br><br>

### Accessing A-Frame interface

- Open your browser and access the URL: `http://<SERVER_IP>:8080`

![picture1](images/picture1.png?raw=true)

<br><br>

### Create an endpoints

- Access the endpoint menu

![picture2](images/picture2.png?raw=true)

<br><br>

### Create an endpoints

- click on creating new endpoints

![picture3](images/picture3.png?raw=true)

<br><br>

### Create an endpoints

- select the discovery method

![picture4](images/picture4.png?raw=true)

<br><br>

In this case, I am choosing CVS

<br><br>

![picture5](images/picture5.png?raw=true)

<br><br>

### Create an endpoints

- Provide the CSV file (must reside in the aframe server)

![picture6](images/picture6.png?raw=true)

<br><br>

### Create an endpoints

- Now we have the VMXes added into the endpoints

<br><br>

Note that our CSV file could have many VMXes instead of just one.

<br><br>

The format of the CSV file is like this:

<br><br>

|ID |Router Name|    Router IP   |  Username  | Password | Device Type|
|---|-----------|----------------|------------|----------|------------|
| 1 |  vmx1     | 10.254.254.100 | dmontagner | diogo123 | junos      |
| 2 |  vmx2     | 10.254.254.200 | dmontagner | diogo123 | junos      |

<br><br>

Below is the CSV file used in this tutorial

```
# id,name,ip,username,password,type
1,vmx1,10.254.254.100,dmontagner,diogo123,junos
```

<br><br>

![picture7](images/picture7.png?raw=true)

<br><br>

### Create an Automation

- Now, let's create an automation to deploy a routing-instance configuration to the routers. For that, click on Automations, then click
on Define New Automation

![picture8](images/picture8.png?raw=true)

<br><br>

### Create an Automation

- In the action provider list, select Netconf

![picture9](images/picture9.png?raw=true)

<br><br>

### Create an Automation

- In the Action Options, select Apply configuration

![picture10](images/picture10.png?raw=true)

<br><br>

### Create an Automation

- The next screen is where we define the template

![picture11](images/picture11.png?raw=true)

<br><br>

### Create an Automation

- Give a name, description, and fill up the template. The template in this case is a JUNOS configuration using jinja2 variables

![picture12](images/picture12.png?raw=true)

<br><br>

Here is the template used in this case

```
interfaces {
    {{ phy_interface }} {
        flexible-vlan-tagging;
        unit {{ vlan_id }} {
            vlan-id {{ vlan_id }};
            family inet {
                address {{ interface_ip }}/{{ subnet_mask }};
            }
        }
    }
}
policy-options {
    policy-statement {{ vpn_name }}_EXPORT {
        term EXPORT {
            then {
                community add {{ vpn_name }}_COMM;
                accept;
            }
        }
    }
    policy-statement {{ vpn_name }}_IMPORT {
        term IMPORT {
            from community {{ vpn_name }}_COMM;
            then accept;
        }
    }
    community {{ vpn_name }}_COMM members target:{{ rt_target }};
}
routing-instances {
    {{ vpn_name }} {
        instance-type vrf;
        interface {{ phy_interface }}.{{ vlan_id }};
        route-distinguisher {{ vpn_rd }};
        vrf-import {{ vpn_name }}_IMPORT;
        vrf-export {{ vpn_name }}_EXPORT;
        protocols {
            bgp {
                group PE {
                    type external;
                    peer-as {{ ce_asn }};
                    neighbor {{ ce_ip }};
                }
            }
        }
    }
}
```

<br><br>

### Create an Automation

- Once you click create, A-Frame will process the template and will present you the web form to be created.

![picture13](images/picture13.png?raw=true)

<br><br>

### Create an Automation

- Now, you can add more meaningful descriptions for the field as well as suggested values

![picture14](images/picture14.png?raw=true)

<br><br>

Note that the values in the default field are used to show the format that the data needs to be entered

<br><br>

### Executing an Automation

- Now, let's deploy the configuration. For that, click in Network Automations

![picture15](images/picture15.png?raw=true)

<br><br>

We can now see the automation we created previously. Because this is an endpoint automation, we need to execute
it with endpoints. So, click on Endpoints, then Click on VMXes. Then select the endpoint VMXes and add then to the
queue clicking on Add Selected Endpoints to the queue. You queue should now show that it has 1 element in the queue
as you can see in the picture below.

<br><br>

![picture16](images/picture16.png?raw=true)

<br><br>

### Executing an Automation

- Now, type the initials or any substring of your template. In our case, if you type Depl that will do. Then click submit.

![picture17](images/picture17.png?raw=true)

<br><br>

### Executing an Automation

- Before proceeding, I just want to demonstrate that the router does not have any config for this VPN:

```
dmontagner@vmx1> show configuration routing-instances

dmontagner@vmx1> show configuration interfaces ge-0/0/1
flexible-vlan-tagging;

dmontagner@vmx1>
```

<br><br>

### Executing an Automation

- Here you can see the web form with the suggested values.

![picture18](images/picture18.png?raw=true)

<br><br>

### Executing an Automation

- Let's fill the form with our values. You also need to provide the username and password that will
be used to execute this deployment

![picture19](images/picture19.png?raw=true)

<br><br>

### Executing an Automation

- Once you click apply, A-Frame will deploy the configuration in the router and present the following screen

![picture20](images/picture20.png?raw=true)

<br><br>

### Checking the results of the automation deployment

- Let's check in the router:

```
dmontagner@vmx1> show configuration routing-instances
VPN1 {
    instance-type vrf;
    interface ge-0/0/1.100;
    route-distinguisher 65000:65000;
    vrf-import VPN1_IMPORT;
    vrf-export VPN1_EXPORT;
    protocols {
        bgp {
            group PE {
                type external;
                peer-as 65300;
                neighbor 192.168.50.2;
            }
        }
    }
}

dmontagner@vmx1> show configuration interfaces ge-0/0/1
flexible-vlan-tagging;
unit 100 {
    vlan-id 100;
    family inet {
        address 192.168.50.1/30;
    }
}

dmontagner@vmx1>
```
