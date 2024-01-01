# -*- coding: utf-8 -*-
import sys
import os
import time
import logging
import urllib
import traceback
import Queue
import threading
import random
import hashlib

try:
    import json
except:
    import simplejson as json

from jinja2 import Environment, FileSystemLoader

import cherrypy
import cherrypy.process as process

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil
import appplatform.wserverutil.webutil as webutil
import icordbmain
import icorapp.idemain as idemain

import icorlib.icorinterface as ICORInterface
import icorlib.icorsecurity as ICORSecurity
import icorlib.wwwserver.doprocess as DoProcess

SPLIT_CHAR_PARAM = '$*$!'
SPLIT_CHAR_VALUE = '$*!$'

import ldap

VERBOSE = 0
MAX_HISTORY = 30

LATTRS=[
   ['c','PL','kraj skrót'],
   ['cn','ICoR_test_email','użytkownik'],
   ['co','Polska','kraj'],
   ['company','firma','firma'],
   ['countryCode','616','kod kraju'],
   ['department','dzial','dział'],
   ['description','opis','opis'],
   ['displayName','test email konto','nazwa użytkownika'],
   ['facsimileTelephoneNumber','faks','telefon faks'],
   ['givenName','imie','imię'],
   ['homePhone','telefon','telefon domowy'],
   ['info','uwagi','uwagi'],
   ['initials','r.s.','inicjały'],
   ['ipPhone','','telefon ip'],
   ['l','miasto','miasto'],
   ['mail','testemail@'+startutil.appconfig.IParams['ad_default_mail'],'email'],
   ['mobile','telefon','telefon komórkowy'],
   ['pager','telefon','pager'],
   ['physicalDeliveryOfficeName','biuro','biuro'],
   ['postalCode','kod','kod pocztowy'],
   ['postOfficeBox','skrytka','skrytka pocztowa'],
   ['sn','nazwisko','nazwisko'],
   ['st','wojewodztwo','województwo'],
   ['streetAddress','ulica1 ulica2','ulica'],
   ['telephoneNumber','telefon','telefon'],
   ['title','stanowisko','stanowisko'],
   ['userPrincipalName','ICOR_test_email@'+startutil.appconfig.IParams['ad_default_domain'],'główna nazwa użytkownika'],
   ['wWWHomePage','strona www','www'],
] # yapf: disable

def LDAP_check_credentials(username, password):
    """Verifies credentials for username and password.
   Returns None on success or a string describing the error on failure
   # Adapt to your needs
   """
    LDAP_SERVER = 'ldap://'+startutil.appconfig.IParams['ad_ldap_server']
    # fully qualified AD user name
    LDAP_USERNAME = '%s@%s' % (username, startutil.appconfig.IParams['ad_default_domain'])
    # your password
    LDAP_PASSWORD = password
    base_dn = 'DC=%s,DC=local'%startutil.appconfig.IParams['ad_default_base_dc']
    ldap_filter = 'userPrincipalName=%s@%s' % (username, startutil.appconfig.IParams['ad_default_domain'])
    attrs = []
    dattrs = {}
    for aattr in LATTRS:
        attrs.append(aattr[0])
        dattrs[aattr[0]] = aattr[2]
    try:
        # build a client
        ldap_client = ldap.initialize(LDAP_SERVER)
        # perform a synchronous bind
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        return 1, {}    #'Wrong username or password'
    except ldap.SERVER_DOWN:
        return 2, {}    #'AD server not awailable'
    # all is well
    # get all user groups and store it in cerrypy session for future use
    ret = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)
    dret = {}
    da = ret[0][1]
    for akey in da.keys():
        v = da[akey][0]
        n = dattrs[akey]
        d2={
           'name':akey,
           'value':v,
           'title':n,
        } # yapf: disable
        dret[akey] = d2
    ldap_client.unbind()
    return 0, dret


class ICORModuleMain(object):

    def __init__(self, aapp):
        self.app = aapp
        self.ide = idemain.ICORIDEMain(self)
        self.jinja_env = Environment(loader=FileSystemLoader(os.path.join(startutil.appconfig.ICORBaseDir, 'wwwroot', 'templates')), block_start_string='{%', block_end_string='%}', variable_start_string='{@', variable_end_string='@}', comment_start_string='{@#', comment_end_string='#@}')

    def clearSession(self, asession=None):
        if asession is None:
            asession = self.app.GetSession()
        asession.set('uid', '', ifexists=1)
        asession.set('UserName', '', ifexists=1)
        asession.set('CMS_UserID', '', ifexists=1)
        asession.set('CMS_IdentityID', '', ifexists=1)

        asession.set('CMS_UserName', '', ifexists=1)
        asession.set('CMS_UserPrettyName', '', ifexists=1)
        asession.set('CMS_UserRoles', '', ifexists=1)
        asession.set('CMS_UserRolesID', '', ifexists=1)
        asession.set('CMS_IdentityUserID', '', ifexists=1)
        asession.set('CMS_IdentityUserName', '', ifexists=1)
        asession.set('CMS_IdentityUserPrettyName', '', ifexists=1)
        asession.set('CMS_TicketID', '', ifexists=1)
        asession.set('CMS_UserGUID', '', ifexists=1)
        asession.set('CMS_UserPESEL', '', ifexists=1)
        asession.set('CMS_UserNIP', '', ifexists=1)
        asession.set('CMS_UserREGON', '', ifexists=1)
        asession.set('CMS_UserEMail', '', ifexists=1)
        asession.set('CMS_UserPhone', '', ifexists=1)
        asession.set('CMS_UserAvatar', '', ifexists=1)
        asession.set('CMS_UserEntryStatus', '', ifexists=1)
        asession.set('CMS_UserDescription', '', ifexists=1)

        asession.set('CMS_UserImie', '', ifexists=1)
        asession.set('CMS_UserImie2', '', ifexists=1)
        asession.set('CMS_UserNazwisko', '', ifexists=1)
        asession.set('CMS_UserRodzajDokumentuTozsamosci', '', ifexists=1)
        asession.set('CMS_UserSeriaNr', '', ifexists=1)
        asession.set('CMS_NazwiskoPanienskieMatki', '', ifexists=1)

        asession.set('CMS_UserTelefonKontaktowy', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaUlica', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaNrDomu', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaNrLokalu', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaKodPocztowy', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaMiejscowosc', '', ifexists=1)
        asession.set('CMS_UserAdresZameldowaniaKraj', '', ifexists=1)

        asession.set('CMS_UserAdresDoKorespondencjiUlica', '', ifexists=1)
        asession.set('CMS_UserAdresDoKorespondencjiNrDomu', '', ifexists=1)
        asession.set('CMS_UserAdresDoKorespondencjiNrLokalu', '', ifexists=1)
        asession.set('CMS_UserAdresDoKorespondencjiKodPocztowy', '', ifexists=1)
        asession.set('CMS_UserAdresDoKorespondencjiMiejscowosc', '', ifexists=1)
        asession.set('CMS_UserAdresDoKorespondencjiKraj', '', ifexists=1)

    def refreshSession(self, asession=None):
        if asession is None:
            asession = self.app.GetSession()
        alogout = asession.get('logout', '')
        if alogout == '1':
            asession.SetTokenLogout()
            asession.set('logout', '')
            raise cherrypy.HTTPRedirect('/icormanager/login.html')
        return

    @cherrypy.expose
    def test01(self):
        return '<h1>test01</h1>'

    # USLUGI - START
    @cherrypy.expose
    def logout(self):
        astatus = 0
        ainfo = ''
        asession = self.app.GetSession()
        asession.SetTokenLogout()
        return webutil.GetJSONResult(status=astatus, info=ainfo)

    def getUserData(self, auser, d):
        d['uid'] = auser.UID
        d['UserName'] = storageutil.CP1250_To_UTF8(auser.UserName)
        d['CMS_UserEMail'] = storageutil.CP1250_To_UTF8(auser.VCFEMail)
        d['CMS_UserPhone'] = storageutil.CP1250_To_UTF8(auser.VCFPhone)
        d['CMS_Avatar'] = 'https://www.gravatar.com/avatar/' + hashlib.md5(auser.VCFEMail.lower()).hexdigest() + '?s=60'
        d['CMS_UserImie'] = storageutil.CP1250_To_UTF8(auser.VCFFirstName)
        d['CMS_UserNazwisko'] = storageutil.CP1250_To_UTF8(auser.VCFLastName)
        d['CMS_UserDescription'] = storageutil.CP1250_To_UTF8(auser.Description)
        lg = []
        grefs = auser.Groups
        while grefs:
            if grefs.Category[grefs.OID] == 'ICOR':
                lg.append(grefs.Name[grefs.OID])
            grefs.Next()
        d['groups'] = lg
        return d

    @cherrypy.expose
    def login_ICOR(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wsession=False, wcontext=False)
        if init.iserror:
            return init.ret
        #if VERBOSE:
        #print 'login_ICOR:',args,kwargs
        #self.app.dumpRequest()
        d = {}
        astatus = 0
        ainfo = 'OK'
        auid = -1
        ausername = init.valueText('username', 44)
        apassword = init.valueText('password', 44)
        afid = init.valueText('fid', 44)
        afdata = init.valueObject('fdata', asstring=1)
        #print 'u:',ausername,'p:',apassword,'i:',afid,'fd:',afdata[:100]
        if not ausername or not apassword:
            astatus = 1
            ainfo = 'nieprawidłowe dane logowania'
        if not astatus:
            auid = ICORSecurity.GetUIDByUserPassword(ausername, apassword, awwwuser=1, averbose=VERBOSE)
            if auid < 0:
                astatus = 2
                ainfo = 'logowanie nie powiodło się'
            else:
                UID = auid
                if VERBOSE:
                    print '  login_ICOR: OK'
                asession = self.app.GetSession()
                asession.SetTokenLogout()
                atoken = asession.getSessionID(anew=1)
                auser = ICORSecurity.ICORSecurityUser(auid)
                if VERBOSE:
                    print '  login_ICOR: user', auid
                asession.set('uid', auid)
                asession.set('fid', afid)
                asession.set('fdata', afdata)
                asession.set('UserName', auser.UserName)
                asession.set('CMS_UserID', auid)
                asession.set('CMS_IdentityID', auser.UserName)
                asession.set('CMS_UserEMail', auser.VCFEMail)
                asession.set('CMS_UserPhone', auser.VCFPhone)
                asession.set('CMS_UserImie', auser.VCFFirstName)
                asession.set('CMS_UserNazwisko', auser.VCFLastName)
                asession.set('CMS_UserDescription', auser.Description)
                if VERBOSE:
                    print '  login_ICOR: user', auser.UserName, auser.VCFEMail, auser.VCFFirstName, auser.VCFLastName, auser.Description
                    print '  login_ICOR: session', asession.get('uid', ''), asession.get('UserName', ''), asession.get('CMS_UserID', ''), asession.get('CMS_IdentityID', ''), asession.get('CMS_UserEMail', ''), asession.get('CMS_UserImie', ''), asession.get('CMS_UserNazwisko', ''), asession.get('CMS_UserDescription', '')
                print 'LOGIN TOKEN:', atoken
                d['token'] = atoken
                self.getUserData(auser, d)
        if VERBOSE:
            print 'd-ret:', d
        return webutil.GetJSONResult(d, astatus, ainfo, adatakey='user')

    @cherrypy.expose
    def login_AD(self, *args, **kwargs):
        if VERBOSE:
            print 'login_AD:', args, kwargs
            self.app.dumpRequest()
        astatus = 0
        ainfo = 'OK'
        auid = -1
        ausername = kwargs.get('username', '')[:44]
        apassword = kwargs.get('password', '')[:44]
        if not ausername or not apassword:
            astatus = 1
            ainfo = storageutil.CP1250_To_UTF8('nieprawidłowe dane logowania')
        if not astatus:
            b, d = LDAP_check_credentials(ausername, apassword)
            if b:
                astatus = 2
                ainfo = 'logowanie nie powiodło się: ' + str(b)
            else:
                asession = self.app.GetSession()
                #self.clearSession(asession)
                asession.set('CMS_UserID', -7)
                asession.set('CMS_IdentityID', ausername)
                for akey, d2 in d.items():
                    asession.set(akey, d2['value'])
        return webutil.GetJSONResult(status=astatus, info=ainfo)

    @cherrypy.expose
    def checksession(self, *args, **kwargs):
        if cherrypy.request.method not in ['POST', 'GET']:
            return
        if VERBOSE:
            print 'checksession:', kwargs, cherrypy.request.body.params
            self.app.dumpRequest()
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1', ifexists=1))
        if VERBOSE:
            print '   checksession: UID:', UID
        if UID < 0:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        ret = {}
        rdata = kwargs
        if hasattr(cherrypy.request, 'json'):
            rdata = cherrypy.request.json
        astatus = 0
        ainfo = 'OK'
        auser = ICORSecurity.ICORSecurityUser(UID)
        d = {}
        d['token'] = asession.getSessionID()
        self.getUserData(auser, d)
        ret['user'] = d
        ret['status'] = astatus
        ret['info'] = ainfo
        return json.dumps(ret)

    # USLUGI - FINISH

    @cherrypy.expose
    def getUsersByAdmin(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, lmethods=['POST', ], wsession=True, wcontext=False, lusersecurity=['User Manager', ])
        if init.iserror:
            return init.ret
        UID = init.UID
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_User']
        l = aclass.GetObjectsValue(fields=set(['UserName', 'VCFFirstName', 'VCFLastName', 'VCFEMail', 'VCFPhone', 'Description', 'AccountDisabled', 'WWWDisabled']), autfconvert=0, aslist=1)
        return webutil.GetJSONResult(l, status=0)

    @cherrypy.expose
    def getUserOperations(self, *args, **kwargs):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID == -1:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'items':[],
        } # yapf: disable
        aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Log_Login']
        aobj = aclass.GetLastObject()
        l = []
        icnt = 10
        while aobj and icnt:
            d1={
               'username':aobj.LoginUser,
               'datetime':aobj.EventDateTime,
               'logged':aobj.Logged,
               'useragent':aobj.HttpUserAgent,
               'remoteaddr':aobj.RemoteAddr,
            } # yapf: disable
            l.append(d1)
            icnt = icnt - 1
            aobj.Prev()
        d['items'] = l
        return json.dumps(d)

    # DANE STRON - FINISH

    @cherrypy.expose
    def sessiontest(self):
        asession = self.app.GetSession()
        atest1 = asession.get('test1', '')
        print 'SESSION TEST: ' + atest1
        asession.set('test2', random.randint(1, 1000))
        return atest1

    @cherrypy.expose
    def icormain(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        UID = init.UID
        self.refreshSession(init.session)
        ret = ''
        ajob = init.valueText('jobtype', 50)
        if VERBOSE:
            print '   icormain.asp ajob:', ajob
        if ajob == 'icorclose':
            return 'not implemented'
        elif ajob == 'lastvisithistory':
            ret = ''
            aid = init.valueText('id', 40)
            if aid:
                init.session.set('lastvisithistory_ignore_click', 1)
                j = int(storageutil.getStrAsInt(init.session.get('LastVisitHistoryID', 0), 0)) - 1
                if aid == 'searchform':
                    for i in range(1, MAX_HISTORY + 1):
                        if j < 1:
                            j = MAX_HISTORY
                        amode = init.session.get('lastvisithistory_mode_%d' % j)
                        aurl = init.session.get('lastvisithistory_url_%d' % j)
                        if aurl:
                            aid = str(j)
                        if amode == 'searchform':
                            break
                        j = j - 1
                if aid == 'singleobject':
                    for i in range(1, MAX_HISTORY + 1):
                        if j < 1:
                            j = MAX_HISTORY
                        amode = init.session.get('lastvisithistory_mode_%d' % j)
                        aurl = init.session.get('lastvisithistory_url_%d' % j)
                        if aurl:
                            aid = str(j)
                        if amode != 'searchform':
                            break
                        j = j - 1
                aurl = init.session.get('lastvisithistory_url_%s' % aid)
                aform = init.session.get('lastvisithistory_form_%s' % aid)
                ret = '''<html><head><meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8"></head><body><form name="form1" id="form1" METHOD="post" ACTION="%s">%s</form><script>form1.submit();</script></body></html>''' % (aurl, aform)
            else:
                s = '''
                  Response.Write "<html xmlns=""http://www.w3.org/TR/REC-html40"">"
                  Response.Write "<head><link rel=STYLESHEET type='text/css' href='/icormanager/icor.css' title='SOI'>"
                  Response.Write "<meta HTTP-EQUIV='Content-Type' content='text/html; charset=utf-8'>"
                  Response.Write "<meta http-equiv='Content-Language' content='pl'>"
                  Response.Write "<meta name='pragma' content='no-cache'>"
                  Response.Write "<meta name='keywords' content='ICOR object oriented database WWW information management repository'>"
                  Response.Write "<meta name='author' content='%s'>"
                  Response.Write "<META NAME='generator' CONTENT='ICOR'>"
                  Response.Write "<META HTTP-EQUIV='expires' CONTENT='Mon, 1 Jan 2001 01:01:01 GMT'>"
                  Response.Write "<title>Ostatnio odwiedzane</title>"
                  Response.Write "<base target='TEXT'>"
                  Response.Write "</head>"
                  Response.Write "<body>"
                  Response.Write "<span class='objectsviewcaption'>Ostatnio odwiedzane:</span>"
                  Response.Write "<TABLE class='objectsviewtable'>"
                  Response.Write "<TR>"
                  Response.Write "   <TH class='objectsviewheader'>l.p.</TH>"
                  Response.Write "   <TH class='objectsviewheader'>Data i czas</TH>"
                  Response.Write "   <TH class='objectsviewheader'>Pozycja</TH>"
'                  Response.Write "   <TH class='objectsviewheader'>Wartoďż˝ďż˝</TH>"
                  Response.Write "</TR>"
                  j=Dession("LastVisitHistoryID")-1
                  k=1
                  for i=1 to MAX_HISTORY
                     if j<1 then
                        j=MAX_HISTORY
                     end if
                     aurl=Dession("lastvisithistory_url_" & CStr(j))
                     if aurl<>"" then
                        aform=Dession("lastvisithistory_form_" & CStr(j))
'                        if aform<>"" then
                        aurl="icormain.asp?jobtype=lastvisithistory&id=" & CStr(j)
'                        end if
                        Response.Write "<TR class='objectsviewrow'>"
                        Response.Write "<td class='objectsviewdataeven' align=left valign=top nowrap><a class='objectitemasanchor' href='" & aurl & "'>" & CStr(k) & "</a></td>"
                        Response.Write "<td class='objectsviewdataeven' align=left valign=top nowrap><a class='objectitemasanchor' href='" & aurl & "'><font color=navy>" & Dession("lastvisithistory_time_" & CStr(j)) & "</font></a></td>"
'                        Response.Write "<td class='objectsviewdataeven' align=left nowrap><a class='objectitemasanchor' href='" & aurl & "'>" & Dession("lastvisithistory_name_" & CStr(j)) & "</a></td>"
'                        Response.Write "<td class='objectsviewdataeven' align=left nowrap><a class='objectitemasanchor' href='" & aurl & "'>" & Dession("lastvisithistory_value_" & CStr(j)) & "</a></td>"
                        Response.Write "<td class='objectsviewdataeven' align=left valign=top nowrap><a class='objectitemasanchor' href='" & aurl & "'><font color=navy>" & Dession("lastvisithistory_name_" & CStr(j)) & "</font></a>"
                        if Dession("lastvisithistory_value_" & CStr(j))<>"" then
                           Response.Write "<table>"
                           Response.Write Dession("lastvisithistory_value_" & CStr(j))
                           Response.Write "</table>"
                        end if
                        Response.Write "</td>"
                        Response.Write "</TR>"
                        k=k+1
                     end if
                     j=j-1
                  next
                  Response.Write "</TABLE>"
                  Response.Write "</body>"
                  Response.Write "</html>"
               end if
                '''%(startutil.appconfig.IParams['meta_author'],)
            return ret
        else:
            #Response.Charset = "utf-8"
            iaction = 0
            #Response.CacheControl = "no-cache"
            #Response.ExpiresAbsolute = #1/1/1999 1:50:00 AM#
            #Response.AddHeader "Pragma", "no-cache"
            #Response.Expires = -1
            if init.valueText('MIMEExcel') == '1':
                cherrypy.response.headers['Content-Type'] = 'application/vnd.ms-excel'
            if init.valueText('MIMEWord') == '1':
                cherrypy.response.headers['Content-Type'] = 'application/msword'
            if (init.valueText('MIMEXML') == '1') or (init.valueText('XMLData') == '1'):
                cherrypy.response.headers['Content-Type'] = 'text/xml'
            if (init.valueText('MIMEJSON') == '1') or (init.valueText('XMLData') == 'json'):
                cherrypy.response.headers['Content-Type'] = 'application/json'
            if init.valueText('MIMEClass') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass')
            if init.valueText('MIMEClass1') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass1')
            if init.valueText('MIMEClass2') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass2')
            if init.valueText('MIMEClass3') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass3')
            if init.valueText('MIMEClass4') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass4')
            if init.valueText('MIMEClass5') != '':
                cherrypy.response.headers['Content-Type'] = init.valueText('MIMEClass5')
            if init.valueText('MIMESave') == '1':
                cherrypy.response.headers['Content-Type'] = 'application/force-download'
            if init.valueText('MIMEContentFileName') != '':
                cherrypy.response.headers['content-disposition'] = 'attachment; filename="%s"' % (init.valueText('MIMEContentFileName'), )
            ld = []
            for k, v in cherrypy.request.body.params.items():
                ld.append([k, storageutil.UTF8_To_CP1250(v)])
            for k, v in cherrypy.request.headers.items():
                ld.append([k, storageutil.UTF8_To_CP1250(v)])
            for k, v in init.kwargs.items():
                ld.append([k, storageutil.UTF8_To_CP1250(v)])
            ld.sort()
            for i in range(len(ld)):
                k = ld[i][0]
                if k[:4] == 'QCNT':
                    ld[i][0] = k[11:]
            ret = DoProcess.ICORMain(-1, ld, iaction, '', init.UID)
            ret = storageutil.CP1250_To_UTF8(ret)
        return ret

    @cherrypy.expose
    def tables(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        amode = init.valueText('mode', 40)
        ret = ''
        if amode == 'dataaccesshistory':
            ret = self.app.storeado.dbtables.getDataAccessHistory(init.context)
        elif amode == 'dataversionhistory':
            ret = self.app.storeado.dbtables.getDataVersionHistory(init.context)
        elif amode == 'tablecapabilities':
            ret = self.app.storeado.dbtables.getTableCapabilities(init.context)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def abstrakt(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        ret = ''
        amode = init.valueText('mode', 40)
        if amode == 'abstraktload':
            ret = self.app.storeado.dbtables.getAbstraktLoad(init.context)
        elif amode == 'abstraktsave':
            atytul = init.valueText('tytul', 199)
            atresc = init.valueText('tresc', 899)
            ret = self.app.storeado.dbtables.getAbstraktSave(init.context, atytul, atresc)
            return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def kalendarium(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        ret = ''
        amode = init.valueText('mode', 50)
        if amode == 'kalendariumload':
            ret = self.app.storeado.dbtables.getKalendariumLoad(init.context)
        elif amode == 'kalendariumsave':
            anazwa = init.valueText('nazwa', 199)
            adataRozpoczecia = init.valueDate('dataRozpoczecia')
            adataZakonczenia = init.valueDate('dataZakonczenia')
            awyswietlajAktualnosciOd = init.valueDate('wyswietlajAktualnosciOd')
            awyswietlajAktualnosciDo = init.valueDate('wyswietlajAktualnosciDo')
            aopis = init.valueText('opis')
            auwagi = init.valueText('uwagi')
            apriorytetWyswietlania = init.valueText('priorytetWyswietlania', 12)
            apriorytetAktualnosci = init.valueText('priorytetAktualnosci', 12)
            astatusZatwierdzenia = init.valueText('statusZatwierdzenia', 12)
            ret = self.app.storeado.dbtables.getKalendariumSave(init.context, anazwa, adataRozpoczecia, adataZakonczenia, awyswietlajAktualnosciOd, awyswietlajAktualnosciDo, aopis, auwagi, apriorytetWyswietlania, apriorytetAktualnosci, astatusZatwierdzenia)
            return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def geolokalizacja(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        ret = ''
        amode = init.valueText('mode', 20)
        if amode == 'geolokalizacjaload':
            ret = self.app.storeado.dbtables.getGeolokalizacjaLoad(init.context)
        elif amode == 'geolokalizacjasave':
            aoid = init.valueOID('_oid')
            atitle = init.valueText('title', 900)
            alat = init.valueDecimal('lat')
            alng = init.valueDecimal('lng')
            ret = self.app.storeado.dbtables.getGeolokalizacjaSave(init.context, aoid, atitle, alat, alng)
        elif amode == 'geolokalizacjadelete':
            aoid = init.valueOID('_oid')
            ret = self.app.storeado.dbtables.getGeolokalizacjaDelete(init.context, aoid)
            return webutil.GetJSONResult(status=ret)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def categories(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        ret = ''
        amode = init.valueText('mode', 20)
        if amode == 'categoriesload':
            ret = self.app.storeado.dbtables.getCategoriesLoad(init.context)
        elif amode == 'categoriessave':
            aoid = init.valueOID('_oid')
            kchecked = init.valueInt('kchecked')
            ret = self.app.storeado.dbtables.getCategoriesSave(init.context, aoid, kchecked)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def tablesassigned(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, laccessview=['table'])
        if init.iserror:
            return init.ret
        UID = init.UID
        ret = []
        amode = init.valueText('mode', 20)
        if amode == 'tablesload':
            ioid = init.valueOID('ioid')
            if ioid:
                ret = self.app.storeado.dbtables.getTablesLoad(init.context, ioid)
        elif amode == 'tablessave':
            ioid = init.valueOID('ioid')
            chapterid = init.valueInt('chapterid')
            xmlid = init.valueInt('oid')
            checked = init.valueBool('checked')
            ret = self.app.storeado.dbtables.getTablesSave(init.context, ioid, chapterid, xmlid, checked)
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def ideObjectEdit(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        UID = init.UID
        jobtype = init.valueText('jobtype', 30)
        oid = init.valueInt('oid', -1)
        cid = init.valueInt('cid', -1)
        broid = init.valueInt('broid', -1)
        brcid = init.valueInt('brcid', -1)
        if oid < 0 or cid < 0 or UID < 0:
            return webutil.GetJSONResult(status=1, info='no data')
        ret, status, info = self.ide.GetObjectEdit(init, oid, cid, broid, brcid)
        return webutil.GetJSONResult(ret, status, info)

    @cherrypy.expose
    def ideObjectEditSheet(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        UID = init.UID
        jobtype = init.valueText('jobtype', 30)
        oid = init.valueInt('oid', -1)
        cid = init.valueInt('cid', -1)
        broid = init.valueInt('broid', -1)
        brcid = init.valueInt('brcid', -1)
        sheetid = init.valueInt('sheetid', 0)
        if oid < 0 or cid < 0 or UID < 0:
            return webutil.GetJSONResult(status=1, info='no data')
        ret, status, info = self.ide.GetObjectEditSheet(init, oid, cid, broid, brcid, sheetid)
        v = webutil.GetJSONResult(ret, status, info)
        return v

    @cherrypy.expose
    def ideObjectEditFormSubmit(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        UID = init.UID
        jobtype = init.valueText('jobtype', 30)
        menuoid = init.valueInt('menuoid', -1)
        oid = init.valueInt('oid', -1)
        cid = init.valueInt('cid', -1)
        broid = init.valueInt('broid', -1)
        brcid = init.valueInt('brcid', -1)
        data = init.valueObject('data')
        if menuoid < 0 or oid < 0 or cid < 0 or UID < 0:
            return webutil.GetJSONResult(status=1, info='no data')
        ret, status, info = self.ide.GetObjectEditFormSubmit(init, menuoid, oid, cid, broid, brcid, data)
        ret = storageutil.IterableCP1250ToUTF(ret)
        return webutil.GetJSONResult(ret, status, info)

    def searchByFields(self, aclass, lsearchfields, searchitem, lresultfields, oidfrom=-1, oidto=-1):
        if oidfrom < 0:
            oidfrom = 0
        elif oidto < 0:
            oidto = oidfrom + 1
        if oidto < 0:
            oidto = 9999999999
        wres = 1
        soids = None
        wsearched = 0
        for aitemname, afieldname in lsearchfields:
            if not searchitem.get(aitemname, ''):
                continue
            wsearched = 1
            afield = aclass.FieldsByName(afieldname)
            sl = afield.GetFieldOIDsBySearchValue(searchitem[aitemname], searchitem.get('isCaseSensitive', 0), searchitem.get('isRegexp', 0))
            if soids is None:
                soids = sl
            else:
                soids.intersection_update(sl)
            wres = len(soids)
            if not wres:
                break
        if soids is None:
            soids = set()
        loids = list(soids)
        loids.sort()
        if not wsearched:
            noid = aclass.NextObject(oidfrom)
            moid = -1
            if noid > oidfrom:
                moid = aclass.PrevObject(noid)
            if moid >= oidfrom:
                aoid = moid
            elif noid >= oidfrom:
                aoid = noid
            else:
                aoid = -1
            icnt = 5000
            while (aoid >= oidfrom) and (aoid < oidto) and (icnt > 0):
                loids.append(aoid)
                aoid = aclass.NextObject(aoid)
                icnt = icnt - 1
        litems = []
        acid = aclass.CID
        for aoid in loids:
            if aoid < oidfrom or aoid >= oidto:
                continue
            d = {'_oid': aoid, '_cid': acid, }
            for aitemname, afield in lresultfields:
                if afield is None:
                    d[aitemname] = ''
                else:
                    d[aitemname] = storageutil.CP1250_To_UTF8(afield[aoid])
            litems.append(d)
        return litems

    @cherrypy.expose
    def search(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        init.Dump()
        UID = init.UID
        ret = {}
        amode = init.valueText('mode', 20)
        #print 'MODE:',amode
        if amode == 'files':
            litems = []

            ret['cnt'] = len(litems)
            ret['items'] = litems
        elif amode == 'repository':
            searchitem = init.kwargs.get('searchitem', {})
            #print 'searchitem:',type(searchitem),
            #print searchitem
            searchmode = searchitem.get('searchMode', '?')
            #print 'searchmode:',searchmode
            litems = []
            if searchmode == 'table':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
                lsearchfields=[
                   ['tableName','Nazwa'],
                   ['tableGroup','Grupa'],
                   ['tableDescription','Komentarz'],
                   ['tableSQL','SQLSource'],
                   ['tableXSL','ShapeXSL'],
                   ['tableXSLTable','ShapeXSLTable'],
                ] # yapf: disable
                lresultfields=[
                   ['tableName',aclass.FieldsByName('Nazwa')],
                   ['tableGroup',aclass.FieldsByName('Grupa')],
                   ['tableDescription',aclass.FieldsByName('Komentarz')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('tableOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('tableOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'html':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_PageHTML_ProjectPageHTML']
                lsearchfields=[
                   ['htmlName','PageTitle'],
                   ['htmlDescription','PageDescription'],
                   ['htmlSource','AddHTML'],
                ] # yapf: disable
                lresultfields=[
                   ['htmlName',aclass.FieldsByName('PageTitle')],
                   ['htmlDescription',aclass.FieldsByName('PageDescription')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('htmlOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('htmlOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'xmldata':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_XMLData_TableXMLData']
                lsearchfields=[
                   ['xmlName','Name'],
                   ['xmlGroup','Grupa'],
                   ['xmlSource','XMLSource'],
                ] # yapf: disable
                lresultfields=[
                   ['xmlName',aclass.FieldsByName('Name')],
                   ['xmlGroup',aclass.FieldsByName('Grupa')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('xmlOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('xmlOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'chapter':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
                lsearchfields=[
                   ['chapterName','Naglowek'],
                   ['chapterNameMenu','NaglowekMenu'],
                   ['chapterHRef','SGHref'],
                   ['chapterHRefMenu','SGHrefApp'],
                   ['chapterDescription','Komentarz'],
                ] # yapf: disable
                lresultfields=[
                   ['chapterName',aclass.FieldsByName('Naglowek')],
                   ['chapterNameMenu',aclass.FieldsByName('NaglowekMenu')],
                   ['chapterDescription',aclass.FieldsByName('Komentarz')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('chapterOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('chapterOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'sql':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_UserTSQL']
                lsearchfields=[
                   ['sqlName','Nazwa'],
                   ['sqlGroup','Grupa'],
                   ['sqlSource','SQLSource'],
                ] # yapf: disable
                lresultfields=[
                   ['sqlName',aclass.FieldsByName('Nazwa')],
                   ['sqlGroup',aclass.FieldsByName('Grupa')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('sqlOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('sqlOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'template':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_PageTemplate']
                lsearchfields=[
                   ['templateName','Template'],
                   ['templateSource','PageTop1'],
                   ['templateXML','PageXML'],
                   ['templateXSLAtEnd','XSLAtEnd'],
                   ['templateXSLMainObjectAtEnd','XSLMainObjectAtEnd'],
                ] # yapf: disable
                lresultfields=[
                   ['templateName',aclass.FieldsByName('Template')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('templateOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('templateOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            elif searchmode == 'event':
                lsearchfields=[
                   #['eventOwner','Nazwa'],
                   #['eventKind','Grupa'],
                   ['eventKey','EventKey'],
                   ['eventDescription','EventDescription'],
                   ['eventSource','EventSource'],
                ] # yapf: disable
                optionsEventOwner={
                   'Table':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Table_EventValue',
                   'Field':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Field_EventValue',
                   'Chapter':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Chapter_EventValue',
                   'Plugin':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Plugin_EventValue',
                   'Template':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Template_EventValue',
                   'XMLData':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_XMLData_EventValue',
                   'PluginExtension':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_PluginExtension_EventValue',
                   'PluginSkin':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_PluginSkin_EventValue',
                   'EffectSkin':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_EffectSkin_EventValue',
                   'AddIn':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_AddIn_EventValue',
                   'AddInTemplate':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_AddInTemplate_EventValue',
                   'Widget':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Widget_EventValue',
                   'WidgetTemplate':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_WidgetTemplate_EventValue',
                   'APIMethod':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_APIMethod_EventValue',
                   'PortletTemplate':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_PortletTemplate_EventValue',
                   'Portlet':'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SourceEvents_Portlet_EventValue',
                } # yapf: disable
                aclasspath = optionsEventOwner.get(searchitem.get('eventOwner', ''), '')
                if aclasspath:
                    aclass = ICORInterface.aICORDBEngine.Classes[aclasspath]
                    lresultfields=[
                       ['eventKey',aclass.FieldsByName('EventKey')],
                       ['eventDescription',aclass.FieldsByName('EventDescription')],
                    ] # yapf: disable
                    aoidfrom = storageutil.getStrAsInt(searchitem.get('eventOIDFrom', -1), -1)
                    aoidto = storageutil.getStrAsInt(searchitem.get('eventOIDTo', -1), -1)
                    litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
                    aeventkind = searchitem.get('eventKind', '')
                    if aeventkind:
                        l = []
                    for d in litems:
                        eobj = aclass[d['_oid']]
                        kobj = eobj.EventKind
                        if kobj:
                            d['eventKind'] = kobj.EventName
                        else:
                            d['eventKind'] = ''
                        if aeventkind and d['eventKind'] == aeventkind:
                            l.append(d)
                    if aeventkind:
                        litems = l
            ret['cnt'] = len(litems)
            ret['items'] = litems
        return webutil.GetJSONResult(ret)

    @cherrypy.expose
    def searchfiles(self, *args, **kwargs):
        init = self.app.getRequestInitData(args, kwargs, wcontext=False)
        if init.iserror:
            return init.ret
        init.Dump()
        UID = init.UID
        ret = {}
        amode = init.valueText('mode', 20)
        if amode == 'files':
            litems = []

            ret['cnt'] = len(litems)
            ret['items'] = litems
        elif amode == 'repository':
            searchitem = init.kwargs.get('searchitem', {})
            #print 'searchitem:',type(searchitem),
            #print searchitem
            searchmode = searchitem.get('searchMode', '?')
            #print 'searchmode:',searchmode
            litems = []
            if searchmode == 'table':
                aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
                lsearchfields=[
                   ['tableName','Nazwa'],
                   ['tableGroup','Grupa'],
                   ['tableDescription','Komentarz'],
                   ['tableSQL','SQLSource'],
                   ['tableXSL','ShapeXSL'],
                   ['tableXSLTable','ShapeXSLTable'],
                ] # yapf: disable
                lresultfields=[
                   ['tableName',aclass.FieldsByName('Nazwa')],
                   ['tableGroup',aclass.FieldsByName('Grupa')],
                   ['tableDescription',aclass.FieldsByName('Komentarz')],
                ] # yapf: disable
                aoidfrom = storageutil.getStrAsInt(searchitem.get('tableOIDFrom', -1), -1)
                aoidto = storageutil.getStrAsInt(searchitem.get('tableOIDTo', -1), -1)
                litems = self.searchByFields(aclass, lsearchfields, searchitem, lresultfields, oidfrom=aoidfrom, oidto=aoidto)
            ret['cnt'] = len(litems)
            ret['items'] = litems
        return webutil.GetJSONResult(ret)
