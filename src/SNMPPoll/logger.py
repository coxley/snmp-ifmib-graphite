import os
import logging
import logging.handlers
import yaml

try:
    with open('/etc/snmp-poller/snmp-poller.yml') as f:
        LOG_PATH = yaml.load(f)['logging']['path']
except KeyError:
    LOG_PATH = '~/.snmp-poller'

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

format = logging.Formatter('%(asctime)s: %(message)s')
log_file = os.path.join(os.path.expanduser(LOG_PATH), 'snmp-poller.log')
logger = logging.getLogger('snmp-poller')
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=500000,
    backupCount=5)
handler.setFormatter(format)

logger.addHandler(handler)
