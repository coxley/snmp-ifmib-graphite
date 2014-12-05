import time
import socket
import struct
import pickle
from snimpy.manager import Manager
from snimpy.manager import load
from configobj import ConfigObj
import SNMPPoll.logger

TIMESTAMP = time.time()
CONFIG_PATH = '/etc/snmp-poller/devices.conf'

log = SNMPPoll.logger.logger


def get_config(path):
    '''Return dict created from ConfigObj
    :param path: path to config file
    :param type: str
    '''
    return ConfigObj(path)


def poll_device(ip, snmp_community, snmp_version, path):
    '''Using SNMP, polls single device for ifMIB returning tuple for graphite.
    :param ip: ip of the device
    :type ip: str
    :param snmp_community: SNMP community that allows ifMIB values to be read
    :type snmp_community: str
    :param snmp_version: version of SNMP device supports
    :type snmp_version: int
    :param path: desired graphite path for device
    :type path: str
    '''
    null_ifs = [
        'Null0',
        'NVI0',
        ]
    pickle_tuples = []
    if snmp_version == 2:
        load('SNMPv2-MIB')
        load('IF-MIB')
        m = Manager(host=ip, community=snmp_community, version=snmp_version)
    else:
        log.warning('SNMP: Version not supported for host: %s', ip)
        return False
    for iface in m.ifIndex:
        if str(m.ifAdminStatus[iface]) == 'up(1)' and \
                str(m.ifDescr[iface]) not in null_ifs:
            interface = m.ifDescr[iface]
            path_out = '%s.%s.octets_out' % (path, interface)
            path_in = '%s.%s.octets_in' % (path, interface)
            out_octets = int(m.ifHCOutOctets[iface])
            in_octets = int(m.ifHCInOctets[iface])
            log.debug('%s: out_octets: %s, in_octets: %s',
                      m.ifDescr[iface], out_octets, in_octets)
            pickle_tuples.append((path_out, (TIMESTAMP, out_octets)))
            pickle_tuples.append((path_in, (TIMESTAMP, in_octets)))
    return pickle_tuples


def pickle_all(config=get_config(CONFIG_PATH)):
    '''Creates pickle for each device configured and calls send_pickle()
    :param config: configuration options for devices
    :param type: dict
    '''
    SERVER = (config['PICKLE']['SERVER'], int(config['PICKLE']['PORT']))
    for section in config:
        if section != 'PICKLE':
            for subsection in config[section]:
                sub = config[section][subsection]
                path = sub['GRAPHITE_PATH']
                ip = sub['IP']
                snmp_community = sub['SNMP_COMMUNITY']
                snmp_version = int(sub['SNMP_VERSION'])
                log.info('Beginning poll of device: %s', ip)
                pickles = poll_device(ip, snmp_community, snmp_version, path)
                log.info('Finished polling device: %s', ip)
                send_pickle(SERVER, pickles)
    return True


def send_pickle(server, pre_pickle):
    '''Open socket and send pickle as packet.
    :param server: server and port to connect to
    :type server: tuple with server as str and port as int
    :param pre_pickle: message to send as payload
    :type pre_pickle: any type to be pickled
    '''

    payload = pickle.dumps(pre_pickle, protocol=2)
    header = struct.pack('!L', len(payload))
    message = header + payload

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.debug('Connecting to %s:%d' % server)
    sock.connect(server)
    try:
        message = ''
        log.debug('Beginning data xfer to %s:%d' % server)
        sock.sendall(message)

        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            log.debug('Received %d bytes', len(data))
    finally:
        log.debug('Xfer completed. Closing socket on %s:%d' % server)


def run():
    '''Initiate the process.
    :params: none
    '''
    return pickle_all()
