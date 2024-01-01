# -*- coding: utf-8 -*-
import sys
import os
import time
import uuid

import paramiko

VERBOSE = 1


class SSHInfo(object):

    def __init__(self, manager):
        self.manager = manager
        self.data = []

    def RegisterInfo(self, name, stdout, stderr):
        ainfo = [time.time(), name, stdout, stderr]
        self.data.append(ainfo)


class SSHInfoSystem(SSHInfo):

    def InfoVersion(self):
        ret, rete = self.manager.ExecCommand('lsb_release -a')
        self.RegisterInfo('Ubuntu version', ret, rete)

    def InfoLimits(self):
        ret, rete = self.manager.ExecCommand('ulimit -a')
        self.RegisterInfo('Check limits', ret, rete)

    def InfoNetwork(self):
        ret, rete = self.manager.ExecCommand('ifconfig')
        self.RegisterInfo('Network configuration', ret, rete)

    def InfoOperatingSystem(self):
        ret, rete = self.manager.ExecCommand('uname -a')
        self.RegisterInfo('Operating system / distribution', ret, rete)

    def InfoProcessors(self):
        ret, rete = self.manager.ExecCommand('cat /proc/cpuinfo')
        self.RegisterInfo('Processor / cores', ret, rete)

    def InfoDisk(self):
        ret, rete = self.manager.ExecCommand('df -h /')
        self.RegisterInfo('Disk', ret, rete)

    def InfoMemory(self):
        ret, rete = self.manager.ExecCommand('free')
        self.RegisterInfo('Memory', ret, rete)

    def InfoUpTime(self):
        ret, rete = self.manager.ExecCommand('uptime')
        self.RegisterInfo('UpTime', ret, rete)

    def InfoOpenResty(self):
        ret, rete = self.manager.ExecCommand('%s -V' % self.manager.openresty)
        self.RegisterInfo('OpenResty', ret, rete)

    def InfoCertbot(self):
        ret, rete = self.manager.ExecCommand('certbot certificates', sudo=True)
        self.RegisterInfo('Certbot / Certificates', ret, rete)

    def InfoNetstatServers(self):
        ret, rete = self.manager.ExecCommand('netstat -tulpn')
        self.RegisterInfo('Active server connections', ret, rete)

    def InfoNetworkIPAddress(self):
        ret, rete = self.manager.ExecCommand('ip address')
        self.RegisterInfo('Network configuration / IP Address', ret, rete)

    def InfoProcessTree(self):
        ret, rete = self.manager.ExecCommand('ps axjf')
        self.RegisterInfo('Process / Tree', ret, rete)

    def InfoProcessByMemory(self):
        ret, rete = self.manager.ExecCommand('ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head')
        self.RegisterInfo('Process / by memory', ret, rete)

    def InfoProcessByCPU(self):
        ret, rete = self.manager.ExecCommand('ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head')
        self.RegisterInfo('Process / by CPU', ret, rete)


class SSHManager(object):

    def __init__(self, hostname, username, password, port=22, anginxbasedir=r'/usr/local/openresty/nginx', aopenresty='openresty'):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.nginx_basedir = anginxbasedir
        self.openresty = aopenresty
        self.isconnected = False
        self.client = None
        self.ftp = None

    def GetUUID(self, aprefix='', asufix=''):
        return aprefix + uuid.uuid4().hex + asufix

    def Open(self):
        if self.isconnected:
            return True
        acnt, amax = 1, 5
        while acnt <= amax:
            if VERBOSE:
                print "Trying to connect to %s (%d/%d)" % (self.hostname, acnt, amax)
            try:
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    #paramiko.WarningPolicy()
                self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
                if VERBOSE:
                    print "Connected to %s" % self.hostname
                self.isconnected = True
                self.ftp = self.client.open_sftp()
                break
            except paramiko.AuthenticationException:
                if VERBOSE:
                    print "Authentication failed when connecting to %s" % self.hostname
                return self.isconnected
            except:
                if VERBOSE:
                    print "Could not SSH to %s, waiting for it to start" % self.hostname
                time.sleep(1)
            acnt += 1
        else:
            if VERBOSE:
                print "Could not connect to %s. Giving up" % self.hostname
        return self.isconnected

    def Close(self):
        if not self.isconnected:
            return
        self.ftp.close()
        self.client.close()
        self.client = None
        self.ftp = None
        self.isconnected = False

    def ExecCommand(self, command, sudo=False):
        ret, rete = [], []
        if not self.Open():
            return ret, rete
        cprefix = ''
        if sudo:
            cprefix = 'sudo '
        if VERBOSE:
            print '> ' + cprefix + command
        stdin, stdout, stderr = self.client.exec_command(cprefix + command, get_pty=True)
        if sudo:
            stdin.write(self.password + '\n')
            stdin.flush()
        while not stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
            time.sleep(0.1)
        ret = [s[:-1] for s in stdout.readlines() if s.find('[sudo] password') < 0]
        rete == [s[:-1] for s in stderr.readlines()]
        if VERBOSE:
            for s in ret:
                print s
            if rete:
                print 'StdErr:'
                for s in rete:
                    print s
        return ret, rete

    def FTPGet(self, src, dst):
        if not self.Open():
            return
        if VERBOSE:
            print '> FTPGet %s %s' % (src, dst)
        ret = self.ftp.get(src, dst)
        return ret

    def PathJoin(self, *args):
        ret = os.path.join(*args)
        ret = ret.replace('\\', '/')
        return ret

    def FTPPut(self, src, dst):
        if not self.Open():
            return
        if VERBOSE:
            print '> FTPPut %s %s' % (src, dst)
        try:
            self.ftp.stat('.sshmanager')
        except IOError, e:
            if e.errno == 2:    # strerror=='No such file'
                self.ftp.mkdir('.sshmanager')
            else:
                raise
        atmpname = self.GetUUID()
        atmppath = self.PathJoin('.sshmanager', atmpname)
        self.ftp.put(src, atmppath)
        self.ExecCommand('chown root:root %s' % (atmppath, ), sudo=True)
        self.ExecCommand('mv -f %s %s' % (atmppath, dst), sudo=True)

    def NGINXInit(self, abasedir):
        if not self.Open():
            return
        self.ExecCommand('mkdir -p %s/cache/d' % (abasedir, ), sudo=True)
        self.ExecCommand('mkdir -p %s/cache/h' % (abasedir, ), sudo=True)
        self.ExecCommand('mkdir -p %s/cache/m' % (abasedir, ), sudo=True)

    def NGINXInitSite(self, abasedir, awwwsite):
        if not self.Open():
            return
        self.ExecCommand('mkdir -p %s/html_%s' % (abasedir, awwwsite), sudo=True)
        self.ExecCommand('mkdir -p %s/html_%s/.well-known' % (abasedir, awwwsite), sudo=True)
        self.ExecCommand('mkdir -p %s/logs/log_%s' % (abasedir, awwwsite), sudo=True)

    def NGINXReload(self):
        if not self.Open():
            return
        self.ExecCommand('%s -s reload' % self.openresty, sudo=True)

    def NGINXTest(self):
        if not self.Open():
            return
        return self.ExecCommand('%s -t' % self.openresty, sudo=True)
