# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import time
import logging
import urllib
import traceback
import Queue
import threading

import pythoncom

import cherrypy
import cherrypy.process as process

try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import icorstartinit
import appplatform.storageutil as storageutil

import enchant

UID = 0


class ICOR2:

    def __init__(self, alog=None):
        self.log = alog
        self.stopping = 0
        try:
            self.enchant_dict = enchant.Dict("pl_PL")
        except:
            print '$$ nie dziala enchant DICT'

    @cherrypy.expose
    def logprint(self, amessage=''):
        amessage = storageutil.UTF8_To_CP1250(amessage)
        return 'logprint'

    @cherrypy.expose
    def isrunning(self):
        return 'ok'

    @cherrypy.expose
    def stop(self):
        self.stopping = 1
        cherrypy.engine.exit()
        return 'stop'

    @cherrypy.expose
    def suggest(self, word=u''):
        if not word:
            return json.dumps([])
        l = self.enchant_dict.suggest(word)
        d = {u'info': 'informacje: ąćęłńóśźż', u'result': l, }
        return json.dumps(d)


def Main():
    cherrypy.config.update({
       'tools.encode.on':True,
       'tools.encode.encoding':'utf-8',
       'log.screen':False, #
       'log.access_file':startutil.appconfig.ICORBaseDir+'/log/sserver_access.log',
       'log.error_file':startutil.appconfig.ICORBaseDir+'/log/sserver_error.log',
       'engine.autoreload.on':False,
       'server.socket_queue_size':12,
       'server.socket_timeout':60,
       'server.shutdown_timeout':10, #
       'server.max_request_body_size':0,
       'server.socket_host':'127.0.0.1',
       'server.socket_port':startutil.appconfig.TCP_SERVER_PORT_SSERVER,
       'server.thread_pool':8,
    }) # yapf: disable
    cherrypy.quickstart(ICOR2(), '/', {'/': {'tools.gzip.on': True}})


if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_SServer_Instance', 1)

    if ret:
        Main()
