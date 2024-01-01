# -*- coding: utf-8 -*-
import sys
import os
import time
import logging
import urllib
import traceback
import Queue
import threading

sys.coinit_flags = 0
import pythoncom
import wmi

import cherrypy
import cherrypy.process as process

try:
    import json
except:
    import simplejson as json

import icordbmain
import appplatform.storageutil as storageutil
import appplatform.wserverutil.webutil as webutil

ALLOWED_GROUP_STATS = 'User Manager'


class ICORStats(object):

    def __init__(self, app):
        self.app = app

    def CheckUserAccessByGroup(self, agroup, UID=-1):
        #print 'CheckUserAccessByGroup:',agroup,UID
        if UID < 0:
            asession = self.app.GetSession()
            UID = asession.get('uid')
            #print '   CheckUserAccessByGroup UID:',UID
            if not UID:
                return -1, 0
        asec = self.app.usersecurity.CheckSecurity(UID, agroup)
        if not asec:
            cherrypy.response.status = 403
        #print '   CheckUserAccessByGroup asec:',UID,asec
        return UID, asec

    @cherrypy.expose
    def getChapterGenTimeCountByUserLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getChapterGenTimeCountByUserLast7d()
        return ret

    @cherrypy.expose
    def getChapterGenTimeCountLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getChapterGenTimeCountLast7d()
        return ret

    @cherrypy.expose
    def getChapterGenTimeCountWithFilesLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getChapterGenTimeCountWithFilesLast7d()
        return ret

    @cherrypy.expose
    def getChapterStates(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getChapterStates()
        return ret

    @cherrypy.expose
    def getCMSGenTimeCountLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getCMSGenTimeCountLast7d()
        return ret

    @cherrypy.expose
    def getFilesGenTimeCountLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getFilesGenTimeCountLast7d()
        return ret

    @cherrypy.expose
    def getFilesCopiedGenTimeCountLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getFilesCopiedGenTimeCountLast7d()
        return ret

    @cherrypy.expose
    def getFilesPathGenTimeCountLast7d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getFilesPathGenTimeCountLast7d()
        return ret

    @cherrypy.expose
    def getExecutorMethodsListAll(self, **params):
        astatus = params.get('status', '')
        if astatus and astatus not in ['Working', 'Ready', 'Processing', 'Deleted']:
            return '[]'
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getExecutorMethodsListAll(astatus)
        return ret

    @cherrypy.expose
    def getExecutorMethodInfo(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, lmethods=None, wsession=True, wcontext=False, laccessview=None, lusersecurity=['User Manager', ])
        if init.iserror:
            return init.ret
        meid = init.valueInt('meid')
        ret = self.app.store.dbstats.getExecutorMethodsInfo(meid)
        return webutil.GetJSONResult(ret, status=0, info='', asjsontext=1)

    @cherrypy.expose
    def getSessionsGenActiveLast1d(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getSessionsGenActiveLast1d()
        return ret

    @cherrypy.expose
    def getDBPGStatActivity(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getDBPGStatActivity()
        return ret

    @cherrypy.expose
    def getDBPGDatabaseSize(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        try:
            ret = self.app.store.dbstats.getDBPGDatabaseSize()
        except:
            import traceback
            traceback.print_exc()
            return '{"status":-1,"info":"error in database access"}'
        return ret

    @cherrypy.expose
    def getDBPGStatIOUserTables(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getDBPGStatIOUserTables()
        return ret

    @cherrypy.expose
    def getDBPGStatUserTables(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getDBPGStatUserTables()
        return ret

    @cherrypy.expose
    def getServerBasicInfo(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = []
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            for disk in c.Win32_LogicalDisk(DriveType=3):
                ret.append({'disk': disk.Caption, 'total': disk.Size, 'free': disk.FreeSpace, 'percent': "%0.2f" % (100.0 * long(disk.FreeSpace) / long(disk.Size))})
        finally:
            pythoncom.CoUninitialize()
        return json.dumps(ret)

    @cherrypy.expose
    def getExecutorMethodsGroupByStatus(self):
        UID, asec = self.CheckUserAccessByGroup(ALLOWED_GROUP_STATS)
        if not asec:
            return '{"status":-1,"info":"access denied"}'
        ret = self.app.store.dbstats.getExecutorMethodsGroupByStatus()
        return ret
