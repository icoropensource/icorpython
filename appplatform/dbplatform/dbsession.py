# -*- coding: utf-8 -*-
import codecs
import thread
import Queue
import types

import appplatform.storageutil as storageutil
import appplatform.dbplatform.dbsessioninit as dbsessioninit

# public.sessiontokens - status:
#   A - aktywny
#   L - wylogowany


class DBSessionUtil(object):

    def __init__(self, adb):
        self.db = adb

    def initSchema(self):
        print 'Init DB: session'
        ainit = dbsessioninit.DBSessionUtilInit(self.db)
        ainit.initSchema()

    def checkValidSessionToken(self, stoken):
        ret = False
        asql = '''
         select * from public.sessiontokens where _oid='%s' and status='A';
      ''' % (stoken, )
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        if res:
            ret = True
        return ret

    def setTokenStatus(self, stoken, astatus):
        ret = False
        asql = '''
         update public.sessiontokens set status='%s' where _oid='%s' returning _oid;
      ''' % (astatus, stoken, )
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        if res:
            ret = True
        return ret

    def getSessionTokenBySessionID(self, swhere):
        ret = ''
        asql = '''
         select si.tokenid 
         from public.sessions si
         left join public.sessiontokens st on st._oid=si.tokenid
         where 
         si.sessionid in (%s)
         and si.status='A'
         and st.status='A'
         order by si._datetime desc
         limit 1;
      ''' % (swhere, )
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            ret = storageutil.UTF8_To_CP1250(arec[0])
        return ret

    def getSessionValue(self, stoken, aname, adefault=''):
        aname = storageutil.CP1250_To_UTF8(aname.lower())
        ret = adefault
        asql = '''
         select valuetype,value from public.sessionvalues 
         where
         tokenid=%s
         and valuename=%s
         and status='A'
         order by created desc
         limit 1;
      '''
        res = self.db.ExecuteSQL(asql, (stoken, aname), atableprefix=1, adefault=[])
        for arec in res:
            atype, ret = storageutil.UTF8_To_CP1250(arec[0]), storageutil.UTF8_To_CP1250(arec[1])
            if atype in ['String', 'Date', 'Boolean']:
                pass
            elif atype in ['Byte', 'Integer', 'Long']:
                ret = int(ret)
            elif atype in ['Single', 'Double', 'Currency', 'Decimal']:
                ret = float(ret)
            elif atype == 'Empty':
                ret = None
        return ret

    def setSessionValue(self, stoken, aname, avalue, atimer=None):
        aname = storageutil.CP1250_To_UTF8(aname.lower())
        ret = ''
        tname = ''
        if isinstance(avalue, types.StringTypes):
            tname = 'String'
            #print 'setSessionValue: 1',stoken,aname,type(avalue),avalue
            avalue = storageutil.CP1250_To_UTF8(avalue)
        elif type(avalue) == type(u''):
            tname = 'String'
            #print 'setSessionValue: 2',stoken,aname,type(avalue),avalue
        elif type(avalue) == type(1):
            tname = "Integer"
            #print 'setSessionValue: 3',stoken,aname,type(avalue),avalue
            avalue = storageutil.CP1250_To_UTF8(str(avalue))
        elif type(avalue) == type(1.1):
            tname = "Double"
            #print 'setSessionValue: 4',stoken,aname,type(avalue),avalue
            avalue = storageutil.CP1250_To_UTF8(str(avalue))
        else:
            tname = 'String'
            #print 'setSessionValue: 5',stoken,aname,type(avalue),avalue
            avalue = storageutil.CP1250_To_UTF8(str(avalue))
        #print '   SessionValue: E',stoken,aname,tname,avalue
        asql = """
         INSERT INTO public.sessionvalues (tokenid, status, valuename, valuetype, value, _datetime) 
            VALUES ( %s , 'A' , %s , %s , %s , current_timestamp )
            ON CONFLICT (tokenid,valuename) DO UPDATE SET valuetype=EXCLUDED.valuetype, value=EXCLUDED.value, _datetime=EXCLUDED._datetime;
      """
        self.db.ExecuteSQL(asql, (stoken, aname, tname, avalue), atableprefix=1, anoresult=1, atimer=atimer, adefault=[])
        return ret

    def getSessionNewToken(self):
        ret = ''
        asql = '''
         INSERT INTO public.sessiontokens (status) VALUES ('A') RETURNING _oid;
      '''
        res = self.db.ExecuteSQL(asql, atableprefix=1, adefault=[])
        for arec in res:
            ret = arec[0]
        return ret

    def getSessionsBySessionID(self, lwhere):
        pass

    def setSessionToken(self, lsessions, stoken):
        pass
        #for asessionid in lsessions:
        #   pass
