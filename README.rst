Installation
============

Must have pip installed.

Clone directory with git or download and extract master tarball/zip.::

    $ python setup.py sdist
    $ pip install https://github.com/coxley/snmp-ifmib-graphite/archive/master.zip


Usage
=====

Will look for configuration at ``/etc/snmp-poller/devices.conf`` by default.
To modify, edit ``config_file`` variable in ``src/snmppoll.py`` before
building.

Follow the configuration example provided. Section and sub-section names 
are completely arbritary, but help maintain structure for managing and 
removing nodes. Do note, however, that a primary section named 'PICKLE' must 
exist and contain the ``SERVER`` and ``PORT`` values desired for metrics to
be sent to.

If ``INTERFACES`` is not defined for a device, by default it will poll all 
interfaces that report as operationally up.

The ``PATH`` attribute will be appended with ifDescr and octets_in/octets_out.
Interface names will be lowercased and ``/`` subbed for ``_``. 

Path I'm using is: customers.<group>.<customer>.devices.<device-type>.<device>
and it will end up looking like:
customers.<group>.<customer>.devices.<device-type>.<device>.<interface>.<sub-if>


After installation, simply call ``snmp-poller.py start`` to start the daemon.
Logs will automatically rotate up to 5 versions and be stored in 
``~/.snmp-poller/snmp-poller.log``.
