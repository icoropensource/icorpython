# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icordbmain.adoutil as ADOLibInit
import appplatform.startutil as startutil
import time
import icordbmain.dbaccess as dbaccess

adolib, adoconst, amajor, aminor = ADOLibInit.ADOInitialize()


class WWWMenuStructHelper:

    def __init__(self, aclass, aoid, alog):
        self.Obj = aclass[aoid]
        self.Log = alog
        self.ConnectionString = dbaccess.GetConnectionString(self.Obj.DBAccess)

    def Process(self):
        lsql = []
        tobj = self.Obj.UserTSQL
        while tobj:
            if tobj['ExecuteNow']:
                lsql.append(tobj.SQLSource)
            tobj.Next()
        if lsql:
            self.Connection = adolib.Connection()
            acnt = 7
            while acnt:
                try:
                    self.Connection.Open(self.ConnectionString)
                    break
                except:
                    acnt = acnt - 1
                    if not acnt:
                        raise
                    time.sleep(7)
            self.Connection.CursorLocation = adoconst.adUseClient
            self.Connection.CommandTimeout = 0
            try:
                for asql in lsql:
                    try:
                        rs1, status = self.Connection.Execute(asql)
                        #print 'XML Gen UserTSQL execute status:',status
                    except:
                        print 'Error in UserTSQL command:', asql
                        self.Log.LogException('Error in UserTSQL command: ' + asql)
                        raise
            finally:
                self.Connection.Close()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    if OID < 0:
        return

    aICORDBEngine.SysBase.SetCMSData(OID, 'Status_UserTSQL', 'G')
    try:
        afname = startutil.GetLogTempFileName('usertsql')
        alog = startutil.MLog(afname, aconsole=0)
        alog.Log('Start generate usertsql for CMS - oid: %d' % (OID, ))

        awwwhelper = WWWMenuStructHelper(aclass, OID, alog)
        awwwhelper.Process()
        alog.Log('Stop generate usertsql for CMS - oid: %d' % (OID, ))
    finally:
        aICORDBEngine.SysBase.SetCMSData(OID, 'Status_UserTSQL', 'Z')
    return
