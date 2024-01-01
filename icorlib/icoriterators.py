# -*- coding: utf-8 -*-
import sys
import string
import types

from icorinterface import *

import appplatform.storageutil as storageutil


class FieldRefIterator:

    def __init__(self, arefstr='', afromrefs=None):
        if isinstance(arefstr, types.StringTypes):
            if (len(arefstr) > 0) and (arefstr[-1:] != ':'):
                arefstr = arefstr + ':'
            alist = map(int, arefstr.split(':')[:-1])
            self.refs = map(list, zip(alist[::2], alist[1::2]))
            if 0:
                alist = string.split(arefstr, ':')
                self.refs = []
                k = 0
                while k < len(alist):
                    if alist[k] == '':
                        break
                    try:
                        i1 = int(alist[k])
                        i2 = int(alist[k + 1])
                    except:
                        break
                    self.refs.append([i1, i2])
                    k = k + 2
        elif type(arefstr) == type([]):
            self.refs = arefstr[:]
        else:
            self.refs = []
        self.len = len(self.refs)
        self._Class = None
        self._CID = -1
        if afromrefs is not None:
            self.RefField = afromrefs.RefField
            self.RefOID = afromrefs.RefOID
        else:
            self.RefField = None
            self.RefOID = None
        self.First()

    def __getattr__(self, name):
        if self.position >= self.len or self.position < 0:
            return -1
        if name == 'OID':
            return self.refs[self.position][0]
        elif name == 'CID':
            return self.refs[self.position][1]
        elif name == 'Class':
            acid = self.refs[self.position][1]
            if self._CID != acid:
                self._CID = acid
                self._Class = aICORDBEngine.Classes[acid]
            return self._Class
        else:
            acid = self.refs[self.position][1]
            if self._CID != acid:
                self._CID = acid
                self._Class = aICORDBEngine.Classes[acid]
            return getattr(self._Class, name)

    def __getitem__(self, key):
        if key >= 0 and key < self.len:
            return self.refs[key][0], self.refs[key][1]
        raise IndexError

    def __setitem__(self, key, value):
        if key >= 0 and key < self.len:
            self.refs[key][0] = value[0]
            self.refs[key][1] = value[1]

    def __delitem__(self, key):
        self.DelRefByID(key)

    def __len__(self):
        return self.len

    def __getslice__(self, i, j):
        return self.AsRefs(self.AsString(i, j))

    def __setslice__(self, i, j, arefs):
        self.__delslice__(i, j)
        arefs.First()
        while arefs.position >= 0:
            self.InsertRef(i, arefs.OID, arefs.CID)
            i = i + 1
            arefs.Next()

    def __delslice__(self, i, j):
        if j == sys.maxint:
            j = self.len
        c = j - i
        while c > 0:
            self.DelRefByID(i)
            c = c - 1

    def __nonzero__(self):
        return self.position >= 0

    def __and__(self, arefs):
        brefs = self.AsRefsEmpty()
        for i in range(self.len):
            if arefs.RefExists(self.refs[i][0], self.refs[i][1]):
                brefs.AddRef(self.refs[i][0], self.refs[i][1])
        return brefs

    def __or__(self, arefs):
        brefs = self.AsRefs()
        for i in range(arefs.len):
            if not brefs.RefExists(arefs.refs[i][0], arefs.refs[i][1]):
                brefs.AddRef(arefs.refs[i][0], arefs.refs[i][1])
        return brefs


#   def __add__(self,other):
#      return self.__or__(other)
#   def __mul__(self,other):
#      return self.__and__(other)

    def __coerce__(self, other):
        return self, other

    def __repr__(self):
        return self.AsString()

    def __str__(self):
        return self.AsString()

    def reverse(self):
        self.refs.reverse()

    def sort(self, afield):
        self.First()
        self._sortedfield = afield
        return self.refs.sort(self._oidcmpfunc)

    def clear(self):
        self.refs = []
        self.len = 0
        self.First()

    def _oidcmpfunc(self, avalue1, avalue2):
        return self._sortedfield.CompareOIDs(avalue1[0], avalue2[0])

    def First(self):
        self.position = 0
        if self.position >= self.len:
            self.position = -1
        return self.position

    def Last(self):
        self.position = self.len - 1
        return self.position

    def Next(self):
        self.position = self.position + 1
        if self.position >= self.len:
            self.position = -1
        return self.position

    def Prev(self):
        if self.position >= 0:
            self.position = self.position - 1
        return self.position

    def SetByPosition(self, apos):
        if apos >= self.len or apos < 0:
            self.position = -1
        else:
            self.position = apos
        return self.position

    def ActualRef(self):
        return str(self.OID) + ':' + str(self.CID) + ':'

    def IsEmpty(self):
        return self.len == 0

    def InsertRef(self, pos, aoid, acid):
        if pos < 0:
            pos = 0
        elif pos >= self.len:
            return self.AddRef(aoid, acid)
        self.refs.insert(pos, [aoid, acid])
        self.len = len(self.refs)
        if self.position < 0:
            self.position = 0
        return pos

    def FindRef(self, aoid, acid):    # zwraca: (apos, afind) !!!
        lref = [aoid, acid]
        for i in range(len(self.refs)):
            if self.refs[i] == lref:
                return i, 1
        return -1, 0

    def BinaryFind(self, afunc, aoid, acid):
        res, l, h = 0, 0, self.len - 1
        while l <= h:
            i = (l + h) / 2
            c = afunc(self.refs[i], [aoid, acid])
            if c < 0:
                l = i + 1
            elif c > 0:
                h = i - 1
            else:
                h, res = i - 1, 1
        return l, res

    def FindRefByValue(self, afield, avalue, asorted=0, adescending=0, aasoidsearch=0, assubstringsearch=0, alowersearch=0):    # zwraca: (apos, afind) !!!
        if isinstance(afield, types.StringTypes):
            afield = self.RefField.ClassOfType.FieldsByName(afield)
        if not assubstringsearch and asorted:
            self._sortedfield = afield
            self._descending = adescending
            return self.BinaryFind(self._oidcmpfuncvalue, avalue, None)
        if assubstringsearch:
            if isinstance(avalue, types.StringTypes):
                avalue = [avalue, ]
            lsearch = []
            for s in avalue:
                if alowersearch:
                    s = s.lower()
                lsearch.append(storageutil.UTF8_To_CP1250(s))
        for i in range(len(self.refs)):
            if aasoidsearch:
                brefs = afield.GetRefList(self.refs[i][0])
                if brefs.RefExists(avalue):
                    return i, 1
            elif assubstringsearch:
                find = 1
                v = afield[self.refs[i][0]]
                if alowersearch:
                    v = v.lower()
                for ss in lsearch:
                    if v.find(ss) >= 0:
                        return i, 1
            else:
                find = afield.CompareOIDValue(self.refs[i][0], avalue)
                if not find:
                    return i, 1
        return -1, 0

    def InsertRefEx(self, adisp, aoid, acid, adescending=0):
        if type(adisp) == type(1):
            return self.InsertRef(adisp, aoid, acid)
        elif isinstance(adisp, ICORDBFieldItem):
            self._sortedfield = adisp
        else:
            #print 'return -1', aoid, acid
            return -1
        self._descending = adescending
        pos, find = self.BinaryFind(self._oidcmpinsertfunc, aoid, acid)
        return self.InsertRef(pos, aoid, acid)

    def _oidcmpinsertfunc(self, avalue1, avalue2):
        if self._descending:
            return -self._sortedfield.CompareOIDs(avalue1[0], avalue2[0])
        else:
            return self._sortedfield.CompareOIDs(avalue1[0], avalue2[0])

    def _oidcmpfuncvalue(self, avalue1, avalue2):
        if self._descending:
            return -self._sortedfield.CompareOIDValue(avalue1[0], avalue2[0])
        else:
            return self._sortedfield.CompareOIDValue(avalue1[0], avalue2[0])

    def AddRef(self, aoid, acid=-1, anoduplicates=0, store=0):
        if (acid < 0) and (self.RefField is not None):
            acid = self.RefField.ClassOfType.CID
        if (acid < 0) and (self.Class is not None):
            acid = self.Class.CID
        if acid < 0:
            return self.len - 1
        if anoduplicates and self.RefExists(aoid, acid):
            return self.len - 1
        self.refs.append([aoid, acid])
        self.len = len(self.refs)
        if self.position < 0:
            self.position = 0
        if store:
            self.Store()
        return self.len - 1

    def AddRefs(self, arefs, store=0):
        lpos = arefs.position
        arefs.First()
        while arefs.position >= 0:
            self.AddRef(arefs.OID, arefs.CID, anoduplicates=1)
            arefs.Next()
        arefs.position = lpos
        if store:
            self.Store()
        return -1

    def DelRef(self, aoid, acid=-1):
        aid = 0
        s = ''
        ret = 0
        while aid < self.len:
            if aoid == self.refs[aid][0]:
                if (acid < 0) or (self.refs[aid][1] == acid):
                    del self.refs[aid]
                    self.len = len(self.refs)
                    if self.position >= self.len:
                        self.position = self.position - 1
                    ret = 1
            aid = aid + 1
        return ret

    def DelRefsInRange(self, aidmin, aidmax, acid=-1):
        aid = 0
        s = ''
        ret = 0
        while aid < self.len:
            boid = self.refs[aid][0]
            if boid >= aidmin and boid < aidmax:
                if (acid < 0) or (self.refs[aid][1] == acid):
                    del self.refs[aid]
                    self.len = len(self.refs)
                    if self.position >= self.len:
                        self.position = self.position - 1
                    ret = 1
            aid = aid + 1
        return ret

    def DelRefByID(self, aid=-1):
        if aid < 0:
            aid = self.position
        if (aid < self.len) and (aid >= 0):
            del self.refs[aid]
            self.len = len(self.refs)
            if self.position >= self.len:
                self.position = self.position - 1
        return -1

    def RefExists(self, aoid, acid=-1):
        if acid < 0:
            for boid, bcid in self.refs:
                if aoid == boid:
                    return 1
        else:
            for boid, bcid in self.refs:
                if aoid == boid and acid == bcid:
                    return 1
        return 0

    def RefsExists(self, arefs):
        arefs.First()
        while arefs.position >= 0:
            if [arefs.OID, arefs.CID] in self.refs:
                #         if self.RefExists(arefs.OID,arefs.CID):
                return 1
            arefs.Next()
        return 0

    def RefsExistsAll(self, arefs):
        if type(arefs) == type([]):
            for aoid, acid in arefs:
                if not self.RefExists(aoid, acid):
                    return 0
        else:
            while arefs.position >= 0:
                if not self.RefExists(arefs.OID, arefs.CID):
                    return 0
                arefs.Next()
        return 1

    def CheckRefs(self, aexists=0, astore=0):
        d = {}
        l, lb = [], []
        w = 0
        for aoid, acid in self.refs:
            if d.has_key(aoid):
                w = 1
                lb.append([aoid, acid])
                continue
            if aexists and not self.Class.ObjectExists(aoid):
                w = 1
                lb.append([aoid, acid])
                continue
            d[aoid] = 1
            l.append([aoid, acid])
        if astore and w:
            self.refs = l
            self.len = len(l)
            self.Store()
        return w, l, lb

    def Store(self, afield=None, aoid=-1):
        if afield is None:
            if self.RefField and self.RefOID >= 0:
                self.RefField[self.RefOID] = self.AsString()
        elif aoid >= 0:
            afield[aoid] = self.AsString()

    def AsObject(self):
        return ICORDBObject(self.OID, self.Class, self)

    def AsRefs(self, afrom=None):
        if afrom is None:
            afrom = self.AsString()
        return FieldRefIterator(afrom, afromrefs=self)

    def AsRefsEmpty(self):
        return self.AsRefs('')

    def AsString(self, i=0, j=-1):
        if j < 0 or j == sys.maxint:
            j = self.len
        s = ''
        while i < j:
            s = s + str(self.refs[i][0]) + ':' + str(self.refs[i][1]) + ':'
            i = i + 1
        return s

    def AsStringOID(self):
        aid = 0
        s = ''
        while aid < self.len:
            s = s + str(self.refs[aid][0]) + ':'
            aid = aid + 1
        return s

    def AsStringCID(self):
        aid = 0
        s = ''
        while aid < self.len:
            s = s + str(self.refs[aid][1]) + ':'
            aid = aid + 1
        return s

    def AsListOID(self):
        aid = 0
        l = []
        while aid < self.len:
            l.append(self.refs[aid][0])
            aid = aid + 1
        return l

    def AsListCID(self):
        aid = 0
        l = []
        while aid < self.len:
            l.append(self.refs[aid][1])
            aid = aid + 1
        return l

    def AsListOIDCID(self):
        aid = 0
        l = []
        while aid < self.len:
            l.append(self.refs[aid][0])
            l.append(self.refs[aid][1])
            aid = aid + 1
        return l


class ICORObjectIterator:

    def __init__(self, *args, **parms):
        for k, v in parms.items():
            self.__dict__[k] = v

    def ForEachObject(self, aclass):
        aclass = aICORDBEngine.Classes[aclass]
        aoid = aclass.FirstObject()
        while aoid >= 0:
            self.OnObject(aclass, aoid)
            aoid = aclass.NextObject(aoid)
        return self

    def ForEachRefObject(self, afield, aoid):
        aref = afield.GetRefList(aoid)
        lcid = -1
        while aref.position >= 0:
            x = aref.CID
            if x != lcid:
                lcid = x
                aclass = aICORDBEngine.Classes[x]
            self.OnObject(aclass, aref.OID)
            aref.Next()
        return self

    def OnObject(self, aclass, aoid):
        return -1


class ObjectIterator(ICORObjectIterator):

    def __init__(self, func, parms):
        self.func = func
        self.parms = parms
        ICORObjectIterator.__init__(self)

    def OnObject(self, aclass, aoid):
        apply(self.func, (aclass, aoid) + self.parms)


def ForEachRefObject(afield, aoid, afunc, *parms):
    ObjectIterator(afunc, parms).ForEachRefObject(afield, aoid)


def ForEachRefObjectParms(afield, aoid, afunc, parms):
    ObjectIterator(afunc, parms).ForEachRefObject(afield, aoid)


def ForEachObject(aclass, afunc, *parms):
    ObjectIterator(afunc, parms).ForEachObject(aclass)


def ForEachObjectParms(aclass, afunc, parms):
    ObjectIterator(afunc, parms).ForEachObject(aclass)


class ICORRepositoryIterator:

    def __init__(self, *args, **parms):
        for k, v in parms.items():
            self.__dict__[k] = v
        self.FieldRecursive = 0

    def ForEachClass(self, aclass=None, afieldrecursive=0):
        self.IteratedClasses = {}
        self.FieldRecursive = afieldrecursive
        self.OnPreIterate()
        if aclass is None:
            self.Iterate()
        else:
            self.IterateRecursive(aclass, afieldrecursive)
        self.OnPostIterate()

    def ForEachField(self, aclass):
        afields = aclass.GetFieldsList()
        afields.sort()
        for afieldname in afields:
            afield = aclass.FieldsByName(afieldname)
            self.OnField(aclass, afield)

    def ForEachMethod(self, aclass):
        amethods = aclass.GetMethodsList(0)
        amethods.sort()
        for amethodname in amethods:
            amethod = aclass.MethodsByName(amethodname)
            self.OnMethod(aclass, amethod)

    def Iterate(self):
        aclass = aICORDBEngine.Classes.FirstClass()
        while aclass is not None:
            self.OnPreClass(aclass)
            afields = aclass.GetFieldsList()
            afields.sort()
            amethods = aclass.GetMethodsList(0)
            amethods.sort()
            for afield in afields:
                self.OnPreField(aclass, afield)
            for amethod in amethods:
                self.OnPreMethod(aclass, amethod)
            for afield in afields:
                self.OnPostField(aclass, afield)
            for amethod in amethods:
                self.OnPostMethod(aclass, amethod)
            self.OnPostClass(aclass)
            aclass = aICORDBEngine.Classes.NextClass(aclass)

    def IterateRecursive(self, aclass, afieldrecursive=0):
        if self.IteratedClasses.has_key(aclass.CID):
            return
        if not self.OnClassAccept(aclass):
            return
        self.IteratedClasses[aclass.CID] = 1
        self.OnPreClass(aclass)
        afields = aclass.GetFieldsList()
        afields.sort()
        amethods = aclass.GetMethodsList(0)
        amethods.sort()
        for afield in afields:
            self.OnPreField(aclass, afield)
            if afieldrecursive:
                afi = aclass.FieldsByName(afield)
                if afi.FieldTID > MAX_ICOR_SYSTEM_TYPE:
                    ret = self.OnBeforeRecursiveField(aclass, afi)
                    if ret:
                        self.IterateRecursive(afi.ClassOfType, afieldrecursive)
                        self.OnAfterRecursiveField(aclass, afi)
        for amethod in amethods:
            self.OnPreMethod(aclass, amethod)
        alist = aclass.GetInheritedClassesList()
        for icid in alist:
            bclass = aICORDBEngine.Classes[icid]
            if bclass is not None:
                if self.OnBeforeRecursiveClass(bclass):
                    self.IterateRecursive(bclass)
                    self.OnAfterRecursiveClass(bclass)
        for afield in afields:
            self.OnPostField(aclass, afield)
        for amethod in amethods:
            self.OnPostMethod(aclass, amethod)
        self.OnPostClass(aclass)

    def OnPreIterate(self):
        pass

    def OnClassAccept(self, aclass):
        return 1

    def OnPreClass(self, aclass):
        pass

    def OnPreField(self, aclass, afieldname):
        pass

    def OnPreMethod(self, aclass, amethodname):
        pass

    def OnPostField(self, aclass, afieldname):
        pass

    def OnPostMethod(self, aclass, amethodname):
        pass

    def OnPostClass(self, aclass):
        pass

    def OnPostIterate(self):
        pass

    def OnField(self, aclass, afield):
        pass

    def OnMethod(self, aclass, amethod):
        pass

    def OnBeforeRecursiveClass(self, aclass):
        return not self.FieldRecursive

    def OnBeforeRecursiveField(self, aclass, afield):
        return 1

    def OnAfterRecursiveField(self, aclass, afield):
        pass

    def OnAfterRecursiveClass(self, aclass):
        pass


class ClassIterator(ICORRepositoryIterator):

    def __init__(self, func, parms):
        self.func = func
        self.parms = parms
        ICORRepositoryIterator.__init__(self)

    def OnPreClass(self, aclass):
        apply(self.func, (aclass, ) + self.parms)


def ForEachClass(afunc, aclass=None, *parms):
    ClassIterator(afunc, parms).ForEachClass(aclass)


def ForEachClassParms(afunc, aclass=None, parms=()):
    ClassIterator(afunc, parms).ForEachClass(aclass)


class FieldMethodIterator(ICORRepositoryIterator):

    def __init__(self, func, parms):
        self.func = func
        self.parms = parms
        ICORRepositoryIterator.__init__(self)

    def OnField(self, aclass, afield):
        apply(self.func, (aclass, afield, ) + self.parms)

    def OnMethod(self, aclass, amethod):
        apply(self.func, (aclass, amethod, ) + self.parms)


def ForEachField(afunc, aclass, *parms):
    FieldMethodIterator(afunc, parms).ForEachField(aclass)


def ForEachFieldParms(afunc, aclass, parms):
    FieldMethodIterator(afunc, parms).ForEachField(aclass)


def ForEachMethod(afunc, aclass, *parms):
    FieldMethodIterator(afunc, parms).ForEachMethod(aclass)


def ForEachMethodParms(afunc, aclass, parms):
    FieldMethodIterator(afunc, parms).ForEachMethod(aclass)


class ClassOIDIterator(object):

    def __init__(self, aclass):
        self.iclass = aclass
        self._current_oid = aclass.FirstObject()

    def __iter__(self):
        return self

    def next(self):
        if self._current_oid < 0:
            raise StopIteration
        ret = self._current_oid
        self._current_oid = self.iclass.NextObject(ret)
        return ret


class FieldOIDIterator(object):

    def __init__(self, afield):
        self.ifield = afield
        self._current_oid = afield.GetFirstValueID()

    def __iter__(self):
        return self

    def next(self):
        if self._current_oid < 0:
            raise StopIteration
        ret = self._current_oid
        self._current_oid = self.ifield.GetNextValueID(ret)
        return ret
