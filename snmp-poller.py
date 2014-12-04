#!/usr/bin/env python2.7

import os
import sys

dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, dir)

import time
import logging
from daemon import Daemon
import snmppoll

logging.basicConfig(filename='log/snmp-poller.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')


class SNMPDaemon(Daemon):
    def run(self):
        while True:
            logging.info('--- Polling devices ---')
            snmppoll.run()
            logging.info('--- Finished polling ---')
            time.sleep(5)

if __name__ == "__main__":
    daemon = SNMPDaemon('/tmp/snmp-poller.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            logging.warning('WARNING -Starting daemon.')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            logging.warning('WARNING - Stopping daemon')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            logging.warning('WARNING - Restarting daemon.')
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
