# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.icorsecurity import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from CLASSES_Library_NetBase_WWW_Server_ServerUtil import ICORReport
from icorlib.wwwserver.icorwwwinterface import *
import string
import time
import base64
import icorlib.projekt.mcrmutil as MCRMUtil

VERBOSE = 0


def ProcessOnUserEvents(aeventname, areport, buid, auserimpersonated='', auserimpersonateduid=-1):
    if buid < 0:
        return
    for acrm in MCRMUtil.CRMByUserIterator(buid):
        dd={
           'LoginName':areport.LOGIN_USER,
           'LoginPassword':areport.LOGIN_PASSWORD,
           'LoginUID':buid,
           'LoginAction':-1,
           'LoginImpersonated':auserimpersonated,
           'LoginImpersonatedUID':auserimpersonateduid,
        } # yapf: disable
        acrm.ProcessEvents(aeventname, dd={'UserParms': dd, 'ServerParms': areport})


class ADProfil(object):

    def __init__(self, acrm, adobj):
        self.CRM = acrm
        self.OID = adobj.OID
        self.Obj = adobj.AsObject()
        self.LDAPDomain = self.Obj.LDAPDomain
        self.LDAPHost = self.Obj.LDAPHost
        self.LDAPUserName = self.Obj.LDAPUserName
        self.LDAPPassword = self.Obj.LDAPPassword


class ADIntegration(object):

    def __init__(self):
        self.ladprofiles = []

    def Process(self):
        for acrm in MCRMUtil.CRMByAllIterator():
            mobj = acrm.Obj.SecurityMap
            if mobj:
                adobj = mobj.ADProfil
                while adobj:
                    aadprofil = ADProfil(acrm, adobj)
                    self.ladprofiles.append(aadprofil)
                    adobj.Next()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    try:
        areport = ICORReport(Value, autfsplit=1)
        aclass = aICORDBEngine.Classes[CID]
        s = areport.HTTP_AUTHORIZATION
        if s is None:
            return '-1'
        if s[:5] != 'Basic':
            return '-1'
        s = base64.decodestring(s[6:])
        sl = string.split(s, ':')
        if len(sl) != 2:
            return '-1'
        lu1 = string.split(sl[0], '#')
        aimpersonateduser = ''
        if len(lu1) == 2:
            sl[0] = lu1[0]
            aimpersonateduser = lu1[1]
        areport['LOGIN_USER'] = sl[0]
        areport['LOGIN_PASSWORD'] = sl[1]
        if aimpersonateduser:
            iuid = aICORDBEngine.User.UserName.Identifiers(aimpersonateduser)
            if iuid < 0:
                return '-1'

        aadintegration = ADIntegration()
        aadintegration.Process()

        if VERBOSE:
            print 'Login for:', areport.LOGIN_USER, areport.LOGIN_PASSWORD
        buid = aICORDBEngine.User.UserName.Identifiers(areport.LOGIN_USER)
        wu = 0
        uid = -1
        wcustomlogin = 0
        if buid >= 0:
            for acrm in MCRMUtil.CRMByUserIterator(buid):
                dd={
                   'LoginName':areport.LOGIN_USER,
                   'LoginPassword':areport.LOGIN_PASSWORD,
                   'LoginUID':buid,
                   'LoginAction':-1,
                } # yapf: disable
                if VERBOSE:
                    print '    process 1'
                acrm.ProcessEvents('OnUserAuthenticate', dd={'UserParms': dd, 'ServerParms': areport})
                if VERBOSE:
                    print '    process 2', dd['LoginAction'], dd['LoginUID']
                if dd['LoginAction'] == 0:
                    wu = 1
                elif dd['LoginAction'] == 1:
                    wu = 1
                    wcustomlogin = 1
                    uid = dd['LoginUID']
                    break
        if VERBOSE:
            print 'Login after', uid, buid, wu
        if not wu:
            uid = GetUIDByUserPassword(areport.LOGIN_USER, areport.LOGIN_PASSWORD, awwwuser=1)
        afields=['LOGIN_USER' #,'LOGIN_PASSWORD'
           ,'REMOTE_ADDR','REMOTE_HOST','REMOTE_USER','HTTP_USER_AGENT','HTTP_COOKIE'
           ,'AUTH_PASSWORD','AUTH_TYPE','AUTH_USER','HTTPS','HTTPS_KEYSIZE','HTTPS_SECRETKEYSIZE'
           ,'HTTPS_SERVER_ISSUER','HTTPS_SERVER_SUBJECT','CERT_COOKIE','CERT_FLAGS','CERT_ISSUER'
           ,'CERT_KEYSIZE','CERT_SECRETKEYSIZE','CERT_SERIALNUMBER','CERT_SERVER_ISSUER'
           ,'CERT_SERVER_SUBJECT','CERT_SUBJECT'] # yapf: disable
        lclass = aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Log_Login']
        #      print uid,sl[0],sl[1],lclass.HttpCookie.Identifiers(areport.get('HTTP_COOKIE'))>=0,areport.get('HTTP_COOKIE')
        loid = lclass.AddObject()
        lclass.EventDateTime.SetValuesAsDateTime(loid, tdatetime())
        lclass.Logged[loid] = str(uid >= 0)
        for afname in afields:
            sl = string.split(afname, '_')
            for i in range(len(sl)):
                sl[i] = string.capitalize(sl[i])
            sf = string.join(sl, '')
            afield = lclass.FieldsByName(sf)
            avalue = areport.get(afname, '')
            if aimpersonateduser and afname == 'LOGIN_USER':
                avalue = avalue + '#' + aimpersonateduser
            afield[loid] = avalue
        if buid >= 0:
            aICORDBEngine.User.WWWLoginLog.AddRefs(buid, [[loid, lclass.CID], ], lclass.EventDateTime, adescending=1)
        wlog = 0
        uid2 = -1
        if uid >= 0:
            wlog = 1
            if not wcustomlogin:
                achange = 0
                if len(areport.LOGIN_PASSWORD) < 6:
                    achange = 1
                if not achange:
                    for s in ['', strLowerPL(areport.LOGIN_USER), strLowerPL(areport.LOGIN_USER[:2])]:
                        if strLowerPL(areport.LOGIN_PASSWORD) == s:
                            achange = 0
                            break
                if achange:
                    aICORDBEngine.User.PasswordMustChange[uid] = '1'
            lclass.SystemUser[loid] = str(uid) + ':' + str(aICORDBEngine.User.CID) + ':'
            if aimpersonateduser:
                wlog = 0
                uid2 = aICORDBEngine.User.UserName.Identifiers(aimpersonateduser)
                if uid2 >= 0:
                    urefs = aICORDBEngine.User.Groups.GetRefList(uid)
                    apos, afind = urefs.FindRefByValue('Name', 'User Impersonator')
                    if afind:
                        #                  urefs2=aICORDBEngine.User.Groups.GetRefList(uid2)
                        #                  if urefs.RefsExistsAll(urefs2):
                        #                     if len(urefs)>len(urefs2):
                        ProcessOnUserEvents('OnUserLogin', areport, uid, auserimpersonated=aimpersonateduser, auserimpersonateduid=uid2)
                        return '#' + str(uid2)
        if wlog:
            ProcessOnUserEvents('OnUserLogin', areport, uid, auserimpersonated=aimpersonateduser, auserimpersonateduid=uid2)
        else:
            ProcessOnUserEvents('OnUserLoginFailed', areport, buid, auserimpersonated=aimpersonateduser, auserimpersonateduid=uid2)
    except:
        print 'Login error!', Value
        import traceback
        traceback.print_exc()
        uid = -1
    return str(uid)
