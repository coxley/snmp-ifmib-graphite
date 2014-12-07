import time
import socket
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
    :param interfaces: ifDescr of interfaces to poll.
    :type interfaces: list of strings or single str 'all'.
    '''
    TIMESTAMP = int(time.time())
    NULL_IFS = [
        'Null0',
        'NVI0',
        ]
    CARBON_STRINGS = []

    if snmp_version == 2:
        load('SNMPv2-MIB')
        load('IF-MIB')
        m = Manager(host=ip, community=snmp_community, version=snmp_version)
    else:
        log.critical('SNMP: Version not supported for host: %s', ip)
        return False
    try:
        str(m.sysDescr)
    except SNMPException:
        log.critical('SNMP: Cannot poll host: %s - Is it restricted?', ip)
        return False
    if interfaces == 'all':
        log.info('Polling for interfaces: %s', interfaces)
        for iface in m.ifIndex:
            if str(m.ifAdminStatus[iface]) == 'up(1)' and \
                    str(m.ifDescr[iface]) not in NULL_IFS:
                iface_name = str(m.ifDescr[iface]).lower()
                path_out = '%s.%s.tx' % (path, iface_name)
                path_in = '%s.%s.rx' % (path, iface_name)
                octets_out = int(m.ifHCOutOctets[iface])
                octets_in = int(m.ifHCInOctets[iface])
                timeseries_out = '%s %s %s' % (path_out, octets_out, TIMESTAMP)
                timeseries_in = '%s %s %s' % (path_in, octets_in, TIMESTAMP)
                CARBON_STRINGS.extend([timeseries_out, timeseries_in])
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
                iface_name = iface.lower()
                path_out = '%s.%s.tx' % (path, iface_name)
                path_in = '%s.%s.rx' % (path, iface_name)
                octets_out = int(m.ifHCOutOctets[index])
                octets_in = int(m.ifHCInOctets[index])
                timeseries_out = '%s %s %s' % (path_out, octets_out, TIMESTAMP)
                timeseries_in = '%s %s %s' % (path_in, octets_in, TIMESTAMP)
                CARBON_STRINGS.extend([timeseries_out, timeseries_in])
    return CARBON_STRINGS


def carbon_all(config=get_config(CONFIG_PATH)):
    '''Creates carbon for each device configured and calls send_carbon()
    :param config: configuration options for devices
    :param type: dict
    '''
    SERVER = (config['CARBON']['SERVER'], int(config['CARBON']['PORT']))
    for section in config:
        if section not in ['CARBON', 'LOGGING']:
            for subsection in config[section]:
                sub = config[section][subsection]
                path = sub['METRIC_PATH']
                ip = sub['IP']
                snmp_community = sub['SNMP_COMMUNITY']
                snmp_version = int(sub['SNMP_VERSION'])
                interfaces = sub.get('INTERFACES', 'all')
                log.info('Beginning poll of device: %s', ip)
                carbon_data = poll_device(
                    ip, snmp_community,
                    snmp_version, path, interfaces)
                if carbon_data is False:
                    continue
                log.info('Finished polling device: %s', ip)
                log.debug('Timeseries are: \n%s' % '\n'.join(carbon_data))
                send_carbon(SERVER, carbon_data)
    return True


def send_carbon(server, timeseries):
    '''Open socket and send carbon as packet.
    :param server: server and port to connect to
    :type server: tuple with server as str and port as int
    :param timeseries: list of timeseries to send
    :type timeseries: list of str
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.info('Connecting to %s:%d' % server)
    try:
        sock.connect(server)
    except socket.error:
        log.critical("CRITICAL: Couldn't connect to %s.",  server)

    payload = '\n'.join(timeseries)
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
    return carbon_all()
