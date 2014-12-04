import time
import logging
from snimpy.manager import Manager
from snimpy.manager import load
from configobj import ConfigObj

timestamp = time.time()


def get_config(path='demos/devices.conf'):
    return ConfigObj(path)


def poll_device(ip, snmp_community, snmp_version, path):
    null_ifs = [
        'Null0',
        'NVI0',
        ]
    pickle_tuples = []
    path_out = path + '.octets_out'
    path_in = path + '.octets_in'
    snmp_version = int(snmp_version)
    if snmp_version == 2:
        load('SNMPv2-MIB')
        load('IF-MIB')
        m = Manager(host=ip, community=snmp_community, version=snmp_version)
    else:
        logging.warning('SNMP: Version not supported for host: %s', ip)
        return False
    for iface in m.ifIndex:
        if str(m.ifAdminStatus[iface]) == 'up(1)' and \
                str(m.ifDescr[iface]) not in null_ifs:
            out_octets = int(m.ifHCOutOctets[iface])
            in_octets = int(m.ifHCInOctets[iface])
            logging.debug('%s: out_octets: %s, in_octets: %s',
                            m.ifDescr[iface], out_octets, in_octets)
            pickle_tuples.append((path_out, (timestamp, out_octets)))
            pickle_tuples.append((path_in, (timestamp, in_octets)))
    return pickle_tuples


def pickle_all(config=get_config()):
    all_pickle = []
    for section in config:
        for subsection in config[section]:
            sub = config[section][subsection]
            path = sub['GRAPHITE_PATH']
            ip = sub['IP']
            snmp_community = sub['SNMP_COMMUNITY']
            snmp_version = sub['SNMP_VERSION']
            logging.info('Beginning poll of device: %s', ip)
            pickles = poll_device(ip, snmp_community, snmp_version, path)
            logging.info('Finished polling device: %s', ip)
            all_pickle.append(pickles)
    return all_pickle


def run():
    pickles = pickle_all()
    return pickles
