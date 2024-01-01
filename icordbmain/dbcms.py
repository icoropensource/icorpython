# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBCMS(object):

    def __init__(self, adb):
        self.db = adb

    ### CMS:
    def SetCMSData(self, cmsid, name, value):
        name, value = storageutil.CP1250_To_UTF8(name), storageutil.CP1250_To_UTF8(value)
        cur = self.db.GetCursor()
        try:
            asql = '''
            WITH upsert AS (UPDATE %s.cmsdata SET value=%%s WHERE cmsid=%%s and name=%%s RETURNING *) 
            INSERT INTO %s.cmsdata (cmsid,name,value) SELECT %%s,%%s,%%s WHERE NOT EXISTS (SELECT * FROM upsert);
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql, (value, cmsid, name, cmsid, name, value))
        finally:
            self.db.CloseCursor(cur)

    def GetCMSData(self, cmsid, name):
        name = storageutil.CP1250_To_UTF8(name)
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT value from %s.cmsdata where cmsid=%%s and name=%%s;
         ''' % (self.db.schema, )
            cur.execute(asql, (cmsid, name, ))
            res = cur.fetchall()
            for arec in res:
                ret = storageutil.UTF8_To_CP1250(arec[0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SetCMSChapterState(self, acmsid=0, acmsname='', achapterid=0, achaptertitle='', apriority='N03', auid=0, ausername='', aoperationtype='generate', aitemoid='', astatus='N'):
        acmsname, achaptertitle, ausername = storageutil.ASCII_CP1250_To_UTF8(acmsname), storageutil.ASCII_CP1250_To_UTF8(achaptertitle), storageutil.ASCII_CP1250_To_UTF8(ausername)
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            INSERT INTO %s.cmschapteroperation (chapterid,uid,username,priority,operationtype,itemoid,status) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING _oid;
         ''' % (self.db.schema, )
            cur.execute(asql, (achapterid, auid, ausername, apriority, aoperationtype, aitemoid, astatus, ))
            res = cur.fetchall()
            for arec in res:
                ret = storageutil.UTF8_To_CP1250(arec[0])
            asql = '''
            INSERT INTO %s.cmschapterstate (chapterid,title,cmsid,cmsname,priority,operationoid,status,created)
                VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,current_timestamp)
                ON CONFLICT (chapterid) DO UPDATE SET 
                  chapterid=EXCLUDED.chapterid,
                  title=EXCLUDED.title,
                  cmsid=EXCLUDED.cmsid,
                  cmsname=EXCLUDED.cmsname,
                  priority=EXCLUDED.priority,
                  operationoid=EXCLUDED.operationoid,
                  status=EXCLUDED.status,
                  created=EXCLUDED.created
            RETURNING _oid;
         ''' % (self.db.schema, )
            cur = self.db.GetCursor(cur)
            cur.execute(asql, (achapterid, achaptertitle, acmsid, acmsname, apriority, ret, astatus))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetCMSChapterGenerateCount(self):
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.cmschapteroperation
            SET STATUS = 'S'
            WHERE _oid IN (
            		SELECT co._oid
            		FROM %s.cmschapteroperation co
            		INNER JOIN %s.cmschapterstate cs ON cs.chapterid = co.chapterid
            		WHERE co.operationtype = 'generate'
            			AND co.STATUS = 'N'
            			AND cs.operationoid<>co._oid
            		);

            UPDATE %s.cmschapteroperation
            SET STATUS = 'N1'
            WHERE _oid IN (
            		SELECT co._oid
            		FROM %s.cmschapteroperation co
            		INNER JOIN %s.cmschapterstate cs ON cs.operationoid = co._oid
            		WHERE co.operationtype = 'generate'
            			AND co.STATUS = 'N'
            			AND cs.STATUS = 'N'
            		);
         ''' % (self.db.schema, self.db.schema, self.db.schema, self.db.schema, self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            ret = cur.rowcount
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetCMSChapterGenerateNext(self):
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT cs.cmsid,co.chapterid,co._oid
            FROM %s.cmschapteroperation co
            INNER JOIN %s.cmschapterstate cs ON cs.operationoid = co._oid
            WHERE co.operationtype = 'generate'
            	AND co.STATUS = 'N1'
            	AND cs.STATUS = 'N'
            ORDER BY co.priority, co.created DESC
            LIMIT 1;
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = (arec[0], arec[1], storageutil.UTF8_To_CP1250(arec[2]))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SetCMSChapterGenerateFinished(self, aoperationoid, atime):
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.cmschapteroperation set finished=current_timestamp, timeoperation=%%s, status='G1' where _oid=%%s;
            update %s.cmschapterstate set status='Z' where operationoid=%%s;
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql, (atime, aoperationoid, aoperationoid, ))
            ret = cur.rowcount
        finally:
            self.db.CloseCursor(cur)
        return ret
