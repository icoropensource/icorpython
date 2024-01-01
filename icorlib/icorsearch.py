# -*- coding: utf-8 -*-
from icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import strLowerPL
import re
import types


class ICORRepositorySearch:

    def __init__(self, afield):
        self.FieldItem = afield
        self.IsCaseSensitive = 0

    def BinaryFind(self, afunc, aposition=0):
        res, l = 0, aposition
        m = self.FieldItem.ObjectsCount() - 1
        while l <= m:
            i = (l + m) / 2
            c = afunc(i)
            if c < 0:
                l = i + 1
            else:
                m = i - 1
                if not c:
                    res = 1
        if not res:
            l = -1
        return l

    def BinaryFindLeft(self, afunc, aposition=0):
        res, lo = 0, aposition
        hi = self.FieldItem.ObjectsCount() - 1
        while lo < hi:
            mid = (lo + hi) / 2
            c = afunc(mid)    #a[mid]<x
            if c < 0:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def BinaryFindRight(self, afunc, aposition=0):
        res, lo = 0, aposition
        hi = self.FieldItem.ObjectsCount() - 1
        while lo < hi:
            mid = (lo + hi) / 2
            c = afunc(mid)    #x<a[mid]:
            if c < 0:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def FirstEQ(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFind(self.CompEQCase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFind(self.CompEQ, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextEQ(self):
        if self.IsCaseSensitive:
            if self.CompEQCase(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = self.BinaryFind(self.CompEQCase, self.Position + 1)
        else:
            if self.CompEQ(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = self.BinaryFind(self.CompEQ, self.Position + 1)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def CompEQCase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value > self.Key:
            return 1
        elif self.Value < self.Key:
            return -1
        else:
            return 0

    def CompEQ(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        if bkey > self.Key:
            return 1
        elif bkey < self.Key:
            return -1
        else:
            return 0
#Left

    def FindLeft(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFindLeft(self.CompLeftCase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFindLeft(self.CompLeft, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def CompLeftCase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value < self.Key:
            return -1
        else:
            return 1

    def CompLeft(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        #      print aposition,aoid,bkey,self.Key
        if bkey < self.Key:
            return -1
        else:
            return 1
#Right

    def FindRight(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFindRight(self.CompRightCase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFindRight(self.CompRight, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def CompRightCase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Key < self.Value:
            return -1
        else:
            return 1

    def CompRight(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        #print aposition, aoid, bkey, self.Key
        if self.Key < self.Value:
            return -1
        else:
            return 1
# Less

    def FirstLE(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFind(self.CompLECase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFind(self.CompLE, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextLE(self):
        if self.IsCaseSensitive:
            if self.CompLECase(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = -1
        else:
            if self.CompLE(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = -1
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def CompLECase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value < self.Key:
            return 0
        else:
            return 1

    def CompLE(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        if bkey < self.Key:
            return 0
        else:
            return 1
# Less or Equal

    def FirstLEQ(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFind(self.CompLEQCase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFind(self.CompLEQ, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextLEQ(self):
        if self.IsCaseSensitive:
            if self.CompLEQCase(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = -1
        else:
            if self.CompLEQ(self.Position + 1) == 0:
                self.Position = self.Position + 1
            else:
                self.Position = -1
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def CompLEQCase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value <= self.Key:
            return 0
        else:
            return 1

    def CompLEQ(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        if bkey <= self.Key:
            return 0
        else:
            return 1
# Greater

    def FirstGE(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFind(self.CompGECase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFind(self.CompGE, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextGE(self):
        self.Position = self.Position + 1
        if self.Position >= self.FieldItem.ObjectsCount():
            self.Position = -1
        return self.Position

    def CompGECase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value > self.Key:
            return 0
        else:
            return -1

    def CompGE(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        if bkey > self.Key:
            return 0
        else:
            return -1
# Greater or Equal

    def FirstGEQ(self, akey):
        if self.IsCaseSensitive:
            self.Key = akey
            self.Position = self.BinaryFind(self.CompGEQCase, 0)
        else:
            if isinstance(akey, types.StringTypes):
                self.Key = strLowerPL(akey)
            else:
                self.Key = akey
            self.Position = self.BinaryFind(self.CompGEQ, 0)
        if self.LastPosition != self.Position and self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextGEQ(self):
        self.Position = self.Position + 1
        if self.Position >= self.FieldItem.ObjectsCount():
            self.Position = -1
        return self.Position

    def CompGEQCase(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        self.LastPosition = aposition
        if self.Value >= self.Key:
            return 0
        else:
            return -1

    def CompGEQ(self, aposition):
        aoid = self.FieldItem.GetValueIDByPosition(aposition)
        self.Value = self.FieldItem.ValuesAsComp(aoid)
        if isinstance(self.Value, types.StringTypes):
            bkey = strLowerPL(self.Value)
        else:
            bkey = self.Value
        self.LastPosition = aposition
        if bkey >= self.Key:
            return 0
        else:
            return -1
# by Range

    def FirstRange(self, akey1, akey2):
        self.Position2 = self.FirstGE(akey2)
        self.Position = self.FirstGEQ(akey1)
        if self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position

    def NextRange(self):
        self.Position = self.Position + 1
        if self.Position >= self.Position2 or self.Position >= self.FieldItem.ObjectsCount():
            self.Position = -1
        else:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
        return self.Position


# by Pattern

    def FirstPattern(self, akey1, apattern):
        self.Position = self.FirstGEQ(akey1)
        if self.IsCaseSensitive:
            self.Pattern = re.compile(apattern)
        else:
            self.Pattern = re.compile(apattern, re.I)
        if self.Position >= 0:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
            if isinstance(self.Value, types.StringTypes):
                bkey = self.Value
            else:
                bkey = self.FieldItem[aoid]
            if not self.Pattern.search(bkey):
                self.Position = -1
        return self.Position

    def NextPattern(self):
        self.Position = self.Position + 1
        if self.Position >= self.FieldItem.ObjectsCount():
            self.Position = -1
        else:
            aoid = self.FieldItem.GetValueIDByPosition(self.Position)
            self.Value = self.FieldItem.ValuesAsComp(aoid)
            if isinstance(self.Value, types.StringTypes):
                bkey = self.Value
            else:
                bkey = self.FieldItem[aoid]
            if not self.Pattern.search(bkey):
                self.Position = -1
        return self.Position


class ICORRepositorySearchIterator(ICORRepositorySearch):

    def __init__(self, afield, afunc, aparms):
        ICORRepositorySearch.__init__(self, afield)
        self.Function = afunc
        self.Parms = aparms

    def ForEachValueByRange(self, akey1, akey2):
        apos = self.FirstRange(akey1, akey2)
        while apos >= 0:
            self.OnValue()
            apos = self.NextRange()

    def ForEachValueByPattern(self, akey1, apattern):
        apos = self.FirstPattern(akey1, apattern)
        while apos >= 0:
            self.OnValue()
            apos = self.NextPattern()

    def OnValue(self):
        apply(self.Function, (self.FieldItem, self.Position, self.Value) + self.Parms)


def ForEachValueByRange(afield, afunc, akey1, akey2, *parms):
    ICORRepositorySearchIterator(afield, afunc, parms).ForEachValueByRange(akey1, akey2)


def ForEachValueByRangeParms(afield, afunc, akey1, akey2, parms):
    ICORRepositorySearchIterator(afield, afunc, parms).ForEachValueByRange(akey1, akey2)


def ForEachValueByPattern(afield, afunc, akey1, apattern, *parms):
    ICORRepositorySearchIterator(afield, afunc, parms).ForEachValueByPattern(akey1, apattern)


def ForEachValueByPatternParms(afield, afunc, akey1, apattern, parms):
    ICORRepositorySearchIterator(afield, afunc, parms).ForEachValueByPattern(akey1, apattern)
