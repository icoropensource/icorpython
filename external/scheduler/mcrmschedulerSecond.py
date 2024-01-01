# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import optparse
import os

import appplatform.startutil as startutil
import icorstartinit

import icorsyncfile

if __name__ == "__main__":
    ret = startutil.WaitForApp('ICOR_Scheduler_Second', 1)
    if ret:
        optparser = optparse.OptionParser()
        optparser.add_option("-w", "--windowhide", action="store_true", dest="window_hide", help="Hide window")
        options, args = optparser.parse_args()

        if options.window_hide:
            try:
                startutil.HideWindow()
            except:
                print 'Can not hide..'

        isc = icorsyncfile.ICORSyncCopy()
        isc.Process()
