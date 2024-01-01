# -*- coding: utf-8 -*-
import sys
import time

try:
    import json
except:
    import simplejson as json

import icorapi

import appplatform.storageutil as storageutil
import icorapp.icorfilemanager as icorfilemanager

UID = 0


class TestApp(object):

    def __init__(self):
        pass


def Test_FM_GetFolder(apath):
    print 'Test_FM_GetFolder', apath
    app = TestApp()
    filemanager = icorfilemanager.ICORFileManager(app)
    ret = filemanager.GetFolder(UID, apath)
    s = json.dumps(ret['data'][:8], sort_keys=True, indent=3, separators=(',', ': '))
    #s=storageutil.CP1250_To_UTF8(aobj.Nazwa)
    #s=storageutil.UTF8_To_CP1250(s)
    print s


if __name__ == '__main__':
    if 0:
        Test_FM_GetFolder('/')
        Test_FM_GetFolder('/projects/')
        Test_FM_GetFolder('/projects/35000/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwsite/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwsite/a/')

        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwfiles/')

        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwchapters/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwchapters/35001/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwchapters/35001/chapterfiles/')
        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwchapters/35001/subchapters/')

        Test_FM_GetFolder('/projects/35000/wwwstructs/35000/wwwchaptergroups/35004/')

        Test_FM_GetFolder('/users/')
        Test_FM_GetFolder('/users/18500/')

    if 1:
        Test_FM_GetFolder('/projects/35000/files/file/Moduly_i_aplikacje_ICOR.pdf')
