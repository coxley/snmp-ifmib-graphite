
Description
===========

Will poll interface octets for devices listed in config file and send time 
series to carbon server in plain-text format. Intended for builds where 
storage backend is not whisper or any other that stores metrics as filesystem
paths. This is only because forward slashes are preserved in the metric name.

Installation
============

Must have pip installed.

`Snimpy`__ is a dependency.

__ https://github.com/vincentbernat/snimpy

Use pip to install directly from git::

    $ python setup.py sdist
    $ pip install https://github.com/coxley/snmp-ifmib-graphite/archive/master.zip


Usage
=====

Will look for configuration at ``/etc/snmp-poller/snmp-poller.yml`` by default.
To modify, edit ``config_file`` variable in ``src/snmppoll.py`` before
building.

Follow the configuration example provided. Section and sub-section names 
are completely arbritary, but help maintain structure for managing and 
removing nodes. Do note, however, that a primary section named ``carbon`` must 
exist and contain the ``server`` and ``port`` values desired for metrics to
be sent to.

If ``ifaces`` is not defined for a device, by default it will poll all 
interfaces that report as operationally up.

The ``metric_path`` attribute will be appended with ifDescr and rx/tx.
Interface names will be lowercased.

If you use a path of::
    
    core.hq.switches.test-sw

it will end up having timeseries of::

    core.hq.switches.test-sw.gigabitethernet7/25.rx
    core.hq.switches.test-sw.gigabitethernet7/25.tx

After installation, simply call ``snmp-poller.py start`` to start the daemon.
Logs will automatically rotate up to 5 versions and be stored in 
``~/.snmp-poller/snmp-poller.log``.

Configuration files can be logically separated into a ``$CONFDIR/conf.d``
directory. Extension must end with ``.yml`` and follow same format as
the main config file.

Note
====

Daemon will not contiune running for exceptions unhandled. Any exception thrown
by the main snmp poller should be captured and logged to log file. Do note, 
however, that if you set a log path that doesn't exist and user daemon is 
running as lacks sufficient permissions to create it, OSError will be raised
and currently I'm not handling that.

As long as the path is where the user has permissions to create files/dirs,
it shouldn't matter if it exists yet or not.
