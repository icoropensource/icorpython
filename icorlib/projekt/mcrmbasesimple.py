# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwserver.icorwwwinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_JSONUtil as JSONUtil
import icordbmain.adoutil as ADOLibInit
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.projekt.mcrmrssinterface as MCRMRSSInterface
import icorlib.projekt.mcrmgeointerface as GeoInterface
import icorlib.projekt.mcrmwwwmenucontext as MCRMWWWMenuContext
import icorlib.projekt.mcrmwwwmenudeploy as MCRMWWWMenuDeploy
import icorlib.icorsecurity as ICORSecurity
import icorlib.projekt.mcrmutil as MCRMUtil
import icorlib.projekt.mcrmlib as MCRMLib
import icorlib.projekt.mcrmbase as MCRMBase
import string
import time
import sys
import re
import os

try:
    import json
except:
    import simplejson as json

import CLASSES_Library_NetBase_WWW_HTML_Util_ConversionsPL as ConversionsPL
import CLASSES_Library_NetBase_Utils_SMTPUtil as SMTPUtil
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.Header import Header
from email.MIMEBase import MIMEBase
try:
    from email import encoders
except:
    from email import Encoders as encoders
from email.Utils import COMMASPACE, formatdate

import smtplib
import icordbmain.dbaccess as dbaccess
import appplatform.startutil as startutil
import appplatform.storageutil as storageutil


class SourceEvent:

    def __init__(self, aobj, aname='', atext='', akey=''):
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.Name = aname
        self.Source = atext
        self.Key = akey

    def Dump(self):
        print '          Event: %d %s' % (self.OID, self.Name)


class WWWPluginSkin:

    def __init__(self, aplugin, sobj):
        self.Plugin = aplugin
        self.OID = sobj.OID
        self.Nazwa = sobj.Nazwa
        self.Klucz = sobj.Klucz
        ehrobj = MCRMUtil.EventHelper(sobj, 'Events')
        self.OnPluginBefore = ehrobj['OnPluginBefore']
        self.OnPluginAfter = ehrobj['OnPluginAfter']

    def ProcessSkin(self):
        pass


class WWWPluginExtension:

    def __init__(self, aplugin, xobj):
        self.Plugin = aplugin
        self.OID = xobj.OID
        self.Nazwa = xobj.Nazwa
        self.Klucz = xobj.Klucz
        ehrobj = MCRMUtil.EventHelper(xobj, 'Events')
        self.OnExtensionExecute = ehrobj['OnExtensionExecute']
        self.OnExtensionAction = ehrobj['OnExtensionAction']

    def ProcessExtension(self):
        pass


class Template:

    def __init__(self, aplugin, aobj):
        self.Plugin = aplugin
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.Name = self.Obj.Nazwa
        self.Events = {}
        self.TemplateVars = ICORUtil.ParseVars(aobj.TemplateVars, {})
        self.thisEventName, self.thisEventKey = '', ''
        self.aIsDerived = None

    def GetEvent(self, aobj, aname='', atext=''):
        if not self.Events.has_key(aobj.OID):
            aevent = SourceEvent(aobj, aname, atext)
            self.Events[aobj.OID] = aevent
        return self.Events[aobj.OID]

    def IsDerived(self):
        if self.aIsDerived is None:
            self.aIsDerived = 0    # ewentualnie sprawdzenie czy rzeczywiscie tak jest
        return self.aIsDerived

    def ProcessEvents(self, aname=''):
        otemplate = self.Plugin.WWWMenuStruct.repldict.get('Template', None)
        self.Plugin.WWWMenuStruct.repldict['Template'] = self
        for aevent in self.Events.values():
            if aname and aevent.Name != aname:
                continue


#         self.Plugin.WWWMenuStruct.Project.CMS.Log('processing template event: '+aevent.Name)
            oevent = self.Plugin.WWWMenuStruct.repldict.get('thisEvent', None)
            self.Plugin.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.Plugin.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SimpleTemplateEvent ' + str(self.OID) + ' ' + aname + ' ' + str(aevent.OID))
            self.Plugin.WWWMenuStruct.repldict['thisEvent'] = oevent
            if atext:
                self.Plugin.WWWMenuStruct.Project.CMS.Log(atext)
        self.Plugin.WWWMenuStruct.repldict['Template'] = otemplate

    def Dump(self):
        print '      Template: %d' % (self.OID, )
        for aevent in self.Events.values():
            aevent.Dump()


class Plugin:

    def __init__(self, astruct, aobj):
        self.WWWMenuStruct = astruct
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.Templates = {}
        self.Events = {}

        dtvars = {}
        tobj = aobj.Template
        while tobj:
            atemplate = self.GetTemplate(tobj)
            dtvars.update(atemplate.TemplateVars)
            tobj.Next()
        st = storageutil.TextReplaceByMarkup(aobj.PluginVars, self.WWWMenuStruct.StructVars, sm1='{^', sm2='^}')
        self.PluginVars = ICORUtil.ParseVars(st, dtvars)

        self.IsDisabled = aobj.Class.SGIsDisabled.ValuesAsInt(aobj.OID)
        self.Skins = []
        sobj = aobj.Skin
        while sobj:
            askin = WWWPluginSkin(self, sobj)
            self.Skins.append(askin)
            sobj.Next()

    def GetTemplate(self, aobj):
        if not self.Templates.has_key(aobj.OID):
            atemplate = Template(self, aobj)
            self.Templates[aobj.OID] = atemplate
        return self.Templates[aobj.OID]

    def HasTemplate(self, aname):
        for k, t in self.Templates.items():
            if t.Name == aname:
                return 1
        return 0

    def GetEvent(self, aobj, aname='', atext=''):
        if not self.Events.has_key(aobj.OID):
            aevent = SourceEvent(aobj, aname, atext)
            self.Events[aobj.OID] = aevent
        return self.Events[aobj.OID]

    def ProcessEvents(self, aname='', aeventcontext=''):
        if self.IsDisabled:
            return
        oplugin = self.WWWMenuStruct.repldict.get('Plugin', None)
        self.WWWMenuStruct.repldict['Plugin'] = self
        aoldeventcontext = self.WWWMenuStruct.repldict.get('EventContext', None)
        self.WWWMenuStruct.repldict['EventContext'] = aeventcontext
        for aevent in self.Events.values():
            if aname and aevent.Name != aname:
                continue
            self.WWWMenuStruct.Project.CMS.Log('processing plugin event: ' + aevent.Name)
            oevent = self.WWWMenuStruct.repldict.get('thisEvent', None)
            self.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SimplePluginEvent ' + str(self.OID) + ' ' + aname + ' ' + str(aevent.OID))
            self.WWWMenuStruct.repldict['thisEvent'] = oevent
            self.WWWMenuStruct.Project.CMS.Log(atext)
        for atemplate in self.Templates.values():
            atemplate.ProcessEvents(aname=aname)
        self.WWWMenuStruct.repldict['Plugin'] = oplugin
        self.WWWMenuStruct.repldict['EventContext'] = aoldeventcontext

    def ProcessSkins(self, aeventname, akey='', adict=None):
        ret = ''
        if self.Skins:
            write = None
            if self.WWWMenuStruct.repldict.has_key('Response'):
                write = self.WWWMenuStruct.repldict['Response'].write
            aplugindict = self.WWWMenuStruct.repldict.get('PluginDict', None)
            if adict is None:
                adict = {}
            self.WWWMenuStruct.repldict['PluginDict'] = adict
            for askin in self.Skins:
                if askin.Klucz != akey:
                    continue
                atext = ''
                if aeventname == 'OnPluginBefore':
                    atext = askin.OnPluginBefore
                if aeventname == 'OnPluginAfter':
                    atext = askin.OnPluginAfter
                if atext:
                    oevent = self.WWWMenuStruct.repldict.get('thisSkin', None)
                    self.WWWMenuStruct.repldict['thisSkin'] = askin
                    atext = ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SimpleSkinEvent ' + str(self.OID) + ' ' + aeventname + ' ' + str(askin.OID))
                    self.WWWMenuStruct.repldict['thisSkin'] = oevent
                    ret = ret + atext
                    if write is not None:
                        write(atext)
            if aplugindict is None:
                self.WWWMenuStruct.repldict['PluginDict'] = None
                del self.WWWMenuStruct.repldict['PluginDict']
            else:
                self.WWWMenuStruct.repldict['PluginDict'] = aplugindict
        return ret

    def ProcessExtensionAction(self, xobj):
        ret = ''
        if self.IsDisabled:
            return ret
        self.WWWMenuStruct.repldict['Plugin'] = self
        ehrobj = MCRMUtil.EventHelper(xobj, 'Events')
        atext = ehrobj['OnExtensionAction']
        if atext:
            oevent = self.WWWMenuStruct.repldict.get('thisExtension', None)
            self.WWWMenuStruct.repldict['thisExtension'] = self
            ret = ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, aglobaldict=1, ascriptname='SimpleExtensionAction ' + str(self.OID))
            self.WWWMenuStruct.repldict['thisExtension'] = oevent
        self.WWWMenuStruct.repldict['Plugin'] = None
        return ret

    def ExtensionInclude(self, akey):
        lExtensions = []
        tobj = self.Obj.Template
        while tobj:
            xobj = tobj.PluginExtension
            while xobj:
                aextension = WWWPluginExtension(self, xobj)
                lExtensions.append(aextension)
                xobj.Next()
            tobj.Next()
        for aextension in lExtensions:
            if aextension.Klucz != akey:
                continue
            atext = aextension.OnExtensionExecute
            if atext:
                oevent = self.WWWMenuStruct.repldict.get('thisExtension', None)
                self.WWWMenuStruct.repldict['thisExtension'] = aextension
                ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, aglobaldict=1, ascriptname='SimpleExtension ' + str(self.OID) + ' ' + aextension.Nazwa + ' ' + str(aextension.OID))
                self.WWWMenuStruct.repldict['thisExtension'] = oevent

    def Dump(self):
        print '    Plugin: %d' % (self.OID, )
        for aevent in self.Events.values():
            aevent.Dump()
        for atemplate in self.Templates.values():
            atemplate.Dump()


class Chapter:

    def __init__(self, astruct, aoid):
        self.WWWMenuStruct = astruct
        self.ClassItem = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
        self.Obj = self.ClassItem[aoid]
        self.OID = aoid
        self.HRef = self.Obj.SGHref
        self.HRefApp = self.Obj.SGHrefApp
        self.HRefParams = self.Obj.SGHrefParams
        self.Target = self.Obj.SGTarget
        self.IsMenuDisabled = self.Obj['SGIsMenuDisabled', mt_Integer]
        self.IsExternalHRef = 0
        self._href = None

    def GetHRef(self):
        if self._href is None:
            ahref = 'chapter_%d.asp' % self.OID
            if self.HRef:
                ahref = self.HRef
                if ahref[:1] == '#':
                    atargetoid = ahref[1:]
                    ahref = 'chapter_%s.asp' % atargetoid
                else:
                    self.IsExternalHRef = 1
            if self.HRefParams:
                ahref = ICORUtil.URLAddParam(ahref, self.HRefParams)
            self._href = ahref
            return ahref
        return self._href


class WWWMenuStruct:

    def __init__(self, aproject, aobj):
        self.Project = aproject
        self.CRM = aproject
        self.Obj = aobj.AsObject()
        self.MenuStructObj = aobj.AsObject()
        self.OID = aobj.OID
        self.Plugins = {}
        self._pluginsinit = 0
        self.ChaptersByID = {}
        self.CacheGen = {}
        self.WriteDisabled = 0
        self.repldict = self.GetReplDict()
        self.returnValue = ''
        self.OptimizationLevel = 0
        oobj = aobj.PoziomOptymalizacji
        if oobj:
            self.OptimizationLevel = oobj['OptLevel', mt_Integer]
        self.PageTemplateObj = aobj.PageTemplate
        self.MetaTemplateObj = aobj.MetaTemplate

        self.InfoTablesSufix = aobj['InfoTablesSufix', mt_Integer]
        self.DefaultEncoding = aproject.DefaultEncoding
        self.DefaultCodePage = aproject.DefaultCodePage
        eobj = aobj.DefaultEncoding
        if eobj:
            self.DefaultEncoding = eobj.IANAName.lower()
            self.DefaultCodePage = eobj.CodePage
        self.WSBaseDirectory = FilePathAsSystemPath(aobj.AppPaths.SciezkaAplikacji)
        if self.WSBaseDirectory[-1:] not in ['/', '\\']:
            self.WSBaseDirectory = self.WSBaseDirectory + '/'
        self.IndexBaseDirectory = aobj.AppPaths.IndexServerBaseDirectory
        if not self.IndexBaseDirectory:
            self.IndexBaseDirectory = self.WSBaseDirectory
        if self.IndexBaseDirectory[-1:] not in ['/', '\\']:
            self.IndexBaseDirectory = self.IndexBaseDirectory + '/'
        self.IndexBaseDirectory = string.replace(self.IndexBaseDirectory, '/', '\\')
        self.IndexServerCatalog = aobj.AppPaths.IndexServerCatalog
        self.VirtualRoot = aobj.AppPaths.KatalogWirtualny
        self.CGIPath = aobj.AppPaths.SciezkaCGI
        self.InternalWWWAddress = aobj.AppPaths.AdresWewnetrznyWWW
        if not self.InternalWWWAddress:
            self.InternalWWWAddress = 'http://127.0.0.1'
        self.ExternalWWWAddress = aobj.AppPaths.AdresZewnetrznyWWW
        if self.ExternalWWWAddress[-1:] == '/':
            self.ExternalWWWAddress = self.ExternalWWWAddress[:-1]
        if self.CGIPath == '':
            self.CGIPath = 'chapter_#.asp'
        if self.VirtualRoot:
            if self.VirtualRoot[-1:] != '/':
                self.VirtualRoot = self.VirtualRoot + '/'
            if self.VirtualRoot[:1] != '/':
                self.VirtualRoot = '/' + self.VirtualRoot
        self.deployscenarios = []
        dsobj = aobj.AppPaths.DeployScenario
        while dsobj:
            adeploy = MCRMWWWMenuDeploy.DeployScenario(self, dsobj)
            if not adeploy.IsDisabled:
                self.deployscenarios.append(adeploy)
            dsobj.Next()
        self.jslibmanagers = []
        dsobj = aobj.AppPaths.JSLibManager
        while dsobj:
            ajslibmanager = MCRMWWWMenuDeploy.JSLibManager(self, dsobj)
            if not ajslibmanager.IsDisabled:
                self.jslibmanagers.append(ajslibmanager)
            dsobj.Next()
        self.WWWMenuContext = MCRMWWWMenuContext.WWWMenuContext
        self.StructVars = ICORUtil.ParseVars(aobj.StructVars, {'aCgiScriptPath': '', 'aFileUploadsOrderInChapters': 'Description,Name', 'aHTTPFileUploadsOrderInChapters': 'Description,Name'})
        self.Dist_Mode = self.StructVars.get('aDistMode', startutil.appconfig.Dist_Mode)

    def OpenText(self, afilename, amode='rb', aencoding=None, aerrors='xmlcharrefreplace', abuffering=1):
        if aencoding is None:
            aencoding = self.DefaultEncoding
        return ICORUtil.OpenText(afilename, amode=amode, aencoding=aencoding, aerrors=aerrors, abuffering=abuffering)

    def InitPlugins(self):
        self._pluginsinit = 1
        uobj = self.Obj.Plugins
        while uobj:
            aplugin = self.GetPlugin(uobj)
            uobj.Next()

    def GetPlugin(self, aobj):
        if not self.Plugins.has_key(aobj.OID):
            aplugin = Plugin(self, aobj)
            self.Plugins[aobj.OID] = aplugin
        return self.Plugins[aobj.OID]

    def GetPluginByTemplate(self, atemplate):
        if not self._pluginsinit:
            self.InitPlugins()
        for aoid, aplugin in self.Plugins.items():
            if aplugin.HasTemplate(atemplate):
                return aplugin
        return None

    def GetEventsByName(self, aname):
        if type(aname) == type([]):
            lnames = aname
        else:
            lnames = [aname, ]
        uobj = self.Obj.Plugins
        while uobj:
            eobj = uobj.PluginEvents
            while eobj:
                ename = eobj.EventKind.EventName
                if ename in lnames:
                    aplugin = self.GetPlugin(uobj)
                    aplugin.GetEvent(eobj, ename, eobj.EventSource)
                eobj.Next()
            tobj = uobj.Template
            while tobj:
                eobj = tobj.TemplateEvents
                while eobj:
                    ename = eobj.EventKind.EventName
                    if ename in lnames:
                        aplugin = self.GetPlugin(uobj)
                        atemplate = aplugin.GetTemplate(tobj)
                        atemplate.GetEvent(eobj, ename, eobj.EventSource)
                    eobj.Next()
                tobj.Next()
            uobj.Next()

    def GetChapterByID(self, aoid):
        if not self.ChaptersByID.has_key(aoid):
            achapter = Chapter(self, aoid)
            self.ChaptersByID[aoid] = achapter
        return self.ChaptersByID[aoid]

    def ProcessEvents(self, adict=None, aname=''):
        self.repldict['ADOLibInit'] = ADOLibInit
        self.repldict['aadoutil'] = self.Project.aadoutil
        if adict:
            self.repldict.update(adict)
        for aplugin in self.Plugins.values():
            try:
                s = aplugin.ProcessEvents(aname=aname)
            except:
                self.Project.CMS.LogException()
        if adict:
            for akey in adict.keys():
                del self.repldict[akey]
        return self.returnValue

    def DoGetChaptersFull(self, robj, lret, lgroups):
        while robj:
            achapter = self.GetChapterByID(robj.OID)
            w = 1
            if achapter.IsMenuDisabled:
                w = 0
            if w:
                ahref = achapter.GetHRef()
                if achapter.IsExternalHRef:
                    w = 0
            if w:
                sgrupa = ''
                gobj = robj.GrupaRozdzialow
                if gobj:
                    sgrupa = gobj.Nazwa
                if not sgrupa in lgroups:
                    w = 0
            if w:
                lret.append(achapter)
                robj2 = robj.PodRozdzialy
                if robj2:
                    self.DoGetChaptersFull(robj2, lret, lgroups)
            robj.Next()

    def GetChapters(self, amode='full', afullchaptersiterate=1, achaptergroup='', anoseochapters=1):
        lret = []
        if amode == 'full' and afullchaptersiterate == 1:
            if achaptergroup:
                lgroups = [achaptergroup, ]
            else:
                lgroups = ['', ]
                gobj = self.Obj.GrupyRozdzialow
                while gobj:
                    aname = gobj.Nazwa
                    w = 1
                    if anoseochapters and gobj['SGIsSEODisabled', mt_Integer]:
                        w = 0
                    if w:
                        lgroups.append(aname)
                    gobj.Next()
            robj = self.Obj.Rozdzialy
            self.DoGetChaptersFull(robj, lret, lgroups)
        return lret

    def GetMenuContext(self, acontextclass=None, achaptergroup='', amode='chapter', alevel=1, alevelmulti=0, aignorechaptergroups=0, afullchaptersiterate=0):
        if acontextclass is not None:
            amenucontext = acontextclass(self)
        else:
            amenucontext = MCRMWWWMenuContext.WWWMenuContext(self)
        amenucontext.ChapterGroup = achaptergroup
        amenucontext.Mode = amode    # chapter, full, submenu, navigator, chapterpeer
        amenucontext.ProcessLevels = alevel
        amenucontext.ProcessLevelsMulti = alevelmulti
        amenucontext.IsIgnoreChapterGroupsIterate = aignorechaptergroups
        amenucontext.IsFullChaptersIterate = afullchaptersiterate
        return amenucontext

    def GetReplDict(self, dd=None):
        d = {'RSSInterface': MCRMRSSInterface, 'aLog': self.Project.CMS.log, 'JSONUtil': JSONUtil, 'aProject': self.Project, 'aWWWMenuStruct': self, 'EventContext': '', 'aCRM': self.CRM, 'this': self, 're': re, 'os': os, 'string': string, 'json': json, 'ICORUtil': ICORUtil, 'ADOLibInit': ADOLibInit, 'FilePathAsSystemPath': FilePathAsSystemPath, 'XMLUtil': XMLUtil, 'GeoInterface': GeoInterface, 'ICORSecurity': ICORSecurity, 'storageutil': storageutil}
        return d

    def Dump(self):
        print '  WWWMenuStruct: %d' % (self.OID, )
        for aplugin in self.Plugins.values():
            aplugin.Dump()


class SMTPServer:

    def __init__(self, aproject, aoid):
        self.Project = aproject
        self.ClassItem = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_SMTPServerParameters']
        self.Obj = self.ClassItem[aoid]
        self.OID = aoid

    def Send(self, ato, asubject, atext, alog=None, afiles=None, afrom=None):
        if afiles is None:
            afiles = []
        if 0:
            msgRoot = MIMEMultipart('related')
            msgRoot['Subject'] = Header(ConversionsPL.Win2ISO(asubject), 'iso-8859-2')
            if afrom is None:
                afrom = self.Obj.SMTPFrom
            msgRoot['From'] = string.strip(afrom)
            if type(ato) == type([]):
                msgRoot['To'] = COMMASPACE.join(map(ConversionsPL.Win2ISO, ato))
            else:
                msgRoot['To'] = ConversionsPL.Win2ISO(ato)
            msgRoot.preamble = 'This is a multi-part message in MIME format.'
            msgAlternative = MIMEMultipart('alternative')
            msgRoot.attach(msgAlternative)
            msgText = MIMEText(ConversionsPL.Win2ISO('Ten komunikat należy odczytać w postaci HTML.'), 'plain', 'iso-8859-2')
            msgAlternative.attach(msgText)
            msgText = MIMEText(ConversionsPL.Win2ISO(atext), 'html', 'iso-8859-2')
            msgAlternative.attach(msgText)
        if 1:
            msgRoot = MIMEMultipart()
            msgRoot.set_charset('utf-8')
            msgRoot['Subject'] = Header(XMLUtil.CP1250_To_UTF8(asubject), 'utf-8')
            msgRoot['From'] = string.strip(self.Obj.SMTPFrom)
            if type(ato) == type([]):
                msgRoot['To'] = COMMASPACE.join(map(XMLUtil.CP1250_To_UTF8, ato))
            else:
                msgRoot['To'] = XMLUtil.CP1250_To_UTF8(ato)
            msgRoot.preamble = 'This is a multi-part message in MIME format.'
            msgRoot.epilogue = ''
            #         msgAlternative = MIMEMultipart('alternative')
            #         msgRoot.attach(msgAlternative)
            #         msgText = MIMEText(XMLUtil.CP1250_To_UTF8('Ten komunikat należy odczytać w postaci HTML.'),'plain','utf-8')
            #         msgRoot.attach(msgText)
            msgText = MIMEText(XMLUtil.CP1250_To_UTF8(atext), 'html', 'utf-8')
            msgRoot.attach(msgText)

        if 1:
            for afpath in afiles:
                if type(afpath) in [type([]), type(())]:
                    afpath, afname = afpath
                else:
                    afname = afpath
                part = MIMEBase('application', 'octet-stream')
                asize1, asize2 = 0, 1
                while asize1 != asize2:
                    asize1 = asize2
                    asize2 = os.path.getsize(afpath)
                    time.sleep(0.9)
                if alog:
                    alog.Log('Dodanie zalacznika: ' + afpath + ' rozmiar ' + str(asize1))
                fb = open(afpath, 'rb')
                bfile = fb.read()
                fb.close()
                part.set_payload(bfile)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(afname))
                msgRoot.attach(part)

        w = 0
        if alog:
            alog.Log('Wysyłanie potwierdzenia na adres: ' + str(ato))
        try:
            asmtp = SMTPUtil.AuthSMTP(self.Obj.SMTPServer)
            if self.Obj.SMTPUser != '' and self.Obj.SMTPPassword != '':
                asmtp.login(self.Obj.SMTPUser, self.Obj.SMTPPassword)
            if type(ato) != type([]):
                lto = [ato, ]
            else:
                lto = ato
            lto = map(string.strip, lto)
            asmtp.sendmail(string.strip(self.Obj.SMTPFrom), lto, msgRoot.as_string())
            asmtp.quit()
            w = 1
        except smtplib.SMTPRecipientsRefused, e:
            rejects = {str(e): 'Recipients refused'}
            if alog:
                alog.LogException()
        except smtplib.SMTPSenderRefused, e:
            rejects = {str(e): self.sender[1]}
            if alog:
                alog.LogException()
        except smtplib.SMTPDataError, e:
            rejects = {smtplib.SMTPDataError: ''}
            if string.find(e.smtp_error, 'try again later') > 0:
                w = -1
            if alog:
                alog.LogException()


#      except socket.error, e:
#         rejects = {sockerror(e): ''}
#         if alog:
#            alog.LogException()
        except Exception, e:
            rejects = {'Error sending mail': e}    # fake the rejects dict
            if alog:
                alog.LogException()
        return w


class Project:

    def __init__(self, acms, aobj):
        self.CMS = acms
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.Project = aobj.Nazwa
        self.wwwmenustruct = {}
        self.smtpserversbyid = {}
        try:
            abasedirectory = aICORWWWServerInterface.AppPath + aobj.AppPath
            if abasedirectory[-1:] != '/':
                abasedirectory = abasedirectory + '/'
        except:
            abasedirectory = ''
        abasedirectory = string.replace(abasedirectory, '\\', '/')
        self.BaseDirectory = FilePathAsSystemPath(abasedirectory)
        self.BaseNameModifier = self.Obj.BaseNameModifier

        self.WWWDataPath = FilePathAsSystemPath(aobj.WWWDataPath)
        self.WWWDataPath = string.replace(self.WWWDataPath, '\\', '/')
        if self.WWWDataPath[-1:] != '/':
            self.WWWDataPath = self.WWWDataPath + '/'
        self.WWWDataPathScan = FilePathAsSystemPath(aobj.WWWDataPathScan)
        self.WWWDataPathScan = ICORUtil.GetProperPath(self.WWWDataPathScan)
        if not self.WWWDataPathScan:
            self.WWWDataPathScan = self.WWWDataPath
        self.WWWDataPathUserFiles = FilePathAsSystemPath(aobj.WWWDataPathUserFiles, aslash='/')
        self.WWWDataPathUserImages = FilePathAsSystemPath(aobj.WWWDataPathUserImages, aslash='/')

        self.CDN_ExternalWWWAddress = ''
        self.CDN_FTPServer = ''
        self.CDN_FTPBasePath = ''
        self.CDN_FTPUser = ''
        self.CDN_FTPPassword = ''
        self.CDN_ServerType = ''
        self.CDN_SMBBasePath = ''
        cobj = aobj.CDNServers
        if cobj:
            if not cobj['SGIsDisabled']:
                self.CDN_ExternalWWWAddress = ICORUtil.GetProperPath(cobj.AdresZewnetrznyWWW)
                self.CDN_FTPServer = cobj.AdresFTP
                self.CDN_FTPBasePath = ICORUtil.GetProperPath(cobj.FTPBasePath)
                self.CDN_FTPUser = cobj.FTPUser
                self.CDN_FTPPassword = cobj.FTPPassword
                self.CDN_ServerType = cobj.SerwerCDN.Nazwa
                self.CDN_SMBBasePath = ICORUtil.GetProperPath(cobj.SMBBasePath)

        self.ProjectVars = ICORUtil.ParseVars(aobj.ProjectVars, {'aCgiScriptPath': '', 'aExternalDictMaxItemsCount': '300', 'aMSSQLVersion': '2008', 'aSQLScriptsCreate': '0'})
        self.SQLVersion = int(self.ProjectVars.get('aMSSQLVersion', '2008'))
        self.DefaultEncoding = self.ProjectVars.get('aDefaultEncoding', 'utf-8').lower()
        self.DefaultCodePage = self.ProjectVars.get('aDefaultCodePage', '65001')
        self.Dist_Mode = self.ProjectVars.get('aDistMode', startutil.appconfig.Dist_Mode)
        self.aadoutil = None
        self.repldict = None
        self.addins = []
        self.ProcessAddIns(aobj.AddIns)

    def InitVariables(self):
        self.ConnectionString = dbaccess.GetConnectionString(self.Obj.DBAccess)

    def GetWWWMenuStruct(self, aobj):
        if aobj['SGIsDisabled']:
            return None
        if not self.wwwmenustruct.has_key(aobj.OID):
            awwwmenustruct = WWWMenuStruct(self, aobj)
            self.wwwmenustruct[aobj.OID] = awwwmenustruct
        return self.wwwmenustruct[aobj.OID]

    def GetSMTPServer(self, aoid):
        if not self.smtpserversbyid.has_key(aoid):
            asmtpserver = SMTPServer(self, aoid)
            self.smtpserversbyid[aoid] = asmtpserver
        return self.smtpserversbyid[aoid]

    def OpenConnection(self):
        try:
            self.aadoutil = ADOLibInit.ADOUtil(acominitialize=1, dbaccessobj=self.Obj.DBAccess)
        except:
            print '@@@ ERROR in OpenConnection: ' + self.Project + ' [' + str(self.OID) + '] : ' + str(self.ConnectionString)
            raise

    def CloseConnection(self):
        self.aadoutil.Close()

    def ProcessAddIns(self, uobj):
        while uobj:
            aaddin = MCRMBase.AddIn(self, uobj)
            self.addins.append(aaddin)
            uobj.Next()

    def ProcessAddInEvents(self, aeventname, akey='', dd=None, arepldict=None):
        lret = []
        wd = 0
        for aaddin in self.addins:
            if aaddin.CheckEvents(aeventname, akey):
                if not wd:
                    orepldict = self.repldict
                    if arepldict:
                        self.repldict = arepldict
                    if self.repldict is None:
                        self.repldict = {'this': self, 're': re, 'os': os, 'string': string, 'time': time, 'ICORUtil': ICORUtil, 'ADOLibInit': ADOLibInit, 'aadoutil': self.aadoutil, 'FilePathAsSystemPath': FilePathAsSystemPath, 'XMLUtil': XMLUtil, 'ICORSecurity': ICORSecurity, 'MCRMLib': MCRMLib, 'storageutil': storageutil}
                    if dd:
                        self.repldict.update(dd)
                    wd = 1
                atext = aaddin.ProcessEvents(aeventname, akey=akey)
                if atext:
                    lret.append(atext)
        if wd:
            if dd:
                for akey in dd.keys():
                    del self.repldict[akey]
            self.repldict = orepldict
        return '\n'.join(lret)

    def ProcessEvents(self, adict=None, aname='', leventschedulernames=None):
        ret = ''
        self.InitVariables()
        self.OpenConnection()
        try:
            for awwwmenustruct in self.wwwmenustruct.values():
                s = awwwmenustruct.ProcessEvents(adict=adict, aname=aname)
                if s:
                    ret = s
            if leventschedulernames:
                for aeventname in leventschedulernames:
                    self.ProcessAddInEvents(aeventname, dd=adict)
        finally:
            self.CloseConnection()
        return ret

    def Dump(self):
        print 'Project: %d' % (self.OID, )
        for awwwmenustruct in self.wwwmenustruct.values():
            awwwmenustruct.Dump()


class CMS:

    def __init__(self, alogname='', aconsole=0, acominitialize=0):
        self.COMInitialize = acominitialize
        self.Projects = {}
        if alogname:
            afname = startutil.GetLogTempFileName(alogname)
            self.log = startutil.MLog(afname, aconsole=aconsole)
            self.saveout = startutil.MemorySysOutWrapper(atimeinclude=0, fout2=afname, aconsole=0)
        else:
            self.log = None
            self.saveout = None
        self.UserParameters = {}

    def RestoreStdOut(self):
        if self.saveout:
            self.saveout.Restore()

    def SetByUID(self, auid):
        aclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        aobj = aclass.GetFirstObject()
        while aobj:
            if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', auid):
                aproject = self.GetProject(aobj)
            aobj.Next()

    def GetProject(self, aobj):
        if aobj['SGIsDisabled']:
            return
        if not self.Projects.has_key(aobj.OID):
            aproject = Project(self, aobj)
            if not aproject.Project:
                return
            self.Projects[aobj.OID] = aproject
        return self.Projects[aobj.OID]

    def ProcessEvents(self, adict=None, aname='', leventschedulernames=None):
        ret = ''
        if self.COMInitialize:
            import pythoncom
            pythoncom.CoInitialize()
        try:
            for aproject in self.Projects.values():
                try:
                    s = aproject.ProcessEvents(adict=adict, aname=aname, leventschedulernames=leventschedulernames)
                    if s:
                        ret = s
                except:
                    self.LogException()
        finally:
            if self.COMInitialize:
                pythoncom.CoUninitialize()
        return ret

    def Log(self, s=''):
        if self.log is None:
            print s
            return
        self.log.Log(s)

    def LogException(self, s=''):
        if self.log is None:
            print s
            import traceback
            traceback.print_exc()
            return
        self.log.LogException(s)

    def Dump(self):
        for aproject in self.Projects.values():
            aproject.Dump()

    def GetAllProjects(self, adump=0):
        pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
        try:
            pobj = pclass.GetFirstObject()
            while pobj:
                if pobj['SGIsDisabled']:
                    pobj.Next()
                    continue
                aproject = self.GetProject(pobj)
                if aproject is None:
                    pobj.Next()
                    continue
                wobj = pobj.WWWMenuStruct
                while wobj:
                    if wobj['SGIsDisabled']:
                        wobj.Next()
                        continue
                    awwwmenustruct = aproject.GetWWWMenuStruct(wobj)
                    if awwwmenustruct is None:
                        wobj.Next()
                        continue
                    try:
                        pass
                    except:
                        self.LogException()
                    wobj.Next()
                pobj.Next()
            if adump:
                self.Dump()
        except:
            self.LogException()
