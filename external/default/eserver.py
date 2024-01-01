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
import importlib

import cherrypy
import cherrypy.process as process

import appplatform.startutil as startutil
import icorstartinit

import icordbmain
import appplatform.session as session
import appplatform.wserverutil.webutil as webutil
import appplatform.storageutil as storageutil

import icorapi

if 0:
    bgtask = webutil.BackgroundTaskQueue(cherrypy.engine)
    bgtask.subscribe()
#bgtask.put(long_func, "param1", p2='param2')

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', webutil.noBodyProcess, priority=0)

UID = 0


def _ret2list(ret):
    l = []
    while ret:
        l.append(int(ret[:8], 16))
        ret = ret[8:]
    return l


def _unhex(s, abase=16):
    v = long(s, abase)
    if v < 2147483648L:
        return int(v)
    return int(v - 4294967296L)


class ICORAPI(object):

    def __init__(self, app):
        self.app = app

    @cherrypy.expose
    def index(self):
        #cherrypy.log('INDEX',context='',severity=logging.DEBUG,traceback=False)
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        aobj = aclass.GetFirstObject()
        atext = ''
        while aobj:
            atext = atext + str(aobj.OID) + '<br>'
            aobj.Next()
        time.sleep(3)
        return atext

    @cherrypy.expose
    @cherrypy.tools.noBodyProcess()
    def message(self, msglen, size, id):
        global icorapi
        if self.app.stopping:
            return ''
        asize = int(size)
        if not asize:
            return ''
        ret = ''
        cherrypy.response.timeout = 600
        amessage = urllib.unquote_plus(cherrypy.request.rfile.read(asize))
        amsgid = _unhex(amessage[:8])
        apos = 8
        #cherrypy.log('MSGID: '+str(amsgid),context='',severity=logging.DEBUG,traceback=False)
        if amsgid == 0:    #AddObject
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.AddObject(fparamI1, fparamI2)
        elif amsgid == 1:    #CheckObjectBySummary
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.CheckObjectBySummary(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5)
        elif amsgid == 2:    #ClassExists
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.ClassExists(fparamI1, fparamI2)
        elif amsgid == 3:    #ClearAllObjects
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.ClearAllObjects(fparamI1, fparamI2)
        elif amsgid == 4:    #ClearAllValues
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.ClearAllValues(fparamI1, fparamI2, fparamS1)
        elif amsgid == 7:    #CompareOIDValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.CompareOIDValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2)
        elif amsgid == 8:    #CompareOIDs
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.CompareOIDs(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4)
        elif amsgid == 9:    #CreateObjectByID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.CreateObjectByID(fparamI1, fparamI2, fparamI3)
        elif amsgid == 10:    #DeleteObject
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.DeleteObject(fparamI1, fparamI2, fparamI3)
        elif amsgid == 11:    #DeleteVariable
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            icorapi.DeleteVariable(fparamI1, fparamS1)
        elif amsgid == 20:    #ExecuteMethod
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            UID = fparamI1
            aclass = ICORInterface.aICORDBEngine.Classes[fparamI2]
            if aclass is not None:
                amethod = aclass.MethodsByName(fparamS1)
                if amethod is not None:
                    cherrypy.log(msg='EXECUTE: %d [%s]' % (fparamI1, amethod.MethodPath), context='', severity=logging.DEBUG, traceback=False)
                    try:
                        ret = amethod.Execute(FieldName=storageutil.UTF8_To_CP1250(fparamS2), OID=fparamI3, Value=storageutil.UTF8_To_CP1250(fparamS3), UID=fparamI1, anostringvalue=0, aqueued=0, ainternalexecute=0)
                    except:
                        cherrypy.log(msg='EXCEPTION: %d [%s] ' % (fparamI1, amethod.MethodPath), context='', severity=logging.DEBUG, traceback=True)
                        #cherrypy.log('Exception in amethod: %s'%(amethod.MethodPath,),context='',severity=logging.DEBUG,traceback=False)
            #ret=icorapi.ExecuteMethod(fparamI1,fparamI2,fparamS1,fparamS2,fparamI3,fparamS3,fparamI4)
        elif amsgid == 21:    #ExportModuleAsString
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.ExportModuleAsString(fparamI1, fparamS1, fparamS2)
        elif amsgid == 22:    #FindValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.FindValue(fparamI1, fparamI2, fparamS1, fparamS2)
        elif amsgid == 23:    #FindValueBoolean
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.FindValueBoolean(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 24:    #FindValueDateTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.FindValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)
        elif amsgid == 25:    #FindValueFloat
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = float(amessage[apos:apos + fparamS1Len])
            apos = apos + fparamS1Len
            ret = icorapi.FindValueFloat(fparamI1, fparamI2, fparamS1, fparamD1)
        elif amsgid == 26:    #FindValueInteger
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.FindValueInteger(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 28:    #GetClassID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetClassID(fparamI1, fparamS1)
        elif amsgid == 29:    #GetClassLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetClassLastModification(fparamI1, fparamI2)
        elif amsgid == 30:    #GetClassProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetClassProperty(fparamI1, fparamI2, fparamS1)
        elif amsgid == 32:    #GetDeletedObjectsList
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetDeletedObjectsList(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)
        elif amsgid == 33:    #GetFieldLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetFieldLastModification(fparamI1, fparamI2, fparamS1)
        elif amsgid == 34:    #GetFieldModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 35:    #GetFieldObjectsCount
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetFieldObjectsCount(fparamI1, fparamI2, fparamS1)
        elif amsgid == 36:    #GetFieldProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.GetFieldProperty(fparamI1, fparamI2, fparamS1, fparamS2)
        elif amsgid == 37:    #GetFieldValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 38:    #GetFieldValueByPosition
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueByPosition(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 39:    #GetFieldValueDate
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 40:    #GetFieldValueDateTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 41:    #GetFieldValueFloat
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueFloat(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 42:    #GetFieldValueFmt
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueFmt(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 43:    #GetFieldValueInt
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueInt(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 44:    #GetFieldValueLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 45:    #GetFieldValuePyTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValuePyTime(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 46:    #GetFieldValueTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 47:    #GetFieldsList
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFieldsList(fparamI1, fparamI2)
        elif amsgid == 48:    #GetFirstClass
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFirstClass(fparamI1, )
        elif amsgid == 49:    #GetFirstDeletedOffset
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetFirstDeletedOffset(fparamI1, fparamI2, fparamS1)
        elif amsgid == 50:    #GetFirstFieldValueID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetFirstFieldValueID(fparamI1, fparamI2, fparamS1)
        elif amsgid == 51:    #GetFirstObjectID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetFirstObjectID(fparamI1, fparamI2)
        elif amsgid == 55:    #GetLastFieldValueID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetLastFieldValueID(fparamI1, fparamI2, fparamS1)
        elif amsgid == 56:    #GetLastObjectID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetLastObjectID(fparamI1, fparamI2)
        elif amsgid == 57:    #GetMethodLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetMethodLastModification(fparamI1, fparamI2, fparamS1)
        elif amsgid == 58:    #GetMethodProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.GetMethodProperty(fparamI1, fparamI2, fparamS1, fparamS2)
        elif amsgid == 59:    #GetMethodsList
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetMethodsList(fparamI1, fparamI2, fparamI3)
        elif amsgid == 60:    #GetNextClass
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetNextClass(fparamI1, fparamI2)
        elif amsgid == 61:    #GetNextDeletedOffset
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetNextDeletedOffset(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 62:    #GetNextFieldValueID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetNextFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 130:    #GetNextFreeObjectID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetNextFreeObjectID(fparamI1, fparamI2, fparamI3, fparamI4)
        elif amsgid == 63:    #GetNextObjectID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetNextObjectID(fparamI1, fparamI2, fparamI3)
        elif amsgid == 64:    #GetObjectCount
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetObjectCount(fparamI1, fparamI2)
        elif amsgid == 65:    #GetObjectIDByPosition
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetObjectIDByPosition(fparamI1, fparamI2, fparamI3)
        elif amsgid == 66:    #GetObjectModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetObjectModification(fparamI1, fparamI2, fparamI3)
        elif amsgid == 67:    #GetPrevFieldValueID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetPrevFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 68:    #GetPrevObjectID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetPrevObjectID(fparamI1, fparamI2, fparamI3)
        elif amsgid == 69:    #GetRecLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetRecLastModification(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 70:    #GetRecOID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetRecOID(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 71:    #GetRecOwnerID
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetRecOwnerID(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 72:    #GetRecValueAsString
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetRecValueAsString(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 75:    #GetSystemID
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetSystemID(fparamS1, )
        elif amsgid == 76:    #GetValueIDByPosition
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.GetValueIDByPosition(fparamI1, fparamI2, fparamS1, fparamI3)
        elif amsgid == 77:    #GetVariable
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.GetVariable(fparamI1, fparamS1)
        elif amsgid == 82:    #ImportModuleAsString
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.ImportModuleAsString(fparamI1, fparamS1)
        elif amsgid == 83:    #IsFieldInClass
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.IsFieldInClass(fparamI1, fparamI2, fparamS1)
        elif amsgid == 84:    #IsMethodInClass
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.IsMethodInClass(fparamI1, fparamI2, fparamS1)
        elif amsgid == 85:    #IsMethodInThisClass
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            ret = icorapi.IsMethodInThisClass(fparamI1, fparamI2, fparamS1)
        elif amsgid == 86:    #IsObjectDeleted
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.IsObjectDeleted(fparamI1, fparamI2, fparamI3)
        elif amsgid == 88:    #ObjectExists
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.ObjectExists(fparamI1, fparamI2, fparamI3)
        elif amsgid == 89:    #OnStdErrPrint
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.OnStdErrPrint(fparamI1, fparamS1, fparamI2)
        elif amsgid == 90:    #OnStdOutPrint
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.OnStdOutPrint(fparamI1, fparamS1, fparamI2)
        elif amsgid == 91:    #RepositoryChange
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            fparamS4Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS4 = amessage[apos:apos + fparamS4Len]
            apos = apos + fparamS4Len
            icorapi.RepositoryChange(fparamI1, fparamS1, fparamI2, fparamI3, fparamS2, fparamS3, fparamS4)
        elif amsgid == 100:    #SetClassLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetClassLastModification(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)
        elif amsgid == 101:    #SetClassProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            icorapi.SetClassProperty(fparamI1, fparamI2, fparamS1, fparamS2)
        elif amsgid == 103:    #SetFieldLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetFieldLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)
        elif amsgid == 104:    #SetFieldModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            icorapi.SetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2)
        elif amsgid == 105:    #SetFieldProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            icorapi.SetFieldProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3)
        elif amsgid == 106:    #SetFieldValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            icorapi.SetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2)
        elif amsgid == 107:    #SetFieldValueDate
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6)
        elif amsgid == 108:    #SetFieldValueDateTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI10 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10)
        elif amsgid == 109:    #SetFieldValueLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI10 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10)
        elif amsgid == 110:    #SetFieldValueTime
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7)
        elif amsgid == 111:    #SetMethodLastModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI5 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI6 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI7 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI8 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI9 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetMethodLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)
        elif amsgid == 112:    #SetMethodProperty
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            icorapi.SetMethodProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3)
        elif amsgid == 113:    #SetObjectModification
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            icorapi.SetObjectModification(fparamI1, fparamI2, fparamI3, fparamS1)
        elif amsgid == 114:    #SetObjectModified
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            icorapi.SetObjectModified(fparamI1, fparamI2, fparamI3)
        elif amsgid == 129:    #SetTestDecFieldValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.SetTestDecFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2)
        elif amsgid == 127:    #SetTestFieldValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            ret = icorapi.SetTestFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, fparamS3)
        elif amsgid == 128:    #SetTestIncFieldValue
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI4 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            ret = icorapi.SetTestIncFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2)
        elif amsgid == 116:    #SetVariable
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            icorapi.SetVariable(fparamI1, fparamS1, fparamS2)
        elif amsgid == 117:    #ShellExecute
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamS2Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS2 = amessage[apos:apos + fparamS2Len]
            apos = apos + fparamS2Len
            fparamS3Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS3 = amessage[apos:apos + fparamS3Len]
            apos = apos + fparamS3Len
            ret = icorapi.ShellExecute(fparamI1, fparamS1, fparamS2, fparamS3)
        elif amsgid == 124:    #ValueExists
            fparamI1 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamI2 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1Len = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            fparamS1 = amessage[apos:apos + fparamS1Len]
            apos = apos + fparamS1Len
            fparamI3 = _unhex(amessage[apos:apos + 8], 16)
            apos = apos + 8
            ret = icorapi.ValueExists(fparamI1, fparamI2, fparamS1, fparamI3)
        if type(ret) == type(1):
            ret = '%08x' % ret
        elif type(ret) != type(''):
            ret = str(ret)
        #cherrypy.log('RET: '+ret,context='',severity=logging.DEBUG,traceback=False)
        return ret


class ICOR2:

    def __init__(self, ascheduler=0):
        self.testcnt = 0
        self.stopping = 0
        self.icorapi = ICORAPI(self)
        self.store = icordbmain.ICORDBICOR()
        print 'EServer start'
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        aobj = aclass.GetFirstObject()
        while aobj:
            if not aobj['SGIsDisabled']:
                #print aobj.OID,aobj.Nazwa
                aProjectVars = ICORUtil.ParseVars(aobj.ProjectVars)
                for akey in aProjectVars.keys():
                    if akey[:15] == 'aEServerModule_':
                        amodule = akey[15:]
                        d = aProjectVars[akey]
                        apath = d.get('path', '')
                        aroute = d.get('route', '')
                        if amodule and apath and aroute:
                            print 'EServer Module:', amodule, apath, aroute
                            pmodule = importlib.import_module(apath)
                            self.__dict__[aroute] = pmodule.ICORModuleMain(self)
            aobj.Next()
        if ascheduler:
            self.schedulerLock = threading.Lock()
            self.schedulerMonitor = cherrypy.process.plugins.Monitor(cherrypy.engine, self.monitorAction, 1)
            self.schedulerMonitor.subscribe()
            self.schedulerMonitor.start()
            self.schedulerCnt = 0

    def monitorAction(self):
        return
        #cnt=self.schedulerCnt=self.schedulerCnt+1
        #print 'monitorAction - start %d'%cnt
        #with self.schedulerLock:
        #print 'monitorAction - working %d'%cnt
        #time.sleep(2)
        #print 'monitorAction - finish %d'%cnt
    @cherrypy.expose
    def schedule(self, id=''):
        print 'schedule start id = %s' % id
        time.sleep(3)
        print 'schedule end id = %s' % id
        return ''

    def GetSession(self):
        asession = session.Session(self.store)
        return asession

    @cherrypy.expose
    def isrunning(self):
        return 'ok'

    @cherrypy.expose
    def stop(self):
        self.stopping = 1
        cherrypy.engine.exit()
        return 'stop'

    @cherrypy.expose
    def index(self):
        cherrypy.request.throw_errors
        atext = 'throw_errors : %s' % (str(cherrypy.request.throw_errors), )
        return atext

    @cherrypy.expose
    def test(self):
        cherrypy.request.throw_errors = True
        cherrypy.request.show_tracebacks = True
        acnt = self.testcnt = 1 + self.testcnt
        #traceback.print_stack()
        for i in range(500):
            adata = ''
            adata = webutil.isClientConnected()
            s = 'test wait: [%d] %d - value: %s' % (acnt, i, adata)
            cherrypy.log(s, context='', severity=logging.DEBUG, traceback=False)
            time.sleep(1)
        return 'test: %d' % (self.testcnt, )

    @cherrypy.expose
    def testwait2(self):
        cherrypy.request.throw_errors = True
        cherrypy.request.show_tracebacks = True
        acnt = self.testcnt = 1 + self.testcnt
        #traceback.print_stack()
        for i in range(500):
            s = 'test wait 2: [%d] %d' % (acnt, i, )
            cherrypy.log(s, context='', severity=logging.DEBUG, traceback=False)
            time.sleep(1)
        return 'test: %d' % (self.testcnt, )

    @cherrypy.expose
    def testexc(self):
        cherrypy.request.throw_errors = True
        cherrypy.request.show_tracebacks = True
        x = 1 / 0
        return 'exception'

    @cherrypy.expose
    def testresponse(self):
        cherrypy.request.throw_errors = True
        cherrypy.request.show_tracebacks = True
        atext = 'timeout : %s' % (str(cherrypy.response.timeout), )
        return atext

    @cherrypy.expose
    def testhello(self, s=''):
        s = storageutil.UTF8_To_CP1250(s)
        return "Hello, %s" % s


def Main():
    cherrypy.config.update({
       'log.screen':False,
       'log.access_file':startutil.appconfig.ICORBaseDir+'/log/eserver_access.log',
       'log.error_file':startutil.appconfig.ICORBaseDir+'/log/eserver_error.log',
       'engine.autoreload.on':False,
       'server.socket_queue_size':12,
       'server.socket_timeout':60,
       'server.shutdown_timeout':10,
       'server.max_request_body_size':0,
       'server.socket_host':'127.0.0.1',
       'server.socket_port':startutil.appconfig.TCP_SERVER_PORT_ESERVER,
       'server.thread_pool':24,
    }) # yapf: disable
    cherrypy.quickstart(ICOR2(), '/', {'/': {'tools.gzip.on': True}})


if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_EServer_Instance', 1)

    if ret:
        import icorlib.icorinterface as ICORInterface
        import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil

        Main()
