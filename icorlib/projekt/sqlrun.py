# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwserver.icorwwwinterface import *
import icordbmain.adoutil as ADOLibInit
import appplatform.startutil as startutil
import string
import sys
import re

import icordbmain.dbaccess as dbaccess

VERBOSE = 0


def ExecuteGoSplitSQLCommand(aConnectionString='', aSql='', aprint=1, acominitialize=1, dbaccessobj=None):
    #   import win32com.client
    if acominitialize:
        import pythoncom
        pythoncom.CoInitialize()
    try:
        if VERBOSE:
            print '  ExecuteGoSplitSQLCommand: %s' % aConnectionString
        if dbaccessobj is not None:
            if VERBOSE:
                print '  ExecuteGoSplitSQLCommand.dbaccessobj: %d %s' % (dbaccessobj.OID, dbaccessobj.Nazwa)
            aConnectionString = dbaccess.GetConnectionString(dbaccessobj)
        adolib, adoconst, amajor, aminor = ADOLibInit.ADOInitialize()
        aconnection = adolib.Connection()
        #      aconnection=win32com.client.Dispatch(r'ADODB.Connection')
        aconnection.Open(aConnectionString)
        aconnection.CursorLocation = adoconst.adUseClient
        aconnection.CommandTimeout = 0
        if VERBOSE:
            startutil.GetLogTempFileName('sqlexec', aprefix='sql', asufix='sqlrun_execute', avalue=aSql, atrace=1)
        aSql = '\n' + string.replace(aSql, chr(13), '') + '\n'
        #      lsql=string.split(aSql,'\nGO\n')
        apatt = re.compile(r'[\n]+ *go[ \n]+|^ *go[ \n]+', re.I)
        lsql = apatt.split(aSql)
        try:
            for asql in lsql:
                asql = string.strip(asql)
                if asql:
                    try:
                        rs, status = aconnection.Execute(asql)
                    except:
                        print 'Error in SQL command:'
                        print asql    #[:16000]
                        raise
                    try:
                        if rs.State != adoconst.adStateClosed:
                            if aprint:
                                mf = rs.Fields.Count
                                while not rs.EOF and not rs.BOF:
                                    for i in range(mf):
                                        if type(rs.Fields.Item(i).Value) == type(u''):
                                            print str(rs.Fields.Item(i).Value), ';',
                                        else:
                                            print rs.Fields.Item(i).Value, ';',
                                    print
                                    rs.MoveNext()
                    except:
                        print 'Error in recordset:'
                        print asql    #[:16000]
                        raise
                else:
                    status = 'Empty SQL string'
                print 'SQL command status:', status
        finally:
            aconnection.Close()
    finally:
        if acominitialize:
            pythoncom.CoUninitialize()


def ExecuteServerSQLCommand(fname, aConnectionString='', dbaccessobj=None):
    f = open(fname, 'r')
    try:
        asql = f.read()
    finally:
        f.close()
    ExecuteGoSplitSQLCommand(aConnectionString, asql, dbaccessobj=dbaccessobj)


def MainI(aproject, fname, asshape=0):
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    poid = pclass.Nazwa.Identifiers(aproject)
    if poid < 0:
        return
    pobj = pclass[poid]
    if pobj['SGIsDisabled']:
        return
    if asshape:
        print 'UWAGA! pojedyncze uruchomienie WWWMenuStruct'
        ExecuteServerSQLCommand(fname, dbaccessobj=pobj.WWWMenuStruct.DBAccess)
    else:
        ExecuteServerSQLCommand(fname, dbaccessobj=pobj.DBAccess)
