Installation
============

Must have easy_install installed. 

Clone directory with git or download and extract master tarball/zip.::

    $ python setup.py sdist
    $ easy_install dist/snmp-ifmib-graphite-<version>.tar.gz


Usage
=====

Will look for configuration at ``/etc/snmp-poller/devices.conf`` by default.
To modify, edit ``config_file`` variable in ``src/snmppoll.py`` before
building.

Follow the configuration example provided. Section and sub-section names 
are completely arbritary, but help maintain structure for managing and 
removing nodes. 

The ``PATH`` attribute will be appended with ifDescr and octets_in/octets_out
for each interface on the device in the operational up(1) state.

After installation, simply call ``snmp-poller.py start`` to start the daemon.
Logs will automatically rotate up to 5 versions and be stored in 
``~/.snmp-poller/snmp-poller.log``.