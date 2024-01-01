# -*- coding: utf-8 -*-
import sys
import os
import time
import re
import types
try:
    import json
except:
    import simplejson as json

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil

import psycopg2
import psycopg2.pool
import psycopg2.extensions

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class TransactionResult(Exception):

    def __init__(self, mode, cursor=None, info=''):
        self.mode = mode
        self.cursor = cursor
        self.info = info

    def __str__(self):
        return 'Transaction: %s - %s' % (self.mode, self.info)


class DBTransaction(object):

    def __init__(self, db):
        self.db = db
        self.cursor = None

    def __enter__(self):
        self.cursor = self.db.GetCursor(aautocommit=False)
        return self

    def __exit__(self, etype, evalue, etraceback):
        # print 'transaction exit:',etype,evalue,etraceback
        if etype is TransactionResult:
            acursor = evalue.cursor
            if acursor is None:
                acursor = self.cursor
            if evalue.mode == 'rollback':
                if acursor is not None:
                    acursor.connection.rollback()
            elif evalue.mode == 'commit':
                if acursor is not None:
                    acursor.connection.commit()
            elif evalue.mode == 'finish':
                pass
            self.db.CloseCursor(acursor)
            return True
        elif etype is None:
            if self.cursor is not None:
                self.db.CloseCursor(self.cursor)
            return True
        if self.cursor is not None:
            self.db.CloseCursor(self.cursor)
        return False

    def Rollback(self, cursor=None, info=''):
        if cursor is None:
            cursor = self.cursor
        if cursor is not None:
            self.db.ConnectionRollback(cursor)

    def Commit(self, cursor=None, info=''):
        if cursor is None:
            cursor = self.cursor
        if cursor is not None:
            self.db.ConnectionCommit(cursor)

    def RollbackAndExit(self, cursor=None, info=''):
        raise TransactionResult('rollback', cursor, info)

    def CommitAndExit(self, cursor=None, info=''):
        raise TransactionResult('commit', cursor, info)

    def Finish(self, cursor=None, info=''):
        raise TransactionResult('finish', cursor, info)


class AppDB(object):

    def __init__(self, aconfig='', aschema=None, atableprefix=None):
        self.config = aconfig
        self.USE_POOL = self.GetConfigValue('USE_PG_POOL', 1)
        if aschema is None:
            aschema = self.GetConfigValue('PGSchema', '')
        self.schema = aschema
        if atableprefix is None:
            atableprefix = self.GetConfigValue('PGTablePrefix', '')
        self.tableprefix = atableprefix
        self.basepath = self.GetConfigValue('AppBaseDir', '')
        if self.USE_POOL:
            self.DPOOL = {}
            self.InitPool()
        self.conncnt = 0
        self.fout = None

    def GetConfigValue(self, aname, adefault=None):
        v = startutil.appconfig.get(aname, adefault)
        return v

    def InitPool(self):
        self.DPOOL['connection_pool'] = psycopg2.pool.ThreadedConnectionPool(2, self.GetConfigValue('PGMaxConnectionQueue'), database=self.GetConfigValue('PGDatabase'), user=self.GetConfigValue('PGUser'), password=self.GetConfigValue('PGPassword'), host=self.GetConfigValue('PGHost'), port=self.GetConfigValue('PGPort'))

    def GetConnection(self, aautocommit=True):
        self.conncnt += 1
        #print '  $$ GetConnection: %d'%self.conncnt
        #if self.conncnt>15:
        #import traceback
        #traceback.print_stack()
        i = 5
        conn = None
        while i:
            try:
                if not self.USE_POOL:
                    conn = psycopg2.connect(dbname=self.GetConfigValue('PGDatabase'), user=self.GetConfigValue('PGUser'), password=self.GetConfigValue('PGPassword'), host=self.GetConfigValue('PGHost'), port=self.GetConfigValue('PGPort'))
                else:
                    conn = self.DPOOL['connection_pool'].getconn()
                conn.set_session(autocommit=aautocommit)
                conn.set_client_encoding('UTF8')
                break
            except psycopg2.pool.PoolError, e:
                print '    $$ GetConnection SLEEP: %d' % i
                print 'psycopg2.PoolError:', e
                if self.USE_POOL:
                    self.Close(areopen=1)
                time.sleep(1.0)
            except psycopg2.OperationalError, e:
                print '    $$ GetConnection SLEEP: %d' % i
                print 'psycopg2.OperationalError:', e
                if self.USE_POOL:
                    self.Close(areopen=1)
                time.sleep(1.0)
            i = i - 1
        else:
            print '    $$ GetConnection EMPTY'
        return conn

    def GetTransaction(self):
        atransaction = DBTransaction(self)
        return atransaction

    def ConnectionRollback(self, cursor, info=''):
        cursor.connection.rollback()
        return cursor

    def ConnectionCommit(self, cursor, info=''):
        cursor.connection.commit()
        return cursor

    def Close(self, areopen=0):
        #print '$$close start'
        if self.USE_POOL:
            try:
                self.DPOOL['connection_pool'].closeall()
            except psycopg2.pool.PoolError, e:
                print '    $$ Close pool.closeall', e
            if areopen:
                self.InitPool()
        if not areopen and self.fout is not None:
            self.CloseLogFile()
        #print '$$close finish'

    def GetCursor(self, acursor=None, aclosecursor=1, aautocommit=True):
        if acursor is None:
            conn = self.GetConnection(aautocommit=aautocommit)
            return conn.cursor()
        cur = acursor.connection.cursor()
        if aclosecursor and not acursor.closed:
            acursor.close()
        return cur

    def CloseCursor(self, cur):
        conn = cur.connection
        if conn.autocommit:
            if not conn.closed:
                conn.commit()
        if not cur.closed:
            cur.close()
        #print '  $$ CloseCursor: %d'%self.conncnt
        if self.USE_POOL:
            if not conn.closed:
                try:
                    conn.set_session(autocommit=False)
                except psycopg2.ProgrammingError, e:
                    pass
            #if conn.status in [psycopg2.extensions.STATUS_READY,psycopg2.extensions.STATUS_BEGIN,psycopg2.extensions.STATUS_IN_TRANSACTION,psycopg2.extensions.STATUS_PREPARED]:
            #   print 'close conn status is OK',conn.status,conn.closed,id(conn)
            #else:
            #   print 'close conn.status:',conn.status,conn.closed,id(conn)
            #print '   pool._used:',self.DPOOL['connection_pool']._used.keys()
            #print '   pool._rused:',self.DPOOL['connection_pool']._rused.keys()
            if id(conn) in self.DPOOL['connection_pool']._rused.keys():
                try:
                    self.DPOOL['connection_pool'].putconn(conn, close=conn.closed)
                except psycopg2.OperationalError, e:
                    print 'CloseCursor psycopg2.OperationalError', e
                    print '    $$ CloseCursor with closed connection'
                except psycopg2.pool.PoolError, e:
                    print 'CloseCursor psycopg2.PoolError', e
                    print '    $$ CloseCursor with closed pool'
        else:
            if not conn.closed:
                conn.close()
        self.conncnt -= 1

    def GetSQL(self, asql, anoschemareplace=0, aschemaname='public', atableprefix=0):
        if not anoschemareplace:
            if aschemaname[-1:] != '.':
                aschemaname = aschemaname + '.'
            if aschemaname[:1] != ' ':
                aschemaname = ' ' + aschemaname
            aprefix = ''
            if type(atableprefix) == type(1):
                if atableprefix:
                    aprefix = self.tableprefix
            elif isinstance(atableprefix, types.StringTypes):
                aprefix = atableprefix
            asql = asql.replace(aschemaname, ' ' + self.schema + '.' + aprefix)
        return asql

    def ExecuteSQL(self, asql, aparams=None, anoresult=0, asingleresult=0, anoclose=0, acursor=None, aclosecursor=1, anoschemareplace=0, aschemaname='public', atableprefix=0, atimer=None, aautocommit=True, adefault=None):
        """Uruchom kod SQL i zwróć wynik (lub nie).
      
      Arguments:
         asql {str} -- kod sql
      
      Keyword Arguments:
         aparams {tuple} -- [description] (default: {None})
         anoresult {int} -- [description] (default: {0})
         asingleresult {int} -- [description] (default: {0})
         anoclose {int} -- [description] (default: {0})
         acursor {cursor} -- [description] (default: {None})
         aclosecursor {int} -- [description] (default: {1})
         anoschemareplace {int} -- [description] (default: {0})
         aschemaname {str} -- [description] (default: {'public'})
         atableprefix {int} -- [description] (default: {0})
         atimer {timer} -- [description] (default: {None})
         aautocommit {bool} -- [description] (default: {True})
         adefault {[type]} -- [description] (default: {None})
      
      Returns:
         [type] -- domyślnie - None lub wartość parametru 'adefault' lub wynik kodu SQL.
      """

        ret = adefault
        if atimer:
            atimer.Info('ExecuteSQL 01')
        if acursor is not None:
            if not acursor.connection.autocommit:
                aautocommit = False
        if not aautocommit:
            anoclose = 1
        asql = self.GetSQL(asql, anoschemareplace=anoschemareplace, aschemaname=aschemaname, atableprefix=atableprefix)
        if atimer:
            atimer.Info('ExecuteSQL 02')
        try:
            cur = self.GetCursor(acursor=acursor, aclosecursor=aclosecursor, aautocommit=aautocommit)
        except psycopg2.OperationalError, e:
            print 'psycopg2.OperationalError - ExecuteSQL.GetCursor', e
            if ret is not None:
                return ret
        if atimer:
            atimer.Info('ExecuteSQL 03')
        try:
            try:
                if aparams:
                    cur.execute(asql, aparams)
                else:
                    cur.execute(asql)
                if atimer:
                    atimer.Info('ExecuteSQL 04')
            except psycopg2.OperationalError, e:
                print 'psycopg2.OperationalError - ExecuteSQL.Execute', e
                if atimer:
                    atimer.Info('ExecuteSQL 04E1')
                if not aautocommit:
                    raise
                self.Close(areopen=1)
                if atimer:
                    atimer.Info('ExecuteSQL 04E2')
                #return ret
            # $$ DatabaseError: could not receive data from server: Software caused connection abort (0x00002745/10053)
            except psycopg2.DatabaseError, e:
                print 'psycopg2.DatabaseError - ExecuteSQL.Close', e
                if atimer:
                    atimer.Info('ExecuteSQL 04E3')
                if not aautocommit:
                    raise
                #self.Close(areopen=1)
                if atimer:
                    atimer.Info('ExecuteSQL 04E4')
                #return ret
            if not cur.closed:
                try:
                    if atimer:
                        atimer.Info('ExecuteSQL 05')
                    if asingleresult:
                        ret = cur.fetchone()
                    elif not anoresult:
                        ret = cur.fetchall()
                    if atimer:
                        atimer.Info('ExecuteSQL 06')
                except psycopg2.ProgrammingError, e:
                    if e.message != 'no results to fetch':
                        pass
        finally:
            if atimer:
                atimer.Info('ExecuteSQL 07')
            if not anoclose:
                self.CloseCursor(cur)
        if atimer:
            atimer.Info('ExecuteSQL 08')
        return ret

    def ExecuteSQLFile(self, afilepath, asplit=None):
        if asplit is None:
            asplit = '(\/\* GO \*\/)'
        fin = storageutil.OpenText(afilepath, 'r')
        try:
            atext = fin.read()
            l = re.split(asplit, atext, flags=re.I + re.M + re.S + re.U)
            for asql in l:
                if storageutil.isEmptyString(asql):
                    continue
                cur = self.GetCursor()
                try:
                    try:
                        cur.execute(asql)
                    except psycopg2.ProgrammingError, e:
                        if e.message != "can't execute an empty query":
                            print 'ERROR in SQL:', len(asql)
                            print storageutil.UTF8_To_ASCII(asql[:200])
                            raise
                finally:
                    self.CloseCursor(cur)
        finally:
            fin.close()

    def OpenLogFile(self, asufix=''):
        foutcnt = 0
        if asufix:
            for c in r'[]/\;,><&*:%+@!#^|?^':
                asufix = asufix.replace(c, '_')
            asufix = '_' + asufix
        while 1:
            fname = storageutil.tdatetime2fmtstr(storageutil.tdatetime(), longfmt=1, adelimiter='-', asmart=0, atimedelimiter='-', apartdelimiter='_', amsdelimiter='.') + '_' + str(foutcnt) + asufix
            fpath = os.path.join(self.basepath, 'out', fname + '.txt')
            if not os.path.exists(fpath):
                break
            foutcnt = foutcnt + 1
        self.fout = storageutil.OpenText(fpath, 'w')
        self.adt = time.clock()

    def WriteLog(self, s, aopen=0, aclose=0, anotime=0):
        if s is None:
            s = 'None'
        if aopen:
            self.OpenLogFile(s)
        if self.fout is None:
            return
        if not anotime:
            adt = time.clock()
            sdt = storageutil.tdatetime2fmtstr(storageutil.tdatetime(), longfmt=1, adelimiter='-', asmart=0, atimedelimiter=':', apartdelimiter=' ', amsdelimiter='.')
            sh = '\n\n### ' + sdt + ' - (' + str(adt - self.adt) + ')\n'
            self.fout.write(sh)
        if type(s) in [type([]), type({})]:
            s = json.dumps(s, indent=3, sort_keys=True)
        elif type(s) in [type(()), ]:
            s = json.dumps(list(s), indent=3, sort_keys=True)
        elif s[:1] in ['{', '[', u'{', u'[']:
            s = json.loads(s)
            s = json.dumps(s, indent=3, sort_keys=True)
        i = 5
        while i:
            try:
                self.fout.write(s)
                if s[-1:] != '\n':
                    self.fout.write('\n')
                break
            except IOError, e:
                print 'WriteLog:', e
                time.sleep(0.2)
                i = i - 1
        if not anotime:
            self.adt = time.clock()
        if aclose:
            self.CloseLogFile()

    def CloseLogFile(self):
        if self.fout is None:
            return
        i = 5
        while i:
            try:
                self.fout.close()
                break
            except IOError, e:
                print 'CloseLogFile:', e
                time.sleep(0.2)
                i = i - 1
        self.fout = None
