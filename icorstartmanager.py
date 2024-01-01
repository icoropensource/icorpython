import sys
import os
import re
import time
import logging
import urllib
import traceback
import Queue
import threading

import cherrypy
import cherrypy.process as process

import appplatform.startutil as startutil


class ICORStartManager(object):

    def __init__(self, aICORStarter):
        self.aICORStarter = aICORStarter
        self.thread = None
        self.running = False

    def start(self):
        self.running = True
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            #self.thread.setDaemon(True)
            self.thread.start()

    def run(self):
        cherrypy.config.update({
            'log.screen': False,
            'log.access_file': startutil.appconfig.ICORBaseDir + '/log/startmanager_access.log',
            'log.error_file': startutil.appconfig.ICORBaseDir + '/log/startmanager_error.log',
            'engine.autoreload.on': False,
            'server.socket_host': '127.0.0.1',
            'server.socket_port': startutil.appconfig.TCP_SERVER_PORT_STARTMANAGER,
            'server.socket_queue_size': 12,
            'server.socket_timeout': 60,
            'server.shutdown_timeout': 300,
            'server.thread_pool': 8,
            'server.max_request_body_size': 0, })
        cherrypy.quickstart(self, '/', {'/': {'tools.gzip.on': True}})

    @cherrypy.expose
    def stop(self):
        cherrypy.engine.exit()
        cherrypy.server.stop()
        self.running = False
        if self.thread:
            if threading.currentThread() != self.thread:
                self.thread.join(3.0)
            self.thread = None
        return 'stop'

    @cherrypy.expose
    def index(self):
        return '<h1>Hello!</h1>'

    @cherrypy.expose
    def test01(self):
        return '<h1>Test01</h1>'


if __name__ == '__main__':

    class testICORStarter(object):

        def __init__(self):
            #self.sysoutwrapper=startutil.MemorySysOutWrapper(apidinclude=0)
            aICORStartManager = ICORStartManager(self)
            aICORStartManager.start()
            while aICORStartManager.running:
                time.sleep(0.5)
            #aICORStartManager.thread.join()

    while 1:
        print 'start'
        t = testICORStarter()
        print 'koniec'
