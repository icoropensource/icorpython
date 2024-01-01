# -*- coding: utf-8 -*-
import sys
import os
import urllib
import time

import pythoncom

import cherrypy
import cherrypy.process as process
from cherrypy.process.plugins import Monitor
import mimetypes

mimetypes.init()

try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import appplatform.smtpemailutil as smtpemailutil
import appplatform.storageutil as storageutil
import appplatform.session as session

import appplatform.dbplatform as dbplatform
import appplatform.dbplatform.dbsession as dbsession
import appplatform.dbplatform.dbauth as dbauth

import appplatform.wserverutil.webutil as webutil


class WebBaseApp(object):

    def __init__(self, application, dconfig, ainit=False):
        webutil.InitCORS()
        DCONFIG = dconfig
        self.init = ainit
        for adir in ['log', 'out', 'temp']:
            apath = os.path.join(DCONFIG['AppBaseDir'], adir)
            if not os.path.exists(apath):
                os.makedirs(apath)
        alogpath = startutil.GetLogTempFileName(application, abasedir=os.path.join(DCONFIG['AppBaseDir'], 'log'))
        alog = startutil.MLog(alogpath)
        awebrootpath = os.path.join(DCONFIG['AppBaseDir'], 'pwa15', 'dist', 'spa-mat')
        print 'Start: ', storageutil.tdatetime2fmtstr()
        print 'Application: ', application
        print 'App mode:', DCONFIG['DIST']['Mode']
        print 'WEBROOT:', awebrootpath
        print 'DB Server - host: %s, port: %d, user: %s, db: %s' % (DCONFIG['PGHost'], DCONFIG['PGPort'], DCONFIG['PGUser'], DCONFIG['PGDatabase'])
        print 'Local Web Server: http://%s:%d/' % (DCONFIG['TCP_SERVER_HOST'], DCONFIG['TCP_SERVER_PORT_GSERVER'], )
        cherrypy.config.update({
           'tools.encode.on':True,
           'tools.encode.encoding':'utf-8',
           'tools.CORS.on':True, #True
           'log.screen':False,
           'log.access_file':DCONFIG['AppBaseDir']+'/log/%s_access.log'%application,
           'log.error_file':DCONFIG['AppBaseDir']+'/log/%s_error.log'%application,
           'engine.autoreload.on':False,
           'server.socket_host':DCONFIG['TCP_SERVER_HOST'],
           'server.socket_port':DCONFIG['TCP_SERVER_PORT_GSERVER'],
           'server.socket_queue_size':12,
           'server.socket_timeout':60,
           'server.shutdown_timeout':300,
           'server.thread_pool':10,
           'server.max_request_body_size':0,
           'tools.json_in.on': True,
           'tools.json_in.force': False,
           'tools.staticdir.on' : True,
           'tools.staticdir.dir' : awebrootpath,
           'tools.staticdir.index' : 'index.html'
        }) # yapf: disable
        self.application = application
        self.log = alog
        if dconfig is None:
            dconfig = {}
        self.dconfig = dconfig
        self.onetimetickets = {}
        self.distconfig = self.dconfig.get('DIST', {})
        self.smtpconfig = self.dconfig.get('SMTP', {})
        self.smtp = smtpemailutil.SMTPServer(self.smtpconfig.get('SMTPServer', ''), self.smtpconfig.get('SMTPUser', ''), self.smtpconfig.get('SMTPPassword', ''), self.smtpconfig.get('SMTPFrom', ''))
        self.store = dbplatform.AppDB(self.application)
        #self.store.InitPlugin('dbsession',dbsession.DBSessionUtil)
        #self.store.InitPlugin('dbauth',dbauth.DBAuthUtil,ainit=self.GetDBAuthInit())
        self.store.dbsession = dbsession.DBSessionUtil(self.store)
        self.store.dbauth = dbauth.DBAuthUtil(self.store)
        self.AppInit()
        self.monitor = Monitor(cherrypy.engine, self.Scheduler, frequency=3)
        self.monitor.subscribe()

    def AppInit(self):
        pass

    def AppScheduler(self):
        pass

    def Scheduler(self):
        self.monitor.unsubscribe()
        try:
            self.AppScheduler()
        finally:
            self.monitor.subscribe()

    def RegisterOneTimeTicket(self, data=None, atype='', expiry=2 * 60 * 60):
        auuid = storageutil.GetUUID()
        d = {}
        d['uuid'] = auuid
        d['type'] = atype
        d['time'] = time.time()
        d['expiry'] = expiry
        if data is None:
            data = {}
        d['data'] = data
        self.onetimetickets[auuid] = d
        return auuid

    def CheckOneTimeTicket(self, auuid):
        d = self.onetimetickets.get(auuid, None)
        if d is None:
            return None
        if d['expiry']:
            adt = time.time()
            if (adt - d['time']) > d['expiry']:
                return None
        del self.onetimetickets[auuid]
        return d['data']

    def ServeFileAccel(self, filepath, aredirect, download=0):
        abasepath, afilename = os.path.split(filepath)
        abasefilename, afileext = os.path.splitext(afilename)
        afilename = afilename.replace('"', "'")
        cherrypy.response.headers['X-Accel-ICOR'] = 'OK'
        amimetype = mimetypes.types_map.get(afileext.lower(), 'application/octet-stream')
        print 'ServeFileAccel:', filepath, 'mime:', amimetype, 'download:', download
        cherrypy.response.headers['Content-Type'] = amimetype
        if download:
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="%s"' % storageutil.CP1250_To_UTF8(afilename)
            #cherrypy.response.headers['Content-Transfer-Encoding']='application/octet-stream'
        else:
            cherrypy.response.headers['Content-Disposition'] = 'inline; filename="%s"' % storageutil.CP1250_To_UTF8(afilename)
            #cherrypy.response.headers['Content-Transfer-Encoding']='application/octet-stream'
        cherrypy.response.headers['X-Accel-Redirect'] = storageutil.CP1250_To_UTF8(aredirect)
        return ''

    def GetSession(self, atimer=None):
        asession = session.Session(self.store, atimer=atimer)
        return asession

    def SendEMail(self, ato, asubject, atext):
        print 'EMAIL 1a:', ato
        if self.distconfig.get('Mode', '') != 'production':
            ato = self.distconfig.get('EMail', '')
        ret = self.smtp.Send(ato, asubject, atext, afrom=self.smtpconfig.get('SMTPFrom', ''), alog=self.log)
        print 'EMAIL 1b', ato, asubject, 'from:', self.smtpconfig.get('SMTPFrom', ''), 'ret:', ret
        #time.sleep(21)
        return ret

    def SendSMS(self, aphone, atext, aemail=''):
        if not self.dconfig.has_key('SMS'):
            return 1, {}
        asmsconfig = self.dconfig['SMS']
        if self.distconfig.get('Mode', '') != 'production':
            btext = '''
            Oto komunikat SMS do nr %s
            %s
         ''' % (storageutil.CP1250_To_UTF8(aphone), storageutil.CP1250_To_UTF8(atext))
            self.SendEMail(self.distconfig.get('EMail', ''), 'SMS', btext)
        if self.distconfig.get('Mode', '') not in ['production', 'stage']:
            return 0, {}
        ret = 2
        result = {}
        if asmsconfig['type'] == 'serwersms.pl':
            try:
                import appplatform.serwersms as serwersms
                api = serwersms.SerwerSMS(asmsconfig['user'], asmsconfig['password'])
                params = {'details': 'true', }
                if (aphone[:3] == '123') or (aphone[:3] == u'123') or (self.distconfig.get('Mode', '') not in ['production', ]):
                    aphone = self.distconfig.get('Phone', '')
                if aphone:
                    response = api.message.send_sms(aphone, atext, asmsconfig['sender'], params)
                    result = json.loads(response)
                #{"error":{"code":3000,"type":"SendError","message":"Wyczerpano limit dost\u0119pnych wiadomo\u015bci SMS ECO"}}
                #{"error":{"code":3106,"type":"SendError","message":"Nie mo\u017cna u\u017cy\u0107 tej nazwy nadawcy"}}
                #{"success":true,"queued":1,"unsent":0,"items":[{"id":"8931c3c014","phone":"+48xxxyyyzzz","status":"queued","queued":"2018-05-21 19:16:22","parts":1,"text":"informacja o konfiguracji 2","stat_id":"7286772"}]}
                if result.has_key('error'):
                    ret = 4
                if result.has_key('success'):
                    ret = 0
                self.log.Log('SendSMS: ' + str(result))
            except:
                ret = 3
                self.log.LogException()
        return ret, result

    def SendEMailByTemplates(self, aemail, asubject, atemplate, adict=None, atemplatesdict=None):
        if adict is None:
            adict = {}
        if atemplatesdict is None:
            atemplatesdict = {}
        dtemplate = self.store.dbauth.getTextTemplateByKind(atemplate)
        atext = dtemplate.get(u'ovalue', '')
        for akey, avalue in adict.items():
            atext = atext.replace('{{%s}}' % akey, avalue)
        for akey, avalue in atemplatesdict.items():
            btemplate = self.store.dbauth.getTextTemplateByKind(avalue)
            btext = btemplate.get(u'ovalue', '')
            atext = atext.replace('{{%s}}' % akey, btext)
        wret = 0
        try:
            wret = self.SendEMail(aemail, asubject, atext)
        except:
            wret = 99
            self.log.LogException()
        return wret

    def dumpCookies(self):
        cookie = cherrypy.request.cookie
        print 'COOKIES', len(cookie)
        for name in cookie.keys():
            print "   name: %s, value: %s" % (name, cookie[name].value)

    def dumpHeaders(self):
        headers = cherrypy.request.headers
        print 'HEADERS', len(headers)
        for name in headers.keys():
            print "   name: %s, value: %s" % (name, str(headers[name]))

    def dumpRequest(self, args=None, kwargs=None, info=''):
        if info:
            print '>>>> ' + info
        self.dumpCookies()
        self.dumpHeaders()
        if args:
            print 'ARGS:', args
        if kwargs:
            print 'KWARGS:', kwargs
        if hasattr(cherrypy.request, 'json'):
            print 'JSON:', cherrypy.request.json

    def getRequestJSONAsDict(self):
        return cherrypy.request.json

    @cherrypy.expose
    def test01(self):
        return '<html><body><h1>aaaa</h1></body></html>'

    @cherrypy.expose
    def logprint(self, amessage=''):
        amessage = storageutil.UTF8_To_CP1250(amessage)
        self.log.Log(urllib.unquote_plus(amessage))
        return ''

    @cherrypy.expose
    def stop(self):
        self.isrunning = 0
        sys.exit()
        return 'stopped'
