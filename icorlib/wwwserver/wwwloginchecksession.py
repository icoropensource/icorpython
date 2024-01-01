# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.icorsecurity import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from CLASSES_Library_NetBase_WWW_Server_ServerUtil import ICORReport
import string
import time
import base64


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    try:
        areport = ICORReport(Value)
        aclass = aICORDBEngine.Classes[CID]
        #      for akey in areport.keys():
        #         print akey,areport[akey]
        s = areport.get('HTTP_AUTHORIZATION')
        if s[:5] != 'Basic':
            #         print 'WWWLoginSessionCheck: no authorisation'
            return '-1'
        s = base64.decodestring(s[6:])
        sl = string.split(s, ':')
        if len(sl) != 2:
            #         print 'WWWLoginSessionCheck: no pass string'
            return '-1'
        areport['LOGIN_USER'] = sl[0]
        areport['LOGIN_PASSWORD'] = sl[1]
        uid = GetUIDByUserPassword(areport.LOGIN_USER, areport.LOGIN_PASSWORD, awwwuser=1)
        if uid < 0:
            #         print 'WWWLoginSessionCheck: no user pass'
            return '-1'
        lclass = aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Log_Login']
        if lclass.HttpCookie.Identifiers(areport.get('HTTP_COOKIE')) >= 0:
            #         print 'WWWLoginSessionCheck: session Exists!!! (1)'
            return '1'
        return '-1'
    except:
        #      print 'LoginCheckSession error!',Value
        raise


#   print 'WWWLoginSessionCheck: exit'
    return '-1'
