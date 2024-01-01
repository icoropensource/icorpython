# -*- coding: utf-8 -*-
import sys
import os
import time
import shutil
import hashlib
import re

import win32api

import icordbmain
import appplatform.storageutil as storageutil

VERBOSE = 1

# SyncFiles.Status:
# C1 - plik jest otwarty, trwa zapis
# C2 - plik jest zamkniety, zapis zakonczony
# C3 - kopiowanie rozpoczete
# C4 - kopiowanie zakonczone
# B1 - blad w trakcie kopiowania

# SyncFiles.StatusDeleted:
# D1 - usuwanie rozpoczete
# D2 - plik usuniety
# B1 - blad w trakcie usuwania pliku

# SyncPaths.Status:
# C1 - plik w trakcie tworzenia
# C2 - plik gotowy do przeniesienia
# C4 - plik skopiowany
# S1 - plik analogiczny do uprzednio skopiowanego (tylko gdy status=C4 i digest=digestcopied)

lSYNC_PRIORITIES = []
for spatt, apriority in icordbmain.startutil.appconfig.SYNC_PRIORITIES:
    apatt = re.compile(spatt, re.I + re.S + re.M)
    lSYNC_PRIORITIES.append((apatt, apriority))

ACCEPTED_PRIORITIES = ['N01', 'N02', 'N03', 'N04', 'N05']


# N01-N05,-
# default: N03
def GetPathPriority(path):
    for apatt, apriority in lSYNC_PRIORITIES:
        if apatt.search(path):
            return apriority
    return 'N03'


def GetPathLevel(path):
    if path[:2] == r'\\':
        path = path[2:]
    path = os.path.normpath(path)
    l = path.split(os.sep)
    return len(l)


class ICORSyncFile(object):

    def __init__(self, filename, mode='r', pathpriority=None):
        self.filename = filename
        self.mode = mode
        self.closed = 0
        self.oid = ''
        if icordbmain.startutil.appconfig.SYNC_DISABLED:
            pathpriority = '-'
        if pathpriority is None:
            self.pathpriority = GetPathPriority(filename)
        else:
            self.pathpriority = pathpriority
        if self.pathpriority != '-':
            self.created = storageutil.tdatetime()
            self.writecnt = 0
            self.firstwrite = None
            self.writemax = 0
            self.digest = hashlib.md5()
            self.store = icordbmain.ICORDBICOR()
            self.oid = self.store.dbsyncfiles.SyncFilesOpen(filename, 'C1', self.pathpriority)
            self.srcdir = os.path.join(icordbmain.startutil.appconfig.WWWSyncDir, self.oid[:2], self.oid[2:4])
            if not os.path.exists(self.srcdir):
                os.makedirs(self.srcdir)
            self.srcfile = os.path.join(self.srcdir, self.oid)
            self.dt1 = time.clock()
        else:
            self.srcfile = filename
        self.file = open(self.srcfile, mode)

    def write(self, adata):
        if self.pathpriority != '-':
            self.writecnt = self.writecnt + 1
            if not self.firstwrite:
                self.firstwrite = storageutil.tdatetime()
            self.writemax = max(self.writemax, len(adata))
            self.digest.update(adata)
        self.file.write(adata)

    def __del__(self):
        if not self.closed:
            self.close()

    def close(self):
        self.file.close()
        self.closed = 1
        if self.pathpriority != '-':
            self.dt2 = time.clock()
            atime = storageutil.tdatetime()
            filesize = os.path.getsize(self.srcfile)
            if not self.firstwrite:
                self.firstwrite = self.created
            adigest = self.digest.hexdigest()
            self.store.dbsyncfiles.SyncFilesClose(self.oid, self.srcfile, storageutil.tdate2fmtstr(atime), filesize, storageutil.tdate2fmtstr(self.firstwrite), self.writecnt, self.writemax, self.dt2 - self.dt1, adigest, self.pathpriority, 'C2')

    def SetPriority(self, pathpriority):
        if not self.oid:
            return
        if pathpriority in ACCEPTED_PRIORITIES:
            self.pathpriority = pathpriority
            self.store.dbsyncfiles.SyncFilesSetPriority(self.oid, pathpriority)


def syncopen(name, mode='r', pathpriority=None):
    f = ICORSyncFile(name, mode, pathpriority=pathpriority)
    return f


class ICORSyncCopy(object):

    def __init__(self):
        self.store = icordbmain.ICORDBICOR()

    def GetFiles(self):
        self.results = []
        self.files = self.store.dbsyncfiles.SyncFilesGetFiles()

    def CopyFiles(self):
        for spoid, dstpath, oid, srcpath, created, digest in self.files:
            status = 'C3'
            adt = 0.0
            try:
                copystart = storageutil.tdate2fmtstr()
                dt1 = time.clock()
                acnt = 5
                atime = 0.2
                while acnt:
                    try:
                        acnt = acnt - 1
                        win32api.CopyFile(srcpath, dstpath, 0)
                        status = 'C4'
                        break
                    except win32api.error, details:
                        if hasattr(details, 'winerror') and details.winerror in [5, 13]:    # access denied
                            time.sleep(atime)
                            atime = atime + atime
                        else:
                            print 'COPY:', srcpath, dstpath
                            print 'USER:', win32api.GetUserName()
                            print 'win32api.error:', win32api.error
                            print 'details:', type(details), details
                            raise
                dt2 = time.clock()
                copyfinish = storageutil.tdate2fmtstr()
                adt = dt2 - dt1
            except:
                status = 'B1'
                copyfinish = storageutil.tdate2fmtstr()
                import traceback
                traceback.print_exc()
            self.results.append([oid, srcpath, dstpath, created, adt, status, copystart, copyfinish, spoid, digest])

    def StoreResults(self):
        self.store.dbsyncfiles.SyncFilesUpdateResults(self.results)

    def MoveProcessedFiles(self):
        self.store.dbsyncfiles.SyncFilesMoveProcessedFiles()

    def RemoveOldFiles(self):
        self.results = []
        self.files = self.store.dbsyncfiles.SyncFilesGetOldFiles()
        for oid, srcpath in self.files:
            status = 'D1'
            try:
                os.unlink(srcpath)
                status = 'D2'
            except:
                status = 'B1'
                import traceback
                traceback.print_exc()
            self.results.append([oid, status])
        self.store.dbsyncfiles.SyncFilesStoreRemoveOldFilesResults(self.results)

    def Process(self):
        self.MoveProcessedFiles()
        self.RemoveOldFiles()
        self.GetFiles()
        self.CopyFiles()
        self.StoreResults()


if __name__ == '__main__':
    print 'START'
    if 1:
        for i in range(5):
            for j in range(3):
                fout = syncopen('d:/icor/tmp/wsync/abc ąćęłńóśźż 123 - %d.txt' % i, 'w')
                fout.write('aaaaaaaa 2 %d - %d\n' % (i, j))
                fout.write('bbbbbbbbbbb\n')
                fout.write('ccccc\n')
                time.sleep(0.2)
                fout.close()
    if 1:
        asc = ICORSyncCopy()
        asc.Process()
    print 'FINISH'
