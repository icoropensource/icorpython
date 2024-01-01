# -*- coding: utf-8 -*-
import sys
import os

import appplatform.startutil as startutil
if startutil.appconfig is None:
    path_file = os.path.abspath(os.path.dirname(__file__))
    path_bin = os.path.abspath(os.path.join(path_file, '../../bin'))
    path_base = os.path.abspath(os.path.join(path_file, '../..'))
    path_methods = os.path.abspath(os.path.join(path_file, '../methods'))
    os.chdir(path_bin)
    startutil.InsertSysPaths(lpaths=[path_bin, path_methods, ])
    import icorconfig
    startutil.InitLibPaths(lpaths=None, envfile=None, application=None, initmodule=icorconfig)
