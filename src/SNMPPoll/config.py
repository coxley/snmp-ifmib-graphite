import os
import glob
import yaml
from SNMPPoll import logger


log = logger.logger

def get_config(path):
    '''Return dict of primary .conf merged with $path/conf.d/*.yml
    :param path: path to parent config directory
    :type path: str
    :example path: /etc/snmp-poller
    '''
    config_file = os.path.join(path, 'snmp-poller.yml')
    with open(config_file) as f:
        config_yml = yaml.load(f)
    log.debug('DEBUG: Master configuration loaded')
    config_yml.update(config_inclusion(path))
    log.debug('DEBUG: All configuration files merged.')
    return config_yml


def config_inclusion(parent_dir):
    '''Return merged dict of all config files under $PARENT/conf.d
    :param parent_dir: The parent dir of where conf.d resides.
    :type parent_dir: str
    :example parent_dir: /etc/snmp-poller
    '''
    include = os.path.join('{}'.format(parent_dir), 'conf.d/*.yml')
    configuration = dict()
    for cfg in glob.iglob(include):
        with open(cfg) as f:
            yml = yaml.load(f)
            configuration.update(yml)
        log.debug('DEBUG: Configuration file (%s) loaded.', cfg)
    return configuration
