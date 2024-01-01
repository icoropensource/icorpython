# -*- coding: utf-8 -*-
import sys
import time
import re

import icorapi

import appplatform.storageutil as storageutil

UID = 0

import icorlib.icorinterface as ICORInterface

CLASSES_Library_Test_NetBase_Input_Test1 = 1189
#CLASSES_Library_Test_NetBase_Input_Test1_PoleB - 6504
#CLASSES_Library_Test_NetBase_Input_Test1_PoleC - 6507
#CLASSES_Library_Test_NetBase_Input_Test1_PoleD - 6505
#CLASSES_Library_Test_NetBase_Input_Test1_PoleF - 6503
#CLASSES_Library_Test_NetBase_Input_Test1_PoleI - 6502
#CLASSES_Library_Test_NetBase_Input_Test1_PoleM - 6506
#CLASSES_Library_Test_NetBase_Input_Test1_PoleS - 6501


class TestTimer(object):

    def __init__(self, aname, amax=1000, astart=1):
        self.name = aname
        self.max = amax
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
                self.wgood = 0
                if aprint:
                    print k, '********************'
                    print 'I:', self.counters[0][k]
                    print 'P:', self.counters[1][k]
            elif self.counters[0][k] != self.counters[2][k]:
                self.wgood = 0
                if aprint:
                    print k, '********************'
                    print 'I:', self.counters[0][k]
                    print 'A:', self.counters[2][k]
        ti = self.timers[0][1] - self.timers[0][0]
        tp = self.timers[1][1] - self.timers[1][0]
        ta = self.timers[2][1] - self.timers[2][0]
        print '%s [%d]=%d - ICOR: %0.5f, PG: %0.5f, ALL: %0.5f, ratio I/P: %0.2f, ratio I/A: %0.2f' % (self.name, self.max, self.wgood, ti, tp, ta, ti / tp, ti / ta)


def Test_FieldPosition():
    # Nazwa 8649
    print 'Test_FieldPosition'
    aclass = ICORInterface.aICORDBEngine.Classes[1747]
    afield = aclass.FieldsByName('Nazwa')
    print afield.Name, afield.FOID, afield.FieldPosition, type(afield.FieldPosition)


def Test_Conversion():
    #ret=storageutil.CP1250_To_UTF8(ret)
    fout = open('d:/icor/out.txt', 'wb')
    aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_System_User']
    arefs = aclass.EditorSheets
    while arefs:
        asheet = arefs.Class.Name[arefs.OID]
        fout.write(asheet)
        fout.write('\n')
        asheet2 = storageutil.CP1250_To_UTF8(asheet)
        fout.write(asheet2)
        fout.write('\n\n')
        arefs.Next()
    fout.close()


d_CP1250_To_UTF8 = {
    chr(0xb9): chr(0xc4) + chr(0x85),    # a
    chr(0xe6): chr(0xc4) + chr(0x87),    # c
    chr(0xea): chr(0xc4) + chr(0x99),    # e
    chr(0xb3): chr(0xc5) + chr(0x82),    # l
    chr(0xf1): chr(0xc5) + chr(0x84),    # n
    chr(0xf3): chr(0xc3) + chr(0xb3),    # o
    chr(0x9c): chr(0xc5) + chr(0x9b),    # s
    chr(0x9f): chr(0xc5) + chr(0xba),    # x
    chr(0xbf): chr(0xc5) + chr(0xbc),    # z
    chr(0xa5): chr(0xc4) + chr(0x84),    # A
    chr(0xc6): chr(0xc4) + chr(0x86),    # C
    chr(0xca): chr(0xc4) + chr(0x98),    # E
    chr(0xa3): chr(0xc5) + chr(0x81),    # L
    chr(0xd1): chr(0xc5) + chr(0x83),    # N
    chr(0xd3): chr(0xc3) + chr(0x93),    # O
    chr(0x8c): chr(0xc5) + chr(0x9a),    # S
    chr(0x8f): chr(0xc5) + chr(0xb9),    # X
    chr(0xaf): chr(0xc5) + chr(0xbb),    # Z
}

spatt_CP1250_To_UTF8=\
   '(?<!%s)%s|'%(chr(0xc5),chr(0xb9),)+\
   '%s|'%(chr(0xe6))+\
   '%s|'%(chr(0xea))+\
   '(?<!%s)%s|'%(chr(0xc3),chr(0xb3),)+\
   '%s|'%(chr(0xf1))+\
   '%s|'%(chr(0xf3))+\
   '%s|'%(chr(0x9c))+\
   '%s|'%(chr(0x9f))+\
   '%s|'%(chr(0xbf))+\
   '%s|'%(chr(0xa5))+\
   '%s|'%(chr(0xc6))+\
   '%s|'%(chr(0xca))+\
   '%s|'%(chr(0xa3))+\
   '%s|'%(chr(0xd1))+\
   '%s|'%(chr(0xd3))+\
   '%s|'%(chr(0x8c))+\
   '%s|'%(chr(0x8f))+\
   '%s'%(chr(0xaf))
patt_CP1250_To_UTF8 = re.compile(spatt_CP1250_To_UTF8, re.M + re.S)


def Char2UTF(m):
    ret = d_CP1250_To_UTF8.get(m.group(0), '')
    return ret


def CP1250_To_UTF8(s, amode=''):
    atext = patt_CP1250_To_UTF8.sub(Char2UTF, s)
    return atext


def Test_UTF():
    fin = open('d:/icor/out_test.txt', 'rb')
    atext = fin.read()
    fin.close()
    atext = CP1250_To_UTF8(atext)
    fout = open('d:/icor/out_test2.txt', 'wb')
    fout.write(atext)
    fout.close()


def PrintClass(aclass):
   print aclass.CID,aclass.NameOfClass
   lfields=aclass.GetFieldsList()
   for afieldname in lfields:
      afield=aclass.FieldsByName(afieldname)
      print '  ',afield.FOID,afield.Name

def TestPrintClasses():
   aclass=ICORInterface.aICORDBEngine.Classes['CLASSES_Library_Test_NetBase_Input_Test1']
   PrintClass(aclass)
   aclass=ICORInterface.aICORDBEngine.Classes['CLASSES_Library_Test_NetBase_Input_Test2']
   PrintClass(aclass)
 
if __name__ == '__main__':
    if 0:
        Test_FieldPosition()
        Test_Conversion()
        Test_UTF()
    if 1:
        TestPrintClasses()