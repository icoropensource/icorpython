# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBSyncFiles(object):

    def __init__(self, adb):
        self.db = adb

    ### SyncFiles:
    def SyncFilesOpen(self, filename, status, pathpriority='N03'):
        #filename,status=storageutil.CP1250_To_UTF8(filename),storageutil.CP1250_To_UTF8(status)
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            INSERT INTO %s.syncfiles (dstpath,status,pathpriority) VALUES (%%s,%%s,%%s) RETURNING _oid;
         ''' % (self.db.schema, )
            cur.execute(asql, (filename, status, pathpriority, ))
            res = cur.fetchall()
            for arec in res:
                ret = storageutil.UTF8_To_CP1250(arec[0])
            asql = '''
            INSERT INTO %s.syncpaths (dstpath, status, srcoid, pathpriority, created)
                VALUES (%%s, %%s, %%s, %%s, current_timestamp)
                ON CONFLICT (dstpath) DO UPDATE SET status=EXCLUDED.status, srcoid=EXCLUDED.srcoid, pathpriority=EXCLUDED.pathpriority, created=EXCLUDED.created
            RETURNING _oid;
         ''' % (self.db.schema, )
            cur = self.db.GetCursor(cur)
            cur.execute(asql, (filename, status, ret, pathpriority))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SyncFilesClose(self, oid, srcpath, closed, filesize, firstwrite, writecnt, writemax, timesave, digest, pathpriority, status):
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.syncfiles SET srcpath=%%s,closed=%%s,filesize=%%s,firstwrite=%%s,writecnt=%%s,writemax=%%s,timesave=%%s,digest=%%s,status=%%s WHERE _oid=%%s;
            UPDATE %s.syncpaths SET status='C2', pathpriority=%%s WHERE srcoid=%%s AND digestcopied<>%%s;
         ''' % (self.db.schema, self.db.schema, )
            cur.execute(asql, (srcpath, closed, filesize, firstwrite, writecnt, writemax, timesave, digest, status, oid, pathpriority, oid, digest))
        finally:
            self.db.CloseCursor(cur)

    def SyncFilesSetPriority(self, oid, pathpriority):
        cur = self.db.GetCursor()
        try:
            asql = '''
            UPDATE %s.syncpaths SET pathpriority=%%s WHERE srcoid=%%s;
         ''' % (self.db.schema, )
            cur.execute(asql, (pathpriority, oid))
        finally:
            self.db.CloseCursor(cur)

    def SyncFilesGetFiles(self):
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT sp._oid, sp.dstpath,sf._oid,sf.srcpath,sf.created,sf.digest
            FROM %s.syncpaths AS sp
            LEFT JOIN %s.syncfiles AS sf ON sf._oid = sp.srcoid
            WHERE sp.STATUS = 'C2' and sf.status='C2'
            ORDER BY sp.pathpriority,sf.created desc
            LIMIT 4000
         ''' % (self.db.schema, self.db.schema)
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret.append([storageutil.UTF8_To_CP1250(arec[0]), storageutil.UTF8_To_CP1250(arec[1]), storageutil.UTF8_To_CP1250(arec[2]), storageutil.UTF8_To_CP1250(arec[3]), arec[4], storageutil.UTF8_To_CP1250(arec[5])])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SyncFilesUpdateResults(self, results):
        cur = self.db.GetCursor()
        try:
            for oid, srcpath, dstpath, created, adt, status, copystart, copyfinish, spoid, digest in results:
                #dstpath=storageutil.ASCII_CP1250_To_UTF8(dstpath)
                asql = '''
               UPDATE %s.syncfiles SET
                  copystart=%%s,
                  copyfinish=%%s,
                  timecopy=%%s,
                  status=%%s
               WHERE _oid=%%s;
               UPDATE %s.syncpaths SET
                  digestcopied=%%s,
                  status=%%s,
                  created=%%s
               WHERE srcoid=%%s;
            ''' % (self.db.schema, self.db.schema)
                cur.execute(asql, (copystart, copyfinish, adt, status, oid, digest, status, created, oid))
        finally:
            self.db.CloseCursor(cur)

    def SyncFilesGetOldFiles(self):
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT 
            _oid,srcpath
            FROM %s.syncfiles
            WHERE 
            status='C4' AND statusdelete=''
            ORDER BY created LIMIT 4000;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret.append([storageutil.UTF8_To_CP1250(arec[0]), storageutil.UTF8_To_CP1250(arec[1])])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def SyncFilesStoreRemoveOldFilesResults(self, files):
        cur = self.db.GetCursor()
        try:
            for oid, status in files:
                asql = '''
               UPDATE %s.syncfiles SET statusdelete=%%s WHERE _oid=%%s;
            ''' % (self.db.schema, )
                cur.execute(asql, (status, oid))
        finally:
            self.db.CloseCursor(cur)

    def SyncFilesMoveProcessedFiles(self):
        return
        cur = self.db.GetCursor()
        try:
            asql = '''
            INSERT INTO %s.syncfilesarchive (_oid,srcpath,dstpath,created,closed,copystart,copyfinish,filesize,firstwrite,writecnt,writemax,timesave,timecopy,status,statusdelete) 
            SELECT _oid,srcpath,dstpath,created,closed,copystart,copyfinish,filesize,firstwrite,writecnt,writemax,timesave,timecopy,status,statusdelete
            FROM %s.syncfiles WHERE status='C4' AND statusdelete='D2';
            DELETE FROM %s.syncfiles WHERE status='C4' AND statusdelete='D2';
         ''' % (self.db.schema, self.db.schema, self.db.schema)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
