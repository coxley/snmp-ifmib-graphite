
Description
===========

Will poll interface octets for devices listed in config file and send
time series to a carbon server serialized as pickle object.

For preserving forward slashes and sending in plain-text carbon, see branch
`carbon-no-pickle`__. Modified for purpose of sending to influxdb via carbon
but will work with any carbon server seeing that storage backend supports 
forward slashes.

__ https://github.com/coxley/snmp-ifmib-graphite/tree/carbon-no-pickle

Installation
============

Must have pip installed.

`Snimpy`__ is a dependency.

__ https://github.com/vincentbernat/snimpy

Clone directory with git or download and extract master tarball/zip::

    $ python setup.py sdist
    $ pip install https://github.com/coxley/snmp-ifmib-graphite/archive/master.zip


Usage
=====

Will look for configuration at ``/etc/snmp-poller/devices.conf`` by default.
To modify, edit ``config_file`` variable in ``src/snmppoll.py`` before
building.

Follow the configuration example provided. Section and sub-section names 
are completely arbritary, but help maintain structure for managing and 
removing nodes. Do note, however, that a primary section named ``CARBON`` must 
exist and contain the ``SERVER`` and ``PORT`` values desired for metrics to
be sent to.

If ``INTERFACES`` is not defined for a device, by default it will poll all 
interfaces that report as operationally up.

The ``METRIC_PATH`` attribute will be appended with ifDescr and rx/tx.
Interface names will be lowercased and ``/`` subbed with ``_``. This is due to 
a limitation of whisper storing metrics as file system paths. Branch 
`carbon-no-pickle`__ keeps ``/`` intact due to primary intent to push to
influxdb in carbon format.

If you use a path of::
    
    core.hq.switches.test-sw

it will end up having timeseries of::

    core.hq.switches.test-sw.gigabitethernet7_25.rx
    core.hq.switches.test-sw.gigabitethernet7_25.tx



After installation, simply call ``snmp-poller.py start`` to start the daemon.
Logs will automatically rotate up to 5 versions and be stored in 
``~/.snmp-poller/snmp-poller.log``.

