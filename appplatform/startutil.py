# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import datetime
import codecs
try:
    import json
except:
    import simplejson as json

# "c:\program files (x86)\python 2.7\lib\site-packages\win32com\gen_py"
sys.coinit_flags = 0
import pythoncom
import wmi

import appplatform.storageutil as storageutil
#pylint: disable=E0401

appconfig = None


def InsertSysPaths(lpaths=None):
    if not lpaths:
        return
    lp = lpaths[:]
    lp.reverse()
    for apath in lp:
        bpath = os.path.abspath(apath)
        if bpath not in sys.path:
            sys.path.insert(0, bpath)


path_file = os.path.abspath(os.path.dirname(__file__))


def InitLibPaths(lpaths=None, envfile=None, application=None, initmodule=None):
    global appconfig
    if lpaths:
        InsertSysPaths(lpaths)
    if appconfig is None:
        appconfig = storageutil.VarDict()
        if envfile:
            fin = codecs.open(envfile, 'r', encoding='utf-8-sig')
            try:
                d = json.load(fin, encoding='utf8')
                appconfig.update(d)
                if application:
                    appconfig['Application'] = application
            finally:
                fin.close()
        if initmodule:
            d = storageutil.DictFromModule(initmodule)
            appconfig.update(d)


_TMP_CNT = 0


def FilePathAsSystemPath(afilepath, aslash=r'\\'):
    s = afilepath.replace('%ICOR%', appconfig.AppBaseDir)
    s = afilepath.replace('%APP%', appconfig.AppBaseDir)
    s = re.sub(r'[/\\]', aslash, s)
    return s


patt_GetStrEnv = re.compile('\{\!(.*?)\!\}', re.M + re.S)


def GetStrEnv(s):
    global appconfig
    if appconfig is None:
        return s
    l = patt_GetStrEnv.findall(s)
    aenv = appconfig.get('PROJECT_ENV', None)
    if aenv is None:
        return s
    for sp in l:
        sr = aenv.get(sp, '')
        if sr:
            s = s.replace('{!' + sp + '!}', sr)
    return s


def GetLogTempFileName(adir, aprefix='log', asufix='', avalue=None, atrace=0, abasedir='', aext='txt', returnfilenameonly=0):
    global _TMP_CNT
    if not abasedir:
        adir = FilePathAsSystemPath(r'%APP%/log/' + adir)
    else:
        adir = os.path.join(abasedir, adir)
    if not os.path.exists(adir):
        os.makedirs(adir)
    afname = aprefix
    if afname:
        afname = afname + '_'
    afname = afname + storageutil.tdatetime2fmtstr(noms=0, adelimiter='', atimedelimiter='', apartdelimiter='_', amsdelimiter='_')
    if asufix:
        afname = afname + '_' + asufix
    while 1:
        bfname = afname + '_%05d.%s' % (_TMP_CNT, aext)
        afpath = adir + '/' + bfname
        _TMP_CNT = _TMP_CNT + 1
        if _TMP_CNT > 99999:
            _TMP_CNT = 0
        if not os.path.exists(afpath):
            break
    if avalue is not None:
        fout = open(afpath, 'w')
        fout.write(avalue)
        if atrace:
            l = storageutil.dumpstack(aslist=1)
            fout.write('\n\n===================================================\n')
            for s in l:
                fout.write(s)
        fout.close()
    if returnfilenameonly:
        return bfname
    return afpath


def WaitForApp(aname, acheckonly=0):
    import win32event
    import win32api
    import winerror
    while 1:
        sys.singleappmutex = win32event.CreateMutex(None, False, aname)
        if win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS:
            return 1
        if acheckonly:
            return 0
        win32api.CloseHandle(sys.singleappmutex)
        time.sleep(0.3)


def CheckApp(aname):
    import win32event
    import win32api
    import winerror
    import pywintypes
    ret = 0
    STANDARD_RIGHTS_REQUIRED = 0xF0000
    SYNCHRONIZE = 0x100000
    MUTANT_QUERY_STATE = 0x1
    MUTEX_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | MUTANT_QUERY_STATE
    try:
        amutex = win32event.OpenMutex(MUTEX_ALL_ACCESS, pywintypes.FALSE, aname)    #pylint: disable=E1101
        if win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS:
            ret = 1
    except pywintypes.error, e:    #pylint: disable=E1101
        if e[0] != 2:    # pywintypes.error: (2, 'OpenMutex', 'Nie mo\xbfna odnale\x9f\xe6 okre\x9clonego pliku.')
            raise
    if ret:
        win32api.CloseHandle(amutex)
    return ret


def WaitNetService(server, port, timeout=None):
    """ Wait for network service to appear 
      @param timeout: in seconds, if None or 0 wait forever
      @return: True of False, if timeout is None may return only True or
         throw unhandled network exception
   """
    import socket
    import errno
    s = socket.socket()
    if timeout:
        # time module is needed to calc timeout shared between two exceptions
        end = time.time() + timeout
    while True:
        try:
            if timeout:
                next_timeout = end - time.time()
                if next_timeout < 0:
                    return False
                else:
                    s.settimeout(next_timeout)
            s.connect((server, port))
        except socket.timeout, err:
            # this exception occurs only if timeout is set
            if timeout:
                return False
        except socket.error, err:
            if err[0] == 10061:    # connection refused
                time.sleep(0.01)
                continue
            if err[0] == 10035:    #The socket operation could not complete without blocking
                return True
            # catch timeout exception from underlying network library
            # this one is different from socket.timeout
            if type(err.args) != tuple or err[0] != errno.ETIMEDOUT:
                raise
        else:
            s.close()
            return True


def Log(s='', amode='a+', fname='', apid=1, ausername=1, atime=1, aconsole=1):
    if not s or s == '\n':
        return s
    try:
        if type(s) == type(u''):
            s = storageutil.UTF8_To_ASCII(s)
        if aconsole:
            print s.replace('\n', ' ')
        f = open(fname, amode)
        if s[-1:] != '\n':
            s = s + '\n'
        if atime:
            s = storageutil.tdatetime2fmtstr(noms=0, adelimiter='-', atimedelimiter=':', apartdelimiter='_', amsdelimiter=' ') + ': ' + s
        if ausername:
            import win32api
            s = '{' + win32api.GetUserName() + '} ' + s
        if apid:
            s = '[' + str(os.getpid()) + '] ' + s
        f.write(s)
        f.close()
    except:
        raise


def LogException(amode='a+', fname='', apid=1, ausername=1, atime=1, aconsole=1):
    try:
        import traceback
        if aconsole:
            traceback.print_exc()
        f = open(fname, amode)
        s = 'Exception!'
        if atime:
            s = storageutil.tdatetime2fmtstr(noms=0, adelimiter='-', atimedelimiter=':', apartdelimiter='_', amsdelimiter=' ') + ': ' + s
        if ausername:
            import win32api
            s = '{' + win32api.GetUserName() + '} ' + s
        if apid:
            s = '[' + str(os.getpid()) + '] ' + s
        f.write(s)
        traceback.print_exc(file=f)
        f.close()
    except:
        raise


class MLog:

    def __init__(self, afname, aconsole=1):
        self.FName = afname
        self.Console = aconsole

    def Log(self, s, aconsole=None):
        if aconsole is None:
            aconsole = self.Console
        Log(s, fname=self.FName, aconsole=aconsole)

    def LogException(self, s='', aconsole=None):
        if aconsole is None:
            aconsole = self.Console
        if s:
            Log(s, fname=self.FName, aconsole=aconsole)
        LogException(fname=self.FName, aconsole=aconsole)

    def write(self, s):
        self.Log(s)

    def flush(self):
        pass

    def close(self):
        pass


class MTimer(object):

    def __init__(self, ainfo=''):
        self.adtstart = time.clock()
        self.adtlast = [self.adtstart]
        self.level = 0
        self.Info(ainfo)

    def Info(self, ainfo='', amode='', aprint=1):
        adtnow = time.clock()
        adt = datetime.datetime.now()
        if amode == 'pop':
            self.level = self.level - 1
            self.adtlast.pop()
        ret = '%s TIMER fl: %0.6f, fs: %0.6f - %s%s' % (adt.strftime('%Y-%m-%d %H:%M:%S'), adtnow - self.adtlast[self.level], adtnow - self.adtstart, '  ' * self.level, ainfo)
        if aprint:
            print ret
        adtnow = time.clock()
        self.adtlast[self.level] = adtnow
        if amode == 'push':
            self.level = self.level + 1
            self.adtlast.append(adtnow)
        return ret


def KillProcess(apid):
    import win32api
    import win32con
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, apid)
        win32api.TerminateProcess(handle, 0)
        win32api.CloseHandle(handle)
    except:
        import traceback
        traceback.print_exc()


def GetActiveExecutorsProcesses(lprocpaths, procmaxminutes=180, killall=0, cominitialize=1):
    l = []
    apid = os.getpid()
    lprocpaths = [s.replace('\\', '/').lower() for s in lprocpaths]
    try:
        if cominitialize:
            pythoncom.CoInitialize()
        # documentation: http://timgolden.me.uk/python/wmi/tutorial.html
        conn = wmi.WMI()
        for process in conn.Win32_Process(['ProcessId', 'ParentProcessId', 'Name', 'CreationDate', 'CommandLine'], Name='python.exe'):
            scmd = process.CommandLine
            if scmd is None:
                continue
            scmd = scmd.replace('\\', '/').lower()
            for asubpath in lprocpaths:
                if scmd.find(asubpath) >= 0:
                    break
            else:
                continue
            sdate = process.CreationDate    #20200623212800.177304+120
            tdate = storageutil.getStrAsDateTime('%s-%s-%s %s:%s:%s' % (sdate[:4], sdate[4:6], sdate[6:8], sdate[8:10], sdate[10:12], sdate[12:14]))
            adt = datetime.datetime.today()
            fdt = datetime.datetime(*tdate[:6])
            adiff = adt - fdt
            procminutes = int(adiff.seconds / 60)
            #amsg='pid: %d, ppid: %d (%d), ProcessName: %s, created: %s (%s)'%(process.ProcessId,process.ParentProcessId,apid,process.Name,str(fdt),str(procminutes))
            #print(amsg)
            if not killall and (process.ParentProcessId == apid) and (procminutes < procmaxminutes):
                l.append(process)
                continue
            try:
                process.Terminate()
            except:
                pass
    finally:
        if cominitialize:
            pythoncom.CoUninitialize()
    return l


class DirClearByDays(object):

    def __init__(self, abasedir='', adays=7, afragments=None, adeleteall=0, averbose=0, aprocess=0):
        self.basedir = abasedir
        self.days = adays
        self.deleteall = adeleteall
        self.verbose = averbose
        if afragments is None:
            afragments = []
        self.fragments = afragments
        if aprocess:
            self.Process()

    def Process(self):
        tnow = datetime.datetime.now()
        for afileentry in self.GetFiles(self.basedir):
            if self.fragments:
                w = 0
                for s in self.fragments:
                    if afileentry.path.find(s) >= 0:
                        w = 1
                        break
                if w:
                    continue
            w = self.deleteall
            if not w:
                fs = afileentry.stat()
                ftime = datetime.datetime.fromtimestamp(fs.st_mtime)
                fdelta = tnow - ftime
                if fdelta.days > self.days:
                    w = 1
            if w:
                try:
                    os.unlink(afileentry.path)
                    if self.verbose:
                        print 'OK: %s' % afileentry.path    #,fs.st_size,ftime,fdelta.days
                except:
                    print 'ERROR: %s' % afileentry.path    #,fs.st_size,ftime,fdelta.days

    def GetFiles(self, adir, alevel=0):
        import scandir
        try:
            l = scandir.scandir(unicode(adir))
        except OSError:
            l = []
        for aentry in l:
            if aentry.is_file():
                yield aentry
            elif aentry.is_dir():
                #if not alevel:
                #   print aentry.name,datetime.datetime.now()
                for bentry in self.GetFiles(aentry.path, alevel + 1):
                    yield bentry


def DeleteOldFiles(apath, adays=7, afragments=None, adeleteall=0, averbose=0):
    DirClearByDays(apath, adays=adays, afragments=afragments, adeleteall=adeleteall, averbose=averbose, aprocess=1)


def HideWindow():
    import win32api
    import win32ui
    import win32con
    awindow = win32ui.GetMainFrame()
    awindow.ShowWindow(win32con.SW_HIDE)
    try:
        win32api.Beep(5000, 100)
        win32api.Beep(4000, 100)
        win32api.Beep(3000, 150)
    except:
        pass
    del awindow
    del win32ui


class LineCollector(object):

    def __init__(self, amaxbuffer=1000):
        self.maxbuffer = amaxbuffer
        self.dlines = {}
        self.minid = 0
        self.maxid = 0

    def write(self, s):
        self.dlines[self.maxid] = s
        self.maxid = self.maxid + 1
        if not self.maxid % 10:
            self.compact()

    def compact(self):
        alen = self.maxid - self.minid
        if alen > self.maxbuffer:
            anewminid = self.maxid - self.maxbuffer
            for i in range(self.minid, anewminid):
                del self.dlines[i]
            self.minid = anewminid

    def getlines(self, afromid, amaxcnt=200):
        if afromid < self.minid:
            afromid = self.minid
        acnt = 0
        lret = []
        while acnt < amaxcnt and afromid < self.maxid:
            lret.append([afromid, self.dlines[afromid]])
            afromid = afromid + 1
            acnt = acnt + 1
        return lret


class MemorySysOutWrapper():

    def __init__(self, atimeinclude=1, asetbinary=0, apidinclude=1, fout2=None, aconsole=1):
        self.restored = 0
        self.TimeInclude = atimeinclude
        self.PIDInclude = apidinclude
        self.data = ''
        self.PID = os.getpid()
        import win32api
        self.UserName = win32api.GetUserName()
        self.sysin = sys.stdin
        if asetbinary:
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)
        self.sysout = sys.stdout
        self.syserr = sys.stderr
        self.sysin = sys.stdin
        sys.stdout = self
        sys.stderr = self
        sys.stdin = self
        self.fout2 = fout2
        self.console = aconsole

    def fileno(self):
        return self.sysout.fileno()

    def __del__(self):
        self.Restore()

    def Restore(self):
        if self.restored:
            return
        sys.stdout = self.sysout
        sys.stderr = self.sysout
        sys.stdin = self.sysin
        self.restored = 1

    def output(self, s):
        self.data = self.data + s
        if self.console:
            self.sysout.write(s)

    def LogException(self):
        if self.fout2:
            LogException(fname=self.fout2, apid=1, ausername=1, atime=1, aconsole=0)

    def read(self):
        return self.data

    def write(self, s):
        if not s:
            return
        if s not in ['\n', '\r']:
            spid = ''
            if self.PIDInclude:
                spid = '[%d]' % self.PID + ' {' + self.UserName + '} '
            if self.TimeInclude:
                spid = spid + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': '
            s = spid + s
        self.output(s)
        if self.fout2:
            Log(s, fname=self.fout2, aconsole=self.console)
