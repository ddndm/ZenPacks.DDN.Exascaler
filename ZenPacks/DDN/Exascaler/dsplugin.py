import logging

from ZenPacks.DDN.Exascaler.lib import DDNRunCmd as esc
from ZenPacks.DDN.Exascaler.lib.DDNMetricPlugin import DDNMetricPlugin
from Products.ZenEvents import ZenEventClasses
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

log = logging.getLogger('zen.zenpymetrics')


class MdsPlugin(DDNMetricPlugin):
    """Explanation of what MyPlugin does for Ost component."""

    # List of device attributes you'll need to do collection.
    @classmethod
    def params(cls, datasource, context):
        log.debug("XXXX Mds Plugin params(cls=%r, datasource=%r, context=%r"
                  % (cls, datasource, context))
        return {'target': context.management_address}

    def __init__(self):
        super(MdsPlugin, self).__init__()
        self.relname = 'metaDataServers'
        self.modname = 'ZenPacks.DDN.Exascaler.MetaDataServer'

    def prepTask(self, config):
        log.info("Collecting Metrics for Device __class__ : %s ",
                 self.__class__.__name__)
        cmds = [{
                    'cmd': '/cm/shared/ddn/dm/exascaler/exascalermetrics.py',
                    'parser': self.parseMdtResults,
                    'filter': 'basic',
                }, {
                    'cmd': '/cm/shared/ddn/dm/exascaler/esHealthCheck.py',
                    'parser': self.parseStatus,
                    'filter': 'state',
                }]

        for c in cmds:
            self.cmd.append(esc.Cmd(command=c['cmd'], template=c['filter'],
                                    config=self.config, parser=c['parser']))
        log.debug('XXX _prepMdsCommand(): self.cmd = %r', self.cmd)


    def parseMdtResults(self, results, notused):
        """ parse the results for each datasource part of config """
        rlines = results.split('\n')
        rkeys = []
        try:
            for line in (rlines):
                words = line.split(' ')
                if len(words) == 3:
                    if 'MDT' not in words[1]:
                        if self.conn_params['fsList'] in words[1]:
                            rkeys.append(words[1:])
        except Exception as e:
            log.error('XXX parse Mds Results-Result comprehension failed %s',
                      str(e))
            rkeys = []

        aggregate = {}
        for ds in self.config.datasources:
            # the below template is available as part of ds.points.id
            component = component_key = ds.component
            if not component:
                component_key = 'MDT'
                log.debug('XXXX MDS [Device] key is: None, ds.component %s',
                          component_key)
            else:
                log.debug('XXXX MDS [Component] key is: %s, ds.component %s',
                          ds.component, component_key)

            dsresult = {}
            for point in ds.points:
                key = point.dpName  # mdt_counters_MetaOps
                ident = point.id  # MetaOps
                log.debug("MSD Key = %s ident = %s " % (key, ident))
                keystr = (component_key + '_' + ident).replace('-', '_')
                val = 0  # extract this value from results!
                try:
                    for word in rkeys:
                        if ident in word[0]:
                            val = word[1]
                            break
                except Exception as e:
                    log.debug('XXXX mds key %s lookup error - %s',
                              keystr, str(e))
                dsresult[key] = val
            aggregate[component] = dsresult
        log.debug('XXX result=%s', (str(aggregate)))
        return aggregate

    def parseStatus(self, results, notused):
        rlines = results.split('\n')
        status = 'null'
        try:
            for line in (rlines):
                words = line.split(' ')
                if len(words[0]) > 1:
                    status = words[0]
        except Exception as e:
            log.error('XXX parse Mds Results-Result comprehension failed %s',
                      str(e))
        return {'status': status}

    def onSuccess(self, result, config):
        log.info("Successfully Collected Metrics for Device __class__ : %s ",
                 self.__class__.__name__)
        log.debug('XXXX mds onSuccess: values is %s', str(result))
        status = result.get('status', 'null')
        if status != 'null':
            del result['status']
        compmap = []
        for ds in self.config.datasources:
            # for each discovered component, update the
            # model for PreferredAddress
            if ds.component:
                compmap.append(
                    ObjectMap({'id': ds.component, 'status': status}))

        maps = [RelationshipMap(relname=self.relname,
                                modname=self.modname,
                                objmaps=compmap)]

        aggregate = self.new_data()
        # Events
        alert = {}
        events = []
        if status != 'PASS' and status != '':
            alert['eventKey'] = ds.component
            alert['severity'] = ZenEventClasses.Warning
            alert[
                'summary'] = "Device Status is Not PASS Actual Status is %s" \
                             % status
            alert['component'] = ds.component
            alert['eventClass'] = '/Perf'
            events.append(alert)
            aggregate['events'] = events

        aggregate['values'] = result
        aggregate['maps'] = maps
        return aggregate

    def onError(self, result, config):
        log.error("Failed to Collect Metrics for Device __class__ : %s ",
                  self.__class__.__name__)
        log.error("XXXX mds onError(self=%r, result=%r, config=%r)",
                  self, result.getErrorMessage(), config)
        aggregate = self.new_data()
        aggregate['events'] = [{
                                   'component': 'Mdt',
                                   'device': config.id,
                                   'summary':
                                       'error connection failed %s'
                                       % str(self.conn_params),
                                   'eventClass': '/Perf',
                                   'eventKey': 'ExascalerPerf',
                                   'severity': ZenEventClasses.Error,
                               }]
        aggregate['maps'] = self.updateModel()

        return aggregate


class OssPlugin(DDNMetricPlugin):
    """Explanation of what MyPlugin does for Ost component."""

    # List of device attributes you'll need to do collection.
    @classmethod
    def params(cls, datasource, context):
        log.debug("XXXX OssPlugin params(cls=%r, datasource=%r, context=%r"
                  % (cls, datasource, context))
        return {'target': context.management_address}

    def __init__(self):
        super(OssPlugin, self).__init__()
        self.relname = 'objectStorageServers'
        self.modname = 'ZenPacks.DDN.Exascaler.ObjectStorageServer'

    def prepTask(self, config):
        log.info("Collecting Metrics for Device __class__ : %s ",
                 self.__class__.__name__)
        cmds = [{
                    'cmd': '/cm/shared/ddn/dm/exascaler/exascalermetrics.py',
                    'parser': self.parseOssResults,
                    'filter': 'basic',
                }, {
                    'cmd': '/cm/shared/ddn/dm/exascaler/esHealthCheck.py',
                    'parser': self.parseStatus,
                    'filter': 'state',
                }]

        for c in cmds:
            self.cmd.append(esc.Cmd(command=c['cmd'], template=c['filter'],
                                    config=self.config, parser=c['parser']))
        log.debug('XXX _prepOssCommand(): self.cmd = %r', self.cmd)

    def parseOssResults(self, results, notused):
        """ parse the results for each datasource part of config """
        rlines = results.split('\n')
        rkeys = []
        try:
            for line in (rlines):
                words = line.split(' ')
                if len(words) == 3:
                    if 'OST' not in words[1]:
                        if self.conn_params['fsList'] in words[1]:
                            rkeys.append(words[1:])
        except Exception as e:
            log.error('XXX parseOssResults-Result comprehension failed %s',
                      str(e))
            rkeys = []

        aggregate = {}
        for ds in self.config.datasources:
            # the below template is available as part of ds.points.id
            component = component_key = ds.component
            if not component:
                component_key = 'MDT'
                log.debug('XXXX Oss [Device] key is: None, ds.component %s',
                          component_key)
            else:
                log.debug('XXXX Oss [Component] key is: %s, ds.component %s',
                          ds.component, component_key)

            dsresult = {}
            for point in ds.points:
                key = point.dpName  # mdt_counters_MetaOps
                ident = point.id  # MetaOps
                log.debug("Oss Key = %s ident = %s " % (key, ident))
                keystr = (component_key + '_' + ident).replace('-', '_')
                val = 0  # extract this value from results!
                try:
                    for word in rkeys:
                        if ident in word[0]:
                            val = word[1]
                            break
                except Exception as e:
                    log.debug('XXXX Oss ds key %s lookup error - %s',
                              keystr, str(e))
                dsresult[key] = val
            aggregate[component] = dsresult
        log.debug('XXX Oss result=%s', (str(aggregate)))
        return aggregate


    def parseStatus(self, results, notused):
        rlines = results.split('\n')
        status = 'null'
        try:
            for line in (rlines):
                words = line.split(' ')
                if len(words[0]) > 1:
                    status = words[0]
        except Exception as e:
            log.error('XXX parseOssResults-Result comprehension failed %s',
                      str(e))
        return {'status': status}


    def onSuccess(self, result, config):
        log.info("Successfully Collected Metrics for Device __class__ : %s ",
                 self.__class__.__name__)
        log.debug('XXXX Oss onSuccess: values is %s', str(result))
        status = result.get('status', 'null')
        if status != 'null':
            del result['status']
        compmap = []
        for ds in self.config.datasources:
            # for each discovered component, update the
            # model for PreferredAddress
            if ds.component:
                compmap.append(
                    ObjectMap({'id': ds.component, 'status': status}))

        maps = [RelationshipMap(relname=self.relname,
                                modname=self.modname,
                                objmaps=compmap)]
        aggregate = self.new_data()
        # Events
        alert = {}
        events = []
        if status != 'PASS' and status != '':
            alert['eventKey'] = ds.component
            alert['severity'] = ZenEventClasses.Warning
            alert[
                'summary'] = "Device Status is Not PASS Actual Status is %s" \
                             % status
            alert['component'] = ds.component
            alert['eventClass'] = '/Perf'
            events.append(alert)
            aggregate['events'] = events

        aggregate['values'] = result
        aggregate['maps'] = maps
        return aggregate

    def onError(self, result, config):
        log.error("Failed to Collect Metrics for Device __class__ : %s ",
                  self.__class__.__name__)
        log.error("XXXX Oss onError(self=%r, result=%r, config=%r)",
                  self, result.getErrorMessage(), config)
        aggregate = self.new_data()
        aggregate['events'] = [{
                                   'component': 'Osp',
                                   'summary':
                                       'error connection failed %s'
                                       % str(self.conn_params),
                                   'eventClass': '/Perf',
                                   'eventKey': 'ExascalerPerf',
                                   'severity': ZenEventClasses.Error,
                                   'device': config.id
                               }]
        aggregate['maps'] = self.updateModel()
        return aggregate
