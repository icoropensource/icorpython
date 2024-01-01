# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import optparse
import os

import appplatform.startutil as startutil
import icorstartinit

import icorapi

if __name__ == "__main__":
    optparser = optparse.OptionParser()
    optparser.add_option("-w", "--windowhide", action="store_true", dest="window_hide", help="Hide window")
    optparser.add_option("-m", "--minute", action="store", type="string", dest="minute", help="Minute mode")
    options, args = optparser.parse_args()
    aminute = ''
    if options.minute:
        aminute = options.minute
    ret = startutil.WaitForApp('ICOR_Scheduler_Minute' + aminute, 1)
    if ret:
        if options.window_hide:
            try:
                startutil.HideWindow()
            except:
                print 'Can not hide..'

        from icorlib.projekt.mcrmscheduler import *

        leventschedulernames = ['OnSchedulerMinute' + aminute, ]
        Main(leventschedulernames)
