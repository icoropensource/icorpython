# -*- coding: utf-8 -*-
import sys
if 0:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import time
import msvcrt
import optparse
import traceback
import datetime

import schedaddle
import mozrunner.killableprocess as killableprocess

import appplatform.consoleutil as consoleutil
import appplatform.startutil as startutil
import appplatform.storageutil as storageutil
import icorstartinit

import icorsubprocess
import icorstartmanager

import icordbmain

UID = 0


class ICORStarter(object):

    def __init__(self, abackup='', astarttime=None):
        #self.sysoutwrapper=startutil.MemorySysOutWrapper(apidinclude=0)
        self.console = consoleutil.ConsoleUtil()
        if abackup:
            self.aBackupDir = abackup
        else:
            self.aBackupDir = startutil.appconfig.ICORBaseDir + '/backup'
        if not os.path.exists(self.aBackupDir):
            try:
                self.console.PrintInfo('Create backup directory: %s' % self.aBackupDir)
                os.makedirs(self.aBackupDir)
            except:
                self.console.PrintError('ERROR: Unable to create backup directory')

        self.aICORDBData = icordbmain.ICORDBData()

        self.starttime = astarttime
        self.alogfile = startutil.appconfig.ICORBaseDir + '/log/starthelper_log.txt'
        self.state = 'CHECK'
        self.nexteventkind, self.nexteventdatetime = '', ''

        self.subprocs = {}

        self.lcommands = [
            ['h', self.cmdHelp, 'help'],
            ['i', self.cmdInfo, 'info'],
            ['q', self.cmdQuit, 'quit'],
            ['p', self.cmdPause, 'pause/continue'],
            ['m', self.cmdMaintenance, 'maintenance tools'],
            ['r', self.cmdStartRedaemon, 'start Redaemon'],
            ['y', self.cmdStopRedaemon, 'stop Redaemon'],
            ['w', self.cmdStartIServer, 'start IServer'],
            ['o', self.cmdStopIServer, 'stop IServer'],
            ['e', self.cmdStartEServer, 'start EServer'],
            ['v', self.cmdStopEServer, 'stop EServer'],
            ['u', self.cmdStartSServer, 'start SServer'],
            ['a', self.cmdStopSServer, 'stop SServer'],
            ['1', self.cmdSchedulerMinutely, 'run scheduler procedure minutely'],
            ['2', self.cmdSchedulerHourly, 'run scheduler procedure hourly'],
            ['3', self.cmdSchedulerDaily, 'run scheduler procedure daily'],
            ['4', self.cmdSchedulerWeekly, 'run scheduler procedure weekly'],
            ['5', self.cmdSchedulerMonthly, 'run scheduler procedure monthly'],
            ['6', self.cmdSchedulerMinutely5, 'run scheduler procedure minutely 5'],
            ['7', self.cmdSchedulerMinutely11, 'run scheduler procedure minutely 11'],
            ['8', self.cmdSchedulerMinutely23, 'run scheduler procedure minutely 23'],
            ['9', self.cmdSchedulerMinutely31, 'run scheduler procedure minutely 31'],
        ] # yapf: disable
        self.commandsdict = {}
        for ashortcut, afunc, ainfo in self.lcommands:
            self.commandsdict[ashortcut] = afunc

        self.aICORStartManager = icorstartmanager.ICORStartManager(self)

    def cmdHelp(self):
        print
        self.console.PrintHelp('ICOR Help')
        for ashortcut, afunc, ainfo in self.lcommands:
            self.console.PrintHelp('  [%s] - %s' % (ashortcut, ainfo))

    def cmdInfo(self):
        anow = datetime.datetime.now()
        print
        self.console.PrintInfo('****** ICOR Status [%s] ******' % (str(anow)))
        self.console.PrintInfo('%30s : %s' % ('ICORBaseDir', startutil.appconfig.ICORBaseDir))
        self.console.PrintInfo('%30s : %s' % ('PythonTopDir', startutil.appconfig.PythonTopDir))
        self.console.PrintInfo('%30s : %s' % ('BackupDir', self.aBackupDir))
        self.console.PrintInfo('%30s : %s' % ('DefaultProcessExecutor', startutil.appconfig.DefaultProcessExecutor))
        self.console.PrintInfo('%30s : %s' % ('TCP_SERVER_PORT_REDAEMON', startutil.appconfig.TCP_SERVER_PORT_REDAEMON))
        self.console.PrintInfo('%30s : %s' % ('TCP_SERVER_PORT_ISERVER', startutil.appconfig.TCP_SERVER_PORT_ISERVER))
        self.console.PrintInfo('%30s : %s' % ('TCP_SERVER_PORT_SSERVER', startutil.appconfig.TCP_SERVER_PORT_SSERVER))
        self.console.PrintInfo('%30s : %s' % ('TCP_SERVER_PORT_ESERVER', startutil.appconfig.TCP_SERVER_PORT_ESERVER))
        self.console.PrintInfo('%30s : %s' % ('TCP_SERVER_PORT_STARTMANAGER', startutil.appconfig.TCP_SERVER_PORT_STARTMANAGER))
        self.console.PrintInfo('%30s : %s' % ('MaxDaemonExecutors', startutil.appconfig.MaxDaemonExecutors))
        self.console.PrintInfo('%30s : %s' % ('UI_Skin', startutil.appconfig.UI_Skin))
        self.console.PrintInfo('%30s : %s' % ('NextEventKind', self.nexteventkind))
        self.console.PrintInfo('%30s : %s' % ('NextEventDateTime', str(self.nexteventdatetime)))
        for aname, aprocess in self.subprocs.items():
            self.console.PrintInfo('process: %20s, pid: %d, isWorking: %s, state: %s' % (aname, aprocess.getPID(), aprocess.isServiceWorking(), aprocess.getState()))

    def stopAll(self):
        for aname, aprocess in self.subprocs.items():
            aprocess.stop()

    def Input(self, amsg, adefault=''):
        s = self.console.Input(atext=amsg)
        if s is None:
            s = adefault
        else:
            s = s.replace('\r', '')
            s = s.replace('\n', '')
        return s

    def cmdQuit(self, asilent=0):
        if asilent:
            x = 'y'
        else:
            x = self.Input('Are you sure? [y/n]')
        if x[:1] == 'y':
            self.state = 'QUIT'
            self.console.PrintText('Stopping ICOR..')
            if self.aICORStartManager.running:
                self.aICORStartManager.stop()
            self.stopAll()
            self.console.PrintText('Quit in progress..')

    def cmdPause(self):
        print
        if self.state == 'PAUSE':
            self.console.PrintText('Continue!')
            self.state = self._laststate
        else:
            self.console.PrintText('Pause..')
            self._laststate = self.state
            self.state = 'PAUSE'

    def cmdStartRedaemon(self):
        self.console.PrintText('Checking Redaemon..')
        self.subprocs['redaemon'].check()

    def cmdStartIServer(self):
        self.console.PrintText('Checking IServer..')
        self.subprocs['iserver'].check()

    def cmdStartSServer(self):
        self.console.PrintText('Checking SServer..')
        self.subprocs['sserver'].check()

    def cmdStartEServer(self):
        self.console.PrintText('Checking EServer..')
        self.subprocs['eserver'].check()

    def cmdStopRedaemon(self):
        self.console.PrintText('Stopping Redaemon..')
        self.subprocs['redaemon'].stop()

    def cmdStopIServer(self):
        self.console.PrintText('Stopping IServer..')
        self.subprocs['iserver'].stop()

    def cmdStopSServer(self):
        self.console.PrintText('Stopping SServer..')
        self.subprocs['sserver'].stop()

    def cmdStopEServer(self):
        self.console.PrintText('Stopping EServer..')
        self.subprocs['eserver'].stop()

    def cmdBackup(self):
        self.console.PrintText('1. Start pg dump.')
        adt = time.localtime()
        afname = 'icorda_%04d-%02d-%02d_%02d-%02d-%02d' % (adt[0], adt[1], adt[2], adt[3], adt[4], adt[5])
        f1, f2 = self.cmdDumpData(afname)
        if not f1:
            return 0
        aparms = ['a', '-bd', '-r', '-ssw', '-y', self.aBackupDir + '/' + afname + '.7z', f1, f2]
        aexe = '/bin/webutils/7-Zip/7z.exe'
        self.console.PrintText('2. Start backup to file %s/%s' % (self.aBackupDir, afname + '.7z'))
        icorsubprocess.ICORSubProcess(self, '7z compressor', ashellprocess=startutil.appconfig.ICORBaseDir + aexe, aparms=aparms, ainitcheck=1, awaittillfinished=1)
        self.console.PrintText('3. Remove uncompressed dumps')
        for afname in [f1, f2]:
            try:
                os.unlink(afname)
            except:
                self.console.PrintError('cant remove file: %s' % afname)
        return 1

    def cmdClean(self):
        self.console.PrintText('Clean old files:')
        startutil.DeleteOldFiles(startutil.appconfig.ICORBaseDir + '/log', adays=7, averbose=1)
        startutil.DeleteOldFiles(startutil.appconfig.ICORBaseDir + '/wwwroot/output', adays=1, afragments=['cache', ], averbose=1)
        startutil.DeleteOldFiles(startutil.appconfig.ICORBaseDir + '/wwwsync', adays=2, averbose=1)

    def cmdDumpData(self, abasefilename):
        r1, r2 = '', ''
        f = storageutil.MakeIdentifier(abasefilename)
        if f:
            filename = self.aBackupDir + '/' + f + '.isf'
            filenamev = self.aBackupDir + '/' + f + '_v.isf'
            try:
                self.aICORDBData.struct.JSONAllDataSave(filename, filenamev)
                r1, r2 = filename, filenamev
            except:
                traceback.print_exc()
        return r1, r2

    def cmdMaintenanceHelp(self):
        self.console.PrintHelp('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('*** Maintenance ***')
        self.console.PrintHelp('  help - (h) show this help')
        self.console.PrintHelp('  exit - (e) exit maintenance menu')
        self.console.PrintHelp('  quit - (q) quit ICOR')
        self.console.PrintHelp('  configuration - (conf) show current configuration')
        self.console.PrintHelp('  list - (l) list db info (alldata, snapshots, data snapshots)')
        self.console.PrintHelp('  dir - show all snapshot files in backup dir')
        self.console.PrintHelp('  - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  snapshot <all|data|security> <snapshot_name> - make all/data/security snapshot from repository')
        self.console.PrintHelp('  rename <all|data|security> <snapshot_name_1> <snapshot_name_2> - rename snapshot from name1 to name2')
        self.console.PrintHelp('  remove <all|data|security> <snapshot_name> - remove snapshot from database')
        self.console.PrintHelp('  save <all|data|security> <snapshot_name> <base_file_name> - save snapshot to file')
        self.console.PrintHelp('  load <all|data|security> <snapshot_name> <base_file_name> - load data from file to snapshot')
        self.console.PrintHelp('  restore <all|data|security> <snapshot_name> - restore snapshot into alldata')
        self.console.PrintHelp('  - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  initdb - init Postgres, create user, database')
        self.console.PrintHelp('  removeversions - remove alldatav history records')
        self.console.PrintHelp('  removedata - remove data from repository - CAREFUL!')
        self.console.PrintHelp('  removesecurity - remove security from repository - CAREFUL!')
        self.console.PrintHelp('  removeemptyreferences - remove empty references from selected fields (use after removedata and removesecurity)')
        self.console.PrintHelp('  clean - clean temp and log files')
        self.console.PrintHelp('  backup - backup repository')
        self.console.PrintHelp('  dump <base_file_name> - dump alldata and alldatav to binary files in backup dir')
        self.console.PrintHelp('  - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  setcheck <process> <bool> - (sc) set checkable status for process [redaemon,eserver,iserver,sserver]')
        self.console.PrintHelp('  start <process> - start process [redaemon,eserver,iserver,sserver] (if process is checkable)')
        self.console.PrintHelp('  stop <process> - stop process [redaemon,eserver,iserver,sserver]')
        self.console.PrintHelp('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  checkdbaccess - check all db access connections and set their inactivity status')
        self.console.PrintHelp('  checkdbaccessstruct - check projects and wwwmenustruct db access connections and set their inactivity status')
        self.console.PrintHelp('  - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  securityload - (sl) upgrade ICOR: load security data from upgradeicor_security.xml')
        self.console.PrintHelp('  fieldreferencecolonrepair - (frcr) repair trailing colon in all field references')
        self.console.PrintHelp('  securityrepair - (sr) repair all users, groups, profiles according to ref objects')
        self.console.PrintHelp('  loadusers <profile> <file> - load users from json file into profile (securityrepair next)')
        self.console.PrintHelp('  replicationload - (rl) upgrade ICOR: load replication recursive data from upgradeicor_objects_recursive.gz')
        self.console.PrintHelp('  searchusers <substr> - search users for substring match - or * for all - or #oid for _oid search)')
        self.console.PrintHelp('  setuserpassword <user> <password> - set user password. <username> or <#uid>)')
        self.console.PrintHelp('  upgradedbaccess - upgrade ICOR: change old dbaccess connectionstrings to dbhost objects')
        self.console.PrintHelp('  securityremoveunused - upgrade ICOR: remove unused security items, needs securityrepair after')
        self.console.PrintHelp('  methodssave - upgrade ICOR: save all method text into python lib')
        self.console.PrintHelp('  - - - - - - - - - - - - - - - - - - -')
        self.console.PrintHelp('  historyload - (hl) load history tables from modbfs in <icor>/db/_history/<source>/*.mfd')
        self.console.PrintHelp('  historystore - (hs) store history txt files from <icor>/db/_history/<source>/COPY/*.txt into _v table')

    def GetSnapshotExtByKind(self, akind):
        d = {'all': '.isf', 'data': '.isdf', 'security': '.issf', }
        return d.get(akind, '.bin')

    def processCommand(self, acommand, aparams):
        if acommand in ['e', 'exit']:
            self.console.PrintText('Exit maintenance mode..')
            return 0
        elif acommand in ['q', 'quit']:
            self.console.PrintText('Quit ICOR')
            self.cmdQuit(asilent=1)
            return 0
        elif acommand in ['h', 'help', '?']:
            self.cmdMaintenanceHelp()
        elif (acommand in ['dump', ]) and (len(aparams) == 1):
            self.console.PrintText('Dump alldata table to binary file.')
            filename, filenamev = self.cmdDumpData(aparams[0])
            if filename:
                self.console.PrintText('data saved to file: "%s", version data to file: "%s"' % (filename, filenamev))
        elif (acommand in ['snapshot', ]) and (len(aparams) == 2):
            snapshot = storageutil.MakeIdentifier(aparams[1])
            if not snapshot or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            if aparams[0] == 'all':
                self.aICORDBData.struct.MakeSnapshot(snapshot)
                self.console.PrintText('data copied to snapshot: "%s"' % (snapshot, ))
                return 1
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            if aparams[0] == 'data':
                lwhere = aupgrade.GetClassImportRanges()
            elif aparams[0] == 'security':
                lwhere = aupgrade.GetSecurityImportRanges()
            self.aICORDBData.struct.MakeSnapshotData(aparams[0], snapshot, lwhere)
            self.console.PrintText('project %s copied to snapshot: "%s"' % (aparams[0], snapshot, ))
        elif (acommand in ['rename', ]) and (len(aparams) == 3):
            snapshot1 = storageutil.MakeIdentifier(aparams[1])
            snapshot2 = storageutil.MakeIdentifier(aparams[2])
            if not snapshot1 or not snapshot2 or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            self.aICORDBData.struct.RenameSnapshot(aparams[0], snapshot1, snapshot2)
            self.console.PrintText('Renamed "%s" snapshot: "%s" to "%s"' % (aparams[0], snapshot1, snapshot2))
        elif (acommand in ['remove', ]) and (len(aparams) == 2):
            snapshot = storageutil.MakeIdentifier(aparams[0])
            if not snapshot or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            self.aICORDBData.struct.RemoveSnapshot(aparams[0], snapshot)
            self.console.PrintText('Removed "%s" snapshot: "%s"' % (aparams[0], snapshot, ))
        elif (acommand in ['save', ]) and (len(aparams) == 3):
            snapshot = storageutil.MakeIdentifier(aparams[1])
            f = storageutil.MakeIdentifier(aparams[2])
            if not f or not snapshot or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            filename = self.aBackupDir + '/' + f + self.GetSnapshotExtByKind(aparams[0])
            self.aICORDBData.struct.JSONAllDataSaveSnapshot(aparams[0], snapshot, filename)
            self.console.PrintText('"%s" saved to file: "%s" from snapshot: "%s"' % (aparams[0], filename, snapshot))
        elif (acommand in ['load', ]) and (len(aparams) == 3):
            snapshot = storageutil.MakeIdentifier(aparams[1])
            f = storageutil.MakeIdentifier(aparams[2])
            if not f or not snapshot or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            filename = self.aBackupDir + '/' + f + self.GetSnapshotExtByKind(aparams[0])
            self.aICORDBData.struct.CreateSnapshotTable(aparams[0], snapshot)
            self.aICORDBData.struct.JSONAllDataLoadSnapshot(aparams[0], snapshot, filename)
            self.console.PrintText('"%s" loaded from file: "%s" to snapshot: "%s"' % (aparams[0], filename, snapshot))
        elif (acommand in ['restore', ]) and (len(aparams) == 2):
            snapshot = storageutil.MakeIdentifier(aparams[1])
            if not snapshot or (aparams[0] not in ['all', 'data', 'security']):
                self.console.PrintError('bad parameters')
                return 1
            if aparams[0] == 'all':
                self.aICORDBData.struct.RestoreSnapshot(snapshot)
                self.console.PrintText('"%s" restored from snapshot: "%s"' % (aparams[0], snapshot, ))
                return 1
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            if aparams[0] == 'data':
                lwhere = aupgrade.GetClassImportRanges()
            elif aparams[0] == 'security':
                lwhere = aupgrade.GetSecurityImportRanges()
            self.aICORDBData.struct.RestoreSnapshotByWhere(aparams[0], snapshot, lwhere)
            self.console.PrintText('"%s" restored from snapshot: "%s"' % (aparams[0], snapshot, ))
        elif (acommand in ['removedata', ]) and (len(aparams) == 0):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            lwhere = aupgrade.GetClassImportRanges()
            self.aICORDBData.struct.RemoveDataByWhere(lwhere)
            self.console.PrintText('all data removed')
        elif (acommand in ['removesecurity', ]) and (len(aparams) == 0):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            lwhere = aupgrade.GetSecurityClearRanges()
            self.aICORDBData.struct.RemoveDataByWhere(lwhere)
            self.console.PrintText('security data removed')
        elif (acommand in ['removeemptyreferences', ]) and (len(aparams) == 0):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.RemoveEmptyReferences()
        elif (acommand in ['dir', ]) and (len(aparams) == 0):
            adir = startutil.DirClearByDays()
            d = {'.isf': [], '.isdf': [], '.issf': [], }
            le = d.keys()
            for afileentry in adir.GetFiles(self.aBackupDir):
                apath, aname = os.path.split(afileentry.path)
                abasename, aext = os.path.splitext(aname)
                if aext in le:
                    fs = afileentry.stat()
                    ftime = datetime.datetime.fromtimestamp(fs.st_mtime)
                    lf = [ftime.isoformat(' '), abasename, afileentry.path, fs.st_size, ]
                    d[aext].append(lf)
            for ainfo, aext in [['all', '.isf'], ['data', '.isdf'], ['security', '.issf']]:
                l = d[aext]
                if not l:
                    continue
                print 'Available snapshots of type: "%s"' % ainfo
                l.sort()
                l.reverse()
                for acreated, abasename, apath, asize in l:
                    self.console.PrintText('    snapshot: "%s", path: "%s", size: %d, created: %s' % (abasename, apath, asize, acreated))
        elif acommand in ['list', 'l']:
            self.console.PrintInfo('Datatables:')
            l, ld, ls, la = self.aICORDBData.struct.GetTableSnapshots()
            for atablename, amax, alast in la:
                self.console.PrintInfo('   %s - %s (%d records)' % (alast, atablename, amax, ))
            self.console.PrintInfo('Snapshots ALL:')
            i = 1
            for alast, asnapshot, amax in l:
                self.console.PrintInfo('   %d: %s - %s (%d records)' % (i, alast, asnapshot, amax))
                i = i + 1
            self.console.PrintInfo('Snapshots DATA only:')
            i = 1
            for alast, asnapshot, amax in ld:
                self.console.PrintInfo('   %d: %s - %s (%d records)' % (i, alast, asnapshot, amax))
                i = i + 1
            self.console.PrintInfo('Snapshots SECURITY only:')
            i = 1
            for alast, asnapshot, amax in ls:
                self.console.PrintInfo('   %d: %s - %s (%d records)' % (i, alast, asnapshot, amax))
                i = i + 1
        elif (acommand in ['initdb', ]):
            aICORDBData = icordbmain.ICORDBData()
            aICORDBData.initSchema()
            aICORDBInit = icordbmain.ICORDBInit()
            aICORDBInit.initSchema()
            self.console.PrintText('Postgres is initialized..')
        elif (acommand in ['removeversions', ]) and (len(aparams) == 0):
            self.aICORDBData.struct.RemoveVersions()
            self.console.PrintText('version data removed...')
        elif (acommand in ['clean', ]):
            self.cmdClean()
        elif (acommand in ['beckup', ]):
            self.cmdBackup()
        elif (acommand in ['configuration', 'conf']):
            self.cmdInfo()
        elif (acommand in ['setcheck', 'sc']) and (len(aparams) == 2):
            aprocess = self.subprocs.get(aparams[0], None)
            if aprocess:
                w = storageutil.str2bool(aparams[1])
                aprocess.checkable = w
                self.console.PrintText('Set process %s checkable status to %s' % (aparams[0], str(w)))
            else:
                self.console.PrintText('Unknown process: %s' % aparams[0])
        elif (acommand in ['start', ]) and (len(aparams) == 1):
            aprocess = self.subprocs.get(aparams[0], None)
            if aprocess:
                if aprocess.checkable:
                    aprocess.check()
                else:
                    self.console.PrintText('Process %s is not checkable' % aparams[0])
            else:
                self.console.PrintText('Unknown process: %s' % aparams[0])
        elif (acommand in ['stop', ]) and (len(aparams) == 1):
            aprocess = self.subprocs.get(aparams[0], None)
            if aprocess:
                aprocess.stop()
            else:
                self.console.PrintText('Unknown process: %s' % aparams[0])
        elif (acommand in ['securityload', 'sl']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.SecurityLoad(aprofile=0)
        elif (acommand in ['securityrepair', 'sr']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.SecurityRepair()
        elif (acommand in ['fieldreferencecolonrepair', 'frcr']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.FieldReferencesColonRepair()
        elif (acommand in ['replicationload', 'rl']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.ReplicationLoad(aprofile=0)
        elif (acommand in ['upgradedbaccess', ]):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.DBAccessMarkSimilar()
            aupgrade.DBAccessMoveHosts()
        elif (acommand in ['checkdbaccess', ]):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.CheckDBAccess(verbose=1)
        elif (acommand in ['checkdbaccessstruct', ]):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.CheckDBAccessByStruct(verbose=1)
        elif (acommand in ['securityremoveunused', ]):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.SecurityRemoveUnusedItems()
        elif (acommand in ['loadusers', ]) and (len(aparams) == 2):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.LoadUsers(aparams[0], aparams[1])
        elif (acommand in ['searchusers', ]) and (len(aparams) == 1):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.SearchUsers(aparams[0])
        elif (acommand in ['setuserpassword', ]) and (len(aparams) == 2):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.SetUserPassword(aparams[0], aparams[1])
        elif (acommand in ['methodssave', ]):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.MethodsSave()
        elif (acommand in ['historyload', 'hl']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.HistoryLoad()
        elif (acommand in ['historystore', 'hs']):
            from icorupgrade import upgrade
            aupgrade = upgrade.ICORUpgrade(self)
            aupgrade.HistoryStore()
        else:
            self.console.PrintText('unknown command or improper number of parameters...')
        return 1

    def cmdMaintenance(self):
        w = 1
        while w:
            s = self.Input('input command (h for help):', adefault='exit')
            l = s.split()
            if l:
                try:
                    w = self.processCommand(l[0], l[1:])
                except:
                    traceback.print_exc()

    def cmdSchedulerSecundely(self):
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Second', amutex='ICOR_Scheduler_Second', apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerSecond.py', ainitcheck=1)

    def cmdSchedulerMinutely(self, aminute=''):
        aparms = []
        if aminute:
            aparms = ['--minute=' + aminute, ]
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Minute' + aminute, amutex='ICOR_Scheduler_Minute' + aminute, apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerMinute.py', aparms=aparms, ainitcheck=1)

    def cmdSchedulerMinutely5(self, aminute=''):
        self.cmdSchedulerMinutely('5')

    def cmdSchedulerMinutely11(self, aminute=''):
        self.cmdSchedulerMinutely('11')

    def cmdSchedulerMinutely23(self, aminute=''):
        self.cmdSchedulerMinutely('23')

    def cmdSchedulerMinutely31(self, aminute=''):
        self.cmdSchedulerMinutely('31')

    def cmdSchedulerHourly(self):
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Hour', amutex='ICOR_Scheduler_Hour', apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerHour.py', ainitcheck=1)

    def cmdSchedulerDaily(self):
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Day', amutex='ICOR_Scheduler_Day', apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerDay.py', ainitcheck=1)

    def cmdSchedulerWeekly(self):
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Week', amutex='ICOR_Scheduler_Week', apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerWeek.py', ainitcheck=1)

    def cmdSchedulerMonthly(self):
        icorsubprocess.ICORSubProcess(self, 'ICOR_Scheduler_Month', amutex='ICOR_Scheduler_Month', apyprocess=startutil.appconfig.PythonTopDir + '/external/Scheduler/mcrmschedulerMonth.py', ainitcheck=1)

    def processCheck(self):
        if not self.subprocs:
            #ubijanie starych procesow serwisowych
            startutil.GetActiveExecutorsProcesses(['/External/default/redaemon2.py', '/External/default/eserver.py', '/External/default/iserver.py', '/External/default/sserver.py'], killall=1, cominitialize=0)
            #kasowanie zawartosci: "c:\program files (x86)\python 2.7\lib\site-packages\win32com\gen_py"
            apythonpath, apythonexe = os.path.split(startutil.appconfig.DefaultProcessExecutor)
            agenpath = apythonpath + '/lib/site-packages/win32com/gen_py'
            startutil.DeleteOldFiles(agenpath, adeleteall=1)
            # inicjacja procesor roboczych
            self.subprocs['redaemon'] = icorsubprocess.ICORSubProcess(self, 'redaemon', amutex='ICOR_Redaemon_Instance', aport=startutil.appconfig.TCP_SERVER_PORT_REDAEMON, apyprocess=startutil.appconfig.PythonTopDir + '/External/default/redaemon2.py')
            self.subprocs['eserver'] = icorsubprocess.ICORSubProcess(self, 'eserver', amutex='ICOR_EServer_Instance', aport=startutil.appconfig.TCP_SERVER_PORT_ESERVER, apyprocess=startutil.appconfig.PythonTopDir + '/External/default/eserver.py')
            self.subprocs['iserver'] = icorsubprocess.ICORSubProcess(self, 'iserver', amutex='ICOR_IServer_Instance', aport=startutil.appconfig.TCP_SERVER_PORT_ISERVER, apyprocess=startutil.appconfig.PythonTopDir + '/External/default/iserver.py')
            self.subprocs['sserver'] = icorsubprocess.ICORSubProcess(self, 'sserver', amutex='ICOR_SServer_Instance', aport=startutil.appconfig.TCP_SERVER_PORT_SSERVER, apyprocess=startutil.appconfig.PythonTopDir + '/External/default/sserver.py')
        else:
            for pname, aprocess in self.subprocs.items():
                aprocess.check()
        if not self.aICORStartManager.running:
            self.aICORStartManager.start()

    def procScheduler(self):
        anow = datetime.datetime.now()
        if anow > self.nexteventdatetime:
            self.console.PrintText('scheduler: %s at %s [%s]' % (self.nexteventkind, str(self.nexteventdatetime), str(anow)))
            if self.nexteventkind == 'secundely':
                self.cmdSchedulerSecundely()
            elif self.nexteventkind[:8] == 'minutely':
                self.cmdSchedulerMinutely(self.nexteventkind[8:])
            elif self.nexteventkind == 'hourly':
                self.cmdSchedulerHourly()
            elif self.nexteventkind == 'daily':
                self.cmdSchedulerDaily()
            elif self.nexteventkind == 'backup':
                self.cmdBackup()
            elif self.nexteventkind == 'clean':
                self.cmdClean()
            elif self.nexteventkind == 'weekly':
                self.cmdSchedulerWeekly()
            elif self.nexteventkind == 'monthly':
                self.cmdSchedulerMonthly()
            self.nexteventkind, anexteventdtuple = self.schedulerevents.next()
            self.nexteventdatetime = datetime.datetime(*anexteventdtuple)

    def StartAll(self, apaused=0, amaintenance=0):
        self.console.PrintInfo('Press [h] for help.')

        anow = datetime.datetime.now()
        levents = []
        sdy, sdm, sdd = storageutil.GetLastWeekday()    # pobranie ostatniej soboty do naliczania czasu schedulera
        for i in [5, 11, 23, 31]:
            aevent = ('minutely' + str(i), datetime.datetime(sdy, sdm, sdd, 0, 1, 0), (0, 0, 0, 0, i, 0, 0))
            levents.append(aevent)
        asecundely = ('secundely', datetime.datetime(sdy, sdm, sdd, 0, 1, 0), (0, 0, 0, 0, 0, 30, 0))
        aminutely = ('minutely', datetime.datetime(sdy, sdm, sdd, 0, 1, 0), (0, 0, 0, 0, 2, 0, 0))
        ahourly = ('hourly', datetime.datetime(sdy, sdm, sdd, 0, 1, 0), 'hourly')
        adaily = ('daily', datetime.datetime(sdy, sdm, sdd, 19, 19, 0), 'daily')
        aweekly = ('weekly', datetime.datetime(sdy, sdm, sdd, 22, 22, 0), 'weekly')    #sobota
        amonthly = ('monthly', datetime.datetime(sdy, sdm, sdd, 2, 2, 0), 'monthly')    #sobota
        abackup = ('backup', datetime.datetime(sdy, sdm, sdd, 4, 4, 0), 'daily')
        aclean = ('clean', datetime.datetime(sdy, sdm, sdd, 4, 44, 0), 'daily')

        levents.extend([asecundely, aminutely, ahourly, adaily, aweekly, amonthly, abackup, aclean])
        self.schedulerevents = schedaddle.upcoming_m(levents, latest=anow)
        self.nexteventkind, anexteventdtuple = self.schedulerevents.next()
        self.nexteventdatetime = datetime.datetime(*anexteventdtuple)

        if apaused:
            self.cmdPause()
        if amaintenance:
            self.cmdMaintenance()

        if self.starttime:
            self.console.PrintText('ICOR is ready! Initialization time: %0.4f sec.' % (time.clock() - self.starttime, ))

        adt_lastcheck = time.clock() - 100
        while self.state != 'QUIT':
            asleep = 0.01
            if self.state == 'CHECK':
                adt_lastcheck2 = time.clock()
                if (adt_lastcheck2 - adt_lastcheck) > 4:
                    self.processCheck()
                    adt_lastcheck = time.clock()
                self.procScheduler()
                asleep = asleep + 1
            while msvcrt.kbhit():
                achar = msvcrt.getch()
                if self.commandsdict.has_key(achar):
                    self.commandsdict[achar]()
                    break
            time.sleep(asleep)


if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-b", "--backup", action="store", type="string", dest="backup", help="Backup dir")
    optparser.add_option("-p", "--paused", action="store_true", dest="paused", help="Start in paused state")
    optparser.add_option("-m", "--maintenance", action="store_true", dest="maintenance", help="Start in maintenance state")

    options, args = optparser.parse_args()

    ret = startutil.WaitForApp(startutil.appconfig.APP_Mutex_ICOR, 1)
    if not ret:
        self.console.PrintError('ICOR instance already exists. Exiting.')
        sys.exit(1)

    apaused=options.paused
    amaintenance=options.maintenance

    if 0:
        apaused=True
        amaintenance=True

    aICORStarter = ICORStarter(abackup=options.backup, astarttime=time.clock())
    aICORStarter.StartAll(apaused=apaused, amaintenance=amaintenance)
    raise SystemExit(0)
