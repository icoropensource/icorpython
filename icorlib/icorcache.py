# -*- coding: utf-8 -*-
import random


class ICORCache:

    def __init__(self, agetfunc, amaxlen=100):
        self.GetValue = agetfunc
        self.MaxLen = amaxlen
        self.VDict = {}
        self.KDict = {}
        self.VPos = 1
        self.AccessRatio = 0
        self.HitRatio = 0

    def __getitem__(self, key):
        self.AccessRatio = self.AccessRatio + 1
        id = self.KDict.get(key, 0)
        if id:
            self.HitRatio = self.HitRatio + 1
            return self.VDict[id][1]
        else:
            v = self.VDict.get(self.VPos, 0)
            if v:
                del self.KDict[v[0]]
            ret = apply(self.GetValue, (key, ))
            self.VDict[self.VPos] = [key, ret]
            self.KDict[key] = self.VPos
            self.VPos = self.VPos + 1
            if self.VPos > self.MaxLen:
                self.VPos = 1
            return ret

    def dump(self):
        print 'Access ratio:', self.AccessRatio
        print 'Hit ratio:', self.HitRatio
        print 'Hit %:', 100.0 * self.HitRatio / self.AccessRatio
        print 'VDict len:', len(self.VDict.keys())
        print 'KDict len:', len(self.KDict.keys())


def GetCalculatedValue(key):
    x = str(key) + 'aaaa'
    y = key * 0.5
    z = x + str(y)
    return z


# model of distribution
max = 1000


def GetIterative(key):
    return key


def GetRandom(key):
    return random.randint(1, max)


l1, l2, l3 = random.randint(1, max), random.randint(1, max), random.randint(1, max)


def GetNDist(key):
    global l1, l2, l3
    l1, l2, l3 = l2, l3, random.randint(1, max)
    return int((l1 + l2 + l3) / 3)


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    #   ClearStdOut()
    for aname, afunc in [['Iterative', GetIterative], ['Random', GetRandom], ['NDist', GetNDist]]:
        acache = ICORCache(GetCalculatedValue, 100)
        for i in range(1000):
            k = afunc(i)
            x = acache[k]
            y = GetCalculatedValue(k)
            if x != y:
                print 'Error!!!', k, x, y
        print 'Name:', aname
        acache.dump()
        print
    return
