# -*- coding: utf-8 -*-
import codecs
import thread
import hashlib
import Queue
try:
    import json
except:
    import simplejson as json

import psycopg2

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil
import appplatform.dbplatform.dbauthinit as dbauthinit


class DBAuthUtil(object):

    def __init__(self, adb):
        self.db = adb

    def initSchema(self):
        print 'Init DB: auth'
        ainit = dbauthinit.DBAuthUtilInit(self.db)
        ainit.initSchema()

    def getPasswordHash(self, username, password):
        return hashlib.md5(password + '_' + username.lower()).hexdigest().lower()

    def addUser(self, auser, aplainpassword=0):
        #acmsname,achaptertitle,ausername=storageutil.ASCII_CP1250_To_UTF8(acmsname),storageutil.ASCII_CP1250_To_UTF8(achaptertitle),storageutil.ASCII_CP1250_To_UTF8(ausername)
        oid, uid, username, description = auser.get('_oid', ''), auser.get('uid', ''), auser.get('username', ''), auser.get('description', '')
        password, passwordexpiration = auser.get('password', ''), auser.get('passwordexpiration', 0)
        vcfemail, vcffirstname, vcflastname, vcfphone = auser.get('vcfemail', ''), auser.get('vcffirstname', ''), auser.get('vcflastname', ''), auser.get('vcfphone', '')
        vcflogin, vcfid = auser.get('vcflogin', ''), auser.get('vcfid', '')
        status, variables = auser.get('status', ''), auser.get('variables', '')
        groups = auser.get('groups', {})
        params = auser.get('params', {})
        if aplainpassword:
            password = self.getPasswordHash(username, password)
        if type(groups) == type([]):
            g = {}
            for s in groups:
                g[s] = 4
            groups = g
        ret = ''
        if oid:
            asql = '''
            INSERT INTO public.users (_oid,uid,username,description,
               password,passwordexpiration,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,status,variables,
               groups,params)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING _oid;
         '''
        else:
            asql = '''
            INSERT INTO public.users (uid,username,description,
               password,passwordexpiration,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,status,variables,
               groups,params)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING _oid;
         '''
        try:
            if oid:
                res = self.db.ExecuteSQL(asql, (oid, uid, username, description, password, passwordexpiration, vcfemail, vcffirstname, vcflastname, vcfphone, vcflogin, vcfid, status, variables, json.dumps(groups), json.dumps(params)), atableprefix=1, adefault=[])
            else:
                res = self.db.ExecuteSQL(asql, (uid, username, description, password, passwordexpiration, vcfemail, vcffirstname, vcflastname, vcfphone, vcflogin, vcfid, status, variables, json.dumps(groups), json.dumps(params)), atableprefix=1, adefault=[])
            for arec in res:
                ret = arec[0]
        except psycopg2.IntegrityError, e:
            if e.pgcode == '23505':
                pass    #podwojna wartosc klucza narusza ograniczenie unikalnosci "users_username"
            else:
                raise
            #print 'Exception:',e
            #print 'args',e.args
            #print 'diag',e.diag
            #print 'message',e.message
            #print 'pgcode',e.pgcode
            #print 'pgerror',e.pgerror
            #print dir(e)
        #uuid.uuid4().hex
        return ret

    def getUserByName(self, ausername):
        ret = {}
        asql = '''
         with subquery
         as (
            SELECT 
               _oid,uid,username,description,
               password,passwordexpiration,passwordhistory,passwordlastchange,passwordmustchange,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,
               wwwdisabled,status,created,
               variables,groups,params
            FROM public.users
            WHERE lower(username)=lower(%s)
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'uid',uid,'username',username,'description',description,
            'password',password,'passwordexpiration',passwordexpiration,'passwordhistory',passwordhistory,'passwordlastchange',passwordlastchange,'passwordmustchange',passwordmustchange,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcflogin',vcflogin,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'variables',variables,'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (ausername, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            ret = json.loads(arec[0])[0]
        return ret

    def getUserByOID(self, uoid):
        ret = {}
        asql = '''
         with subquery
         as (
            SELECT 
               _oid,uid,username,description,
               password,passwordexpiration,passwordhistory,passwordlastchange,passwordmustchange,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,
               wwwdisabled,status,created,
               variables,groups,params
            FROM public.users
            WHERE _oid=lower(%s)
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'uid',uid,'username',username,'description',description,
            'password',password,'passwordexpiration',passwordexpiration,'passwordhistory',passwordhistory,'passwordlastchange',passwordlastchange,'passwordmustchange',passwordmustchange,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcflogin',vcflogin,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'variables',variables,'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (uoid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            ret = json.loads(arec[0])[0]
        return ret

    def getUserByFirstUser(self, avcfid):
        if type(avcfid) == type(1):
            avcfid = str(avcfid)
        ret = '[]'
        asql = '''
         with subquery
         as (
            select _oid,username,description,vcfemail,vcffirstname,vcflastname,vcfphone,vcfid,wwwdisabled,status,created,groups,params
            from public.users
            where 
               vcfid=%s
               and params @> '{"firstUser": 1}'::jsonb
               and status<>'U'
            order by created
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (avcfid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                ret = '[]'
            else:
                ret = arec[0]
        return json.loads(ret)

    def getUsersByGroupAdmin(self):
        ret = '[]'
        asql = '''
         with subquery
         as (
            select _oid,username,description,vcfemail,vcffirstname,vcflastname,vcfphone,vcfid,wwwdisabled,status,created,groups,params
            from public.users
            where 
               groups @> '{"%s": 4}'::jsonb
               and status='Z'
            order by created
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''%(startutil.appconfig.IParams['users_admin_group'],)
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                ret = '[]'
            else:
                ret = arec[0]
        return json.loads(ret)

    def getUsersByVCFID(self, avcfid):
        if type(avcfid) == type(1):
            avcfid = str(avcfid)
        ret = []
        asql = '''
         with subquery
         as (
            SELECT 
               _oid,uid,username,description,
               passwordexpiration,passwordlastchange,passwordmustchange,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,
               wwwdisabled,status,created,
               variables,groups,params
            FROM public.users
            WHERE vcfid=%s and status<>'U'
            ORDER BY username
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'uid',uid,'username',username,'description',description,
            'passwordexpiration',passwordexpiration,'passwordlastchange',passwordlastchange,'passwordmustchange',passwordmustchange,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcflogin',vcflogin,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'variables',variables,'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (avcfid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = json.loads(arec[0])
        return ret

    def getUsersByStatus(self, astatus):
        ret = []
        asql = '''
         with subquery
         as (
            SELECT 
               _oid,uid,username,description,
               passwordexpiration,passwordlastchange,passwordmustchange,
               vcfemail,vcffirstname,vcflastname,vcfphone,vcflogin,vcfid,
               wwwdisabled,status,created,
               variables,groups,params
            FROM public.users
            WHERE status=%s
            ORDER BY username
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'uid',uid,'username',username,'description',description,
            'passwordexpiration',passwordexpiration,'passwordlastchange',passwordlastchange,'passwordmustchange',passwordmustchange,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcflogin',vcflogin,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'variables',variables,'groups',groups,'params',params
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (astatus, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = json.loads(arec[0])
        return ret

    def getUsersByAdmin(self):
        ret = '[]'
        asql = '''
         with subquery
         as (
            select _oid,username,description,vcfemail,vcffirstname,vcflastname,vcfphone,vcfid,wwwdisabled,status,created,groups
            from public.users
            order by vcflastname,vcffirstname,username
         )
         select cast(json_agg(json_build_object(
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def removeUser(self, uoid):
        ret = ''
        if not uoid:
            return ret
        asql = '''
         update public.users
         set status ='U'
         where _oid=%s
         returning _oid;
      '''
        res = self.db.ExecuteSQL(asql, (uoid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def deleteUser(self, uoid):
        ret = ''
        if not uoid:
            return ret
        asql = '''
         DELETE FROM public.users
         WHERE _oid=%s
         RETURNING _oid;
      '''
        res = self.db.ExecuteSQL(asql, (uoid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def addUserGroups(self, uoid, groups):
        if type(groups) == type([]):
            g = {}
            for s in groups:
                g[s] = 4
            groups = g
        ret = ''
        asql = '''
         update public.users
         set groups = groups || %s::jsonb
         where _oid=%s
         returning _oid;
      '''
        res = self.db.ExecuteSQL(asql, (json.dumps(groups), uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def removeUserGroup(self, uoid, group):
        ret = ''
        asql = '''
         update public.users
         set groups = groups - %s
         where _oid=%s
         returning _oid;
      '''
        res = self.db.ExecuteSQL(asql, (group, uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def addUserParams(self, uoid, params):
        ret = ''
        asql = '''
         update public.users
         set params = params || %s::jsonb
         where _oid=%s
         returning _oid;
      '''
        res = self.db.ExecuteSQL(asql, (json.dumps(params), uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def removeUserParam(self, uoid, param):
        ret = ''
        asql = '''
         update public.users
         set params = params - %s
         where _oid=%s
         returning _oid;
      '''
        res = self.db.ExecuteSQL(asql, (param, uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def setUserInfo(self, uoid, aname, avalue):
        lfields = ['uid', 'description', 'password', 'passwordexpiration', 'passwordhistory', 'passwordlastchange', 'passwordmustchange', 'vcfemail', 'vcffirstname', 'vcflastname', 'vcfphone', 'vcflogin', 'vcfid', 'wwwdisabled', 'status', 'variables']
        ret = ''
        if aname not in lfields:
            return ret
        ret = ''
        asql = '''
         update public.users
         set %s = %%s
         where _oid=%%s
         returning _oid;
      ''' % (aname, )
        res = self.db.ExecuteSQL(asql, (avalue, uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def setUserPassword(self, uoid, apassword, aplainpassword=0):
        ret = ''
        if aplainpassword:
            asql = '''
            update public.users
            set password = md5(%s::text || '_'::text || lower(username))
            where _oid=%s
            returning _oid;
         '''
        else:
            asql = '''
            update public.users
            set password = %s
            where _oid=%s
            returning _oid;
         '''
        res = self.db.ExecuteSQL(asql, (apassword, uoid), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                break
            ret = arec[0]
        return ret

    def setUserOperation(self, auid, akind, atype='', avalue='', ainfo='', aoidref='', astatus='', aposition=0, anumber1=0, anumber2=0):
        '''
         okind:
            'phone-change','email-change','email',
            'cart-add','cart-update','cart-checkmissing','cart-uncheckmissing','cart-delete','cart-submit','cart-order','cart-unsubmit',
            'template',
            'user-newoperator',
            'user-add',
            'user-confirm',
            'news'
      '''
        ret = ''
        asql = '''
         INSERT INTO public.useroperations (uid,okind,otype,ovalue,oinfo,ooidref,ostatus,oposition,onumber1,onumber2)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
         RETURNING _oid;
      '''
        try:
            res = self.db.ExecuteSQL(asql, (auid, akind, atype, avalue, ainfo, aoidref, astatus, aposition, anumber1, anumber2), atableprefix=1, adefault=[])
            for arec in res:
                ret = arec[0]
        except psycopg2.IntegrityError, e:
            if e.pgcode == '23505':
                pass    #podwojna wartosc klucza narusza ograniczenie unikalnosci "users_username"
            else:
                raise
        return ret

    def getOperationByOID(self, ooid):
        ret = {}
        asql = '''
         select 
           cast(
             coalesce(jsonb_agg(
               jsonb_build_object(
                'ooid',ooid,'ouid',ouid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'oinfo',oinfo,'ooidref',ooidref,'ostatus',ostatus,'ovariables',ovariables,'oparams',oparams,'oposition',oposition,'onumber1',onumber1,'onumber2',onumber2,'odatetime2',odatetime2
               )
             ),'{}') as text
           )
           as result
         from (
           SELECT 
             t1._oid as ooid,t1.uid as ouid,t1.odatetime,t1.okind,t1.otype,t1.ovalue,t1.oinfo,t1.ooidref,t1.ostatus,t1.ovariables,t1.oparams,t1.oposition,t1.onumber1,t1.onumber2,t1.odatetime2
           FROM public.useroperations t1
           where t1._oid=%s
         ) t0;
      '''
        res = self.db.ExecuteSQL(asql, (ooid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            ret = json.loads(arec[0])
            if type(ret) == type([]):
                ret = ret[0]
        return ret

    def setOperationStatus(self, ooid, astatus):
        ret = ''
        asql = '''
         UPDATE public.useroperations SET ostatus=%s
         WHERE _oid=%s
         RETURNING _oid;
      '''
        try:
            res = self.db.ExecuteSQL(asql, (astatus, ooid), atableprefix=1, adefault=[])
            for arec in res:
                ret = arec[0]
        except psycopg2.IntegrityError, e:
            if e.pgcode == '23505':
                pass    #podwojna wartosc klucza narusza ograniczenie unikalnosci "users_username"
            else:
                raise
        return ret

    def getUserLastOperation(self, auid, akind):
        ret = {}
        asql = '''
         with subquery
         as (
            SELECT 
               uid,okind,ovalue,oinfo,ostatus
            FROM public.useroperations
            WHERE uid=lower(%s) and okind=%s
            ORDER BY odatetime DESC
            LIMIT 1
         )
         select cast(json_agg(json_build_object(
            'uid',uid,'kind',okind,'value',ovalue,
            'token',oinfo,'status','ostatus'
         )) as text) as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (auid, akind, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            ret = json.loads(arec[0])[0]
        # $$ zrobic zmiane statusu kodu
        return ret

    def getUsersByOperationsUser(self, auid):
        ret = '[]'
        asql = '''
         with subquery
         as (
           SELECT 
             t1._oid as ooid,t1.odatetime,t1.okind,t1.otype,left(t1.ovalue,80) as ovalue,t1.ostatus
           FROM public.useroperations t1
           where 
             t1.okind in (
               'phone-change','email-change','email',
               'cart-add','cart-update','cart-checkmissing','cart-uncheckmissing','cart-delete','cart-submit','cart-order','cart-unsubmit'
             )
             and t1.uid=%s
           order by t1.odatetime desc
           limit 1000
         )
         select
         cast(
         jsonb_agg(jsonb_build_object(
            'ooid',ooid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'ostatus',ostatus
         ))
         as text)
          as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (auid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def getUsersByOperationsOperator(self, avcfid):
        ret = '[]'
        asql = '''
         with subquery
         as (
           SELECT 
             t1._oid as ooid,t1.odatetime,t1.okind,t1.otype,left(t1.ovalue,80) as ovalue,t1.ostatus
             ,t1.uid as ouid,
             t1.oinfo,t1.ooidref,t1.ovariables,t1.oparams,t1.oposition,t1.onumber1,t1.onumber2,t1.odatetime2,
             t2._oid,t2.uid,t2.username,t2.description,
             --t2.password,t2.passwordexpiration,t2.passwordhistory,t2.passwordlastchange,t2.passwordmustchange,t2.variables,t2.params
             t2.vcfemail,t2.vcffirstname,t2.vcflastname,t2.vcfphone,t2.vcflogin,t2.vcfid,t2.wwwdisabled,t2.status,t2.created,t2.groups
           FROM public.useroperations t1
           left join public.users t2 on t1.uid=t2._oid
           where 
             t1.okind in (
               'phone-change','email-change','email',
               'cart-add','cart-update','cart-checkmissing','cart-uncheckmissing','cart-delete','cart-submit','cart-order','cart-unsubmit'
             ) -- template
             and t2.vcfid=%s
           order by t1.odatetime desc
           limit 1000
         )
         select
         cast(
         jsonb_agg(jsonb_build_object(
            'ooid',ooid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'ostatus',ostatus
            ,'ouid',ouid,'oinfo',oinfo,'ooidref',ooidref,'ovariables',ovariables,'oparams',oparams,'oposition',oposition,'onumber1',onumber1,'onumber2',onumber2,'odatetime2',odatetime2,
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups
         ))
         as text)
          as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, (avcfid, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def getUsersByOperationsAdmin(self):
        ret = '[]'
        asql = '''
         with subquery
         as (
           SELECT 
             t1._oid as ooid,t1.odatetime,t1.okind,t1.otype,left(t1.ovalue,80) as ovalue,t1.ostatus
             ,t1.uid as ouid,
             t1.oinfo,t1.ooidref,t1.ovariables,t1.oparams,t1.oposition,t1.onumber1,t1.onumber2,t1.odatetime2,
             t2._oid,t2.uid,t2.username,t2.description,
             --t2.password,t2.passwordexpiration,t2.passwordhistory,t2.passwordlastchange,t2.passwordmustchange,t2.variables,t2.params
             t2.vcfemail,t2.vcffirstname,t2.vcflastname,t2.vcfphone,t2.vcflogin,t2.vcfid,t2.wwwdisabled,t2.status,t2.created,t2.groups
           FROM public.useroperations t1
           left join public.users t2 on t1.uid=t2._oid
           where 
             t1.okind in (
               'phone-change','email-change','email',
               'cart-add','cart-update','cart-checkmissing','cart-uncheckmissing','cart-delete','cart-submit','cart-order','cart-unsubmit'
             ) -- template
           order by t1.odatetime desc
           limit 1000
         )
         select
         cast(
         jsonb_agg(jsonb_build_object(
            'ooid',ooid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'ostatus',ostatus
            ,'ouid',ouid,'oinfo',oinfo,'ooidref',ooidref,'ovariables',ovariables,'oparams',oparams,'oposition',oposition,'onumber1',onumber1,'onumber2',onumber2,'odatetime2',odatetime2,
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups
         ))
         as text)
          as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def getUsersByOperations(self):
        ret = '[]'
        asql = '''
         with subquery
         as (
           SELECT 
             t1._oid as ooid,t1.odatetime,t1.okind,t1.otype,left(t1.ovalue,80) as ovalue,t1.ostatus
             ,t1.uid as ouid,
             t1.oinfo,t1.ooidref,t1.ovariables,t1.oparams,t1.oposition,t1.onumber1,t1.onumber2,t1.odatetime2,
             t2._oid,t2.uid,t2.username,t2.description,
             --t2.password,t2.passwordexpiration,t2.passwordhistory,t2.passwordlastchange,t2.passwordmustchange,t2.variables,t2.params
             t2.vcfemail,t2.vcffirstname,t2.vcflastname,t2.vcfphone,t2.vcflogin,t2.vcfid,t2.wwwdisabled,t2.status,t2.created,t2.groups
           FROM public.useroperations t1
           left join public.users t2 on t1.uid=t2._oid
           where 
             t1.okind in (
               'phone-change','email-change','email',
               'cart-add','cart-update','cart-checkmissing','cart-uncheckmissing','cart-delete','cart-submit','cart-order','cart-unsubmit',
               'template','news',
               'user-newoperator','user-add','user-confirm'
             ) 
           order by t1.odatetime desc
           limit 2000
         )
         select
         cast(
         jsonb_agg(jsonb_build_object(
            'ooid',ooid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'ostatus',ostatus
            ,'ouid',ouid,'oinfo',oinfo,'ooidref',ooidref,'ovariables',ovariables,'oparams',oparams,'oposition',oposition,'onumber1',onumber1,'onumber2',onumber2,'odatetime2',odatetime2,
            '_oid',_oid,'username',username,'description',description,
            'vcfemail',vcfemail,'vcffirstname',vcffirstname,'vcflastname',vcflastname,'vcfphone',vcfphone,'vcfid',vcfid,
            'wwwdisabled',wwwdisabled,'status',status,'created',created,
            'groups',groups
         ))
         as text)
          as result
         from subquery;
      '''
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def getTextTemplateByKind(self, akind):
        ret = {}
        asql = '''
         select 
           cast(
             coalesce(jsonb_agg(
               jsonb_build_object(
                'ooid',ooid,'ouid',ouid,'odatetime',odatetime,'okind',okind,'otype',otype,'ovalue',ovalue,'oinfo',oinfo,'ooidref',ooidref,'ostatus',ostatus,'ovariables',ovariables,'oparams',oparams,'oposition',oposition,'onumber1',onumber1,'onumber2',onumber2,'odatetime2',odatetime2
               )
             ),'{}') as text
           )
           as result
         from (
           SELECT 
             t1._oid as ooid,t1.uid as ouid,t1.odatetime,t1.okind,t1.otype,t1.ovalue,t1.oinfo,t1.ooidref,t1.ostatus,t1.ovariables,t1.oparams,t1.oposition,t1.onumber1,t1.onumber2,t1.odatetime2
           FROM public.useroperations t1
           where t1.okind='template' and t1.otype=%s
           order by t1.odatetime desc
           limit 1
         ) t0;
      '''
        res = self.db.ExecuteSQL(asql, (akind, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            ret = json.loads(arec[0])
            if type(ret) == type([]):
                ret = ret[0]
        return ret

    def setTextTemplateByKind(self, auid, akind, atext, astatus):
        ret = ''
        asql = '''
         INSERT INTO public.useroperations (uid,okind,otype,ovalue,ostatus)
         VALUES (%s,'template',%s,%s,%s)
         RETURNING _oid;
      '''
        try:
            res = self.db.ExecuteSQL(asql, (auid, akind, atext, astatus), atableprefix=1, adefault=[])
            for arec in res:
                ret = arec[0]
        except psycopg2.IntegrityError, e:
            if e.pgcode == '23505':
                pass    #podwojna wartosc klucza narusza ograniczenie unikalnosci "users_username"
            else:
                raise
        return ret

    def getPosts(self, amode, aaction):
        ret = '[]'
        if amode == 'all':
            asql = '''
            with subquery
            as (
              SELECT 
                t1._oid,t1.uid,t1.odatetime,t1.okind,t1.otype,t1.ostatus,
                t1.ooidref,t1.odatetimefrom,t1.odatetimeto,t1.odatetimeviewfrom,t1.odatetimeviewto,t1.otitle,t1.osubtitle,t1.oauthor,t1.oabstract,t1.otext,t1.ocomment,t1.oprioritydisplay,t1.opriorityitem,t1.oposition,
                t1.oparams,t1.ocategories
              FROM public.usercontent t1
              order by t1.odatetime desc
              limit 1000
            )
            select
            cast(
            jsonb_agg(jsonb_build_object(
                '_oid',_oid,'uid',uid,'odatetime',odatetime,'okind',okind,'otype',otype,'ostatus',ostatus,
                'ooidref',ooidref,'odatetimefrom',odatetimefrom,'odatetimeto',odatetimeto,'odatetimeviewfrom',odatetimeviewfrom,'odatetimeviewto',odatetimeviewto,
                'otitle',otitle,'osubtitle',osubtitle,'oauthor',oauthor,'oabstract',oabstract,'otext',otext,'ocomment',ocomment,
                'oprioritydisplay',oprioritydisplay,'opriorityitem',opriorityitem,'oposition',oposition,
                'oparams',oparams,'ocategories',ocategories
            ))
            as text) 
            as result
            from subquery;
         '''
            res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        else:
            asql = '''
            with subquery
            as (
              SELECT 
                t1._oid,t1.uid,t1.odatetime,t1.okind,t1.otype,t1.ostatus,
                t1.ooidref,t1.odatetimefrom,t1.odatetimeto,t1.odatetimeviewfrom,t1.odatetimeviewto,t1.otitle,t1.osubtitle,t1.oauthor,t1.oabstract,t1.otext,t1.ocomment,t1.oprioritydisplay,t1.opriorityitem,t1.oposition,
                t1.oparams,t1.ocategories
              FROM public.usercontent t1
              where
                t1.okind=%s
                and t1.opriorityitem<>'00'
                and t1.odatetimeviewfrom<now() and t1.odatetimeviewto>now()
                and t1.ostatus='Z1'
              order by t1.odatetimefrom desc
              limit 1000
            )
            select
            cast(
            jsonb_agg(jsonb_build_object(
                '_oid',_oid,'uid',uid,'odatetime',odatetime,'okind',okind,'otype',otype,'ostatus',ostatus,
                'ooidref',ooidref,'odatetimefrom',odatetimefrom,'odatetimeto',odatetimeto,'odatetimeviewfrom',odatetimeviewfrom,'odatetimeviewto',odatetimeviewto,
                'otitle',otitle,'osubtitle',osubtitle,'oauthor',oauthor,'oabstract',oabstract,'otext',otext,'ocomment',ocomment,
                'oprioritydisplay',oprioritydisplay,'opriorityitem',opriorityitem,'oposition',oposition,
                'oparams',oparams,'ocategories',ocategories
            ))
            as text) 
            as result
            from subquery;
         '''
            res = self.db.ExecuteSQL(asql, (amode, ), atableprefix=1, adefault=[])
        for arec in res:
            if arec[0] is None:
                return ret
            #ret=json.loads(arec[0])[0]
            ret = arec[0]
        return ret

    def postAddUpdate(self, auid, aoid, aaction, aokind, aostatus, aodatetimefrom, aodatetimeto, aodatetimeviewfrom, aodatetimeviewto, aotitle, aosubtitle, aoauthor, aoabstract, aotext, aocomment, aoprioritydisplay, aopriorityitem):
        ret = ''
        aparams = ()
        if aaction == 'new':
            asql = '''
            INSERT INTO public.usercontent (uid,okind,ostatus,odatetimefrom,odatetimeto,odatetimeviewfrom,odatetimeviewto,otitle,osubtitle,oauthor,oabstract,otext,ocomment,oprioritydisplay,opriorityitem)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING _oid;
         '''
            aparams = (auid, aokind, aostatus, aodatetimefrom, aodatetimeto, aodatetimeviewfrom, aodatetimeviewto, aotitle, aosubtitle, aoauthor, aoabstract, aotext, aocomment, aoprioritydisplay, aopriorityitem)
        elif aaction == 'update':
            asql = '''
            UPDATE public.usercontent SET
            uid=%s,
            odatetime=now(),
            okind=%s,
            ostatus=%s,
            odatetimefrom=%s,
            odatetimeto=%s,
            odatetimeviewfrom=%s,
            odatetimeviewto=%s,
            otitle=%s,
            osubtitle=%s,
            oauthor=%s,
            oabstract=%s,
            otext=%s,
            ocomment=%s,
            oprioritydisplay=%s,
            opriorityitem=%s
            WHERE _oid=%s
            RETURNING _oid;
         '''
            aparams = (auid, aokind, aostatus, aodatetimefrom, aodatetimeto, aodatetimeviewfrom, aodatetimeviewto, aotitle, aosubtitle, aoauthor, aoabstract, aotext, aocomment, aoprioritydisplay, aopriorityitem, aoid)
        else:
            pass
        try:
            res = self.db.ExecuteSQL(asql, aparams, atableprefix=1, adefault=[])
            for arec in res:
                ret = arec[0]
        except psycopg2.IntegrityError, e:
            if e.pgcode == '23505':
                pass    #podwojna wartosc klucza narusza ograniczenie unikalnosci "users_username"
            else:
                raise
        return ret
