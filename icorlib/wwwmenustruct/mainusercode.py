# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icordbmain.adoutil as ADOLibInit
import appplatform.startutil as startutil
import time
import re
import string
import os
import sys
import shutil
import smtplib
import icordbmain.dbaccess as dbaccess

adolib, adoconst, amajor, aminor = ADOLibInit.ADOInitialize()


class WWWMenuStructHelper:

    def __init__(self, aclass, aoid, alog):
        self.Obj = aclass[aoid]
        self.Log = alog

        self.StructVars = ICORUtil.ParseVars(aobj.StructVars, {'aCgiScriptPath': '', 'aFileUploadsOrderInChapters': 'Description,Name', 'aHTTPFileUploadsOrderInChapters': 'Description,Name'})

        self.BaseNameModifier = aobj.Projekt.BaseNameModifier

        self.Path = FilePathAsSystemPath(aobj.AppPaths.SciezkaAplikacji)
        self.FilesPath = self.Path + '/files/'

        awwwdatafilespath = FilePathAsSystemPath(aobj.Projekt.WWWDataPath)
        awwwdatafilespath = string.replace(awwwdatafilespath, '\\', '/')
        if awwwdatafilespath[-1:] != '/':
            awwwdatafilespath = awwwdatafilespath + '/'
        self.WWWDataFilesPath = awwwdatafilespath + 'SQLFiles/'

        self.ConnectionString = dbaccess.GetConnectionString(self.Obj.DBAccess)

    def Process(self):
        lcode = []
        tobj = self.Obj.UserCode
        while tobj:
            if tobj['ExecuteNow']:
                acode = tobj.SourceCode + '\n'
                acode = string.replace(acode, chr(13), '')
                lcode.append([acode, tobj.Nazwa, tobj.OID])
            tobj.Next()
        if lcode:
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
            arepldict={'this':self.Obj,'re':re,'string':string,'ICORUtil':ICORUtil,'os':os,'sys':sys,'shutil':shutil,'smtplib':smtplib,'adolib':adolib,
               'aICORDBEngine':aICORDBEngine,
               'aPath':self.Path,
               'aBaseNameModifier':self.BaseNameModifier,
               'aFilesPath':self.FilesPath,
               'aWWWDataFilesPath':self.WWWDataFilesPath,
               'aConnection':self.Connection,
               } # yapf: disable
            try:
                for acode, tnazwa, toid in lcode:
                    try:
                        #print 'XML Gen UserCode execute: %s <OID:%d>'%(tnazwa,toid)
                        ICORUtil.do_exec(acode, arepldict, arepldict)
                    except:
                        print 'Error in UserCode command:', acode
                        self.Log.LogException('Error in UserCode command: ' + acode)
                        raise
            finally:
                self.Connection.Close()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    if OID < 0:
        return

    aICORDBEngine.SysBase.SetCMSData(OID, 'Status_UserCode', 'G')
    try:
        afname = startutil.GetLogTempFileName('usercode')
        alog = startutil.MLog(afname, aconsole=0)
        alog.Log('Start generate usercode for CMS - oid: %d' % (OID, ))

        awwwhelper = WWWMenuStructHelper(aclass, OID, alog)
        awwwhelper.Process()
    finally:
        aICORDBEngine.SysBase.SetCMSData(OID, 'Status_UserCode', 'Z')
    return
