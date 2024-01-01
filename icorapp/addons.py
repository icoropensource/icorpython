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

import appplatform.storageutil as storageutil
import icordbmain
import appplatform.wserverutil.webutil as webutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit


class ICORModuleMain(object):
    # BLOKI HTML - START
    @cherrypy.expose
    def block_menu(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return ''
        atemplate = self.jinja_env.get_template('blocks/menu.html')
        ahtml = atemplate.render()
        return ahtml

    # BLOKI HTML - FINISH
    # DANE STRON - START
    @cherrypy.expose
    def pagedata_index(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID < 0:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        auser = ICORSecurity.ICORSecurityUser(UID)
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        d['user']['FirstName'] = storageutil.CP1250_To_UTF8(auser.VCFFirstName)
        d['user']['LastName'] = storageutil.CP1250_To_UTF8(auser.VCFLastName)
        d['user']['EMail'] = storageutil.CP1250_To_UTF8(auser.VCFEMail)
        return json.dumps(d)

    @cherrypy.expose
    def pagedata_ad(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID != -7:
            return webutil.GetJSONResult(status=1, info='dostęp wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        da = {}
        la = []
        for akey, v, title in LATTRS:
            v = asession.get(akey, v)
            if v:
                v = v.replace('\r\n', '<br>')
                da[akey] = v, title
                d2={
                   'name':akey,
                   'value':v,
                   'title':title,
                } # yapf: disable
                la.append(d2)
        d['user']['FirstName'] = da.get('givenName', ('', ''))[0]
        d['user']['LastName'] = da.get('sn', ('', ''))[0]
        d['user']['EMail'] = da.get('mail', ('', ''))[0]
        d['user']['params'] = la
        return json.dumps(d)

    @cherrypy.expose
    def pagedata_profile(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID == -1:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        return json.dumps(d)

    @cherrypy.expose
    def pagedata_profile_edit(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID == -1:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        return json.dumps(d)

    @cherrypy.expose
    def pagedata_help(self):
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID == -1:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        return json.dumps(d)

    @cherrypy.expose
    def pagedata_pageinfo(self, *args, **kwargs):
        achid = storageutil.UTF8_To_CP1250(kwargs.get('chid', '')[:12])
        if not achid:
            return webutil.GetJSONResult(status=2, info='błędny parametr')
        try:
            achid = int(achid)
            if achid < 0:
                return webutil.GetJSONResult(status=2, info='błędny parametr')
        except:
            return webutil.GetJSONResult(status=2, info='błędny parametr')
        asession = self.app.GetSession()
        UID = int(asession.get('uid', '-1'))
        if UID == -1:
            return webutil.GetJSONResult(status=1, info='dostep wymaga zalogowania')
        d={
           'status':0,
           'info':'',
           'user':{},
        } # yapf: disable
        lf = []
        try:
            aadoutil = ADOLibInit.ADOUtil(CONNECTION_STRING, acominitialize=1)
        except:
            d['status'] = 1
            d['info'] = 'db error'
            return json.dumps(d)
        try:
            asql = '''
select t1._OID,t1.Tytul,
tf._OID as foid,tf.Name,tf.Path,tf.FileSize,tf.LastModification,tf.Description,
tf.InformacjaPodmiotUdostepniajacy,tf.InformacjaOsobaOdpowiedzialna,tf.InformacjaDataWytworzenia,tf.InformacjaOpisCzynnosci,
tf._datetime
from TMP_BZR_6008 t1 
left join TMP_FILEUPLOADS_0 tf on t1._OID=tf.RefOID
where
t1._ChapterID=%d
order by tf.Name
         ''' % achid
            rs = aadoutil.GetRS(asql)
            if rs.State != aadoutil.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    d2 = {}
                    mf = rs.Fields.Count
                    for i in range(mf):
                        d2[rs.Fields.Item(i).Name] = storageutil.CP1250_To_UTF8(ADOLibInit.GetRSValueAsStr(rs, rs.Fields.Item(i).Name, astype=0))
                    rs.MoveNext()
                    lf.append(d2)
                rs = aadoutil.CloseRS(rs)
        finally:
            aadoutil.Close()
        d['files'] = lf
        return json.dumps(d)
