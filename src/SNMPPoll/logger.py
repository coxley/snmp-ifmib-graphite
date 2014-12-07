import os
import logging
import logging.handlers
from configobj import ConfigObj


try:
    LOG_PATH = ConfigObj('/etc/snmp-poller/devices.conf')['LOGGING']['PATH']
except KeyError:
    LOG_PATH = '~/.snmp-poller'

format = logging.Formatter('%(asctime)s: %(message)s')
log_file = os.path.join(os.path.expanduser(LOG_PATH), 'snmp-poller.log')
logger = logging.getLogger('snmp-poller')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=500000,
    backupCount=5)
handler.setFormatter(format)

logger.addHandler(handler)
