# -*- coding: utf-8 -*-
from icorinterface import *
import types
import random


class ICORSortedDictionary:

    def __init__(self):
        self.keys = []
        self.values = []

    def FindKey(self, key):
        l = 0
        m = len(self.keys) - 1
        while l <= m:
            i = (l + m) / 2
            c = self.keys[i] - key
            if c < 0:
                l = i + 1
            elif c > 0:
                m = i - 1
            else:
                l = i
                break
        return l

    def __len__(self):
        return len(self.keys)

    def __repr__(self):
        return str(map(None, self.keys, self.values))

    def __getitem__(self, key):
        x = self.Index(key)
        if x >= 0:
            return self.values[x]
        return None

    def __setitem__(self, key, value):
        x = self.Index(key)
        if x >= 0:
            self.values[x] = value
        else:
            self.Add(key, value)

    def Add(self, key, value):
        x = self.FindKey(key)
        self.keys.insert(x, key)
        self.values.insert(x, value)

    def Remove(self, key):
        x = self.FindKey(key)
        if x >= 0:
            del self.keys[x]
            del self.values[x]

    def Append(self, value):
        if self.keys == []:
            key = 0
        else:
            key = self.keys[len(self.keys) - 1] + 1
        self.Add(key, value)

    def Index(self, key):
        try:
            return self.keys.index(key)
        except:
            return -1

    def GetFirst(self):
        if self.keys == []:
            return -1, None
        return self.keys[0], self.values[0]

    def GetNext(self, akey):
        akey = akey + 1
        l = self.keys[len(self.keys) - 1]
        if akey > l:
            return -1, None
        x = self.Index(akey)
        if x >= 0:
            return akey, self.values[x]
        return akey, None

    def Len(self):
        return len(self.keys)

    def MaxLen(self):
        if self.keys == []:
            return -1
        return self.keys[len(self.keys) - 1]


class ICORMDSpace:

    def __init__(self, value=None):
        self.header = ICORSortedDictionary()
        self._items = ICORSortedDictionary()
        self.footer = ICORSortedDictionary()
        self.Value = value
        self.Caption = ''
        self.MinCol = 999999999    #very big
        self.MaxCol = -1

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key):
        if type(key) == types.IntType:
            if self._items.Index(key) >= 0:
                return self._items[key].Value
            else:
                return None
        else:
            f, r = key[0], key[1:]
            if len(r) == 1:
                r = r[0]
            if self._items.Index(f) >= 0:
                return self._items[f][r]
            else:
                return None

    def __setitem__(self, key, value):
        if type(key) == types.IntType:
            if self._items.Index(key) >= 0:
                self._items[key].Value = value
            else:
                x = ICORMDSpace(value)
                self._items[key] = x
        else:
            f, r = key[0], key[1:]
            if len(r) == 1:
                r = r[0]
                if r < self.MinCol:
                    self.MinCol = r
                if r > self.MaxCol:
                    self.MaxCol = r
            if self._items.Index(f) >= 0:
                self._items[f][r] = value
            else:
                x = ICORMDSpace()
                x[r] = value
                self._items[f] = x

    def Remove(self, key):
        if type(key) == types.IntType:
            self._items.Remove(key)
        else:
            f, r = key[0], key[1:]
            if len(r) == 1:
                r = r[0]
            if self._items.Index(f) >= 0:
                self._items[f].Remove(r)

    def __cmp__(self, other):
        print 'cmp:', self.Value, other.Value
        if other.Value < self.Value:
            return -1
        elif other.Value > self.Value:
            return 1
        else:
            return 0

    def Dump(self, aspaces=0):
        print '>%s<' % (self.Value)
        for aspace in self._items.keys:
            x = self._items[aspace]
            s = '%s[%d]' % (' ' * aspaces, aspace)
            print s,
            x.Dump(aspaces + 3)


class ICORMDSpaceTableIterator:

    def __init__(self, aspace, askiplastcolumns=0):
        self.space = aspace
        self.HeaderLen = len(self.space.header)
        self.SkipLastColumns = askiplastcolumns
        self.IsOdd = 0
        self.ShowProgress = 0
        self.RandomNameModifier = str(random.randint(0, 1000000))

    def ForEachRow(self, fc=-1, lc=-1):
        self.OnStartPage()
        self.ProcessTable(0, fc, lc)
        self.OnEndPage()

    def ForEachNotEmptyRow(self, fc=-1, lc=-1):
        self.OnStartPage()
        self.ProcessTable(1, fc, lc)
        self.OnEndPage()

    def ProcessTable(self, aempty=0, fc=-1, lc=-1):
        self.Value = None
        self.RowCount = 0
        if fc < 0:
            fc = self.space.MinCol
        if lc < 0:
            lc = self.space.MaxCol + 1
        if lc < fc:
            return
        self.OnStart(self.space.Caption)
        if len(self.space.header) > 0:
            self.OnStartHeader()
            for x in range(len(self.space.header) - self.SkipLastColumns):
                self.OnHeader(x, self.space.header.values[x])
            self.OnEndHeader()
        if not aempty:
            self.ProcessEachRow(fc, lc)
        else:
            self.ProcessEachRowEmpty(fc, lc)
        if len(self.space.footer) > 0:
            self.OnStartFooter()
            for x in range(len(self.space.footer) - self.SkipLastColumns):
                self.OnFooter(x, self.space.footer.values[x])
            self.OnEndFooter()
        self.OnEnd()

    def ProcessEachRow(self, fc, lc):
        #if self.ShowProgress:
        #   pmax=self.space._items.MaxLen()
        #   ppos=0
        #   SetProgress(0,pmax)
        self.OnStartBody()
        k, v = self.space._items.GetFirst()
        while k >= 0:
            self._rowchanged = 0
            self.Value = None
            self.OnStartRow(k)
            if fc >= 0:
                self.ProcessEachCol(k, v, fc, lc)
            else:
                self.ProcessEachColEmpty(k, v)
            self.OnEndRow(k)
            if self._rowchanged:
                self.IsOdd = 1 - self.IsOdd
                self.RowCount = self.RowCount + 1
            k, v = self.space._items.GetNext(k)
            #if self.ShowProgress:
            #   ppos=ppos+1
            #   if (ppos % 15)==0:
            #      SetProgress(ppos,pmax)
        self.OnEndBody()
        #if self.ShowProgress:
        #   SetProgress(0,0)
    def ProcessEachRowEmpty(self, fc, lc):
        #      print 'ProcessEachRowEmpty',self.space.MinCol,self.space.MaxCol
        #      print 'fc,lc',fc,lc
        #      print 'hl,slc',self.HeaderLen,self.SkipLastColumns
        #if self.ShowProgress:
        #   pmax=self.space._items.Len()
        #   ppos=0
        #   SetProgress(0,pmax)
        self.OnStartBody()
        for x in range(len(self.space._items)):
            k = self.space._items.keys[x]
            #         print 'row:',x,k
            self._rowchanged = 0
            self.Value = None
            self.OnStartRow(k)
            v = self.space._items[k]
            if fc >= 0:
                #            print 'a',fc,lc
                self.ProcessEachCol(k, v, fc, lc)
            else:
                #            print 'b',v
                self.ProcessEachColEmpty(k, v)
            self.OnEndRow(k)
            if self._rowchanged:
                self.IsOdd = 1 - self.IsOdd
                self.RowCount = self.RowCount + 1
        #   if self.ShowProgress:
        #      ppos=ppos+1
        #      if (ppos % 15)==0:
        #         SetProgress(ppos,pmax)
        self.OnEndBody()
        #if self.ShowProgress:
        #   SetProgress(0,0)
    def ProcessEachCol(self, arow, aspace, fc, lc):
        self._rowchanged = 1
        for k in range(fc, lc):
            if k > self.HeaderLen - self.SkipLastColumns:
                continue
            if aspace is None:
                self.Value = None
            else:
                v = aspace._items[k]
                if v is not None:
                    self.Value = v.Value
                else:
                    self.Value = None
            self.OnStartCol(arow, k)
            self.OnData(arow, k)
            self.OnEndCol(arow, k)

    def ProcessEachColEmpty(self, arow, aspace):
        if aspace is None:
            return
        k, v = aspace._items.GetFirst()
        while k >= 0:
            self.Value = v.Value
            if k <= self.HeaderLen - self.SkipLastColumns:
                self.OnStartCol(arow, k)
                if self.Value is not None:
                    self.OnData(arow, k)
                    self._rowchanged = 1
                self.OnEndCol(arow, k)
            k, v = aspace._items.GetNext(k)

    def OnStartPage(self):
        pass

    def OnEndPage(self):
        pass

    def OnStart(self, acaption=''):
        pass

    def OnEnd(self):
        pass

    def OnStartHeader(self):
        pass

    def OnEndHeader(self):
        pass

    def OnHeader(self, acol, avalue):
        pass

    def OnStartFooter(self):
        pass

    def OnEndFooter(self):
        pass

    def OnFooter(self, acol, avalue):
        pass

    def OnStartBody(self):
        pass

    def OnEndBody(self):
        pass

    def OnStartRow(self, arow):
        pass

    def OnEndRow(self, arow):
        pass

    def OnStartCol(self, arow, acol):
        pass

    def OnEndCol(self, arow, acol):
        pass

    def OnData(self, arow, acol):
        pass


def Test2():
    #def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    print 'ICORSortedDictionary'
    sl = ICORSortedDictionary()
    sl.Add(1, 1)
    sl.Add(10, 10)
    sl.Add(11, 11)
    sl.Add(14, 14)
    k, v = sl.GetFirst()
    while k >= 0:
        print k, v
        k, v = sl.GetNext(k)
    print 'ICORMDSpace'
    aspace = ICORMDSpace()
    aspace[0, 1] = 1
    aspace[0, 2] = 2
    aspace[1, 2] = 12
    aspace[2, 1] = 21
    aspace[1, 2, 3, 4] = 1234
    aspace[4, 2, 3] = 423
    aspace['aaa', 'bbb'] = 441
    aspace['aaa', 'bbb', 'ccc'] = 442
    aspace['bbb', 'bbb'] = 443
    aspace.Dump()

    print aspace[0, 1]
    print aspace[0, 2]
    print aspace[1, 2]
    print aspace[2, 1]
    print aspace[1, 2, 3, 4]
    print aspace[4, 2, 3]
    print 'text:'
    print aspace['aaa', 'bbb']
    print aspace['aaa', 'bbb', 'ccc']
    print aspace['bbb', 'bbb']
    aspace.Remove([0, 1])
    aspace.Remove([1, 2])
    aspace.Dump()
