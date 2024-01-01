# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')
import os
import traceback
import win32api

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil
import icorstartinit

import icorapi

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil

UID = 0


def Main():
    ret = 1
    amdata = None
    result = ''
    PID = os.getpid()
    try:
        try:
            icnt = int(sys.argv[1])
            alog = startutil.MemorySysOutWrapper()
            try:
                amdata = ICORInterface.aICORDBEngine.SysBase.GetExecutorMethod(pid=PID)
                if amdata:
                    aclass = ICORInterface.aICORDBEngine.Classes[amdata['CID']]
                    bmethod = aclass.MethodsByName(amdata['Name'])
                    mname = bmethod.MethodPath.replace('\\', '_')
                    mname = mname.replace('/', '_')
                    amethod = __import__(mname)
                    result = amethod.ICORMain(amdata['CID'], amdata['FieldName'], amdata['OID'], amdata['Value'], amdata['UID'])
                    ret = 0
                else:
                    ret = 0
            except:
                print 'Error in method: [PID:%d] : %s' % (PID, str(amdata))
                traceback.print_exc()
        finally:
            alog.Restore()
            werr = 0
            if amdata:
                try:
                    werr = 1
                    out = alog.read()
                    ICORInterface.aICORDBEngine.SysBase.ExecutorMethodSetDone(amdata['MID'], result=result, output=out)
                except:
                    werr = 2
                    so = storageutil.GetLastExceptionInfo(asstring=1)
                    ICORInterface.aICORDBEngine.SysBase.ExecutorMethodSetDone(amdata['MID'], result='ERROR #M10', output=so)
    finally:
        if not ret:
            werr = 3
            if amdata:
                ICORInterface.aICORDBEngine.SysBase.RemoveExecutorMethod(amdata['MID'])
            werr = 4
    sys.exit(ret)


if __name__ == "__main__":
    Main()
