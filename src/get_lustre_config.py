import os
import json
from ConfigParser import SafeConfigParser
import re

CONF_FILE = "/etc/ddn/exascaler.conf"

try:
    config_file = open(CONF_FILE, 'r')
    config_parser = SafeConfigParser()
    config_parser.readfp(config_file)

    conf = {}

    for sec in config_parser.sections():
        hostname = None
        fsname = None
        nw_addrs = []
        if sec.startswith('host'):
            hostname = re.split('[ _]+', sec, 1)[1]
            if not conf.get('host'):
                conf['host'] = {}
            conf['host'][hostname] = {}
        elif sec.startswith('fs'):
            fsname = sec.split(' ', 1)[1]
            if not conf.get('fs'):
                conf['fs'] = {}
            conf['fs'][fsname] = {}
        else:
            if not conf.get(sec):
                conf[sec] = {}
        for item in config_parser.items(sec):
            k = item[0]
            v = ','.join(item[1:])

            #import pdb; pdb.set_trace()

            if hostname:
                conf['host'][hostname][k] = v
                if '_ip' in k:
                    nw_addrs.append(v)
            elif fsname:
                conf['fs'][fsname][k] = v
            else:
                conf[sec][k] = v
        else:
            if hostname and hostname != 'defaults':
                conf['host'][hostname]['nw_addr'] = ','.join(nw_addrs)

    hostdefaults = conf['host'].get('defaults', None)
    if hostdefaults:
        # A default section for hosts exists
        for host in conf['host'].keys():
            if host == 'defaults':
                continue
            for k, v in hostdefaults.items():
                if not conf['host'][host].get(k, None):
                    # update default attr within host, if non-existant
                    conf['host'][host][k] = v
        conf['host'].pop('defaults')

    print json.dumps(conf, indent=4, sort_keys=True)
except Exception as e:
    #print 'Hit exception %r' % e
    print "{}"
