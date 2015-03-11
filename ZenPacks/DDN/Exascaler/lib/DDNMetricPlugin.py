import logging
from twisted.internet.defer import maybeDeferred, Deferred, DeferredList

from ZenPacks.DDN.Exascaler.lib import DDNNetworkLib
from Products.ZenEvents import ZenEventClasses
from Products.ZenUtils.Executor import TwistedExecutor
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin


log = logging.getLogger('zen.zenpymetrics')

class DDNMetricPlugin(PythonDataSourcePlugin):
    """
    Base plugin framework for all DDN products/solutions
    Collects metrics for each device in MDS nodes and OSS nodes
    """

    proxy_attributes = (
        'zCommandUsername',
        'zCommandPassword',
        'zKeyPath',
        'zSshConcurrentSessions',
        'zCommandPort',
        'zCommandCommandTimeout',
        'zCommandLoginTimeout',
        'fs_list',
        'zESMdsNodes',
        'zESOssNodes',
    )

    def __init__(self):
        self.config = None  # pass configuration or device
        self.relname = None
        self.modname = None
        self._config_key = None  # tuple generated through config_key()
        self._config_params = {}  # dict prepared through param
        self.conn_params = {}  # connection options
        self._connection = None  # valid connection
        self.cmd = []  # list of cmds to run over the connection
        self._internal_defer = None  # internal defer chain
        self._task_defer = None  # external defer chain
        self._executor = None  # a framework to run deferred lists
        self.err_connFailed = False  # connection Failed flag

    # called when collect() method gets called.
    def initConnectionParams(self, config):
        self.config = config
        ds = config.datasources[0]

        self._config_key = ds.config_key
        self._config_params = ds.params
        self.conn_params = {
            'user': ds.zCommandUsername,
            'pass': ds.zCommandPassword,
            'target': ds.params['target'],  # Target
            'port': ds.zCommandPort,
            'keypath': ds.zKeyPath,
            'consess': ds.zSshConcurrentSessions,
            'logintimeout': ds.zCommandLoginTimeout,
            'cmdtimeout': ds.zCommandCommandTimeout,
            'fsList': ds.fs_list,
        }


    @classmethod
    def config_key(cls, datasource, context):
        """
        Return a tuple defining collection uniqueness.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.
 
        This example implementation is the default. Split configurations by
        device, cycle time, template id, datasource id and the Python data
        source's plugin class name.
 
        You can omit this method from your implementation entirely if this
        default uniqueness behavior fits your needs. In many cases it will.
        """
        log.info("XXXX config_key(cls=%r, datasource=%r, context=%r"
                 % (cls, datasource, context))
        log.info("XXXX context: %r,Id:%s,title:%s" % (context, context.id,
                                                      context.title))
        return (
            context.id,  # component id
            datasource.getCycleTime(context),
            datasource.plugin_classname)

    @classmethod
    def params(cls, datasource, context):
        """
        Return params dictionary needed for this plugin.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.
 
        This example implementation will provide no extra information for
        each data source to the collect method.
 
        You can omit this method from your implementation if you don't require
        any additional information on each of the datasources of the config
        parameter to the collect method below. If you only need extra
        information at the device level it is easier to just use
        proxy_attributes as mentioned above.
        """
        raise NotImplementedError

    def _addDatasource(self, cmd):
        """
        Add a new instantiation of ProcessRunner or SshRunner
        for every datasource.
        """
        runner = DDNNetworkLib.SshRunner(self._connection)
        d = runner.start(cmd)
        d.addBoth(cmd.processCompleted)
        return d

    def _parseResults(self, resultList):
        aggregate = {}
        errmsgs = {}
        for success, result in resultList:
            log.debug("XXXX _parseResults (success/ds %s) %s", success, result)
            if success:
                aggregate.update(result.result)
            else:
                errmsgs.update(result.result)
        if errmsgs:  # empty dictionary evaluate to False
            aggregate['errors'] = errmsgs
        d, self._task_defer = self._task_defer, None
        if d is not None and not d.called:
            d.callback(aggregate)
        return resultList

    def _fetchPerf(self, connection):
        """ Run all command in parallel through a connection """
        # Bundle up the list of tasks
        log.debug("XXXX _fetchPerf called on connection %r", connection)
        deferredCmds = []
        for c in self.cmd:
            task = self._executor.submit(self._addDatasource, c)
            deferredCmds.append(task)
        # Return a deferred List
        dl = DeferredList(deferredCmds, consumeErrors=True)
        return dl

    def _connect(self):
        """
        create a connection to object the remote device.
        Make a new SSH connection object if there isn't one available.  
        This doesn't actually connect to the device.
        """
        conn_params = self.conn_params
        log.debug("XXXX _connect instance %r, param %s",
                  self, str(conn_params))

        options = DDNNetworkLib.SshOptions(conn_params['user'],  # user
                       conn_params['pass'],  # pass
                       conn_params['logintimeout'], # logincmdtimeout
                       conn_params['cmdtimeout'], # cmdcmdtimeout
                       conn_params['keypath'],  # keypath
                       conn_params['consess'])  # concurrent session

        connection = DDNNetworkLib.MySshClient(conn_params['target'],  # target
                               conn_params['target'], # targetIp
                               conn_params['port'],  # port
                               options=options)

        # connection.sendEvent = zope.component.queryUtility(IEventService)
        d = connection.run()
        return d

    def connectCallback(self, connection):
        """
        Callback called after a successful connect to the remote device.
        """
        log.debug("XXX _connectCallback with connection %r", connection)
        self._connection = connection  # objects of DDNNetworkLib.MySshClient
        self._connection._taskList.add(self)  # all tasks run over a conn
        # creating a new internal deferred list for all tasks
        dl = self._internal_defer = self._fetchPerf(connection)
        dl.addCallback(self._parseResults)
        # return connections for the ssh defered callback chain
        return connection

    def connectionFailed(self, msg):
        """
        Metric collection failed no other fallback option.
        """
        log.debug("XXXX connectionFailed called for connection %r", msg)
        # invoke the errBack chain because connection has failed.
        self.err_connFailed = True
        if self._task_defer is not None:
            self._task_defer.errback(msg)
        return msg

    def collect(self, config):
        self.initConnectionParams(config)
        self.prepTask(config)
        return self.post_collect(config)

    def post_collect(self, config):
        self._executor = TwistedExecutor(self.conn_params['consess'])
        d = maybeDeferred(self._connect)
        d.addCallbacks(self.connectCallback, self.connectionFailed)
        # do not return internal connection handling deferred, but global
        # tasks deferred.
        self._task_defer = Deferred()
        return self._task_defer

    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
 
        You should return a data structure with zero or more events, values
        and maps.
        """
        log.debug("XXXX onSuccess(self=%r, result=%r, config=%r)",
                  self, result, config)
        return {'events': [{}], 'maps': [], 'values': result}

    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """
        log.debug("XXXX onError(self=%r, result=%r, config=%r)",
                  self, result.getErrorMessage(), config)
        aggregate = self.new_data()
        aggregate['events'] = [{
                                   'component': '',
                                   'summary':
                                       'Generic failure %s' % str(
                                           self.conn_params),
                                   'eventClass': 'Perf',
                                   'eventKey': 'ExascalerPerf',
                                   'severity': ZenEventClasses.Error,
                                   'device': config.id
                               }]

        return aggregate

    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        self.cmd = []  # oncomplete: Clear the commands list bcoz it leads
        # error while we run zenpython in background
        return result

    def cleanup(self, config):
        """
        Called when collector exits, or task is deleted or changed.
        """
        # log.debug("XXXX cleanup(self=%r, config=%r)", self, config)
        # return

    def prepTask(self, config):
        """
         This has to be defined in subclass.
        """
        raise NotImplementedError()
