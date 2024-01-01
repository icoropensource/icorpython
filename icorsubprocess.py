# -*- coding: utf-8 -*-
import sys
import os
import time
import msvcrt
import datetime
import traceback

import requests
import mozrunner.killableprocess as killableprocess

import appplatform.startutil as startutil

GET_TIMEOUT = 0.12


class ICORSubProcess(object):

    def __init__(self, astarter, aname, amutex='', aserver=None, aport=None, akillwait=0, apyprocess=None, ashellprocess=None, acheckable=1, aparms=None, ainitcheck=0, awaittillfinished=0):
        self.starter = astarter
        self.name = aname
        self.mutex = ''
        self.server = aserver
        self.port = aport
        if self.port is not None:
            if self.server is None:
                self.server = '127.0.0.1'
        self.killwait = akillwait
        self.pyprocess = apyprocess
        self.shellprocess = ashellprocess
        self.waittillfinished = awaittillfinished
        self.checkable = acheckable
        self.process = None
        if aparms is None:
            aparms = []
        self.parms = aparms
        self.states = []
        self.setState('INIT')
        if ainitcheck:
            self.check()

    def setState(self, astate):
        self.states.insert(0, [astate, datetime.datetime.now()])

    def getState(self):
        ret = ''
        if self.states:
            ret = self.states[0][0]
        return ret

    def getPID(self):
        ret = -1
        if self.process:
            ret = self.process.pid
        return ret

    def getURL(self, aurl):
        ret = ''
        at = GET_TIMEOUT
        i = 3
        while i:
            try:
                r = requests.get(aurl, timeout=at)
                ret = r.text
            except requests.ReadTimeout:
                pass
            except requests.ConnectionError:
                break
            i = i - 1
            at = at + at
        return ret

    def isServiceWorking(self):
        ret = 0
        if not self.port:
            if self.process:
                ret = 1
            return ret
        try:
            aurl = 'http://%s:%d/isrunning' % (self.server, self.port, )
            s = self.getURL(aurl)
            if s == 'ok':
                ret = 1
        except:
            print 'ERROR: isServiceWorking: %s' % (aurl, )
            traceback.print_exc()
        return ret

    def sleep(self, asecs, astop=0):
        adt = time.clock()
        aport = self.port
        while (time.clock() - adt) < asecs:
            if aport:
                w = startutil.WaitNetService(self.server, self.port, timeout=0.001)
                if (not astop and w) or (astop and not w):
                    asecs = 5
                    aport = None
            print 'sleep: %d  - [SPACE - skip]    \r' % (int(asecs - time.clock() + adt), ),
            if msvcrt.kbhit():
                achar = msvcrt.getch()
                if achar == ' ':
                    break
            time.sleep(0.2)
        print '                                          \r',

    def executeProcess(self, aprocess, aparms=None, await=0, env=None, shell=0, **kwargs):
        self.setState('EXECUTING')
        aprocess = aprocess.replace('/', '\\')
        if not aparms:
            aparms = []
        aparms = [s.replace('/', '\\') for s in aparms]
        if not shell:
            stdout = sys.stdout
            stderr = sys.stderr
            stdin = sys.stdin
            killable_kwargs = {'stdout': stdout, 'stderr': stderr, 'stdin': stdin}
            killable_kwargs.update(kwargs)
        else:
            killable_kwargs = {}
        aprocess = killableprocess.Popen([aprocess, ] + aparms, env=env, shell=shell, **killable_kwargs)
        self.setState('RUNNING')
        if await != 0:
            aprocess.wait()    # czekamy az sie skonczy...
            return None
        return aprocess

    def executePyProcess(self, afilepath, aparms=None, shell=0):
        if not aparms:
            aparms = []
        return self.executeProcess(startutil.appconfig.DefaultProcessExecutor, [afilepath, ] + aparms, shell=shell)

    def check(self):
        if not self.checkable:
            return
        if not self.mutex:
            if self.process is None:
                self.start()
        else:
            wexists = startutil.CheckApp(self.mutex)
            if not wexists:
                self.start()

    def shutdown(self):
        ret = 0
        if not self.port:
            return ret
        self.setState('SHUTDOWN START')
        try:
            aurl = 'http://%s:%d/stop' % (self.server, self.port, )
            s = self.getURL(aurl)
            if s == 'stop':
                ret = 1
                self.process = None
                self.setState('SHUTDOWN OK')
            else:
                self.setState('SHUTDOWN NOT OK')
        except:
            self.setState('SHUTDOWN ERROR')
            print 'ERROR: shutdown: %s' % (aurl, )
            traceback.print_exc()
        return ret

    def start(self):
        self.setState('STARTING')
        startutil.Log('activate ' + self.name, fname=self.starter.alogfile)
        self.stop()
        astate = 'STARTED'
        if self.pyprocess:
            self.process = self.executePyProcess(self.pyprocess, aparms=self.parms)
        elif self.shellprocess:
            self.process = self.executeProcess(self.shellprocess, aparms=self.parms, await=self.waittillfinished)
            if self.waittillfinished:
                astate = 'STOPPED'
        self.setState(astate)

    def kill(self):
        if self.process:
            self.setState('KILLING')
            print 'killing %s - pid=%d, job=%d' % (self.name, self.process.pid, self.process._job)
            if self.killwait:
                self.process.wait(timeout=self.killwait)
            else:
                self.process.kill()
            self.process = None
            self.setState('KILLED')

    def stop(self):
        self.setState('STOPPING')
        #startutil.Log('stop '+self.name,fname=self.starter.alogfile)
        if not self.shutdown():
            self.kill()
            #self.sleep(self.sleepstop,astop=1)
        self.setState('STOPPED')
