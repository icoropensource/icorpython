# -*- coding: utf-8 -*-
import sys
import time

sys.__icordisablecheckexists = 1

import icorapi

import appplatform.storageutil as storageutil

UID = 0

CLASSES_Library_Test_NetBase_Input_Test1 = 1189
CLASSES_Library_Test_NetBase_Input_Test2 = 1190
CLASSES_Library_Test_NetBase_Input_Test3 = 2093
#CLASSES_Library_Test_NetBase_Input_Test1_PoleB - 6504
#CLASSES_Library_Test_NetBase_Input_Test1_PoleC - 6507
#CLASSES_Library_Test_NetBase_Input_Test1_PoleD - 6505
#CLASSES_Library_Test_NetBase_Input_Test1_PoleF - 6503
#CLASSES_Library_Test_NetBase_Input_Test1_PoleI - 6502
#CLASSES_Library_Test_NetBase_Input_Test1_PoleM - 6506
#CLASSES_Library_Test_NetBase_Input_Test1_PoleS - 6501


class TestTimer(object):

    def __init__(self, aname, amax=1000, astart=1, atests=3):
        self.name = aname
        self.max = amax
        self.tests = atests
        self.Reset()
        if astart:
            self.Start()

    def Reset(self):
        self.counters = [{}, {}, {}]
        self.timers = [[0, 0], [0, 0], [0, 0]]
        self.currentcounter = 0
        self.wgood = 1

    def Start(self, acounter=0):
        if acounter >= len(self.timers):
            return
        self.currentcounter = acounter
        self.timers[self.currentcounter][0] = time.clock()

    def Finish(self, astartnext=1):
        self.timers[self.currentcounter][1] = time.clock()
        if astartnext:
            self.Start(self.currentcounter + 1)

    def AddData(self, k, v):
        self.counters[self.currentcounter][k] = v

    def CheckGood(self, aprint=0):
        self.wgood = 1
        lk = self.counters[0].keys()
        lk.sort()
        for k in lk:
            if self.counters[0][k] != self.counters[1][k]:
                if (self.counters[0][k] is None) and (self.counters[1][k] is None):
                    pass
                else:
                    self.wgood = 0
                    if aprint:
                        print k, '********************-'
                        print 'I:', self.counters[0][k], type(self.counters[0][k])
                        print 'P:', self.counters[1][k], type(self.counters[1][k])
            elif (self.tests > 2) and (self.counters[0][k] != self.counters[2][k]):
                self.wgood = 0
                if aprint:
                    print k, '********************--'
                    print 'I:', self.counters[0][k]
                    print 'A:', self.counters[2][k]
        ti = self.timers[0][1] - self.timers[0][0]
        if self.tests > 2:
            tp = self.timers[1][1] - self.timers[1][0]
            ta = self.timers[2][1] - self.timers[2][0]
            print '%s [%d]=%d - ICOR: %0.5f, PG: %0.5f, ALL: %0.5f, ratio I/P: %0.2f, ratio I/A: %0.2f' % (self.name, self.max, self.wgood, ti, tp, ta, ti / tp, ti / ta)
        else:
            ta = self.timers[1][1] - self.timers[1][0]
            print '%s [%d]=%d - ICOR: %0.5f, ALL: %0.5f, ratio I/A: %0.2f' % (self.name, self.max, self.wgood, ti, ta, ti / ta)


def Test_API_ClassExists(amax=1000):
    atimer = TestTimer('Test_API_ClassExists')
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.ClassExists(UID, cid, usepg=0))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.ClassExists(UID, cid, usepg=1))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.ClassExists(UID, cid, usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_GetClassID(amax=200):
    lc = ['CLASSES_System_ICORClass', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', 'CLASSES_System_User', 'XXX']
    atimer = TestTimer('Test_API_GetClassID')
    for i in range(amax):
        for aclasspath in lc:
            atimer.AddData(aclasspath, icorapi.GetClassID(UID, aclasspath, usepg=0))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            atimer.AddData(aclasspath, icorapi.GetClassID(UID, aclasspath, usepg=1))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            atimer.AddData(aclasspath, icorapi.GetClassID(UID, aclasspath, usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_GetFieldValue(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValue')
    for i in range(1, amax + 1):
        s = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=0)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleF',i,usepg=0)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleD',i,usepg=0)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleM', i, usepg=0)
        atimer.AddData(i, s)
    atimer.Finish()
    for i in range(1, amax + 1):
        s = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=1)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleF',i,usepg=1)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleD',i,usepg=1)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleM', i, usepg=1)
        atimer.AddData(i, s)
    atimer.Finish()
    for i in range(1, amax + 1):
        s = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=2)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleF',i,usepg=2)
        #s+=icorapi.GetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleD',i,usepg=2)
        s += icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleM', i, usepg=2)
        atimer.AddData(i, s)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueInt(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueInt')
    for i in range(1, amax + 1):
        if i > 500:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=0))
        else:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        if i > 500:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=1))
        else:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        if i > 500:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, usepg=2))
        else:
            atimer.AddData(i, icorapi.GetFieldValueInt(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueFloat(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueFloat')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueDateTime(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueDateTime')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueDate(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueDate')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDate(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDate(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueDate(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueTime(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueTime')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValuePyTime(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValuePyTime')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValuePyTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValuePyTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValuePyTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueLastModification(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueLastModification')
    for i in range(1, amax + 1):
        v = icorapi.GetFieldValueLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0)
        v[6] = 0
        atimer.AddData(i, v)
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_ValueExists(amax=1000):
    atimer = TestTimer('Test_API_ValueExists')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ValueExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ValueExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ValueExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_ObjectExists(amax=1000):
    atimer = TestTimer('Test_API_ObjectExists')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ObjectExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ObjectExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.ObjectExists(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetObjectCount(amax=1000):
    atimer = TestTimer('Test_API_GetObjectCount')
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetObjectCount(UID, cid, usepg=0))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetObjectCount(UID, cid, usepg=1))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetObjectCount(UID, cid, usepg=2))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetObjectCount(UID, cid, usepg=1))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFirstObjectID(amax=1000):
    atimer = TestTimer('Test_API_GetFirstObjectID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFirstObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFirstObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFirstObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetLastObjectID(amax=1000):
    atimer = TestTimer('Test_API_GetLastObjectID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetLastObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetLastObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetLastObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetNextObjectID(amax=1000):
    atimer = TestTimer('Test_API_GetNextObjectID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetPrevObjectID(amax=1000):
    atimer = TestTimer('Test_API_GetPrevObjectID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFirstFieldValueID(amax=1000):
    lp = ['PoleB', 'PoleC', 'PoleD', 'PoleF', 'PoleI', 'PoleM', 'PoleS', 'XXX']
    atimer = TestTimer('Test_API_GetFirstFieldValueID')
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetFirstFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetFirstFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetFirstFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetLastFieldValueID(amax=1000):
    lp = ['PoleB', 'PoleC', 'PoleD', 'PoleF', 'PoleI', 'PoleM', 'PoleS', 'XXX']
    atimer = TestTimer('Test_API_GetLastFieldValueID')
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetLastFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetLastFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        for afieldname in lp:
            atimer.AddData((i, afieldname), icorapi.GetLastFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, afieldname, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetNextFieldValueID(amax=1000):
    atimer = TestTimer('Test_API_GetNextFieldValueID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetPrevFieldValueID(amax=1000):
    atimer = TestTimer('Test_API_GetPrevFieldValueID')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetPrevFieldValueID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetObjectIDByPosition(amax=1000):
    atimer = TestTimer('Test_API_GetObjectIDByPosition')
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetObjectIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetObjectIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=1))
    atimer.Finish()
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetObjectIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetValueIDByPosition(amax=1000):
    atimer = TestTimer('Test_API_GetValueIDByPosition')
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetValueIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0))
    atimer.Finish()
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetValueIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1))
    atimer.Finish()
    for i in range(0, amax):
        atimer.AddData(i, icorapi.GetValueIDByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldValueByPosition(amax=1000):
    atimer = TestTimer('Test_API_GetFieldValueByPosition')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldValueByPosition(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldObjectsCount(amax=1000):
    atimer = TestTimer('Test_API_GetFieldObjectsCount')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldObjectsCount(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldObjectsCount(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldObjectsCount(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_IsObjectDeleted(amax=1000):
    atimer = TestTimer('Test_API_IsObjectDeleted')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.IsObjectDeleted(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.IsObjectDeleted(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.IsObjectDeleted(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFieldsList(amax=1000):
    atimer = TestTimer('Test_API_GetFieldsList')
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFieldsList(UID, cid, usepg=0))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFieldsList(UID, cid, usepg=1))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFieldsList(UID, cid, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetFirstClass(amax=1000):
    atimer = TestTimer('Test_API_GetFirstClass')
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFirstClass(UID, usepg=0))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFirstClass(UID, usepg=1))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetFirstClass(UID, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetNextClass(amax=1000):
    atimer = TestTimer('Test_API_GetNextClass')
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetNextClass(UID, cid, usepg=0))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetNextClass(UID, cid, usepg=1))
    atimer.Finish()
    for cid in range(1, amax + 1):
        atimer.AddData(cid, icorapi.GetNextClass(UID, cid, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_FindValue(amax=1000):
    atimer = TestTimer('Test_API_FindValue')
    sconst = 'AAAA ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ bbbb - %d'
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', sconst % i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', sconst % i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', sconst % i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_FindValueBoolean(amax=1000):
    atimer = TestTimer('Test_API_FindValueBoolean')
    for i in range(1, amax + 1):
        w = 0
        if i > 500:
            w = 1
        atimer.AddData(i, icorapi.FindValueBoolean(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleB', w, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        w = 0
        if i > 500:
            w = 1
        atimer.AddData(i, icorapi.FindValueBoolean(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleB', w, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        w = 0
        if i > 500:
            w = 1
        atimer.AddData(i, icorapi.FindValueBoolean(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleB', w, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_FindValueDateTime(amax=1000):
    atimer = TestTimer('Test_API_FindValueDateTime')
    for i in range(1, amax + 1):
        i1, i2, i3, i4, i5, i6, i7 = 2016, 1, 26, 0, 0, 0, 0
        if i > 300:
            i1, i2, i3, i4, i5, i6, i7 = 2014, 7, 30, 6, 39, 0, 0
        if i > 700:
            i1, i2, i3, i4, i5, i6, i7 = 2019, 7, 30, 6, 39, 0, 0
        atimer.AddData(i, icorapi.FindValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i1, i2, i3, i4, i5, i6, i7, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        i1, i2, i3, i4, i5, i6, i7 = 2016, 1, 26, 0, 0, 0, 0
        if i > 300:
            i1, i2, i3, i4, i5, i6, i7 = 2014, 7, 30, 6, 39, 0, 0
        if i > 700:
            i1, i2, i3, i4, i5, i6, i7 = 2019, 7, 30, 6, 39, 0, 0
        atimer.AddData(i, icorapi.FindValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i1, i2, i3, i4, i5, i6, i7, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        i1, i2, i3, i4, i5, i6, i7 = 2016, 1, 26, 0, 0, 0, 0
        if i > 300:
            i1, i2, i3, i4, i5, i6, i7 = 2014, 7, 30, 6, 39, 0, 0
        if i > 700:
            i1, i2, i3, i4, i5, i6, i7 = 2019, 7, 30, 6, 39, 0, 0
        atimer.AddData(i, icorapi.FindValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i1, i2, i3, i4, i5, i6, i7, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_FindValueFloat(amax=1000):
    atimer = TestTimer('Test_API_FindValueFloat')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', 124.4 + i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', 124.4 + i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueFloat(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleF', 124.4 + i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_FindValueInteger(amax=1000):
    atimer = TestTimer('Test_API_FindValueInteger')
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueInteger(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', 123 + i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueInteger(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', 123 + i, usepg=1))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.FindValueInteger(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', 123 + i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_GetFieldOIDsBySearchValue():
    CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy = 1744
    for value, acase, aregexp in [('rad', 0, 0), ('rad', 0, 1), ('rad', 1, 0), ('rad', 1, 1)]:
        ret1 = icorapi.GetFieldOIDsBySearchValue(UID, CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy, 'Nazwa', value, acasesensitive=acase, aregexp=aregexp, usepg=1)
        ret2 = icorapi.GetFieldOIDsBySearchValue(UID, CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy, 'Nazwa', value, acasesensitive=acase, aregexp=aregexp, usepg=2)
        print 'ret:', value, acase, aregexp, '=', ret1, '=', ret2


def Test_API_GetFieldValue_BadField(amax=1000):
    ret1 = icorapi.aICORDB.struct.API_GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 0, afid=20000, alldata=1)
    ret2 = icorapi.aICORDB.struct.API_GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 0, afid=20000, alldata=2)
    print 'Test_API_GetFieldValue_BadField = %s | %s' % (ret1, ret2)


def Test_API_CompareOIDs(amax=1000):
    atimer = TestTimer('Test_API_CompareOIDs', atests=2)
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.CompareOIDs(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, i + 1, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.CompareOIDs(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, i + 1, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_CompareOIDValue(amax=1000):
    atimer = TestTimer('Test_API_CompareOIDValue', atests=2)
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.CompareOIDValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, '   ', usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.CompareOIDValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, '   ', usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=0)


def Test_API_GetMethodsList(amax=50):
    lc = ['CLASSES_Library_Test_NetBase_Input_Test1', 'CLASSES_System_ICORClass', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', 'CLASSES_System_User', 'XXX']
    atimer = TestTimer('Test_API_GetMethodsList', atests=2)
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.GetMethodsList(UID, acid, 1, usepg=0))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.GetMethodsList(UID, acid, 1, usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_IsMethodInClass(amax=50):
    lc = ['CLASSES_Library_Test_NetBase_Input_Test1', 'CLASSES_System_ICORClass', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', 'CLASSES_System_User', 'XXX']
    atimer = TestTimer('Test_API_IsMethodInClass', atests=2)
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsMethodInClass(UID, acid, 'OnObjectDelete', usepg=0))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsMethodInClass(UID, acid, 'OnObjectDelete', usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_IsMethodInThisClass(amax=50):
    lc = ['CLASSES_Library_Test_NetBase_Input_Test1', 'CLASSES_System_ICORClass', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', 'CLASSES_System_User', 'XXX']
    atimer = TestTimer('Test_API_IsMethodInThisClass', atests=2)
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsMethodInThisClass(UID, acid, 'OnObjectDelete', usepg=0))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsMethodInThisClass(UID, acid, 'OnObjectDelete', usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_IsFieldInClass(amax=50):
    lc = ['CLASSES_Library_Test_NetBase_Input_Test1', 'CLASSES_System_ICORClass', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt', 'CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura', 'CLASSES_System_User', 'XXX']
    atimer = TestTimer('Test_API_IsFieldInClass', atests=2)
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsFieldInClass(UID, acid, 'PoleS', usepg=0))
    atimer.Finish()
    for i in range(amax):
        for aclasspath in lc:
            acid = icorapi.GetClassID(UID, aclasspath, usepg=2)
            if acid > 255:
                atimer.AddData(aclasspath, icorapi.IsFieldInClass(UID, acid, 'PoleS', usepg=2))
    atimer.Finish()
    atimer.CheckGood()


def Test_API_GetFieldModification(amax=1000):
    atimer = TestTimer('Test_API_GetFieldModification', atests=2)
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetFieldModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetObjectModification(amax=1000):
    atimer = TestTimer('Test_API_GetObjectModification', atests=2)
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetObjectModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetObjectModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_GetNextFreeObjectID(amax=1000):
    atimer = TestTimer('Test_API_GetNextFreeObjectID', atests=2)
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextFreeObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, i + 20, usepg=0))
    atimer.Finish()
    for i in range(1, amax + 1):
        atimer.AddData(i, icorapi.GetNextFreeObjectID(UID, CLASSES_Library_Test_NetBase_Input_Test1, i, i + 20, usepg=2))
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_ExecuteMethod(amax=10):
    #ret=icorapi.GetMethodInfo(0,CLASSES_Library_Test_NetBase_Input_Test1,'Test1')
    #ret=icorapi.GetClassInfo(0,CLASSES_Library_Test_NetBase_Input_Test1)
    #print ret
    #return
    lm = ['ETest1N', 'ETest1P', 'ETest1PQ', 'ETest1Q', 'ETest1I']    # 'ETest1E','XXX'
    atimer = TestTimer('Test_API_ExecuteMethod', atests=2)
    for i in range(amax):
        for amethodname in lm:
            v = icorapi.ExecuteMethod(UID, CLASSES_Library_Test_NetBase_Input_Test1, amethodname, 'afieldname', 123, 'avalue', 0, usepg=0)
            #print 1,amethodname,v,type(v)
            atimer.AddData(amethodname, v)
    atimer.Finish()
    for i in range(amax):
        for amethodname in lm:
            v = icorapi.ExecuteMethod(UID, CLASSES_Library_Test_NetBase_Input_Test1, amethodname, 'afieldname', 123, 'avalue', 0, usepg=2)
            #print 2,amethodname,v,type(v)
            atimer.AddData(amethodname, v)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_SetFieldValue_Class(amax=10):
    #icorapi.SetFieldValue(UID,CLASSES_Library_Test_NetBase_Input_Test1,'PoleS',3,'ZZZ',usepg=2)
    ovalue = '4:1190:5:1190:'
    nvalue = '5:1190:7:1190:8:1190:'
    icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleC', 3, nvalue, usepg=2)


def Test_API_SetFieldValue_String(amax=100):
    atimer = TestTimer('Test_API_SetFieldValue_String', atests=2)
    for i in range(2000, 2000 + amax + 1):
        avalue = 'ZZZ4 - ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ ' + ` i `
        avalue = storageutil.UTF8_To_CP1250(avalue)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, avalue, usepg=0)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        avalue = 'ZZZ4 - ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ ' + ` i ` + 'X'
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, avalue, usepg=2)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', i, usepg=2)
        atimer.AddData(i, avalue[:-1])
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_SetFieldValueDate(amax=100):
    atimer = TestTimer('Test_API_SetFieldValueDate', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueDate(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 2020, 02, 15, usepg=0)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueDate(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 2020, 02, 16, usepg=2)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_SetFieldValueDateTime(amax=100):
    atimer = TestTimer('Test_API_SetFieldValueDateTime', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 2020, 02, 15, 12, 12, 12, 0, usepg=0)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueDateTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 2020, 02, 16, 12, 12, 14, 0, usepg=2)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_API_SetFieldValueTime(amax=100):
    atimer = TestTimer('Test_API_SetFieldValueTime', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 12, 12, 12, 0, usepg=0)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValueTime(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, 12, 12, 14, 0, usepg=2)
        avalue = icorapi.GetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleD', i, usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_SetTestDecFieldValue(amax=100):
    atimer = TestTimer('Test_SetTestDecFieldValue', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=0)
        avalue = icorapi.SetTestDecFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=2)
        avalue = icorapi.SetTestDecFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_SetTestIncFieldValue(amax=100):
    atimer = TestTimer('Test_SetTestIncFieldValue', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=0)
        avalue = icorapi.SetTestIncFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=2)
        avalue = icorapi.SetTestIncFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_SetTestFieldValue(amax=100):
    atimer = TestTimer('Test_SetTestFieldValue', atests=2)
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=0)
        avalue = icorapi.SetTestFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', '105', usepg=0)
        atimer.AddData(i, avalue)
    atimer.Finish()
    for i in range(2000, 2000 + amax + 1):
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, '100', usepg=2)
        avalue = icorapi.SetTestFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleI', i, 1, '100', '105', usepg=2)
        atimer.AddData(i, avalue)
    atimer.Finish()
    atimer.CheckGood(aprint=1)


def Test_SetClassLastModification():
    icorapi.SetClassLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 2020, 06, 20, 22, 22, 23, 0, usepg=0)
    icorapi.SetClassLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 2020, 06, 20, 22, 22, 24, 0, usepg=2)


def Test_SetFieldLastModification():
    icorapi.SetFieldLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 2020, 06, 20, 22, 22, 23, 0, usepg=0)
    icorapi.SetFieldLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 2020, 06, 20, 22, 22, 24, 0, usepg=2)


def Test_SetFieldModification():
    icorapi.SetFieldModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 3, '2020-06-30 12:22:33', usepg=0)
    icorapi.SetFieldModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 3, '2020-06-30 12:22:34', usepg=2)


def Test_SetMethodLastModification():
    icorapi.SetMethodLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'Test1', 2020, 06, 20, 22, 22, 23, 0, usepg=0)
    icorapi.SetMethodLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'Test1', 2020, 06, 20, 22, 22, 24, 0, usepg=2)


def Test_SetObjectModification():
    icorapi.SetObjectModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3, '2020-07-01 12:22:33', usepg=0)
    icorapi.SetObjectModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3, '2020-07-01 12:22:34', usepg=2)


def Test_SetFieldValueLastModification():
    icorapi.SetFieldValueLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 3, 2020, 06, 23, 22, 22, 23, 0, usepg=0)
    icorapi.SetFieldValueLastModification(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 3, 2020, 06, 23, 22, 22, 24, 0, usepg=2)


def Test_SetObjectModified():
    icorapi.SetObjectModified(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3, usepg=2)


def Test_SetClassProperty():
    icorapi.SetClassProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'ClassDescription', 'Klasa testowa do API', usepg=2)


def Test_SetFieldProperty():
    icorapi.SetFieldProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 'FieldNameAsDisplayed', 'Pole testowe S', usepg=2)
    icorapi.SetFieldProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 'IsObligatory', '1', usepg=2)
    icorapi.SetFieldProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'PoleS', 'FieldLeft', '11', usepg=2)


def Test_SetMethodProperty():
    icorapi.SetMethodProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'Test2', 'MethodText', '''from icorlib.icorinterface import *

#hello 1 ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ
def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
   aclass=aICORDBEngine.Classes[CID]
   return
   ''', usepg=2)
    icorapi.SetMethodProperty(UID, CLASSES_Library_Test_NetBase_Input_Test1, 'Test2', 'WWWConfirmExecute', '1', usepg=2)


def Test_CreateObjectByID():
    icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3000, usepg=2)
    icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3000, usepg=2)
    icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test1, 3000, usepg=2)


def Test_AddObject():
    ret = icorapi.AddObject(UID, CLASSES_Library_Test_NetBase_Input_Test1, usepg=2)
    print 'object added:', ret


def Test_DeleteObject():
    for i in range(1, 3):
        icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test3, i, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleS', i, 'test - kasowanie ' + ` i `, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleC', i, '100:' + ` CLASSES_Library_Test_NetBase_Input_Test2 ` + ':', usepg=2)
        ret = icorapi.DeleteObject(UID, CLASSES_Library_Test_NetBase_Input_Test3, i, usepg=2)
        print 'deleted:', i, 'res:', ret


def Test_ClearAllObjects():
    for i in range(1, 5):
        icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test3, i, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleS', i, 'test - kasowanie ' + ` i `, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleC', i, '100:' + ` CLASSES_Library_Test_NetBase_Input_Test2 ` + ':', usepg=2)
    ret = icorapi.ClearAllObjects(UID, CLASSES_Library_Test_NetBase_Input_Test3, usepg=2)


def Test_ClearAllValues():
    for i in range(1, 5):
        icorapi.CreateObjectByID(UID, CLASSES_Library_Test_NetBase_Input_Test3, i, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleS', i, 'test - kasowanie ' + ` i `, usepg=2)
        icorapi.SetFieldValue(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleC', i, '100:' + ` CLASSES_Library_Test_NetBase_Input_Test2 ` + ':', usepg=2)
    ret = icorapi.ClearAllValues(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleS', usepg=2)


def Test_GetFieldVersions():
    ret = icorapi.GetFieldVersions(UID, CLASSES_Library_Test_NetBase_Input_Test3, 'PoleS', 1)
    for rec in ret:
        print 'REC:', rec


def Test_Variables():
    print icorapi.GetVariable(1, 'test1'), 'e'
    icorapi.SetVariable(1, 'test1', 'v1')
    print icorapi.GetVariable(1, 'test1'), 'v'
    icorapi.DeleteVariable(1, 'test1')
    print icorapi.GetVariable(1, 'test1'), 'e'


def Test_GetObjectsValue():
    ret = icorapi.GetObjectsValue(UID, CLASSES_Library_Test_NetBase_Input_Test1, fields=set(['PoleD', 'PoleI']))
    for o in ret:
        print o, ret[o]


if __name__ == '__main__':
    if 0:
        Test_API_ClassExists()
        Test_API_GetClassID()
        Test_API_GetFieldValue()
        Test_API_GetFieldValueInt()
        Test_API_GetFieldValueFloat()
        Test_API_GetFieldValueDateTime()
        Test_API_GetFieldValueDate()
        Test_API_GetFieldValueTime()
        Test_API_GetFieldValuePyTime()
        Test_API_GetFieldValueLastModification()
        Test_API_ValueExists()
        Test_API_ObjectExists()
        Test_API_GetObjectCount()
        Test_API_GetFirstObjectID()
        Test_API_GetLastObjectID()
        Test_API_GetNextObjectID()
        Test_API_GetPrevObjectID()
        Test_API_GetFirstFieldValueID()
        Test_API_GetLastFieldValueID()
        Test_API_GetNextFieldValueID()
        Test_API_GetPrevFieldValueID()
        Test_API_GetObjectIDByPosition()
        Test_API_GetValueIDByPosition()
        Test_API_GetFieldValueByPosition()
        Test_API_GetFieldObjectsCount()
        Test_API_IsObjectDeleted()
        Test_API_GetFieldsList()
        Test_API_GetFieldValue_BadField()
        Test_API_GetFirstClass()
        Test_API_GetNextClass()
        Test_API_FindValue()
        Test_API_FindValueBoolean()
        Test_API_FindValueDateTime()
        Test_API_FindValueFloat()
        Test_API_FindValueInteger()
        Test_API_GetFieldOIDsBySearchValue()
        Test_API_GetFieldValue()
        Test_API_CompareOIDs()
        Test_API_CompareOIDValue()
        Test_API_GetMethodsList()
        Test_API_IsMethodInClass()
        Test_API_IsMethodInThisClass()
        Test_API_IsFieldInClass()
        Test_API_GetFieldModification()
        Test_API_GetObjectModification()
        Test_API_GetNextFreeObjectID()
        Test_API_ExecuteMethod()
        Test_API_SetFieldValue_Class()
        Test_API_SetFieldValue_String()
        Test_API_SetFieldValueDate()
        Test_API_SetFieldValueDateTime()
        Test_API_SetFieldValueTime()
        Test_SetTestDecFieldValue()
        Test_SetTestIncFieldValue()
        Test_SetTestFieldValue()
        Test_SetClassLastModification()
        Test_SetFieldLastModification()
        Test_SetFieldModification()
        Test_SetMethodLastModification()
        Test_SetObjectModification()
        Test_SetFieldValueLastModification()
        Test_SetObjectModified()
        Test_SetClassProperty()
        Test_SetFieldProperty()
        Test_SetMethodProperty()
        Test_CreateObjectByID()
        Test_AddObject()
        Test_DeleteObject()
        Test_ClearAllObjects()
        Test_ClearAllValues()
        Test_GetFieldVersions()
        Test_GetFieldVersions()
        Test_Variables()
        Test_GetObjectsValue()

    if 1:
        pass
