# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import traceback
import time
import datetime
import logging
#import threading

import cherrypy
import cherrypy.process as process

import appplatform.startutil as startutil
import icorstartinit

import icordbmain
import appplatform.storageutil as storageutil

import icorapi

import icorlib.icorinterface as ICORInterface

UID = 0


class ICOR2:

    def __init__(self):
        self.testcnt = 0
        self.stopping = 0

        print 'ReDaemon start'
        self.executorSubPath = '/External/default/main2.py'
        ICORInterface.aICORDBEngine.SysBase.ExecutorMethodCheckProcessing()

        #self.schedulerLock=threading.Lock()
        self.schedulerMonitor = cherrypy.process.plugins.Monitor(cherrypy.engine, self.monitorAction, 0.23)
        self.schedulerMonitor.subscribe()
        self.schedulerMonitor.start()
        self.schedulerCnt = 0

    def monitorAction(self):
        if self.stopping:
            return
        cnt = self.schedulerCnt = self.schedulerCnt + 1
        #print 'monitorAction - start %d'%cnt
        #with self.schedulerLock:
        try:
            lprocesses = startutil.GetActiveExecutorsProcesses([self.executorSubPath, ])
            if len(lprocesses) >= startutil.appconfig.MaxDaemonExecutors:
                return
            maxworkers = startutil.appconfig.MaxDaemonExecutors - len(lprocesses)
            amcount = ICORInterface.aICORDBEngine.SysBase.GetExecutorMethodReadyCount(afirst=1)
            for i in range(min(amcount, maxworkers)):
                try:
                    os.spawnv(os.P_NOWAIT, sys.executable, ['"%s"' % sys.executable, '"' + icorapi.startutil.appconfig.PythonTopDir + self.executorSubPath + '"', '1', ''])
                except:
                    cherrypy.log(msg='SPAWN', context='', severity=logging.DEBUG, traceback=True)
                    #traceback.print_exc()
        except:
            #traceback.print_exc()
            cherrypy.log(msg='MONITOR ERROR', context='', severity=logging.DEBUG, traceback=True)
        #print 'monitorAction - finish %d'%cnt
        return

    @cherrypy.expose
    def isrunning(self):
        return 'ok'

    @cherrypy.expose
    def stop(self):
        self.stopping = 1
        cherrypy.engine.exit()
        return 'stop'


def Main():
    cherrypy.config.update({
       'log.screen':False,
       'log.access_file':startutil.appconfig.ICORBaseDir+'/log/redaemon_access.log',
       'log.error_file':startutil.appconfig.ICORBaseDir+'/log/redaemon_error.log',
       'engine.autoreload.on':False,
       'server.socket_queue_size':12,
       'server.socket_timeout':60,
       'server.shutdown_timeout':3,
       'server.max_request_body_size':0,
       'server.socket_host':'127.0.0.1',
       'server.socket_port':startutil.appconfig.TCP_SERVER_PORT_REDAEMON,
       'server.thread_pool':4,
    }) # yapf: disable
    cherrypy.quickstart(ICOR2(), '/', {'/': {'tools.gzip.on': True}})


if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_Redaemon_Instance', 1)
    if ret:
        Main()
