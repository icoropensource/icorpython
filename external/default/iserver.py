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
import types
import importlib

sys.coinit_flags = 0
import pythoncom
import wmi

import cherrypy
import cherrypy.process as process

try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import icorstartinit

import icordbmain
import appplatform.storageutil as storageutil
import appplatform.session as session
from icordbmain import dbado

import icorapi
import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil

import icorapp.icormain as icormain
import icorapp.icorstats as icorstats
import icorapp.icorfilemanager as icorfilemanager

import appplatform.wserverutil.webutil as webutil

UID = 0
TIME_TOKEN_VALID = 60 * 60
VERBOSE = 0


class ICORUserSecurity(object):

    def __init__(self, app):
        self.app = app
        self.data = {}
        self.uclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_User']
        self.umethod = self.uclass.MethodsByName('WWWCheckUserAccessGroup')

    def CheckSecurity(self, auid, agroupname):
        du = self.data.get(auid, {})
        ret = du.get(agroupname, None)
        if ret is None:
            ret = self.umethod.Execute(FieldName='', OID=-1, Value=agroupname, UID=auid)
            if ret != '':
                du[agroupname] = int(ret)
        self.data[auid] = du
        return ret


class RequestInitData(object):

    def __init__(self, app, args, kwargs, lmethods=None, wsession=True, wcontext=True, laccessview=None, lusersecurity=None):
        self.app = app
        self.iserror = False
        self.ret = None
        self.session = None
        self.UID = -1
        self.context = None
        self.args = args
        self.kwargs = kwargs
        if lmethods is None:
            lmethods = ['POST', 'GET']
        if laccessview is None:
            laccessview = []
        if lusersecurity is None:
            lusersecurity = []
        if cherrypy.request.method not in lmethods:
            self.iserror = True
            return
        if VERBOSE:
            print 'initRequest:', kwargs, cherrypy.request.body.params
            self.app.dumpRequest()
        if hasattr(cherrypy.request, 'json'):
            self.kwargs = self.app.getRequestJSONAsDict()
        if wsession:
            self.session = self.app.GetSession()
            self.UID = int(self.session.get('uid', '-1'))
            if VERBOSE:
                print '   record: UID:', self.UID
            if self.UID < 0:
                self.iserror = True
                self.ret = webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
                return
            for agroup in lusersecurity:
                asec = self.app.usersecurity.CheckSecurity(self.UID, agroup)
                if not asec:
                    self.iserror = True
                    self.ret = webutil.GetJSONErrorResult('no_auth', 403, 'Brak uprawnień użytkownika', asstring=1)
                    return
        if wcontext:
            self.context = self.app.GetADOContext(self.kwargs, self.UID)
            if self.context is None:
                self.iserror = True
                self.ret = webutil.GetJSONErrorResult('no_data', 403, 'Błędne parametry', asstring=1)
                return
            for aaccessview in laccessview:
                if not self.context.CheckContextAccess(aaccessview, 'AccessLevelView'):
                    self.iserror = True
                    self.ret = webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp do danych zabroniony', asstring=1)
                    return

    def Dump(self):
        print 'RequestInitData: UID=%d, iserror=%s' % (self.UID, str(self.iserror))
        print '  args:', self.args
        print '  kwargs:', self.kwargs

    def getInputValue(self, name, adefault=''):
        if self.kwargs.has_key(name):
            return self.kwargs[name]
        return cherrypy.request.body.params.get(name, adefault)

    def valueObject(self, name, adefault=None, asstring=0):
        if adefault is None:
            adefault = {}
        ret = self.getInputValue(name, adefault)
        if asstring:
            ret = json.dumps(ret)
        return ret

    def valueText(self, name, amaxlength=0, adefault=''):
        ret = self.getInputValue(name, adefault)
        if amaxlength:
            ret = ret[:amaxlength]
        return ret

    def valueDate(self, name):
        ret = self.getInputValue(name)
        ret = storageutil.getStrAsSQLDate(ret)
        return ret

    def valueOID(self, name):
        ret = self.getInputValue(name)
        ret = storageutil.getStrAsOID(ret)
        return ret

    def valueDecimal(self, name):
        ret = self.getInputValue(name)
        ret = storageutil.getStrAsDecimal(ret)
        return ret

    def valueInt(self, name, adefault=0):
        ret = self.getInputValue(name)
        ret = storageutil.getStrAsInt(ret, adefault)
        return ret

    def valueFloat(self, name):
        ret = self.getInputValue(name)
        ret = storageutil.getStrAsFloat(ret)
        return ret

    def valueBool(self, name):
        ret = self.getInputValue(name)
        ret = storageutil.str2bool(ret)
        return ret


class ICOR2(object):

    def __init__(self, alog=None):
        self._timetokens = {}
        self.log = alog
        self.stopping = 0
        self.usersecurity = ICORUserSecurity(self)
        self.store = icordbmain.ICORDBICOR()
        self.storeado = dbado.ICORDBADO()
        self.stats = icorstats.ICORStats(self)
        self.filemanager = icorfilemanager.ICORFileManager(self)
        self.manager = icormain.ICORModuleMain(self)
        print 'IServer start'
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        aobj = aclass.GetFirstObject()
        while aobj:
            if not aobj['SGIsDisabled']:
                #print aobj.OID,aobj.Nazwa
                aProjectVars = ICORUtil.ParseVars(aobj.ProjectVars)
                for akey in aProjectVars.keys():
                    if akey[:15] == 'aIServerModule_':
                        amodule = akey[15:]
                        d = aProjectVars[akey]
                        apath = d.get('path', '')
                        aroute = d.get('route', '')
                        if amodule and apath and aroute:
                            print 'IServer Module:', amodule, apath, aroute
                            try:
                                pmodule = importlib.import_module(apath)
                                self.__dict__[aroute] = pmodule.ICORModuleMain(self)
                            except:
                                print '  initialization error:', amodule, apath, aroute
            aobj.Next()

    def updateRequestByTimeToken(self, args, kwargs):
        atoken = storageutil.UTF8_To_CP1250(kwargs.get('_ttt', None))
        if atoken is None:
            return 0, None, ''
        d = self._timetokens.get(atoken, None)
        if d is None:
            return -1, None, ''
        adt = time.time() - d['adt']
        if adt > (TIME_TOKEN_VALID):
            del self._timetokens[atoken]
            return -2, None, ''
        if type(args) == type([]):
            args[0:0] = d['args'][:]
        elif type(args) == type(()):
            for v in d['args']:
                args = args + (v, )
        kwargs.update(d['kwargs'])
        return 1, d['UID'], d['sid']

    def GetSession(self, asessiontoken='', args=None, kwargs=None):
        if args is not None and kwargs is not None:
            atstat, auid, asessiontoken = self.updateRequestByTimeToken(args, kwargs)
        asession = session.Session(self.store, asessiontoken=asessiontoken)
        return asession

    def GetADOContext(self, kwargs, UID, abyproject=0):
        ioid = storageutil.getStrAsOID(kwargs.get('ioid', ''))
        tid = storageutil.getStrAsInt(kwargs.get('tid', '-1'))
        poid = storageutil.getStrAsInt(kwargs.get('poid', '-1'))
        chapterid = storageutil.getStrAsInt(kwargs.get('chapterid', '-1'))
        if abyproject:
            acontext = self.storeado.GetConnectionByProject(poid, aservercursor=1)
        else:
            if not ioid or (tid < 0) or (poid < 0):
                return None
            if chapterid >= 0:
                acontext = self.storeado.GetConnectionByChapter(chapterid, aservercursor=1)
            elif tid >= 0:
                acontext = self.storeado.GetConnectionByTable(tid, aservercursor=1)
            else:
                acontext = self.storeado.GetConnectionByProject(poid, aservercursor=1)
        acontext.SetContextVars(uid=UID, poid=poid, cmsid=None, toid=tid, coid=chapterid, ioid=ioid, basenamemodifier=None, infotablessufix=None)
        return acontext

    def dumpRequest(self, args=None, kwargs=None):
        cookie = cherrypy.request.cookie
        print 'COOKIES', len(cookie)
        for name in cookie.keys():
            print "   name: %s, value: %s" % (name, cookie[name].value)
        headers = cherrypy.request.headers
        print 'HEADERS', len(headers)
        for name in headers.keys():
            print "   name: %s, value: %s" % (name, str(headers[name]))
        if args:
            print 'ARGS:', args
        if kwargs:
            print 'KWARGS:', kwargs
        if hasattr(cherrypy.request, 'json'):
            print 'JSON:', cherrypy.request.json

    def getRequestJSONAsDict(self, dv=None):
        if dv is None:
            dv = cherrypy.request.json
        ret = storageutil.IterableUTF2CP1250(dv)
        return ret

    def getRequestInitData(self, args, kwargs, lmethods=None, wsession=True, wcontext=True, laccessview=None, lusersecurity=None):
        ainit = RequestInitData(self, args, kwargs, lmethods=lmethods, wsession=wsession, wcontext=wcontext, laccessview=laccessview, lusersecurity=lusersecurity)
        return ainit

    @cherrypy.expose
    def isrunning(self):
        return 'ok'

    @cherrypy.expose
    def stop(self):
        self.stopping = 1
        cherrypy.engine.exit()
        return 'stop'

    @cherrypy.expose
    def cacheClear(self):
        self.usersecurity = ICORUserSecurity(self)
        return 'cache cleared'

    @cherrypy.expose
    def logprint(self, amessage=''):
        self.log.Log(urllib.unquote_plus(amessage))
        return ''

    @cherrypy.expose
    def getTimeToken(self, *args, **kwargs):
        asession = self.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONErrorResult('no_auth', 403, 'Dostęp zabroniony', asstring=1)
        ahttpmethod = cherrypy.request.method
        if hasattr(cherrypy.request, 'json'):
            #self.dumpRequest(args,kwargs)
            kwargs = self.getRequestJSONAsDict()
        adt, atoken = storageutil.GetTimeToken()
        self._timetokens[atoken] = {'adt': adt, 'UID': UID, 'sid': asession.getSessionID(), 'args': args, 'kwargs': kwargs}
        return webutil.GetJSONResult({'_ttt': atoken}, status='OK')

    @cherrypy.expose
    def stateGet(self, aid=''):
        aid = storageutil.getStrAsInt(aid)
        if aid < 0:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak stanu', asstring=1)
        sclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_SystemDictionary_Synchronization_State']
        smethod = sclass.MethodsByName('GetState')
        ret = smethod('', aid, '')
        l = ret.split(storageutil.SPLIT_CHAR_PARAM)
        if len(l) != 2:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak stanu', asstring=1)
        aname, avalue = l
        if avalue in ['BAD', 'OK']:
            smethod = sclass.MethodsByName('DelState')
            smethod('', aid, '')
        return webutil.GetJSONResult({'name': storageutil.CP1250_To_UTF8(aname), 'value': storageutil.CP1250_To_UTF8(avalue)}, status='OK')

    @cherrypy.expose
    def stateSet(self, aid='', aname='', avalue=''):
        aid = storageutil.getStrAsInt(aid)
        if aid < 0:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak stanu', asstring=1)
        avalue = storageutil.UTF8_To_CP1250(avalue)
        sclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_SystemDictionary_Synchronization_State']
        smethod = sclass.MethodsByName('SetState')
        astate = smethod(aname, aid, avalue)
        astate = int(astate)
        return webutil.GetJSONResult({'state': astate}, status='OK')

    @cherrypy.expose
    def stateDel(self, aid=''):
        aid = storageutil.getStrAsInt(aid)
        if aid < 0:
            return webutil.GetJSONErrorResult('no_data', 403, 'brak stanu', asstring=1)
        sclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_SystemDictionary_Synchronization_State']
        smethod = sclass.MethodsByName('DelState')
        astate = smethod('', aid, '')
        astate = int(astate)
        return webutil.GetJSONResult({'ret': astate}, status='OK')

    @cherrypy.expose
    def testhello(self, s=''):
        return "Hello, %s" % s


def CORS():
    sorigin = cherrypy.request.headers.get('Origin', '*')
    cherrypy.response.headers["Access-Control-Allow-Origin"] = sorigin
    if cherrypy.request.method == 'OPTIONS':
        # preflight request
        # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
        # tell CherryPy to avoid normal handler
        return True
    #else:
    #cherrypy.response.headers['Access-Control-Allow-Origin'] = sorigin


cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)


def Main():
    afname = startutil.GetLogTempFileName('iserver')
    alog = startutil.MLog(afname, aconsole=0)

    cherrypy.config.update({
       'tools.encode.on':True,
       'tools.encode.encoding':'utf-8',
       'tools.CORS.on':False, #True
       'log.screen':False,
       'log.access_file':startutil.appconfig.ICORBaseDir+'/log/iserver_access.log',
       'log.error_file':startutil.appconfig.ICORBaseDir+'/log/iserver_error.log',
       'engine.autoreload.on':False,
       'server.socket_queue_size':12,
       'server.socket_timeout':60,
       'server.shutdown_timeout':10,
       'server.max_request_body_size':0,
       'tools.json_in.on': True,
       'tools.json_in.force': False,
       'server.socket_host':'127.0.0.1',
       'server.socket_port':startutil.appconfig.TCP_SERVER_PORT_ISERVER,
       'server.thread_pool':24,
    }) # yapf: disable
    cherrypy.quickstart(ICOR2(alog), '/', {'/': {'tools.gzip.on': True}})


if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_IServer_Instance', 1)

    if ret:
        Main()
