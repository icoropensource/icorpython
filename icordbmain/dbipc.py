# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBIPC(object):

    def __init__(self, adb):
        self.db = adb

    ### IPC:
    def SemaphoreSet(self, aname, amaxvalue):
        aname = storageutil.CP1250_To_UTF8(aname)
        cur = self.db.GetCursor()
        try:
            asql = '''
            WITH upsert AS (UPDATE %s.semaphores SET value=%%s WHERE name=%%s RETURNING *) 
            INSERT INTO %s.semaphores (name,value) SELECT %%s,%%s WHERE NOT EXISTS (SELECT * FROM upsert);
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql, (amaxvalue, aname, aname, amaxvalue))
        finally:
            self.db.CloseCursor(cur)

    def SemaphoreAcquire(self, aname):
        aname = storageutil.CP1250_To_UTF8(aname)
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.semaphores SET value=value-1 WHERE name=%%s and value>0 RETURNING value;
         ''' % (self.db.schema, )
            cur.execute(asql, (aname, ))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SemaphoreRelease(self, aname):
        aname = storageutil.CP1250_To_UTF8(aname)
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.semaphores SET value=value+1 WHERE name=%%s RETURNING value;
         ''' % (self.db.schema, )
            cur.execute(asql, (aname, ))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SemaphoreInfo(self, aname):
        aname = storageutil.CP1250_To_UTF8(aname)
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT value from %s.semaphores where name=%%s;
         ''' % (self.db.schema, )
            cur.execute(asql, (aname, ))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret
