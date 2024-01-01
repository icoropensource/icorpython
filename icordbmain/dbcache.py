# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBCache(object):

    def __init__(self, adb):
        self.db = adb

    ### Cache:
    def SetCacheFieldValue(self, f, o, v):
        v = storageutil.ASCII_CP1250_To_UTF8(v)
        cur = self.db.GetCursor()
        try:
            asql = '''
            WITH upsert AS (UPDATE %s.fieldvalues SET v=%%s WHERE f=%%s and o=%%s RETURNING *) 
            INSERT INTO %s.fieldvalues (f,o,v) SELECT %%s,%%s,%%s WHERE NOT EXISTS (SELECT * FROM upsert);
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql, (v, f, o, f, o, v))
        finally:
            self.db.CloseCursor(cur)

    def GetCacheFieldValue(self, f, o):
        ret = None
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT v from %s.fieldvalues where f=%%s and o=%%s;
         ''' % (self.db.schema, )
            cur.execute(asql, (f, o, ))
            res = cur.fetchall()
            for arec in res:
                ret = storageutil.UTF8_To_CP1250(arec[0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def DeleteCacheFieldValue(self, f, o):
        cur = self.db.GetCursor()
        try:
            asql = '''
            DELETE FROM %s.fieldvalues where f=%%s and o=%%s;
         ''' % (self.db.schema, )
            cur.execute(asql, (f, o))
        finally:
            self.db.CloseCursor(cur)

    def Clear(self):
        pass
