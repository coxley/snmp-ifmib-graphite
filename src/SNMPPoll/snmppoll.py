import time
import socket
import struct
import pickle
from snimpy.manager import Manager
from snimpy.manager import load
from configobj import ConfigObj
import SNMPPoll.logger

CONFIG_PATH = '/etc/snmp-poller/devices.conf'

log = SNMPPoll.logger.logger


def get_config(path):
    '''Return dict created from ConfigObj
    :param path: path to config file
    :param type: str
    '''
    return ConfigObj(path)


def poll_device(ip, snmp_community, snmp_version, path, interfaces='all'):
    '''Using SNMP, polls single device for ifMIB returning tuple for graphite.
    :param ip: ip of the device
    :type ip: str
    :param snmp_community: SNMP community that allows ifMIB values to be read
    :type snmp_community: str
    :param snmp_version: version of SNMP device supports
    :type snmp_version: int
    :param path: desired graphite path for device
    :type path: str
    :param interfaces: ifDescr of interfaces to poll.
    :type interfaces: list of strings or single str 'all'.
    '''
    TIMESTAMP = int(time.time())
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
        log.critical('SNMP: Version not supported for host: %s', ip)
        return False
    if interfaces == 'all':
        log.info('Polling for interfaces: %s', interfaces)
        for iface in m.ifIndex:
            if str(m.ifAdminStatus[iface]) == 'up(1)' and \
                    str(m.ifDescr[iface]) not in null_ifs:
                iface_name = str(m.ifDescr[iface]).replace('/', '_')
                path_out = '%s.%s.octets_out' % (path, iface_name)
                path_in = '%s.%s.octets_in' % (path, iface_name)
                out_octets = int(m.ifHCOutOctets[iface])
                in_octets = int(m.ifHCInOctets[iface])
                log.debug('%s: out_octets: %s, in_octets: %s',
                          iface_name, out_octets, in_octets)
                pickle_tuples.append((path_out, (TIMESTAMP, out_octets)))
                pickle_tuples.append((path_in, (TIMESTAMP, in_octets)))
    else:
        if isinstance(interfaces, basestring):
            interface_tmp = interfaces
            interfaces = []
            interfaces.append(interface_tmp)
        elif isinstance(interfaces, list):
            log.info('Polling for interfaces: %s', ', '.join(interfaces))
            if_indexes = \
                {v: k for k, v in m.ifDescr.iteritems() if v in interfaces}
            for iface, index in if_indexes.iteritems():
                iface_name = iface.replace('/', '_')
                path_out = '%s.%s.octets_out' % (path, iface_name)
                path_in = '%s.%s.octets_in' % (path, iface_name)
                out_octets = int(m.ifHCOutOctets[index])
                in_octets = int(m.ifHCInOctets[index])
                log.debug('%s: out_octets: %s, in_octets: %s',
                          iface_name, out_octets, in_octets)
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
                try:
                    interfaces = sub['INTERFACES']
                    log.info('Beginning poll of device: %s', ip)
                    pickles = poll_device(ip, snmp_community, snmp_version,
                                          path, interfaces)
                except KeyError:
                    log.info('Beginning poll of device: %s', ip)
                    pickles = poll_device(ip, snmp_community, snmp_version,
                                          path)
                finally:
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.info('Connecting to %s:%d' % server)
    try:
        sock.connect(server)
    except socket.error:
        log.critical("CRITICAL: Couldn't connect to %s." % server)

    payload = pickle.dumps(pre_pickle, protocol=2)
    header = struct.pack('!L', len(payload))
    message = header + payload

    log.info('Beginning data xfer to %s:%d' % server)
    log.debug('-' * 80)
    log.debug(message)
    log.debug('-' * 80)
    sock.sendall(message)

    log.info('Xfer completed. Closing socket on %s:%d' % server)
    sock.close()


def run():
    '''Initiate the process.
    :params: none
    '''
    return pickle_all()
