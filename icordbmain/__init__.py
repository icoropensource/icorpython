# -*- coding: utf-8 -*-
import sys
import os
import time

import appplatform.startutil as startutil
import icorstartinit

import appplatform.storageutil as storageutil

import appplatform.dbplatform as dbplatform
import appplatform.dbplatform.dbsession as dbsession
import appplatform.dbplatform.dbauth as dbauth

import dbstruct
import dbexecutor
import dbipc
import dbcms
import dbcache
import dbsyncfiles
import dbstats


class ICORDB(dbplatform.AppDB):

    def __init__(self, aconfig='', aschema=None, atableprefix=None):
        dbplatform.AppDB.__init__(self, aconfig=aconfig, aschema=aschema, atableprefix=atableprefix)
        self.dbsession = dbsession.DBSessionUtil(self)
        self.dbauth = dbauth.DBAuthUtil(self)
        self.executor = dbexecutor.ICORDBExecutor(self)
        self.dbipc = dbipc.ICORDBIPC(self)
        self.dbcms = dbcms.ICORDBCMS(self)
        self.dbcache = dbcache.ICORDBCache(self)
        self.dbsyncfiles = dbsyncfiles.ICORDBSyncFiles(self)
        self.dbstats = dbstats.ICORDBStats(self)


class ICORDBICOR(dbplatform.AppDB):

    def __init__(self, aconfig='', aschema=None, atableprefix=None):
        dbplatform.AppDB.__init__(self, aconfig=aconfig, aschema=startutil.appconfig.PGSchemaICOR, atableprefix=atableprefix)
        self.dbsession = dbsession.DBSessionUtil(self)
        self.dbauth = dbauth.DBAuthUtil(self)
        self.executor = dbexecutor.ICORDBExecutor(self)
        self.dbipc = dbipc.ICORDBIPC(self)
        self.dbcms = dbcms.ICORDBCMS(self)
        self.dbcache = dbcache.ICORDBCache(self)
        self.dbsyncfiles = dbsyncfiles.ICORDBSyncFiles(self)
        self.dbstats = dbstats.ICORDBStats(self)


class ICORDBData(dbplatform.AppDB):

    def __init__(self, aconfig='', aschema=None, atableprefix=None):
        dbplatform.AppDB.__init__(self, aconfig=aconfig, aschema=startutil.appconfig.PGSchema, atableprefix=atableprefix)
        self.schemasnapshots = 'msnapshots'
        self.schemahistory = 'mhistory'
        self.struct = dbstruct.ICORDBStruct(self)

    def initSchema(self):
        self.struct.initSchema()


class ICORDBInit(dbplatform.AppDB):

    def __init__(self, aconfig='', aschema=None, atableprefix=None):
        dbplatform.AppDB.__init__(self, aconfig=aconfig, aschema=startutil.appconfig.PGSchemaICOR, atableprefix=atableprefix)
        self.dbsession = dbsession.DBSessionUtil(self)
        self.dbauth = dbauth.DBAuthUtil(self)

    def initSchema(self):
        self.dbsession.initSchema()
        self.dbauth.initSchema()
