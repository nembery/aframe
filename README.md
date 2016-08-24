AFrame is a minimalistic automation framework / experiment. The goal is to allow
network engineers to easily use network automation *without programming*. That means creating and using templates,
consuming APIs, etc.

The idea is to present a single point of management for network automation.
Virtually any API is, or can be, supported from one central place.

To build, you'll need pyez, django 1.9, python-netaddr, nmap, and a few other libraries installed to get started.

Instructions for Ubuntu 14.04:
sudo apt-get install python-netaddr python-pip python-nmap nmap python-lxml python-dev libssl-dev libxslt-dev python-paramiko -y
sudo pip install django junos-eznc

first, create your db by running "$ python ./manage.py migrate"
then run the application by "$ python ./manage.py runserver 0.0.0.0:8080"

To do interesting things, you'll need to create an endpoint group or write an
endpoint group plugin to pull devices from whatever repo you currently use.
I've written a couple that should handle most situations: CSV file, static
configuration, Junos Space, and nmap based network discovery.

Next, you'll want to build some templates. The central idea in AFrame is that
*everything* is a template. Devices Configuration, REST API Payloads,
python scripts, shell scripts, etc. It's all just templates that can be
customized and executed / applied via some action.

I've written a couple of action providers like: NetconfAction, RestAction,
and ShellExecution. These should handle most things you'd want to do. However,
if you happen to need to tie in some system with a SOAP or XML-RPC API, then
writing an action provider for those should be easy. That's the whole point
of aframe.

Check it out and let me know how we can improve it, what ideas work, and which
ones don't.

An additional A-Frame tutorial can be found here: [A-Frame Tutorial](tutorial/tutorial.md)
