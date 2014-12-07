Installation
============

Must have pip installed.

`Snimpy`__ is a dependency.

__ https://github.com/vincentbernat/snimpy

Clone directory with git or download and extract carbon-no-pickle tarball/zip::

    $ python setup.py sdist
    $ pip install https://github.com/coxley/snmp-ifmib-graphite/archive/carbon-no-pickle.zip


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
Interface names will be lowercased.

If you use a path of::
    
    core.hq.switches.test-sw

it will end up having timeseries of::

    core.hq.switches.test-sw.gigabitethernet7/25.rx
    core.hq.switches.test-sw.gigabitethernet7/25.tx

After installation, simply call ``snmp-poller.py start`` to start the daemon.
Logs will automatically rotate up to 5 versions and be stored in 
``~/.snmp-poller/snmp-poller.log``.
