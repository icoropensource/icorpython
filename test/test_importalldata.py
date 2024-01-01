# -*- coding: utf-8 -*-
import sys
import time
try:
    import json
except:
    import simplejson as json

import icorapi

import appplatform.storageutil as storageutil

UID = 0

import icorlib.icorinterface as ICORInterface

MIN_DATE_TIME = [0, 0, 0, 0, 0, 0, 0]
START_DATE_TIME = [1899, 12, 30, 0, 0, 0, 0]


def GetObjectAsJSON(aclass, aoid, atextindexsize):
    d = {}
    flist = aclass.GetFieldsList()
    maxadt = START_DATE_TIME
    for afname in flist:
        afield = aclass.FieldsByName(afname)
        if afield.IsVirtual == '1':
            continue
        adt = afield.GetValueLastModified(aoid)
        v = afield.ValuesAsComp(aoid, ajsonfriendly=1)
        vi = v
        if type(v) in [type(''), type(u'')]:
            #v=storageutil.CP1250_To_UTF8(v)
            v = unicode(v, 'cp1250', 'ignore')
            vi = v[:atextindexsize].lower()
            v = v.encode('utf-8', 'xmlcharrefreplace')
            vi = vi.encode('utf-8', 'xmlcharrefreplace')
        else:
            vi = str(vi).lower()
        if (adt < START_DATE_TIME) or (adt[0] < 1974):
            adt = START_DATE_TIME
        d['v' + afname] = v
        d['l' + afname] = storageutil.tdatetime2fmtstr(adt)
        d['i' + afname] = vi
        if adt > maxadt:
            maxadt = adt
    #return json.dumps(d,ensure_ascii=False)
    return maxadt, d


def Test_AllData_UpdateObjects():
    adt1a = time.clock()
    aclass = ICORInterface.aICORDBEngine.Classes.FirstClass()
    #aclass=ICORInterface.aICORDBEngine.Classes[1783]
    atextindexsize = icorapi.aICORDB.GetConfigValue('PGTextIndexSize')
    lc = []
    while aclass is not None:
        aoid = aclass.FirstObject()
        maxadt = START_DATE_TIME
        cnt = 0
        while aoid >= 0:
            omaxadt, v = GetObjectAsJSON(aclass, aoid, atextindexsize)
            if omaxadt > maxadt:
                maxadt = omaxadt
            icorapi.aICORDB.struct.AllData_UpdateObject(aclass.CID, aoid, 0, omaxadt, v)
            cnt += 1
            aoid = aclass.NextObject(aoid)
        print aclass.CID, cnt, maxadt
        lc.append([aclass.CID, cnt, maxadt])
        aclass = ICORInterface.aICORDBEngine.Classes.NextClass(aclass.CID)
    adt1b = time.clock()
    #print lc
    amax = len(lc)
    wgood = 1
    ti, tp = adt1b - adt1a, adt1b - adt1a
    print 'Test_AllData_UpdateObjects [%d]=%d - ICOR: %0.5f, PG: %0.5f, ratio: %0.2f' % (amax, wgood, ti, tp, ti / tp)


if __name__ == '__main__':
    if 0:
        aclass = ICORInterface.aICORDBEngine.Classes[1189]
        v = aclass.PoleM[1]
        v1 = storageutil.CP1250_To_UTF8(v)
        print U'V: ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ'
        print 1, type(v1), v1
        #print 2,v.encode('utf-8','xmlcharrefreplace')
        print 3, unicode(v, 'cp1250', 'ignore').lower()    #.encode('utf-8','xmlcharrefreplace')

    if 1:
        Test_AllData_UpdateObjects()
