from setuptools import setup, find_packages


setup(
        include_package_data = True,
        name = 'SNMP Poller',
        version = '0.01',
        author = 'Codey Oxley',
        author_email = 'codey.oxley@citynet.net',
        package_dir = {'': 'src',},
        packages = find_packages('src'),
        install_requires = ['nose', 'snimpy >=0.8.3', 'configobj >=4.7.1',],
        scripts = ['snmp-poller.py'],
        setup_requires = ['setuptools_git >=0.3'],
        description = '''Daemon for polling SNMP''',
        )

