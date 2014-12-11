from setuptools import setup, find_packages


setup(
        include_package_data = True,
        name = 'snmp-ifmib-graphite',
        version = '0.45',
        author = 'Codey Oxley',
        author_email = 'codey@cwv.net',
        package_dir = {'': 'src',},
        packages = find_packages('src'),
        install_requires = ['nose', 'snimpy >=0.8.3', 'pyyaml',],
        scripts = ['snmp-poller.py'],
        setup_requires = ['setuptools_git >=0.3'],
        description = '''Configurable SNMP poller for ifMIB data.
Will run as daemon and output to Graphite via Carbon.''',
        )

