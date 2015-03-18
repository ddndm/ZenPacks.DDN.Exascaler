import logging

log = logging.getLogger('zen.zenpymodelMdt')

from ZenPacks.DDN.Exascaler.lib import DDNRunCmd as esc
from ZenPacks.DDN.Exascaler.lib import DDNEsUtil as es
from ZenPacks.DDN.Exascaler.lib.DDNModelPlugin import DDNModelPlugin
from Products.DataCollector.plugins.DataMaps import RelationshipMap


EXMODEL = {None:
               {'modname': 'ZenPacks.DDN.Exascaler.ExascalerDevice',
                'compname': '',
                'relname': ''},
           'fsLists':
               {'modname': 'ZenPacks.DDN.Exascaler.FsList',
                'compname': 'fsLists',
                'relname': 'fsLists'},
           'metaDataServers':
               {'modname': 'ZenPacks.DDN.Exascaler.MetaDataServer',
                'compname': 'metaDataServers',
                'relname': 'metaDataServers'},
           'objectStorageServers':
               {'modname': 'ZenPacks.DDN.Exascaler.ObjectStorageServer',
                'compname': 'objectStorageServers',
                'relname': 'objectStorageServers'},
}

DEVMODEL = EXMODEL[None]


class ModelExaScaler(DDNModelPlugin):
    """
     following components of Exascaler devices and modelled
     Fs Lists
     MetaDataServers
     ObjectStorageServers
     Updates device level attributes also
    """
    relname = 'fsLists'
    modname = 'ZenPacks.DDN.Exascaler.FsList'

    def prepTask(self, device, log):
        self.device = device
        log.debug("%s: preparing MDT devices", device.id)
        cmdinfo = [{
          'cmd': 'python /cm/shared/ddn/dm/exascaler/get_lustre_config.py',
          'parser': es.es_process_esmodel,
          'filter': ''
        }]

        myCmds = []
        for c in cmdinfo:
            myCmds.append(esc.Cmd(command=c['cmd'], template=c['filter'],
                                  config=self.config, parser=c['parser']))
        self.cmd = myCmds
        log.debug('XXX _prepMdtCommand(): self.cmd = %r', self.cmd)

    def parseResults(self, resultList):
        errmsgs = {}
        log.debug("XXX _parseResults with resultList : %r ", resultList)
        res = []
        for success, result in resultList:
            log.debug("XXX __Result STATUS: %s and DATA: %s ", success, result)
            if success:
                if isinstance(result.result, dict):
                    infoData = result.result
                    log.debug("InfoData %s " % infoData)

                    fs_rm = self.get_fslist_rel_maps(infoData)
                    mdt_rm = self.get_mds_rel_maps(infoData)
                    oss_rm = self.get_oss_rel_maps(infoData)

                    res.append(fs_rm)
                    res.append(mdt_rm)
                    res.append(oss_rm)

                    # Update device attributes
                    d_attr = {}
                    devom = self.objectMap()
                    devom.updateFromDict(d_attr)
                    devom.updateFromDict(infoData.get('global'))
                    devom.updateFromDict(infoData.get('HA'))
                    res.append(devom)

                else:
                    log.warn("XXX __Result is Not instance of Dict"
                             "TYPE: %s RESULT: %r", type(result.result),
                             result.result)
            else:
                errmsgs.update(str(result))

        d, self._task_defer = self._task_defer, None
        if d is None or d.called:
            return  # already processed, nothing to do now

        if errmsgs:
            log.warn('XXX GridScalar FsLIST collection failed %s',
                     str(errmsgs))
            d.callback([{}])
            return

        log.debug("XXX Collected GridScalar FsLIST DATA: %r", res)
        d.callback(res)

    def get_fslist_rel_maps(self, es_response):
        rm = []
        fs_dict = es_response.get('fs', {})
        for key, val in fs_dict.items():
            log.debug("XXX KEY: %s and VALUE: %r", key, val)
            if val.get('id') is None:
                val['id'] = str(key)
            if val.get('title') is None:
                val['title'] = str(key)
            # Create Object Map
            om = self.objectMap()
            om.updateFromDict(val)
            # Update Object Map to RelationShip Map
            rm.append(om)

        return RelationshipMap(
            relname=EXMODEL['fsLists']['relname'],
            modname=EXMODEL['fsLists']['modname'],
            objmaps=rm)

    def get_mds_rel_maps(self, es_response):
        mds = getattr(self.device, 'zESMdsNodes', None)
        mdsList = mds.split(",")
        rm = []
        fs_dict = es_response.get('host', {})
        nw_data = self.filter_server(fs_dict, 'mds')
        i = 0
        for key, val in nw_data.items():
            log.debug("XXX KEY: %s and VALUE: %r", key, val)
            if val.get('id') is None:
                val['id'] = str(key)
            if val.get('title') is None:
                val['title'] = str(key)
            try:
                val['management_address'] = mdsList[i]
            except IndexError:
                val['management_address'] = 'null'
            # Create Object Map
            om = self.objectMap()
            om.updateFromDict(val)
            # Update Object Map to RelationShip Map
            rm.append(om)
            i += 1

        return RelationshipMap(
            relname=EXMODEL['metaDataServers']['relname'],
            modname=EXMODEL['metaDataServers']['modname'],
            objmaps=rm)

    def get_oss_rel_maps(self, es_response):
        oss = getattr(self.device, 'zESOssNodes', None)
        ossList = oss.split(",")
        rm = []
        fs_dict = es_response.get('host', {})
        nw_data = self.filter_server(fs_dict, 'oss')
        i = 0
        for key, val in nw_data.items():
            log.debug("XXX KEY: %s and VALUE: %r", key, val)
            if val.get('id') is None:
                val['id'] = str(key)
            if val.get('title') is None:
                val['title'] = str(key)
            try:
                val['management_address'] = ossList[i]
            except IndexError:
                val['management_address'] = 'null'
            # Create Object Map
            om = self.objectMap()
            om.updateFromDict(val)
            # Update Object Map to RelationShip Map
            rm.append(om)
            i += 1

        return RelationshipMap(
            relname=EXMODEL['objectStorageServers']['relname'],
            modname=EXMODEL['objectStorageServers']['modname'],
            objmaps=rm)

    def filter_server(self, data, s_filter='mds'):
        matching = [s for s in data.keys() if s_filter in s]
        server_list = {}
        for i in matching:
            server_list[i] = data[i]
        return server_list

    def process(self, device, results, log):
        """ Process results, return iterable of datamaps or None."""
        log.debug('XXXX modeler process(dev=%r) got results %s',
                  device, str(results))
        return results
