import logging
import logging.handlers


format = logging.Formatter('%(asctime)s: %(message)s')
log_file = 'log/snmp-poller.log'
logger = logging.getLogger('snmp-poller')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=500000,
    backupCount=5)
handler.setFormatter(format)

logger.addHandler(handler)
