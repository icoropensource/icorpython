# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBExecutor(object):

    def __init__(self, adb):
        self.db = adb

    ### Executor:
    def AddExecutorMethod(self, CID, amethodname, FieldName, OID, Value, UID, aparallel, aqueued, status, priority='N03'):
        amethodname, FieldName, Value, status, priority = storageutil.CP1250_To_UTF8(amethodname), storageutil.CP1250_To_UTF8(FieldName), storageutil.CP1250_To_UTF8(Value), storageutil.CP1250_To_UTF8(status), storageutil.CP1250_To_UTF8(priority)
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.executormethods set status='Skipped' where cid=%%s and name=%%s and fieldname=%%s and oid=%%s and value=%%s and status in ('Processing','Ready');
         ''' % (self.db.schema, )
            cur = self.db.GetCursor(cur)
            cur.execute(asql, (CID, amethodname, FieldName, OID, Value))
            asql = '''
            INSERT INTO %s.executormethods (cid,name,fieldname,oid,value,uid,isparallel,isqueued,status,priority) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING meid;
         ''' % (self.db.schema, )
            cur.execute(asql, (CID, amethodname, FieldName, OID, Value, UID, aparallel, aqueued, status, priority))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetExecutorMethodReadyCount(self, afirst=0):
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.executormethods set status='Processing' where status='Ready';
         ''' % (self.db.schema, )
            cur.execute(asql)
            ret = cur.rowcount
            if afirst:
                cur = self.db.GetCursor(cur)
                asql = '''
               select (select count(*) from %s.executormethods where status='Processing') as pc,(select count(*) from %s.executormethods where status='Working') as wc;
            ''' % (self.db.schema, self.db.schema, )
                cur.execute(asql)
                res = cur.fetchall()
                for arec in res:
                    ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetExecutorMethod(self, pid=-1):
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.executormethods set status='Working',eventtime_working=current_timestamp,pid=%%s where meid in (
               select t2.meid from %s.executormethods t2 
               where 
               	t2.status='Processing'
               	and not exists (
               		select t3.meid 
               		from %s.executormethods t3
               		where
               			t2.cid=t3.cid and
               			t2.name=t3.name and
               			t2.fieldname=t3.fieldname and
               			t2.oid=t3.oid and
               			t2.value=t3.value and
               			t3.status='Working'
               	)
               order by t2.priority,t2.eventtime 
               limit 1
               )
            returning meid as "MID",cid as "CID",name as "Name",fieldname as "FieldName",oid as "OID",value as "Value",uid as "UID",isparallel as "IsParallel",isqueued as "IsQueued",eventtime as "EventTime",status as "Status",pid as "PID";
         ''' % (self.db.schema, self.db.schema, self.db.schema,
                )
            cur.execute(asql, (pid, ))
            res = cur.fetchall()
            for arec in res:
                ret={
                   'MID':arec[0],
                   'CID':arec[1],
                   'Name':storageutil.UTF8_To_CP1250(arec[2]), #unicode!
                   'FieldName':storageutil.UTF8_To_CP1250(arec[3]), #unicode!
                   'OID':arec[4],
                   'Value':storageutil.UTF8_To_CP1250(arec[5]), #unicode!
                   'UID':arec[6],
                   'IsParallel':arec[7],
                   'IsQueued':arec[8],
                   'EventTime':arec[9], #datetime.datetime
                   'Status':storageutil.UTF8_To_CP1250(arec[10]), #unicode!
                   'PID':arec[11],
                } # yapf: disable
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetExecutorMethodByID(self, meid):
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            select meid as "MID",cid as "CID",name as "Name",fieldname as "FieldName",oid as "OID",value as "Value",uid as "UID",isparallel as "IsParallel",isqueued as "IsQueued",
            eventtime as "EventTime",
            eventtime_ready as "EventTimeReady",
            eventtime_deleted as "EventTimeDeleted",
            eventtime_working as "EventTimeWorking",
            eventtime_done as "EventTimeDone",
            status as "Status",
            pid as "PID"
            from %s.executormethods where meid=%%s
         ''' % (self.db.schema, )
            cur.execute(asql, (meid, ))
            res = cur.fetchall()
            for arec in res:
                ret={
                   'MID':arec[0],
                   'CID':arec[1],
                   'Name':storageutil.UTF8_To_CP1250(arec[2]), #unicode!
                   'FieldName':storageutil.UTF8_To_CP1250(arec[3]), #unicode!
                   'OID':arec[4],
                   'Value':storageutil.UTF8_To_CP1250(arec[5]), #unicode!
                   'UID':arec[6],
                   'IsParallel':arec[7],
                   'IsQueued':arec[8],
                   'EventTime':arec[9], #datetime.datetime
                   'EventTimeReady':arec[10], #datetime.datetime
                   'EventTimeDeleted':arec[11], #datetime.datetime
                   'EventTimeWorking':arec[12], #datetime.datetime
                   'EventTimeDone':arec[13], #datetime.datetime
                   'Status':storageutil.UTF8_To_CP1250(arec[14]), #unicode!
                   'PID':arec[15],
                } # yapf: disable
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SetExecutorMethodStatus(self, meid, status, result='', output=''):
        """status:
            Ready
            Deleted
            Working
            Done
      """
        status, result, output = storageutil.CP1250_To_UTF8(status), storageutil.CP1250_To_UTF8(result), storageutil.CP1250_To_UTF8(output)
        cur = self.db.GetCursor()
        try:
            afield = ''
            if status in ['Ready', 'Deleted', 'Working', 'Done']:
                afield = ',eventtime_%s=current_timestamp' % (status.lower(), )
            if status == 'Done':
                asql = '''
               update %s.executormethods set status=%%s,result=%%s,output=%%s%s where meid=%%s;
            ''' % (self.db.schema, afield)
                if not result:
                    result = ''
                if not output:
                    output = ''
                cur.execute(asql, (status, result, output, meid))
            else:
                asql = '''
               update %s.executormethods set status=%%s%s where meid=%%s;
            ''' % (self.db.schema, afield)
                cur.execute(asql, (status, meid))
        finally:
            self.db.CloseCursor(cur)

    def GetExecutorMethodIDByStatus(self, status):
        status = storageutil.CP1250_To_UTF8(status)
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT meid from %s.executormethods where status=%%s order by eventtime;
         ''' % (self.db.schema, )
            cur.execute(asql, (status, ))
            res = cur.fetchall()
            for arec in res:
                ret.append(arec[0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def ExecutorMethodCheckProcessing(self):
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.executormethods SET status='Ready' WHERE status='Working';
         ''' % (self.db.schema, )
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return
