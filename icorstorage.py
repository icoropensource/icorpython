# -*- coding: utf-8 -*-
import time
import sys
import re
import types

import appplatform.storageutil as storageutil
import icordbmain


def exceptionsafe(fn):
    return fn

    def wrapper(*args, **kwargs):
        xcnt = 4
        asleep = 0.23
        while xcnt > 0:
            try:
                return fn(*args, **kwargs)
            except:
                xcnt = xcnt - 1
                if xcnt:
                    time.sleep(asleep)
                    asleep = asleep + asleep / 2.0
        raise

    return wrapper


class MBase(object):

    def __init__(self, astore):
        self.store = astore


class MDataFile(MBase):
    """
      fi: field id list : set
      f: field value actual : hash [v,m,u]
      fv: field value version : list (0,*)
      fm: field modification version : list (0,*)
      fu: field userid version : list (0,*)
      fs: field sorted values : list
   """

    def __init__(self, astore, afid, aisversion=1, amaxversion=100):
        super(self.__class__, self).__init__(astore)
        self.FID = afid
        self.isversion = aisversion
        self.maxversion = amaxversion

    @exceptionsafe
    def GetAllIds(self):
        return self.store.r.smembers('i:' + self.FID)

    @exceptionsafe
    def Update(self, aid, avalue, amodtime=None, auid=0):
        if amodtime is None:
            amodtime = time.strftime('%Y%m%d%H%M%S', time.gmtime())

        bid = self.FID + ':' + aid

        ovalue = self.store.r.hget('f:' + bid, 'v')
        if ovalue == avalue:
            return

        p = self.store.r.pipeline()

        # id list
        p.sadd('i:' + self.FID, aid)

        # set value
        p.hset('f:' + bid, 'v', avalue)
        p.hset('f:' + bid, 'm', amodtime)
        p.hset('f:' + bid, 'u', auid)

        # version value
        p.lpush('v:' + bid, avalue)
        p.ltrim('v:' + bid, 0, self.maxversion)
        p.lpush('m:' + bid, amodtime)
        p.ltrim('m:' + bid, 0, self.maxversion)
        p.lpush('u:' + bid, auid)
        p.ltrim('u:' + bid, 0, self.maxversion)

        # remove sorted index
        p.delete('s:' + self.FID)

        p.execute()

    @exceptionsafe
    def Dump(self):
        print 'FID:', self.FID
        print 'i:', self.store.r.smembers('i:' + self.FID)
        print 's:', self.store.r.lrange('s:' + self.FID, 0, 1000)

    @exceptionsafe
    def DumpId(self, aid):
        bid = self.FID + ':' + aid
        print 'f:', bid, self.store.r.hmget('f:' + bid, ['v', 'm', 'u'])
        lv = self.store.r.lrange('v:' + bid, 0, 1000)
        lm = self.store.r.lrange('m:' + bid, 0, 1000)
        lu = self.store.r.lrange('u:' + bid, 0, 1000)
        print 'v:', bid, zip(lv, lm, lu)

    @exceptionsafe
    def GetSortedIds(self):
        if self.store.r.exists('s:' + self.FID):
            return self.store.r.lrange('s:' + self.FID, 0, -1)
        bid = 'f:' + self.FID + ':*'
        p = self.store.r.pipeline()
        self.store.sort('i:' + self.FID, start=None, num=None, by=bid + '->v', get=[bid + '->v', '#'], desc=False, alpha=True, store='s:' + self.FID, pipeline=p)
        p.lrange('s:' + self.FID, 0, -1)
        l = p.execute()
        return l[1]

    def DeleteId(self, aid):
        pass

    def CheckIsDeleted(self, aid):
        pass

    def ExistsId(self, aid):
        pass

    def ExistsValue(self, avalue):
        pass

    def FirstId(self):
        pass

    def FirstValue(self):
        pass

    def NextId(self, aid):
        pass

    def NextValue(self, avalue):
        pass

    def PrevId(self, aid):
        pass

    def PrevValue(self, value):
        pass

    def LastId(self):
        pass

    def LastValue(self):
        pass

    def GetModification(self, aid):
        pass

    def Count(self):
        pass

    def DeletedCount(self):
        pass

    def OwnerClassId(self):
        pass

    def DefaultTypeId(self):
        pass

    def DefaultTypeModifier(self):
        pass


class MClassFile(MBase):

    def __init__(self, astore, acid):
        super(self.__class__, self).__init__(astore)
        self.CID = acid


class MDefaultBase(MBase):

    def __init__(self, astore):
        super(self.__class__, self).__init__(astore)


class MLogBase(MBase):

    def __init__(self, astore):
        super(self.__class__, self).__init__(astore)


class MSysBase(MBase):

    def __init__(self, astore):
        super(self.__class__, self).__init__(astore)

    def CleanUp(self):
        pass

    @exceptionsafe
    def AddExecutorMethod(self, CID, amethodname, FieldName='', OID=-1, Value='', UID=-1, aparallel=0, aqueued=0, priority='N03'):
        ret = self.store.executor.AddExecutorMethod(CID, amethodname, FieldName, OID, Value, UID, aparallel, aqueued, 'Ready', priority)
        return ret

    @exceptionsafe
    def GetExecutorMethod(self, ameid=-1, pid=-1):
        if ameid < 0:
            ret = self.store.executor.GetExecutorMethod(pid=pid)
            return ret
        ret = self.store.executor.GetExecutorMethodByID(ameid)
        return ret

    @exceptionsafe
    def GetExecutorMethodReadyCount(self, afirst=0):
        ret = self.store.executor.GetExecutorMethodReadyCount(afirst)
        return ret

    @exceptionsafe
    def RemoveExecutorMethod(self, ameid):
        self.store.executor.SetExecutorMethodStatus(ameid, 'Deleted')

    @exceptionsafe
    def ExecutorMethodSetWorking(self, ameid):
        self.store.executor.SetExecutorMethodStatus(ameid, 'Working')

    @exceptionsafe
    def ExecutorMethodSetDone(self, ameid, result='', output=''):
        self.store.executor.SetExecutorMethodStatus(ameid, 'Done', result, output)

    @exceptionsafe
    def ExecutorMethodCheckProcessing(self, aforcemove=0):
        self.store.executor.ExecutorMethodCheckProcessing()
        return

    @exceptionsafe
    def ExecutorMethodGetReadyList(self):
        ret = self.store.executor.GetExecutorMethodIDByStatus('Ready')
        return ret

    @exceptionsafe
    def ExecutorMethodGetProcessingList(self):
        ret = self.store.executor.GetExecutorMethodIDByStatus('Working')
        return ret

    @exceptionsafe
    def SemaphoreSet(self, aname, amaxvalue):
        self.store.dbipc.SemaphoreSet(aname, amaxvalue)

    @exceptionsafe
    def SemaphoreAcquire(self, aname, await=0.04):
        while 1:    # timeout
            ret = self.store.dbipc.SemaphoreAcquire(aname)
            if ret is not None:
                return ret
            time.sleep(await)

    @exceptionsafe
    def SemaphoreRelease(self, aname):
        self.store.dbipc.SemaphoreRelease(aname)

    @exceptionsafe
    def SemaphoreInfo(self, aname):
        return self.store.dbipc.SemaphoreInfo(aname)

    @exceptionsafe
    def SetCMSData(self, acms, akey, avalue=''):
        if type(akey) == type({}):
            for bkey, bvalue in akey.items():
                self.store.dbcms.SetCMSData(acms, bkey, bvalue)
        else:
            self.store.dbcms.SetCMSData(acms, akey, avalue)

    @exceptionsafe
    def GetCMSData(self, acms, akey, adefault=''):
        ret = self.store.dbcms.GetCMSData(acms, akey)
        if ret is None:
            ret = adefault
        return ret

    @exceptionsafe
    def SetCMSChapterState(self, acmsid=0, acmsname='', achapterid=0, achaptertitle='', apriority='N03', auid=0, ausername='', aoperationtype='generate', aitemoid='', astatus='N'):
        return self.store.dbcms.SetCMSChapterState(acmsid, acmsname, achapterid, achaptertitle, apriority, auid, ausername, aoperationtype, aitemoid, astatus)

    @exceptionsafe
    def GetCMSChapterGenerateCount(self):
        return self.store.dbcms.GetCMSChapterGenerateCount()

    @exceptionsafe
    def GetCMSChapterGenerateNext(self):
        return self.store.dbcms.GetCMSChapterGenerateNext()

    @exceptionsafe
    def SetCMSChapterGenerateFinished(self, aoperationoid, atime):
        return self.store.dbcms.SetCMSChapterGenerateFinished(aoperationoid, atime)


class MCacheBase(MBase):

    def __init__(self, astore):
        super(self.__class__, self).__init__(astore)

    def Clear(self):
        pass

    @exceptionsafe
    def SetFieldValue(self, afid, aoid, atype, avalue):
        return None
        #print 'SetFieldValue',afid,aoid,atype,avalue
        if atype in [storageutil.mt_String, storageutil.mt_Memo]:
            self.store.dbcache.SetCacheFieldValue(afid, aoid, avalue)
        elif atype > storageutil.MAX_ICOR_SYSTEM_TYPE:
            if type(avalue) == type([]):
                if avalue:
                    if type(avalue[0]) == type(1):
                        avalue = ':'.join(map(repr, avalue) + [''])
                    else:
                        avalue = ''.join(map(lambda x: str(x[0]) + ':' + str(x[1]) + ':', avalue))
                else:
                    avalue = ''
            elif hasattr(avalue, 'AsString'):
                avalue = avalue.AsString()
            self.store.dbcache.SetCacheFieldValue(afid, aoid, avalue)
        elif atype in [storageutil.mt_Integer, storageutil.mt_Double]:
            if not isinstance(avalue, types.StringTypes):
                avalue = str(avalue)
            elif not avalue:
                avalue = '0'
            self.store.dbcache.SetCacheFieldValue(afid, aoid, avalue)
        elif atype in [storageutil.mt_Boolean, storageutil.mt_Bool]:
            bvalue = storageutil.str2bool(avalue)
            self.store.dbcache.SetCacheFieldValue(afid, aoid, str(bvalue))
        elif atype in [storageutil.mt_DateTime, storageutil.mt_Date, storageutil.mt_Time]:
            try:
                v = storageutil.GetDateTime(float(avalue))
            except:
                v = storageutil.getStrAsDateTime(avalue)
            #print 'v:',v
            bvalue = ':'.join(map(str, v))
            #print 'bvalue:',bvalue
            self.store.dbcache.SetCacheFieldValue(afid, aoid, bvalue)
        else:
            print 'unknown field %d type: %d' % (afid, atype)

    @exceptionsafe
    def GetFieldValue(self, afid, aoid, atype, aasstring=0):
        return None
        ret = self.store.dbcache.GetCacheFieldValue(afid, aoid)
        if ret is None:
            return None
        if (atype in [storageutil.mt_String, storageutil.mt_Memo]) or (atype > storageutil.MAX_ICOR_SYSTEM_TYPE):
            return ret
        elif atype in [storageutil.mt_Integer, ]:
            if not ret:
                ret = '0'
            if not aasstring:
                return int(ret)
            return ret
        elif atype in [storageutil.mt_Double, ]:
            if not ret:
                ret = '0.0'
            if not aasstring:
                return float(ret)
            return ret
        elif atype in [storageutil.mt_Boolean, storageutil.mt_Bool]:
            v = storageutil.str2bool(ret)
            if not aasstring:
                return v
            return str(v)
        elif atype in [storageutil.mt_DateTime, storageutil.mt_Date, storageutil.mt_Time]:
            dt = tuple(map(int, ret.split(':')))
            if aasstring:
                if dt == storageutil.ZERO_DATE_TZ:
                    return ''
                return storageutil.tdatetime2fmtstr(dt)
            return dt
        else:
            print 'unknown field %d type: %d' % (afid, atype)
        return ret

    @exceptionsafe
    def DelFieldValue(self, afid, aoid):
        return None
        self.store.dbcache.DeleteCacheFieldValue(afid, aoid)


class MTempBase(MBase):

    def __init__(self, astore):
        super(self.__class__, self).__init__(astore)


class MManager(object):

    def __init__(self, ahost='127.0.0.1', aport=6379):
        self._datastores = {}
        self._datafiles = {}
        self._classfiles = {}

        self._mDefaultStore = None
        self._mLogStore = None
        self._mSysStore = None
        self._mTempStore = None
        self._mDBStore = None

        self._mDefaultBase = None
        self._mLogBase = None
        self._mSysBase = None
        self._mTempBase = None

    def GetDataStore(self, aschema):
        if not self._datastores.has_key(aschema):
            self._datastores[aschema] = icordbmain.ICORDB(aconfig=icordbmain.startutil.appconfig.DefaultConfig, aschema=aschema)
        return self._datastores[aschema]

    def GetDefaultBase(self):
        if self._mDefaultBase is None:
            if self._mDefaultStore is None:
                self._mDefaultStore = self.GetDataStore('main')
            self._mDefaultBase = MDefaultBase(self._mDefaultStore)
        return self._mDefaultBase

    def GetLogBase(self):
        if self._mLogBase is None:
            if self._mLogStore is None:
                self._mLogStore = self.GetDataStore('mlogs')
            self._mLogBase = MLogBase(self._mLogStore)
        return self._mLogBase

    def GetSysBase(self):
        if self._mSysBase is None:
            if self._mSysStore is None:
                self._mSysStore = self.GetDataStore('icor')
            self._mSysBase = MSysBase(self._mSysStore)
        return self._mSysBase

    def GetTempBase(self):
        if self._mTempBase is None:
            if self._mTempStore is None:
                self._mTempStore = self.GetDataStore('mtemp')
            self._mTempBase = MLogBase(self._mTempStore)
        return self._mTempBase

    def GetDataFile(self, afid):
        if not self._datafiles.has_key(afid):
            if self._mDBStore is None:
                self._mDBStore = self.GetDataStore('main')
            self._datafiles[afid] = MDataFile(self._mDBStore, afid)
        return self._datafiles[afid]

    def GetClassFile(self, acid):
        if not self._classfiles.has_key(acid):
            if self._mDBStore is None:
                self._mDBStore = self.GetDataStore('main')
            self._classfiles[acid] = MClassFile(self._mDBStore, acid)
        return self._classfiles[acid]
