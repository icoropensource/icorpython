# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwserver.icorwwwinterface import *
from CLASSES_Library_DBBase_Util_CSVImport import CSVImport, CSVExport
import appplatform.startutil as startutil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.projekt.sqlrun as SQLRun
import icordbmain.adoutil as ADOLibInit
import icordbmain.dbaccess as dbaccess
import pythoncom
import string
import time
import sys

adolib, adoconst, amajor, aminor = ADOLibInit.ADOInitialize()


def GetConnection(aproject):
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    poid = pclass.Nazwa.Identifiers(aproject)
    if poid < 0:
        return None
    pobj = pclass[poid]
    if pobj['SGIsDisabled']:
        return None
    aConnectionString = dbaccess.GetConnectionString(pobj.DBAccess)
    aconnection = adolib.Connection()
    aconnection.Open(aConnectionString)
    return aconnection


def DoSQLImport(aproject, fname, asqldropcreate, stable, lfields, adoraise=0, adelimiter=';', atextQualifier='"', ahasheader=1, astripdata=1, aheaderline='', adropcreate=0, acolumnconversion=None):    #"
    aconnection = GetConnection(aproject)
    if aconnection is None:
        return
    if adropcreate:
        rs, status = aconnection.Execute(asqldropcreate)
        startutil.Log('SQL command status: ' + str(status) + '\n')
    wcolumnconverion = 1
    dcolumnconverion = acolumnconversion
    if acolumnconversion is None:
        wcolumnconverion = 0
        dcolumnconverion = {}
    asqladd = """
SET IDENTITY_INSERT %s ON
select %s from %s WHERE _OID=-1
""" % (stable, string.join(lfields, ','), stable)
    rs = adolib.Recordset()
    rs.ActiveConnection = aconnection
    rs.CursorType = adoconst.adOpenKeyset
    rs.LockType = adoconst.adLockOptimistic
    #   rs.Source=asqladd
    rs.Open(stable, Options=adoconst.adCmdTable)
    start = time.time()
    acsv = CSVImport(adelimiter=adelimiter, atextQualifier=atextQualifier, ahasheader=ahasheader, astripdata=astripdata, aheaderline=aheaderline)
    acsv.Open(fname)
    try:
        cnt = 0
        while not acsv.EOF:
            try:
                rs.AddNew()
            except:
                startutil.Log('Error during addnew - line %d ' % (cnt + 2, ) + 'record not updated!\n')
                if adoraise:
                    raise
            if not cnt % 20:
                print cnt, '\r',
            for afname in acsv.Header:
                s = acsv[afname]
                if s:
                    try:
                        if wcolumnconverion:
                            rs.Fields.Item(dcolumnconverion[afname]).Value = s
                        else:
                            rs.Fields.Item(afname).Value = s
                    except:
                        startutil.Log('Error in field: ' + afname + ' bad value at line %d : "%s"\n' % (cnt + 2, s))
                        if adoraise:
                            raise
            rs.Fields.Item("_UID").Value = "0"
            try:
                rs.Update()
            except:
                startutil.Log('Error during update - line %d ' % (cnt + 2, ) + 'record not updated. Line: %s\n' % (acsv.line, ))
                rs.CancelUpdate()
                if adoraise:
                    raise
            cnt = cnt + 1
            acsv.Next()
        print
    finally:
        acsv.Close()
    if rs.State != adoconst.adStateClosed:
        rs.Close()
    finish = time.time()
    startutil.Log('processed ' + str(cnt) + ' records in ' + str(finish - start) + '\n')
    aconnection.Close()


def DoSQLCreate(aproject, asqldropcreate):
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    poid = pclass.Nazwa.Identifiers(aproject)
    if poid < 0:
        return
    pobj = pclass[poid]
    if pobj['SGIsDisabled']:
        return None
    SQLRun.ExecuteGoSplitSQLCommand('', asqldropcreate, dbaccessobj=pobj.DBAccess)

    #aconnection=win32com.client.Dispatch(r'ADODB.Connection')
    #aconnection.Open(aConnectionString)
    #rs,status=aconnection.Execute(asqldropcreate)
    #startutil.Log('SQL command status: '+str(status)+'\n')
    #aconnection.Close()


def DoSQLCreateStoredProcs(aproject, astoredprocs):
    if not astoredprocs:
        return
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    poid = pclass.Nazwa.Identifiers(aproject)
    if poid < 0:
        return
    pobj = pclass[poid]
    if pobj['SGIsDisabled']:
        return None
    aConnectionString = dbaccess.GetConnectionString(pobj.DBAccess)
    aconnection = adolib.Connection()
    aconnection.Open(aConnectionString)
    for asp in astoredprocs:
        rs, status = aconnection.Execute(asp)
        startutil.Log('SP Create SQL command status: ' + str(status) + '\n')
    aconnection.Close()


def DoSQLCopy(aproject, dtable, stable, lfields, adoraise=0):
    pass


def DoSQLExport(aproject, fname, stable, lfields, adoraise=0):
    aconnection = GetConnection(aproject)
    if aconnection is None:
        return
    asql = 'SELECT %s FROM %s ORDER BY _OID' % (string.join(lfields, ','), stable)
    try:
        rs, status = aconnection.Execute(asql)
        if rs.State != adoconst.adStateClosed:
            bcsv = CSVExport()
            bcsv.Header = lfields
            bcsv.Open(fname)
            try:
                i = 10
                while not rs.EOF and not rs.BOF and i:
                    for fname in lfields:
                        v = rs.Fields.Item(fname).Value
                        if v is None:
                            v = ''
                        elif type(v) == type(u''):
                            #                     v='v'[2:-1]
                            v = v.encode('utf-8', 'replace')    #cp1250
                        elif isinstance(v, pythoncom.PyTimeType):
                            try:
                                v = ICORUtil.tdatetime2fmtstr(tdatetime(int(v)))
                            except:
                                v = '1900/1/1 0:0:0'
                        bcsv[fname] = v
                    bcsv.Next()
                    rs.MoveNext()


#               i=i-1
            finally:
                bcsv.Close()
    finally:
        aconnection.Close()
    print 'SQL command status:', status


def DoSQLXMLImport(aproject, fname, asqldropcreate, stable, lfields, adoraise=0):
    aconnection = GetConnection(aproject)
    if aconnection is None:
        return
    rs, status = aconnection.Execute(asqldropcreate)
    startutil.Log('SQL command status: ' + str(status) + '\n')
    rs = adolib.Recordset()
    rs.Open(fname)
    rs.ActiveConnection = aconnection
    rs.UpdateBatch()
    if rs.State != adoconst.adStateClosed:
        rs.Close()
    aconnection.Close()


def DoSQLXMLExport(aproject, fname, stable, lfields, adoraise=0):
    aconnection = GetConnection(aproject)
    if aconnection is None:
        return
    asql = 'SELECT %s FROM %s ORDER BY _OID' % (string.join(lfields, ','), stable)
    try:
        rs, status = aconnection.Execute(asql)
        if rs.State != adoconst.adStateClosed:
            if not rs.EOF and not rs.BOF:
                rs.Save(fname, adoconst.adPersistXML)
        if rs.State != adoconst.adStateClosed:
            rs.Close()
    finally:
        aconnection.Close()
    print 'SQL command status:', status


def Main(sql1, atablename, aproject, lfields, adelimiter=';', atextQualifier='"', ahasheader=1, astripdata=1, astoredprocs=None, aheaderline=''):    #"
    info = 0
    sys.argv.extend(['', '', '', '', '', ])
    if sys.argv[1] == 'IMPORT':
        DoSQLImport(aproject, sys.argv[2], sql1, atablename, lfields, adelimiter=adelimiter, atextQualifier=atextQualifier, ahasheader=ahasheader, astripdata=astripdata, aheaderline=aheaderline)
    elif sys.argv[1] == 'EXPORT':
        DoSQLExport(aproject, sys.argv[2], atablename, lfields)
    elif sys.argv[1] == 'CREATE':
        DoSQLCreate(aproject, sql1)
    elif sys.argv[1] == 'CREATESP':
        DoSQLCreateStoredProcs(aproject, astoredprocs)
    elif sys.argv[1] == 'COPY':
        DoSQLCopy(aproject, sys.argv[2], atablename, lfields)
    elif sys.argv[1] == 'XMLIMPORT':
        DoSQLXMLImport(aproject, sys.argv[2], sql1, atablename, lfields)
    elif sys.argv[1] == 'XMLEXPORT':
        DoSQLXMLExport(aproject, sys.argv[2], atablename, lfields)
    else:
        info = 1
    if info:
        print 'Usage:'
        print sys.argv[0], 'IMPORT file.csv'
        print sys.argv[0], 'EXPORT file.csv'
        print sys.argv[0], 'CREATE'
        print sys.argv[0], 'CREATESP'
        print sys.argv[0], 'COPY fromtable'
        print sys.argv[0], 'XMLEXPORT file.xml'
        print sys.argv[0], 'XMLIMPORT file.xml'
