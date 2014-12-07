#!/usr/bin/env python2.7

import os
import sys

dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, dir)

import time
from SNMPPoll.daemon import Daemon
from SNMPPoll import logger
from SNMPPoll import snmppoll

log = logger.logger


class SNMPDaemon(Daemon):
    def run(self):
        while True:
            log.info('--- Polling devices ---')
            try:
                snmppoll.run()
            except:
                log.critical('Unexpected error:', sys.exc_info()[0])
            log.info('--- Finished polling ---')
            time.sleep(30)

if __name__ == "__main__":
    daemon = SNMPDaemon('/tmp/snmp-poller.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            log.warning('WARNING -Starting daemon.')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            log.warning('WARNING - Stopping daemon')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            log.warning('WARNING - Restarting daemon.')
            daemon.restart()
        elif 'debug' == sys.argv[1]:
            log.warning('WARNING - Running single debug run')
            snmppoll.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
