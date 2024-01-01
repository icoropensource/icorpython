import sys
import time

import icorapi


def Exists(averbose=0, aretries=5):
    while aretries:
        try:
            acid = icorapi.GetClassID(0, 'CLASSES_Library_NetBase_WWW_Server')
            if acid >= 0:
                s = icorapi.ExecuteMethod(0, acid, 'ICORExists', '', -1, '', 0)
                if averbose:
                    print 'ICORExists returned: %s' % s
                if s == '1':
                    return 1
        except:
            if averbose:
                print 'unable to check ICOR'
                import traceback
                traceback.print_exc()
        aretries = aretries - 1
        time.sleep(1)
    return 0
