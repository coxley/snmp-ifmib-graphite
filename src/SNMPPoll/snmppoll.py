import time
import socket
import re
import pickle
from snimpy.snmp import SNMPException
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
    :param interfaces: **ifName** of interfaces to poll. Careful because this
                       value can be different even within the same vendor. 
                       Cisco ASA will return full iface name while IOS abbrev.
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
        try:
            m = Manager(
                host=ip, community=snmp_community, version=snmp_version
                )
        except socket.gaierror, error:
            log.error('SNMP: Error raised for host: %s - %s', ip, error)
    else:
        log.error('SNMP: Version not supported for host: %s', ip)
        return False
    try:
        str(m._sysDescr)
    except SNMPException:
        log.error('SNMP: Cannot poll host: %s - Is it restricted?', ip)
        return False
    if interfaces == 'all':
        log.info('Polling for interfaces: %s', interfaces)
        for iface in m.ifIndex:
            if str(m.ifAdminStatus[iface]) == 'up(1)' and \
                    str(m.ifName[iface]) not in null_ifs:
                iface_name = normalize_ifname(str(m.ifName[iface]).
                                              replace('/', '_'))
                path_out = '%s.%s.tx' % (path, iface_name)
                path_in = '%s.%s.rx' % (path, iface_name)
                octets_out = int(m.ifHCOutOctets[iface])
                octets_in = int(m.ifHCInOctets[iface])
                log.debug('%s: octets_out: %s, octets_in: %s',
                          iface_name, octets_out, octets_in)
                pickle_tuples.append((path_out, (TIMESTAMP, octets_out)))
                pickle_tuples.append((path_in, (TIMESTAMP, octets_in)))
    # Need to combine if statements
    else:
        if isinstance(interfaces, basestring):
            interface_tmp = interfaces
            interfaces = []
            interfaces.append(interface_tmp)
        elif isinstance(interfaces, list):
            log.info('Polling for interfaces: %s', ', '.join(interfaces))
            if_indexes = \
                {v: k for k, v in m.ifName.iteritems() if v in interfaces}
            for iface, index in if_indexes.iteritems():
                iface_name = normalize_ifname(iface.replace('/', '_'))
                path_out = '%s.%s.tx' % (path, iface_name)
                path_in = '%s.%s.rx' % (path, iface_name)
                octets_out = int(m.ifHCOutOctets[index])
                octets_in = int(m.ifHCInOctets[index])
                log.debug('%s: octets_out: %s, octets_in: %s',
                          iface_name, octets_out, octets_in)
                pickle_tuples.append((path_out, (TIMESTAMP, octets_out)))
                pickle_tuples.append((path_in, (TIMESTAMP, octets_in)))
    return pickle_tuples


def normalize_ifname(ifname):
    '''Normalizes interfaces for two letter abbreviation and number appended.
    :param ifname: interface name
    :param type: str
    '''
    m = re.match(r'(?P<name>.*?) *(?P<numbers>[0-9-:./]*$)', ifname)
    numbers = m.group('numbers')
    if not numbers:
        name = m.group('name').lower()
    else:
        name = m.group('name')[0:2].lower()
    return '{}{}'.format(name, numbers)


def pickle_all(config=get_config(CONFIG_PATH)):
    '''Creates pickle for each device configured and calls send_pickle()
    :param config: configuration options for devices
    :param type: dict
    '''
    SERVER = (config['PICKLE']['SERVER'], int(config['PICKLE']['PORT']))
    for section in config:
        if section != ['PICKLE','LOGGING']:
            for subsection in config[section]:
                sub = config[section][subsection]
                path = sub['METRIC_PATH']
                ip = sub['IP']
                snmp_community = sub['SNMP_COMMUNITY']
                snmp_version = int(sub['SNMP_VERSION'])
                interfaces = sub.get('INTERFACES', 'all')
                log.info('Beginning poll of device: %s', ip)
                pickle_data = poll_device(
                    ip, snmp_community,
                    snmp_version, path, interfaces)
                if pickle_data is False:
                    continue
                log.info('Finished polling device: %s', ip)
                log.debug('Timeseries are: \n%s' % '\n'.join(pickle_data))
                send_pickle(SERVER, pickle_data)
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
        log.critical("CRITICAL: Couldn't connect to %s.", server)

    payload = pickle.dumps(pre_pickle, protocol=2)
    message = payload

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
