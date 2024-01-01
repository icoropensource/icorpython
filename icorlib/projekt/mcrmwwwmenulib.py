# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mcrmlib as MCRMLib
import icorlib.projekt.mcrmutil as MCRMUtil
import icorlib.projekt.mcrmwwwmenucontext as MCRMWWWMenuContext
import icorlib.projekt.mcrmwwwmenumodel as MCRMWWWMenuModel
import icorlib.projekt.mcrmwwwmenuview as MCRMWWWMenuView
import icorlib.projekt.mcrmwwwmenudeploy as MCRMWWWMenuDeploy
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.projekt.msqlquery as MSQLQuery
import icorlib.projekt.mhtmlsqlgen2 as mhtmlsqlgen2
import icorlib.projekt.mcrmwwwmenu as MCRMWWWMenu
import icorlib.projekt.mcrmgeointerface as GeoInterface
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_NetBase_Utils_Slimmer as Slimmer
import appplatform.storageutil as storageutil
import appplatform.startutil as startutil
import icordbmain.dbaccess as dbaccess
import string
import re
import os
import cPickle
import time

try:
    import json
except:
    import simplejson as json

try:
    import jinja2
except:
    jinja2 = None


class TemplateFile(object):

    def __init__(self, fobj=None, aname=None, asource=None):
        if asource is None:
            self.OID = fobj.OID
            self.name = unicode(XMLUtil.CP1250_To_UTF8(fobj.Name), 'utf-8', 'ignore')
            self.kind = fobj.PageFileItemKind.Nazwa    # XML, PyHTML, text, HTML, Jinja
            self.source = unicode(XMLUtil.CP1250_To_UTF8(fobj.SourceData), 'utf-8', 'ignore')
        else:
            self.name = unicode(XMLUtil.CP1250_To_UTF8(aname), 'utf-8', 'ignore')
            self.source = unicode(XMLUtil.CP1250_To_UTF8(asource), 'utf-8', 'ignore')
        #print 'TemplateFile:',self.name,type(self.name),type(self.source)


if jinja2:

    class TemplateJinjaLoader(jinja2.BaseLoader):

        def __init__(self, abasetemplate):
            self.basetemplate = abasetemplate

        def get_source(self, environment, template):
            afile = self.basetemplate.files.get(template, None)
            if afile is None:
                raise jinja2.TemplateNotFound(template)
            # source = f.read().decode('utf-8')
            return afile.source, template, True
else:

    class TemplateJinjaLoader(object):

        def __init__(self, abasetemplate):
            self.basetemplate = abasetemplate

        def get_source(self, environment, template):
            return '', '', True


class TemplateJinja(object):

    def __init__(self, atobj, loids, block_start_string='{%', block_end_string='%}', variable_start_string='{$', variable_end_string='$}', tvars=None):
        self.TemplateObj = atobj
        self.files = {}
        for toid in loids[::-1]:
            tobj = self.TemplateObj.Class[toid]
            if not tobj:
                continue
            fobj = tobj.PageFileItems
            while fobj:
                atemplatefile = TemplateFile(fobj)
                self.files[atemplatefile.name] = atemplatefile
                fobj.Next()
        if tvars is None:
            tvars = {}
        aloader = TemplateJinjaLoader(self)
        if jinja2:
            self.jinja_env = jinja2.Environment(loader=aloader, block_start_string=block_start_string, block_end_string=block_end_string, variable_start_string=variable_start_string, variable_end_string=variable_end_string, auto_reload=False)
            self.jinja_env.filters['asPath'] = self.FilterAsPath
            self.jinja_env.globals.update(tvars)

    def FilterAsPath(self, value):
        return value.replace('\\', '/')

    def Process(self, afilename, atext, repldict=None):
        if repldict is None:
            repldict = {}
        atemplatefile = TemplateFile(aname=afilename, asource=atext)
        self.files[atemplatefile.name] = atemplatefile
        #print 'GETTEMPLATE:',atemplatefile.name,type(atemplatefile.name)
        atemplate = self.jinja_env.get_template(atemplatefile.name, globals=repldict)
        atext = atemplate.render()
        atext = atext.encode('cp1250', 'xmlcharrefreplace')
        return atext


class Alert:

    def __init__(self, aobj, awwwmenustruct):
        self.OID = aobj.OID
        self.Nazwa = aobj.Nazwa
        self.Grupa = aobj.Grupa
        self.WWWMenuStruct = awwwmenustruct
        self.XMLDataOIDs = []
        xobj = aobj.XMLData
        while xobj:
            self.XMLDataOIDs.append(xobj.OID)
            xobj.Next()


class EffectSkin:

    def __init__(self, aplugin, aobj):
        self.OID = aobj.OID
        self.Plugin = aplugin
        self.Nazwa = aobj.Nazwa
        self.Klucz = aobj.Klucz
        ehrobj = MCRMUtil.EventHelper(aobj, 'Events')
        self.Scripts = filter(lambda x: x and x[0] != '#', string.split(string.replace(ehrobj['OnGetScript'], chr(13), ''), '\n'))
        self.CSSFiles = filter(lambda x: x and x[0] != '#', string.split(string.replace(ehrobj['OnGetCSS'], chr(13), ''), '\n'))
        self.Scripts, self.CSSFiles = self.Plugin.WWWMenuStruct.ProcessScriptsCSS(self.Scripts, self.CSSFiles)
        self.OnGetScriptSource = ehrobj['OnGetScriptSource']
        self.OnGetCSSSource = ehrobj['OnGetCSSSource']


class Effect:

    def __init__(self, aobj, awwwmenustruct):
        self.OID = aobj.OID
        self.WWWMenuStruct = awwwmenustruct
        self.Scripts, self.CSSFiles = self.ProcessDependents(aobj, {})
        self.Scripts, self.CSSFiles = self.WWWMenuStruct.ProcessScriptsCSS(self.Scripts, self.CSSFiles)
        self.InitScript = aobj.InitScript
        self.processed = 0

    def Process(self):
        if self.processed:
            return
        self.processed = 1
        self.InitScript = ICORUtil.GetTextAsHTMLText(self.InitScript, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='EffectInit ' + str(self.OID))

    def NormalizeLines(self, l1, l2):
        lret = l1[:]
        for s in l2:
            if not s in lret:
                lret.append(s)
        return lret

    def ProcessDependents(self, aobj, dr):
        ls, lc = [], []
        if dr.has_key(aobj.OID):
            return ls, lc
        dr[aobj.OID] = 1
        lscripts = filter(lambda x: x and x[0] != '#', string.split(string.replace(aobj.URLScripts, chr(13), ''), '\n'))
        lcss = filter(lambda x: x and x[0] != '#', string.split(string.replace(aobj.URLCSSFiles, chr(13), ''), '\n'))
        dobj = aobj.DependsOn
        while dobj:
            ls1, lc1 = self.ProcessDependents(dobj, dr)
            ls = ls + ls1
            lc = lc + lc1
            dobj.Next()
        lscripts = self.NormalizeLines(ls, lscripts)
        lcss = self.NormalizeLines(lc, lcss)
        return lscripts, lcss


class WWWTemplate:

    def __init__(self, aplugin, aobj):
        self.Plugin = aplugin
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.Events = []
        self.EventsDict = {}
        eobj = aobj.TemplateEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, aevent.Key)
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()
        self.ManualEffects = aobj['SGManualEffects', mt_Integer]
        self.Effects = []
        eobj = aobj.Effects
        while eobj:
            aeffect = self.Plugin.WWWMenuStruct.GetEffect(eobj)
            self.Effects.append(aeffect)
            eobj.Next()
        self.TemplateVars = ICORUtil.ParseVars(aobj.TemplateVars, {})
        self.thisEventName, self.thisEventKey = '', ''
        self.aIsDerived = None
        self.aIsGlobalDerived = None

    def IsDerived(self, aglobal=0):
        if aglobal and self.aIsGlobalDerived is not None:
            return self.aIsGlobalDerived
        elif self.aIsDerived is not None:
            return self.aIsDerived
        if aglobal:
            self.aIsGlobalDerived = 0
            levents = []
            for aplugin in self.Plugin.WWWMenuStruct.Plugins:
                levents.append(aplugin.Events)
        else:
            self.aIsDerived = 0
            levents = [self.Plugin.Events, ]
        for aevents in levents:
            for aevent in aevents:
                if aevent.Name == self.thisEventName and aevent.Key == self.thisEventKey:
                    if aglobal:
                        self.aIsGlobalDerived = 1
                    else:
                        self.aIsDerived = 1
                    break
        if aglobal:
            return self.aIsGlobalDerived
        return self.aIsDerived

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        write = None
        if self.Plugin.WWWMenuStruct.repldict.has_key('Response'):
            write = self.Plugin.WWWMenuStruct.repldict['Response'].write
        otemplate = self.Plugin.WWWMenuStruct.repldict.get('Template', None)
        self.Plugin.WWWMenuStruct.repldict['Template'] = self
        for aevent in self.EventsDict.get((aeventname, akey), []):
            self.thisEventName, self.thisEventKey = aeventname, akey
            oevent = self.Plugin.WWWMenuStruct.repldict.get('thisEvent', None)
            self.Plugin.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.Plugin.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='TemplateEvent ' + str(self.OID) + ' ' + aeventname + ' ' + str(aevent.OID))
            self.Plugin.WWWMenuStruct.repldict['thisEvent'] = oevent
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        self.Plugin.WWWMenuStruct.repldict['Template'] = otemplate
        return '\n'.join(lret)

    def ProcessHeaderLines(self, amanualeffects=0, anowrite=0, aheaderlines=None, anoregister=0):
        lscripts, lcss = [], []
        if not amanualeffects and self.ManualEffects:
            return lscripts, lcss
        write = None
        if self.Plugin.WWWMenuStruct.repldict.has_key('Response'):
            write = self.Plugin.WWWMenuStruct.repldict['Response'].write
        for aeffect in self.Effects:
            if not anoregister:
                self.Plugin.WWWMenuStruct.RegisterEffect(aeffect)
            for s in aeffect.Scripts:
                w = self.Plugin.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lscripts.append(s)
                    if write and not anowrite:
                        write(s + '\n')
            for s in aeffect.CSSFiles:
                w = self.Plugin.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lcss.append(s)
                    if write and not anowrite:
                        write(s + '\n')
        return lscripts, lcss


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


class APIMethodParameter:

    def __init__(self, aobj):
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.NazwaID = aobj.NazwaID
        self.IsObligatory = aobj['SGIsObligatory', mt_Integer]
        self.Dokumentacja = aobj.Dokumentacja
        tobj = aobj.ParameterType
        self.Type = tobj.Nazwa
        self.TypeDescription = tobj.Opis
        self.TypeRegex = tobj.Regex
        self.Size = tobj.Rozmiar
        self.DictValues = []


class APIMethod:

    def __init__(self, alibrary, aobj):
        self.APILibrary = alibrary
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.NazwaID = aobj.NazwaID
        self.Grupa = aobj.Grupa
        self.GrupaID = ICORUtil.MakeIdentifier(self.Grupa, asimple=1)
        self.IsCached = aobj['SGIsCached', mt_Integer]
        self.IsDisabled = aobj['SGIsDisabled', mt_Integer]
        self.Dokumentacja = aobj.Dokumentacja
        self.Events = []
        self.EventsDict = {}
        eobj = aobj.MethodEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, '')
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()
        self.Parameters = []
        eobj = aobj.Parameters
        while eobj:
            aparameter = APIMethodParameter(eobj)
            self.Parameters.append(aparameter)
            eobj.Next()

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        if self.IsDisabled:
            return ''
        self.APILibrary.WWWMenuStruct.repldict['APIMethod'] = self
        aoldeventcontext = self.APILibrary.WWWMenuStruct.repldict.get('EventContext', None)
        self.APILibrary.WWWMenuStruct.repldict['EventContext'] = aeventcontext
        write = None
        if self.APILibrary.WWWMenuStruct.repldict.has_key('Response'):
            write = self.APILibrary.WWWMenuStruct.repldict['Response'].write
        for aevent in self.EventsDict.get((aeventname, akey), []):
            oevent = self.APILibrary.WWWMenuStruct.repldict.get('thisEvent', None)
            self.APILibrary.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.APILibrary.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='APIMethodEvent ' + str(self.OID) + ' ' + aevent.Name + ' ' + str(aevent.OID))
            self.APILibrary.WWWMenuStruct.repldict['thisEvent'] = oevent
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        self.APILibrary.WWWMenuStruct.repldict['APIMethod'] = None
        self.APILibrary.WWWMenuStruct.repldict['EventContext'] = aoldeventcontext
        return '\n'.join(lret)


class APILibrary:

    def __init__(self, astruct, aobj):
        self.WWWMenuStruct = astruct
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.Dokumentacja = aobj.Dokumentacja
        self.Methods = []
        eobj = aobj.Metody
        while eobj:
            ametoda = APIMethod(self, eobj)
            self.Methods.append(ametoda)
            eobj.Next()


class WWWPlugin:

    def __init__(self, astruct, aobj, achapter=None):
        self.WWWMenuStruct = astruct
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Chapter = achapter
        self.Nazwa = aobj.Nazwa
        self.IsDisabled = aobj['SGIsDisabled', mt_Integer]
        dtvars = {}
        self.Templates = []
        tobj = aobj.Template
        while tobj:
            atemplate = WWWTemplate(self, tobj)
            self.Templates.append(atemplate)
            dtvars.update(atemplate.TemplateVars)
            tobj.Next()
        self.Events = []
        self.EventsDict = {}
        eobj = aobj.PluginEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, aevent.Key)
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()
        self.ManualEffects = aobj['SGManualEffects', mt_Integer]
        self.Effects = []
        eobj = aobj.Effects
        while eobj:
            aeffect = self.WWWMenuStruct.GetEffect(eobj)
            self.Effects.append(aeffect)
            eobj.Next()
        self.Skins = []
        sobj = aobj.Skin
        while sobj:
            askin = WWWPluginSkin(self, sobj)
            self.Skins.append(askin)
            sobj.Next()
        self.Extensions = []
        xobj = aobj.Extensions
        while xobj:
            aextension = WWWPluginExtension(self, xobj)
            self.Extensions.append(aextension)
            xobj.Next()
        self.EffectSkins = []
        sobj = aobj.EffectSkins
        while sobj:
            aeffectskin = EffectSkin(self, sobj)
            self.EffectSkins.append(aeffectskin)
            sobj.Next()


#      print 'PLUGIN:',self.Nazwa,self.OID
#      if self.Chapter:
#         print 'CHAPTER',self.Chapter.OID
#      print 'VARS:',aobj.PluginVars
        st = storageutil.TextReplaceByMarkup(aobj.PluginVars, self.WWWMenuStruct.StructVars, sm1='{^', sm2='^}')
        self.PluginVars = ICORUtil.ParseVars(st, dtvars)
        self.PluginVarsLastModification = aobj.Class.PluginVars.GetValueLastModified(aobj.OID)
        self.AccessLevelView = aobj.Class.AccessLevelView[aobj.OID]
        self._DataStore = None

    def ProcessExtensions(self, aeventname, akey='', adict=None):
        ret = ''
        if self.Extensions:
            write = None
            if self.WWWMenuStruct.repldict.has_key('Response'):
                write = self.WWWMenuStruct.repldict['Response'].write
            aplugindict = self.WWWMenuStruct.repldict.get('PluginDict', None)
            if adict is None:
                adict = {}
            self.WWWMenuStruct.repldict['PluginDict'] = adict
            for aextension in self.Extensions:
                if aextension.Klucz != akey:
                    continue
                atext = ''
                if aeventname == 'OnExtensionExecute':
                    atext = aextension.OnExtensionExecute
                if atext:
                    oevent = self.WWWMenuStruct.repldict.get('thisExtension', None)
                    self.WWWMenuStruct.repldict['thisExtension'] = self
                    atext = ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='PluginExtension ' + str(self.OID) + ' ' + aeventname + ' ' + str(aextension.OID))
                    self.WWWMenuStruct.repldict['thisExtension'] = oevent
                    ret = ret + atext
                    if write is not None:
                        write(atext)
            if aplugindict is None:
                self.WWWMenuStruct.repldict['PluginDict'] = None
                del self.WWWMenuStruct.repldict['PluginDict']
            else:
                self.WWWMenuStruct.repldict['PluginDict'] = aplugindict
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
                ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, aglobaldict=1, ascriptname='ExtensionInclude ' + str(self.OID) + ' ' + akey + ' ' + str(aextension.OID))
                self.WWWMenuStruct.repldict['thisExtension'] = oevent

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
                    atext = ICORUtil.GetTextAsHTMLText(atext, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='PluginSkin ' + str(self.OID) + ' ' + aeventname + ' ' + str(askin.OID))
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

    def CheckEvents(self, aeventname, akey=''):
        for atemplate in self.Templates:
            if atemplate.EventsDict.has_key((aeventname, akey)):
                return 1
        if self.EventsDict.has_key((aeventname, akey)):
            return 1
        return 0

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        if self.IsDisabled:
            return ''
        oplugin = self.WWWMenuStruct.repldict.get('Plugin', None)
        self.WWWMenuStruct.repldict['Plugin'] = self
        aoldeventcontext = self.WWWMenuStruct.repldict.get('EventContext', None)
        self.WWWMenuStruct.repldict['EventContext'] = aeventcontext
        for atemplate in self.Templates:
            atext = atemplate.ProcessEvents(aeventname, akey=akey, aeventcontext=aeventcontext)
            if atext:
                lret.append(atext)
        write = None
        if self.WWWMenuStruct.repldict.has_key('Response'):
            write = self.WWWMenuStruct.repldict['Response'].write
        for aevent in self.EventsDict.get((aeventname, akey), []):
            oevent = self.WWWMenuStruct.repldict.get('thisEvent', None)
            self.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='PluginEvent ' + str(self.OID) + ' ' + aevent.Name + ' ' + str(aevent.OID))
            self.WWWMenuStruct.repldict['thisEvent'] = oevent
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        self.WWWMenuStruct.repldict['Plugin'] = oplugin
        self.WWWMenuStruct.repldict['EventContext'] = aoldeventcontext
        return '\n'.join(lret)

    def ProcessHeaderLines(self, amanualeffects=0, anowrite=0, aheaderlines=None, anoregister=0):
        lscripts, lcss = [], []
        if self.IsDisabled:
            return lscripts, lcss
        if not amanualeffects and self.ManualEffects:
            return lscripts, lcss
        for atemplate in self.Templates:
            lscripts2, lcss2 = atemplate.ProcessHeaderLines(amanualeffects=amanualeffects, anowrite=anowrite, aheaderlines=aheaderlines, anoregister=anoregister)
            lscripts.extend(lscripts2)
            lcss2.extend(lcss2)
        write = None
        if self.WWWMenuStruct.repldict.has_key('Response'):
            write = self.WWWMenuStruct.repldict['Response'].write
        for aeffect in self.Effects:
            if not anoregister:
                self.WWWMenuStruct.RegisterEffect(aeffect)
            for s in aeffect.Scripts:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lscripts.append(s)
                    if write and not anowrite:
                        write(s + '\n')
            for s in aeffect.CSSFiles:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lcss.append(s)
                    if write and not anowrite:
                        write(s + '\n')
        for aeffectskin in self.EffectSkins:
            if not anoregister:
                self.WWWMenuStruct.RegisterEffectSkin(aeffectskin)
            for s in aeffectskin.Scripts:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lscripts.append(s)
                    if write and not anowrite:
                        write(s + '\n')
            for s in aeffectskin.CSSFiles:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lcss.append(s)
                    if write and not anowrite:
                        write(s + '\n')
        return lscripts, lcss

    def LoadData(self):
        if self._DataStore is None:
            self._DataStore = {}
            ss = self.Obj['DataStore']
            if ss:
                self._DataStore = cPickle.loads(ss)
        return self._DataStore

    def SaveData(self, avalue):
        self._DataStore = avalue
        self.Obj['DataStore'] = cPickle.dumps(avalue)


class WWWMenuChapterCSS:

    def __init__(self, aoid, amedia=None, atitle='', aisalternate=0, ahref='', arole='', aisdisabled=0, akey='', aname=''):
        self.OID = aoid
        if amedia:
            self.Media = amedia
        else:
            self.Media = ['all', ]
        self.Title = atitle
        self.IsAlternate = aisalternate
        self.Role = arole
        self.IsDisabled = aisdisabled
        self.Key = akey
        if aname:
            self.Name = aname
        else:
            self.Name = 'css_%d' % self.OID
        if ahref:
            self.HRef = ahref
        else:
            self.HRef = 'css/style_%d.css' % aoid

    def AsHTML(self):
        salternate = ''
        if self.IsAlternate:
            salternate = 'alternate '
        sdisabled = ''
        if self.IsDisabled:
            sdisabled = ' disabled'
        stoggle = ''
        skey = ''
        if self.Key:
            stoggle = ' data-toggle="1"'
            skey = ' data-key="%s"' % (self.Key, )
        stitle = ''
        if self.Title:
            stitle = ' title="%s"' % (XMLUtil.GetAsXMLString(self.Title), )
        aname = self.Name.replace('"', "'")
        return '<link rel="%sstylesheet" type="text/css" media="%s" href="%s"%s%s%s%s data-name="%s">\n' % (salternate, string.join(self.Media, ', '), self.HRef, stitle, stoggle, skey, sdisabled, aname)


class WWWMenuFile:

    def __init__(self, afilename='', atype='', atext='', aencoding=''):
        self.FileName = afilename
        self.Type = atype
        self.Text = atext
        self.AllowWrite = 1
        self.Encoding = aencoding

    def Write(self):
        if self.AllowWrite:
            fout = ICORUtil.OpenText(self.FileName, 'w', aencoding=self.Encoding)
            #         if self.Encoding=='utf-8':
            #            fout.write(XMLUtil.CP1250_To_UTF8(self.Text))
            #         else:
            fout.write(self.Text)
            fout.close()
            return 1
        return 0


class WWWMenuChapter:

    def __init__(self, astruct, aparent, robj, alevel):
        self.WWWMenuStruct = astruct
        self.Parent = aparent
        self.OID = robj.OID
        self.Obj = robj.AsObject()
        self.Caption = robj.Naglowek
        self.CaptionMenu = robj.NaglowekMenu
        if self.CaptionMenu == '':
            self.CaptionMenu = self.Caption
        if self.Caption == '':
            self.Caption = self.CaptionMenu
        if self.CaptionMenu == '':
            self.CaptionMenu = '---==*==---'
        self.HRef = robj.SGHref
        self.HRefApp = robj.SGHrefApp
        self.HRefParams = robj.SGHrefParams
        self.Target = robj.SGTarget
        self.IsMenuDisabled = robj['SGIsMenuDisabled', mt_Integer]
        self.IsRSSDisabled = robj['RSSDisabled', mt_Integer]
        zobj = robj.RodzajZaglebienia
        if zobj:
            self.RodzajZaglebienia = zobj['IDZaglebienia', mt_Integer]    # 1-full submenu, 2-subchapters
        elif self.Parent is not None:
            self.RodzajZaglebienia = self.Parent.RodzajZaglebienia
        else:
            self.RodzajZaglebienia = 0
            nobj = robj.NadRozdzial
            while nobj:
                if self.WWWMenuStruct.chapters_rodzajzaglebien.has_key(nobj.OID):
                    self.RodzajZaglebienia = self.WWWMenuStruct.chapters_rodzajzaglebien[nobj.OID]
                    break
                zobj = nobj.RodzajZaglebienia
                if zobj:
                    self.RodzajZaglebienia = zobj['IDZaglebienia', mt_Integer]    # 1-full submenu, 2-subchapters
                    self.WWWMenuStruct.chapters_rodzajzaglebien[nobj.OID] = self.RodzajZaglebienia
                    break
                nobj = nobj.NadRozdzial
        self.WWWMenuStruct.chapters_rodzajzaglebien[self.OID] = self.RodzajZaglebienia
        self.Grupa = ''
        zobj = robj.GrupaRozdzialow
        if zobj:
            self.Grupa = zobj.Nazwa
        self.Level = alevel
        self.SubChapters = []
        self.ExtraTables = []
        tobj = robj.TabelaZrodlowa
        if tobj:
            self.TableID = tobj.OID
            self.TableName = tobj.Nazwa
            tobj.Next()
            while tobj:
                self.ExtraTables.append(tobj.OID)
                tobj.Next()
        else:
            self.TableID = -1
            self.TableName = ''
        if self.Parent is not None:
            self.Parent.SubChapters.append(self)
            if not self.Grupa:
                self.Grupa = self.Parent.Grupa
        self._visiblesubchapters = None

        self.Events = []
        self.EventsDict = {}
        eobj = robj.ChapterEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, aevent.Key)
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()

        uobj = robj.Plugins
        l = []
        while uobj:
            aplugin = WWWPlugin(self.WWWMenuStruct, uobj, achapter=self)
            l.append([uobj['SGTabID'], aplugin.Nazwa, aplugin])
            uobj.Next()
        l.sort()
        self.Plugins = []
        for aid, anazwa, aplugin in l:
            self.Plugins.append(aplugin)

        self.Effects = []
        eobj = robj.Effects
        while eobj:
            aeffect = self.WWWMenuStruct.GetEffect(eobj)
            self.Effects.append(aeffect)
            eobj.Next()

        self.EffectSkins = []
        sobj = robj.EffectSkins
        while sobj:
            aeffectskin = EffectSkin(self, sobj)
            self.EffectSkins.append(aeffectskin)
            sobj.Next()

        self.Models = MCRMWWWMenuModel.WWWMenuChapterModels(self.Obj)
        self.Views = MCRMWWWMenuView.WWWMenuChapterPresentation(self.Obj)

        self.ChapterParams = ICORUtil.ParseVars(robj.ChapterParams, {})
        self.WWWMenuStruct.ProcessEventsInternal('OnCMSChapterInit', dd={'MenuChapterOID': self.OID, 'thisChapter': self})

    def GetHRef(self):
        ahref = 'chapter_%d.asp' % self.OID
        if self.HRef:
            ahref = self.HRef
            if ahref[:1] == '#':
                atargetoid = ahref[1:]
                ahref = 'chapter_%s.asp' % atargetoid
        if self.HRefParams:
            ahref = ICORUtil.URLAddParam(ahref, self.HRefParams)
        return ahref

    def ProcessEventsInternal(self, aeventname, akey='', aeventcontext=''):
        lret = []
        #if self.IsMenuDisabled:
        #   return ''
        aoldchapter = self.WWWMenuStruct.repldict.get('Chapter', None)
        self.WWWMenuStruct.repldict['Chapter'] = self
        aoldeventcontext = self.WWWMenuStruct.repldict.get('EventContext', None)
        self.WWWMenuStruct.repldict['EventContext'] = aeventcontext
        write = None
        if self.WWWMenuStruct.repldict.has_key('Response'):
            write = self.WWWMenuStruct.repldict['Response'].write
        for aevent in self.EventsDict.get((aeventname, akey), []):
            oevent = self.WWWMenuStruct.repldict.get('thisEvent', None)
            self.WWWMenuStruct.repldict['thisEvent'] = aevent
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='ChapterEvent ' + str(self.OID) + ' ' + aevent.Name + ' ' + str(aevent.OID))
            self.WWWMenuStruct.repldict['thisEvent'] = oevent
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        self.WWWMenuStruct.repldict['Chapter'] = aoldchapter
        self.WWWMenuStruct.repldict['EventContext'] = aoldeventcontext
        return '\n'.join(lret)

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        for aplugin in self.Plugins:
            if aplugin.CheckEvents(aeventname, akey):
                atext = aplugin.ProcessEvents(aeventname, akey=akey, aeventcontext=aeventcontext)
                if atext:
                    lret.append(atext)
        atext = self.ProcessEventsInternal(aeventname, akey, aeventcontext)
        if atext:
            lret.append(atext)
        return '\n'.join(lret)

    def ProcessHeaderLines(self, amanualeffects=0, anowrite=0, aheaderlines=None, anoregister=0):
        for aplugin in self.Plugins:
            aplugin.ProcessHeaderLines(amanualeffects=amanualeffects, anowrite=anowrite, aheaderlines=aheaderlines, anoregister=anoregister)

        lscripts, lcss = [], []
        write = None
        if self.WWWMenuStruct.repldict.has_key('Response'):
            write = self.WWWMenuStruct.repldict['Response'].write
        for aeffect in self.Effects:
            if not anoregister:
                self.WWWMenuStruct.RegisterEffect(aeffect)
            for s in aeffect.Scripts:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lscripts.append(s)
                    if write and not anowrite:
                        write(s + '\n')
            for s in aeffect.CSSFiles:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lcss.append(s)
                    if write and not anowrite:
                        write(s + '\n')
        for aeffectskin in self.EffectSkins:
            if not anoregister:
                self.WWWMenuStruct.RegisterEffectSkin(aeffectskin)
            for s in aeffectskin.Scripts:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lscripts.append(s)
                    if write and not anowrite:
                        write(s + '\n')
            for s in aeffectskin.CSSFiles:
                w = self.WWWMenuStruct.RequireHeaderLine(s, amanual=amanualeffects, aheaderlines=aheaderlines)
                if w:
                    lcss.append(s)
                    if write and not anowrite:
                        write(s + '\n')
        return lscripts, lcss

    def HasVisibleSubChapters(self):
        if self.RodzajZaglebienia:
            return 0
        if self._visiblesubchapters is None:
            self._visiblesubchapters = 0
            for achapter in self.SubChapters:
                if not achapter.IsMenuDisabled and achapter.Grupa == self.Grupa:
                    self._visiblesubchapters = 1
                    break
        return self._visiblesubchapters

    def HasChild(self, aoid, alevel=99999):
        achild = self.WWWMenuStruct.chapters_byid[aoid]
        if achild is None:
            return 0
        return achild.HasParent(self.OID, alevel)

    def HasParent(self, aoid, alevel=99999):
        achapter = self
        if type(aoid) == type(1):
            aoid = [aoid, ]
        while achapter is not None and alevel > 0:
            if achapter.OID in aoid:
                return 1
            achapter = achapter.Parent
            alevel = alevel - 1
        return 0

    def GetRecursiveParameter(self, aparameter, adefault=None):
        ret = adefault
        achapter = self
        while achapter is not None:
            if achapter.ChapterParams.has_key(aparameter):
                ret = achapter.ChapterParams[aparameter]
            achapter = achapter.Parent
        return ret


class WWWMenuStruct(MCRMLib.MCRMItemBase):

    def Process(self, sobj, awritedisabled=0):
        self.ClassItem = sobj.Class
        self.OID = sobj.OID
        self.MenuStructObj = sobj.AsObject()
        self.WriteDisabled = awritedisabled
        self.InfoTablesSufix = sobj['InfoTablesSufix', mt_Integer]
        self.IgnoreResponse = 0
        eobj = sobj.DefaultEncoding
        if eobj:
            self.DefaultEncoding = eobj.IANAName.lower()
            self.DefaultCodePage = eobj.CodePage
        self.WSBaseDirectory = FilePathAsSystemPath(sobj.AppPaths.SciezkaAplikacji)
        if self.WSBaseDirectory[-1:] not in ['/', '\\']:
            self.WSBaseDirectory = self.WSBaseDirectory + '/'
        for rdir in ['api', 'css', 'fonts', 'images', 'img', 'inc', 'files', 'js', 'lib', 'rss', 'xml', 'xsl']:
            try:
                if not os.path.exists(self.WSBaseDirectory + rdir):
                    os.makedirs(self.WSBaseDirectory + rdir)
            except:
                print '$$ ERROR creating directory: ' + self.WSBaseDirectory + rdir
        self.IndexBaseDirectory = sobj.AppPaths.IndexServerBaseDirectory
        if not self.IndexBaseDirectory:
            self.IndexBaseDirectory = self.WSBaseDirectory
        if self.IndexBaseDirectory[-1:] not in ['/', '\\']:
            self.IndexBaseDirectory = self.IndexBaseDirectory + '/'
        self.IndexBaseDirectory = string.replace(self.IndexBaseDirectory, '/', '\\')
        self.PageTemplateObj = sobj.PageTemplate
        self.MetaTemplateObj = sobj.MetaTemplate
        self.ConnectionString = ''
        dobj = sobj.DBAccess
        if dobj:
            self.ConnectionString = dbaccess.GetConnectionString(dobj)
        self.ConnectionStringPublic = self.CRM.ConnectionString
        dobj = sobj.DBAccessPublic
        if dobj:
            self.ConnectionStringPublic = dbaccess.GetConnectionString(dobj)
        self.OptimizationLevel = 0
        oobj = sobj.PoziomOptymalizacji
        if oobj:
            self.OptimizationLevel = oobj['OptLevel', mt_Integer]
        self.CacheGen = {}
        self.pagetemplateoids = {}
        self.pagetemplatecss = {}
        self.pagetemplatecssmedia = {}
        self.pagetemplatecsskeys = {}
        self.pagetemplatecssattrs = {}
        self.pagetemplatedoctype = {}
        self.IndexServerCatalog = sobj.AppPaths.IndexServerCatalog
        self.VirtualRoot = sobj.AppPaths.KatalogWirtualny
        self.CGIPath = sobj.AppPaths.SciezkaCGI
        self.InternalWWWAddress = sobj.AppPaths.AdresWewnetrznyWWW
        if not self.InternalWWWAddress:
            self.InternalWWWAddress = 'http://127.0.0.1'
        self.ExternalWWWAddress = sobj.AppPaths.AdresZewnetrznyWWW
        if self.ExternalWWWAddress[-1:] == '/':
            self.ExternalWWWAddress = self.ExternalWWWAddress[:-1]
        if self.CGIPath == '':
            self.CGIPath = 'chapter_#.asp'
        if self.VirtualRoot:
            if self.VirtualRoot[-1:] != '/':
                self.VirtualRoot = self.VirtualRoot + '/'
            if self.VirtualRoot[:1] != '/':
                self.VirtualRoot = '/' + self.VirtualRoot
        smp = sobj.AppPaths.StronaGlowna
        self.chapters_rodzajzaglebien = {}
        self.MainPage = []
        if smp:
            sl1 = string.split(smp, ',')
            for ss in sl1:
                ss = string.strip(ss)
                if not ss:
                    continue
                sl2 = string.split(ss, ':')
                if len(sl2) == 1:
                    self.MainPage.append(string.strip(ss))
                elif len(sl2) == 2:
                    self.MainPage.append([string.strip(sl2[0]), string.strip(sl2[1])])
        self.WWWMenuContext = MCRMWWWMenuContext.WWWMenuContext
        self.chapters = []
        self.chapters_byid = {}
        self._TemplateXML = {}
        self._TemplateJinja = {}
        self.IsFullChaptersIterate = 0
        self.IsIgnoreChapterGroupsIterate = 0
        #      self.Table_ChaptersID=None
        self.Table_RejestrZmian = None
        self.Table_MenuChapters = None
        self.Table_MenuCounterChapter = None
        self.StructVars = ICORUtil.ParseVars(sobj.StructVars, {'aCgiScriptPath': '', 'aFileUploadsOrderInChapters': 'Description,Name', 'aHTTPFileUploadsOrderInChapters': 'Description,Name'})
        self.Dist_Mode = self.StructVars.get('aDistMode', startutil.appconfig.Dist_Mode)
        self.XMLOutputDirName = self.StructVars.get('aXMLOutputDirName', 'xml')
        self.XMLOutputByChapter = int(self.StructVars.get('aXMLOutputByChapter', '0'))
        self.NoIndexFiles = int(self.StructVars.get('aNoIndexFiles', '0'))
        self.DBSession = int(self.StructVars.get('aDBSession', '1'))
        self.RSSOutputDirName = self.StructVars.get('aRSSOutputDirName', 'rss')
        self.RSSOutputByChapter = int(self.StructVars.get('aRSSOutputByChapter', '0'))

        self.RSSExists = 0
        if sobj.RSSInfo:
            self.RSSExists = 1

        self.Effects = {}

        dtableoids = {}
        l = []
        uobj = sobj.Plugins
        while uobj:
            aplugin = WWWPlugin(self, uobj)
            l.append([uobj['SGTabID'], aplugin.Nazwa, aplugin])
            for avar in aplugin.PluginVars.keys():
                if string.find(avar, 'aTableOID') == 0:
                    ls = string.split(aplugin.PluginVars[avar], ',')
                    for atid in ls:
                        try:
                            dtableoids[int(atid)] = 1
                        except ValueError:
                            pass
            uobj.Next()
        l.sort()
        self.Plugins = []
        for aid, anazwa, aplugin in l:
            self.Plugins.append(aplugin)
        tobj = sobj.TabeleZrodlowe
        while tobj:
            dtableoids[tobj.OID] = 1
            tobj.Next()
        for toid in dtableoids.keys():
            l = self.CRM.pluginsources_tables.get(toid, [])
            l.append(self)
            self.CRM.pluginsources_tables[toid] = l
            btable = self.CRM.sourcetables[toid]

        self.Alerts = []
        lobj = sobj.Alerty
        while lobj:
            aalert = Alert(lobj, self)
            self.Alerts.append(aalert)
            lobj.Next()

        self.APILibraries = []
        eobj = sobj.APILibraries
        while eobj:
            aapilibrary = APILibrary(self, eobj)
            self.APILibraries.append(aapilibrary)
            eobj.Next()

        self.repldict = None
        self.ThisChapter = None

        self.deployscenarios = []
        dsobj = sobj.AppPaths.DeployScenario
        while dsobj:
            adeploy = MCRMWWWMenuDeploy.DeployScenario(self, dsobj)
            self.deployscenarios.append(adeploy)
            dsobj.Next()
        self.jslibmanagers = []
        dsobj = sobj.AppPaths.JSLibManager
        while dsobj:
            ajslibmanager = MCRMWWWMenuDeploy.JSLibManager(self, dsobj)
            self.jslibmanagers.append(ajslibmanager)
            dsobj.Next()

        self.InitVariables()
        self.ProcessEvents('OnCMSInit', 'system')
        self.ProcessEvents('OnCMSInit', 'database')
        self.ProcessEvents('OnCMSInit', 'tables')
        self.ProcessEvents('OnCMSInit')

    def InitVariables(self):
        self.ChapterLevelFunc = None
        self.ChapterLevelMulti = 0
        self.SubChaptersCheck = 0
        self.ChapterGroup = ''
        self.IsFullChaptersIterate = 0
        self.IsIgnoreChapterGroupsIterate = 0
        self.requiredLines = {}
        self.plugineventsexistscache = {}

    def OnWriteASPText(self, atext):
        if self.DBSession:
            atext = MCRMUtil.ChangeDession(atext)
        return atext

    def ProcessScriptsCSS(self, lscripts, lcss):
        if self.OptimizationLevel:
            l = []
            for apath in lscripts:
                if string.find(apath, '/icorlib/') == 0 and string.find(apath, '.min.js') < 0:
                    fpath = FilePathAsSystemPath(string.replace(apath, '/icorlib/', '%ICOR%/WWWData/_icorlib/'))
                    fpath = string.replace(fpath, '.js', '.min.js')
                    if os.path.exists(fpath):
                        apath = string.replace(apath, '.js', '.min.js')
                l.append(apath)
            lscripts = l
            l = []
            for apath in lcss:
                if string.find(apath, '/icorlib/') == 0 and string.find(apath, '.min.css') < 0:
                    fpath = FilePathAsSystemPath(string.replace(apath, '/icorlib/', '%ICOR%/WWWData/_icorlib/'))
                    fpath = string.replace(fpath, '.css', '.min.css')
                    if os.path.exists(fpath):
                        apath = string.replace(apath, '.css', '.min.css')
                l.append(apath)
            lcss = l
        l = []
        for s in lscripts:
            if s[:1] != '<':
                s = '<script type="text/javascript" src="' + s + '"></script>'
            l.append(s)
        lscripts = l
        l = []
        for s in lcss:
            if s[:1] != '<':
                amedia = 'screen'
                lls = s.split('@')
                if len(lls) == 2:
                    amedia, s = lls
                s = '<link rel="stylesheet" href="' + s + '" type="text/css" media="' + amedia + '">'
            l.append(s)
        lcss = l
        return lscripts, lcss

    def PrepareChapterGroups(self, sobj):
        gobj = sobj.GrupyRozdzialow
        while gobj:
            hobj = gobj.Rozdzialy
            while hobj:
                if not hobj['SGIsMenuDisabled'] and not self.chapters_byid.has_key(hobj.OID):
                    self.PrepareChapters(hobj)
                hobj.Next()
            gobj.Next()

    def ProcessChapterGroups(self, sobj):
        gobj = sobj.GrupyRozdzialow
        self.chaptersgroups = {}
        while gobj:
            l = []
            hobj = gobj.Rozdzialy
            while hobj:
                if not hobj['SGIsMenuDisabled']:
                    achapter = self.chapters_byid[hobj.OID]
                    l.append(achapter)
                hobj.Next()
            self.chaptersgroups[gobj.Nazwa] = l
            gobj.Next()

    def OpenText(self, afilename, amode='rb', aencoding=None, aerrors='xmlcharrefreplace', abuffering=1):
        if aencoding is None:
            aencoding = self.DefaultEncoding
        return ICORUtil.OpenText(afilename, amode=amode, aencoding=aencoding, aerrors=aerrors, abuffering=abuffering)

    def WriteSingle(self, adirectory, robj):
        self.InitVariables()
        sobj = self.ClassItem[self.OID]
        self.MenuStructObj = sobj
        self.ThisChapter = None
        cobj = sobj.Rozdzialy
        while cobj:
            #         if not cobj['SGIsMenuDisabled']:
            self.PrepareChapters(cobj)
            cobj.Next()
        self.PrepareChapterGroups(sobj)
        self.ProcessChapterGroups(sobj)
        self.WriteChapter(robj, anorecur=1)

    def Write(self, adirectory, adisablechaptercreate=0):
        self.InitVariables()
        sobj = self.ClassItem[self.OID]
        self.MenuStructObj = sobj
        self.WriteDirectory = adirectory
        self.ThisChapter = None
        if self.WriteDisabled:
            print '*** WWWMenuStruct is disabled for write: ' + str(self.OID)
            self.ProcessEvents('OnCMSWrite')
            return
        rrefs = self.ClassItem.Rozdzialy.GetRefList(self.OID)
        rrefs.sort(self.ClassItem.Rozdzialy.ClassOfType.SGTabID)
        self.ClassItem.Rozdzialy[self.OID] = rrefs.AsString()
        if not adisablechaptercreate:
            robj = sobj.Rozdzialy
            while robj:
                if not robj['SGIsMenuDisabled']:
                    self.PrepareChapters(robj)
                robj.Next()
            self.PrepareChapterGroups(sobj)
            self.ProcessChapterGroups(sobj)
            robj = sobj.Rozdzialy
            while robj:
                if not robj['SGIsMenuDisabled']:
                    self.WriteChapter(robj, acheckdisabled=1)
                robj.Next()
            gobj = sobj.GrupyRozdzialow
            while gobj:
                hobj = gobj.Rozdzialy
                while hobj:
                    if not hobj['SGIsMenuDisabled']:
                        self.WriteChapter(hobj, acheckdisabled=1)
                    hobj.Next()
                gobj.Next()
        self.ProcessEvents('OnCMSWrite')

    def PrepareChapters(self, robj, alevel=0, anorecur=0):
        #      if robj['SGIsMenuDisabled']:
        #         return
        self.ThisChapter = WWWMenuChapter(self, self.ThisChapter, robj, alevel)
        self.chapters_byid[robj.OID] = self.ThisChapter
        dv = {'ChapterID': self.ThisChapter.OID, 'TableID': self.ThisChapter.TableID, 'ChapterName': self.ThisChapter.Caption, 'TableName': self.ThisChapter.TableName, }
        self.Table_ChaptersID.AddValues(dv)
        if not anorecur:
            rrefs = robj.Class.PodRozdzialy.GetRefList(robj.OID)
            rrefs.sort(robj.Class.SGTabID)
            robj.Class.PodRozdzialy[robj.OID] = rrefs.AsString()
            sobj = robj.PodRozdzialy
            while sobj:
                self.PrepareChapters(sobj, alevel + 1)
                sobj.Next()
        if not alevel:
            self.chapters.append(self.ThisChapter)
        self.ThisChapter = self.ThisChapter.Parent

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

    def RequireLine(self, aline):
        if self.requiredLines.has_key(aline):
            return
        self.requiredLines[aline] = 1
        self.repldict['Response'].write(aline + '\n')

    def RequireHeaderLine(self, aline, ainsert=0, amanual=0, aheaderlines=None):
        if aheaderlines is None:
            aheaderlines = self.headerlines
        for i in range(len(aheaderlines)):
            bmanual, bline = aheaderlines[i]
            if aline == bline:
                if not amanual and bmanual:
                    aheaderlines[i][0] = 0
                return 0
        if ainsert:
            aheaderlines.insert(0, [amanual, aline])
        else:
            aheaderlines.append([amanual, aline])
        return amanual

    def GetEffect(self, eobj):
        aeffect = self.Effects.get(eobj.OID, None)
        if aeffect is None:
            aeffect = Effect(eobj, self)
            self.Effects[aeffect.OID] = aeffect
        return aeffect

    def RegisterEffect(self, aeffect):
        if self.processedEffects_d.has_key(aeffect.OID):
            return
        self.processedEffects_d[aeffect.OID] = aeffect
        self.processedEffects_l.append(aeffect)

    def RegisterEffectSkin(self, aeffectskin):
        if self.processedEffectsSkins_d.has_key(aeffectskin.OID):
            return
        self.processedEffectsSkins_d[aeffectskin.OID] = aeffectskin
        self.processedEffectsSkins_l.append(aeffectskin)

    def RegisterChapterCSS(self, acss):
        if not self.processedCSSs_d.has_key(acss):
            self.processedCSSs_d[acss] = 1
            self.processedCSSs_l.append(acss)

    def RegisterChapterScript(self, ascript):
        if not self.processedScripts_d.has_key(ascript):
            self.processedScripts_d[ascript] = 1
            self.processedScripts_l.append(ascript)

    def ProcessHeaderLines(self, amanualeffects=0):
        for aplugin in self.Plugins:
            aplugin.ProcessHeaderLines(amanualeffects=amanualeffects)
        if self.ThisChapter is not None:
            achapter = self.chapters_byid[self.ThisChapter.OID]
            achapter.ProcessHeaderLines(amanualeffects=amanualeffects)

    def ProcessEvents(self, aeventname, akey=''):
        alines = self.requiredLines
        self.requiredLines = {}
        arepldict = self.repldict
        if self.repldict is None:
            self.repldict = self.GetReplDict()
        for aplugin in self.Plugins:
            if aplugin.CheckEvents(aeventname, akey):
                aplugin.ProcessEvents(aeventname, akey=akey)
        if self.ThisChapter is not None:
            achapter = self.chapters_byid[self.ThisChapter.OID]
            achapter.ProcessEvents(aeventname, akey=akey, aeventcontext='Chapter')
        self.CRM.ProcessEvents(aeventname, akey, arepldict=self.repldict)
        self.requiredLines = alines
        self.repldict = arepldict

    def ProcessEventsInternal(self, aeventname, dd=None, akey='', aeventschapter=None, asinglepluginoid=-1):
        lret = []
        arepldict = self.repldict
        if self.repldict is None:
            self.repldict = self.GetReplDict()
        if dd:
            self.repldict.update(dd)
        if aeventschapter is not None:
            atext = aeventschapter.ProcessEvents(aeventname, akey=akey, aeventcontext='ChapterInternal')
            if atext:
                lret.append(atext)
        elif self.ThisChapter is not None:
            achapter = self.chapters_byid[self.ThisChapter.OID]
            atext = achapter.ProcessEvents(aeventname, akey=akey, aeventcontext='Chapter')
            if atext:
                lret.append(atext)
        ckey = (aeventname, akey, asinglepluginoid)
        cc = self.plugineventsexistscache.get(ckey, -1)
        if cc != 0:
            cc = 0
            for aplugin in self.Plugins:
                if asinglepluginoid >= 0 and aplugin.OID != asinglepluginoid:
                    continue
                if aplugin.CheckEvents(aeventname, akey):
                    atext = aplugin.ProcessEvents(aeventname, akey=akey)
                    if atext:
                        lret.append(atext)
                    cc = 1
            self.plugineventsexistscache[ckey] = cc
        atext = self.CRM.ProcessEvents(aeventname, akey, arepldict=self.repldict)
        if atext:
            lret.append(atext)
        if dd:
            for akey in dd.keys():
                del self.repldict[akey]
        self.repldict = arepldict
        return '\n'.join(lret)

    def PushQueryTable(self, aquery, asrctable, aistableview=0):
        btable = aquery.PushTable(asrctable.SQLTable, aistableview=aistableview)
        if btable is None:
            return
        for alink in asrctable.TableLinks:
            if alink.SrcFieldStr:
                aquery.LinkFields = (alink.SrcFieldStr, alink.DstFieldStr, alink.LinkConstraint)
            else:
                aquery.LinkFields = None
            self.PushQueryTable(aquery, alink.DstTable, aistableview=alink.IsTableView)
        aquery.PopTable()

    def GetChapterQuery(self, robj=None, tobj=None, wistableview=None, wshowastable=None, asxmlshape=0, queryparams=None):
        if robj is None:
            robj=self.ThisChapter
        if tobj is None:
            tobj = robj.TabelaZrodlowa
        if wistableview is None:
            wistableview = robj['SGIsTableView', mt_Integer]
        if wshowastable is None:
            wshowastable = robj['SGShowAsTable', mt_Integer]
        if queryparams is None:
            queryparams = {}
        asrctable = self.CRM.sourcetables[tobj.OID]
        if not queryparams.has_key('atop'):
            queryparams['atop']=1000
        aquery = MSQLQuery.QuerySQL(aisaliased=0, aencoding=self.DefaultEncoding, **queryparams)
        aquery.DisableHiddenDictFields = 1
        aquery.XSLCaption = robj.Naglowek
        aquery.XSLChapterOID = robj.OID
        aquery.XSLIsTableView = wistableview
        aquery.XSLShowAsTable = wshowastable
        aquery.TemplateXML = self.TemplateXML
        aquery.XLSMenuTable = self.Table_MenuChapters.NameSQL
        aquery.PushTable(asrctable.SQLTable, aistableview=wistableview)
        for alink in asrctable.TableLinks:
            if not alink.CMSDisabledTable:
                #print 'PushLink:',alink
                if alink.SrcFieldStr:
                    aquery.LinkFields = (alink.SrcFieldStr, alink.DstFieldStr, alink.LinkConstraint)
                else:
                    aquery.LinkFields = None
                self.PushQueryTable(aquery, alink.DstTable, aistableview=alink.IsTableView)
        if asxmlshape:
            aquery.AsSQL(asxmlshape=1, acontext=self)
        else:
            aquery.AsSQL(aasshape=1, acontext=self)
        return aquery

    def GetTemplateCSS(self, toid=-1):
        lcss = []
        if toid < 0:
            tobj = self.TemplateObj
        else:
            tobj = self.PageTemplateObj.Class[toid]
        ljoids = self.GetTemplateLibs(tobj)
        lcobj = []
        dcobj = {}
        for toid in ljoids[::-1]:
            tobj = self.PageTemplateObj.Class[toid]
            cobj = tobj.PageCSSTemplate
            while cobj:
                aname = cobj.CSSName
                aklucz = cobj.Klucz
                ck = (aname, aklucz)
                if aname or aklucz:
                    if dcobj.has_key(ck):
                        lcobj[dcobj[ck]] = cobj.AsObject()
                    else:
                        dcobj[ck] = len(lcobj)
                        lcobj.append(cobj.AsObject())
                else:
                    lcobj.append(cobj.AsObject())
                cobj.Next()
        for cobj in lcobj:
            l = []
            mobj = cobj.CSSMedia
            while mobj:
                l.append(mobj.Nazwa)
                mobj.Next()
            if not l:
                l = ['all', ]
            self.pagetemplatecssmedia[cobj.OID] = l
            self.pagetemplatecsskeys[cobj.OID] = cobj.Klucz
            self.pagetemplatecssattrs[cobj.OID] = [cobj.Tytul, cobj.Rola, cobj['IsAlternate', mt_Integer], cobj['IsDisabled', mt_Integer], cobj.CSSName]
            lcss.append(cobj.OID)
        self.pagetemplatecss[tobj.OID] = lcss
        return lcss

    def GetChapterCSS(self, akey='', toid=-1):
        lret = []
        if toid < 0:
            toid = self.TemplateObj.OID
        l = self.pagetemplatecss.get(toid, None)
        if l is None:
            l = self.GetTemplateCSS(toid)
        for coid in l:
            bkey = self.pagetemplatecsskeys.get(coid, '')
            if (bkey == akey) or (akey == '*'):
                lmedia = self.pagetemplatecssmedia.get(coid, ['all', ])
                atytul, arole, aisalternate, aisdisabled, aname = self.pagetemplatecssattrs.get(coid, ['', '', 0, 0, ''])
                acss = WWWMenuChapterCSS(coid, amedia=lmedia, atitle=atytul, aisalternate=aisalternate, arole=arole, aisdisabled=aisdisabled, akey=bkey, aname=aname)
                lret.append(acss)
        return lret

    def WriteChapterCSS(self, akey='', anoduplicates=0, dk=None, dd=None):
        if dk is None:
            dk = {}
        if dd is None:
            dd = {}
        if not akey:
            akey = '*'
        if self.repldict.has_key('Response'):
            write = self.repldict['Response'].write
            lcss = self.GetChapterCSS(akey)
            #dcss={}
            for acss in lcss:
                #cek=(acss.Name,acss.Key)
                #if anoduplicates and dcss.has_key(cek):
                #   continue
                #dcss[cek]=1
                if acss.Key:
                    ck = dk.get(acss.Key, 0)
                    dk[acss.Key] = 1 + ck
                    if not acss.IsDisabled:
                        dd[acss.Key] = ck
                    elif not dd.has_key(acss.Key):
                        dd[acss.Key] = 0
                write(acss.AsHTML() + '\n')

    def GetReplDict(self, dd=None):
        d = {'aCRM': self.CRM, 'this': self, 're': re, 'os': os, 'string': string, 'json': json, 'ICORUtil': ICORUtil, 'storageutil': storageutil, 'ADOLibInit': ADOLibInit, 'FilePathAsSystemPath': FilePathAsSystemPath, 'XMLUtil': XMLUtil, 'GeoInterface': GeoInterface, 'ICORSecurity': ICORSecurity}
        return d

    def AddInitScript(self, ascript, aindex=-1):
        if ascript in self.initScripts:
            return
        if aindex >= 0:
            self.initScripts.insert(aindex, ascript)
        else:
            self.initScripts.append(ascript)

    def AddAppScript(self, ascript, aindex=-1):
        if ascript in self.appScripts:
            return
        if aindex >= 0:
            self.appScripts.insert(aindex, ascript)
        else:
            self.appScripts.append(ascript)

    def GetTemplateXML(self, tobj):
        if type(tobj) == type(1):
            tobj = self.PageTemplateObj.Class[tobj]
        ret = self._TemplateXML.get(tobj.OID, None)
        if ret is None:
            ret = MCRMWWWMenu.ICORBIPTemplateParser()
            ret.Parse(self, tobj.PageXML)
            #         ret.Dump()
            self._TemplateXML[tobj.OID] = ret
        return ret

    def GetTemplateLibs(self, tobj, ret=None):
        if type(tobj) == type(1):
            tobj = self.PageTemplateObj.Class[tobj]
        if ret is None:
            ret = [tobj.OID, ]
        aTemplateXML = self.GetTemplateXML(tobj)
        joids = aTemplateXML.Variables.get('jinja_Libs', None)
        if joids is not None:
            lt = storageutil.SafeSplitInt(joids)
            for toid in lt:
                if toid not in ret:
                    ret.append(toid)
                    self.GetTemplateLibs(toid, ret)
        return ret

    def GetTemplateFieldValue(self, tobj, afieldname, adefault=''):
        ljoids = self.GetTemplateLibs(tobj)
        for toid in ljoids:
            tobj = self.PageTemplateObj.Class[toid]
            v = None
            if afieldname == 'XSLAtEnd':
                v = tobj.XSLAtEnd
            elif afieldname == 'XSLMainObjectAtEnd':
                v = tobj.XSLMainObjectAtEnd
            elif afieldname == 'DeklaracjaDOCTYPE':
                v = tobj.DeklaracjaDOCTYPE
            elif afieldname == 'PageTop1':
                v = tobj.PageTop1
            if v:
                return v
        return adefault

    def WriteChapter(self, robj, anorecur=0, acheckdisabled=0):
        if acheckdisabled:
            if robj['SGIsMenuDisabled']:
                return
        atimestart = time.clock()
        self.ThisChapter = robj
        self.ThisModels = MCRMWWWMenuModel.WWWMenuChapterModels(robj)
        self.ThisViews = MCRMWWWMenuView.WWWMenuChapterPresentation(robj)
        self.XSLData = ''
        self.XSLDataSO = ''
        self.SQLData = ''
        self.QuasarData = ''
        self.QuasarDataSO = ''
        self.SQLXMLData = ''
        self.WriteMode = 'chapter'
        self.TemplateObj = None
        self.headerlines = []
        self.processedEffects_d = {}
        self.processedEffects_l = []
        self.processedEffectsSkins_d = {}
        self.processedEffectsSkins_l = []
        self.processedCSSs_d = {}
        self.processedCSSs_l = []
        self.processedScripts_d = {}
        self.processedScripts_l = []
        self.initScripts = []
        self.appScripts = []
        r1obj = robj.AsObject()
        while r1obj:
            self.TemplateObj = r1obj.PageTemplate
            if self.TemplateObj:
                break
            r1obj = r1obj.NadRozdzial
        if not self.TemplateObj:
            self.TemplateObj = self.PageTemplateObj
        if not self.pagetemplateoids.has_key(self.TemplateObj.OID):
            self.GetTemplateCSS()
            dobj = self.GetTemplateFieldValue(self.TemplateObj, 'DeklaracjaDOCTYPE', None)
            sdoc = ''
            if dobj:
                sdoc = dobj.Nazwa
            self.pagetemplatedoctype[self.TemplateObj.OID] = sdoc
        print '@Chapter:', robj.OID, 'Template:', self.TemplateObj.Template
        gobj = robj.Galeria
        if gobj:
            self.IsGallery = 1
            self.GalleryColumns = gobj['IloscWWierszu']
        else:
            self.IsGallery = 0
            self.GalleryColumns = 4


#      print '  Gallery:',self.IsGallery,self.GalleryColumns

        self.TemplateXML = self.GetTemplateXML(self.TemplateObj)
        self.TemplateJinja = self._TemplateJinja.get(self.TemplateObj.OID, None)
        if self.TemplateJinja is None:
            ljoids = self.GetTemplateLibs(self.TemplateObj)
            if ljoids:
                self.TemplateJinja = TemplateJinja(self.TemplateObj, ljoids)
                self._TemplateJinja[self.TemplateObj.OID] = self.TemplateJinja

        aDefaultEncoding = self.TemplateXML['DefaultEncoding']
        if not aDefaultEncoding:
            aDefaultEncoding = self.DefaultEncoding

        self.repldict = self.GetReplDict()
        XSLAtEnd = self.GetTemplateFieldValue(self.TemplateObj, 'XSLAtEnd')
        self.XSLAtEnd = ICORUtil.GetTextAsHTMLText(XSLAtEnd, repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='XSLAtEnd')
        XSLMainObjectAtEnd = self.GetTemplateFieldValue(self.TemplateObj, 'XSLMainObjectAtEnd')
        self.XSLMainObjectAtEnd = ICORUtil.GetTextAsHTMLText(XSLMainObjectAtEnd, repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='XSLMainObjectAtEnd')

        tobj = robj.TabelaZrodlowa
        wcustomxsl = robj['IsCustomXSL', mt_Integer]
        wcustomxsllist = robj['IsCustomXSLList', mt_Integer]
        wcustomxslso = robj['IsCustomXSLSO', mt_Integer]
        wcustomquasar = robj['IsCustomHandlebars', mt_Integer]
        wcustomquasarlist = robj['IsCustomHandlebarsList', mt_Integer]
        wcustomquasarso = robj['IsCustomHandlebarsSO', mt_Integer]
        wrozdzialcustomsql = robj['IsCustomSQL', mt_Integer]
        wrozdzialcustomsqlxml = robj['IsCustomSQLXML', mt_Integer]

        wistableview = robj['SGIsTableView', mt_Integer]
        wshowastable = robj['SGShowAsTable', mt_Integer]
        wtablecustomxsl = tobj['IsCustomShapeXSL', mt_Integer]
        wtablecustomquasar = tobj['IsCustomShapeHandlebars', mt_Integer]

        SHAPE_SOURCE_CHAPTER = 8000
        SHAPE_SOURCE_TABLE = 8001

        wchangezrodlodanychwzorca = 0
        if not robj.ZrodloDanychWzorca:
            wchangezrodlodanychwzorca = 1
        else:
            if not robj.ZrodloDanychWzorca.OID in [SHAPE_SOURCE_CHAPTER, SHAPE_SOURCE_TABLE]:
                wchangezrodlodanychwzorca = 1
            else:
                zclass = robj.Class.ZrodloDanychWzorca.ClassOfType
                zrefs = robj.Class.ZrodloDanychWzorca.GetRefList(robj.OID)
                zlcids = zrefs.AsListCID()
                for zcid in zlcids:
                    if zcid != zclass.CID:
                        wchangezrodlodanychwzorca = 1
                        break
        if wchangezrodlodanychwzorca:
            if wcustomxsl or wcustomxsllist or wcustomxslso or wcustomquasar or wcustomquasarlist or wcustomquasarso:
                robj.ZrodloDanychWzorca = [SHAPE_SOURCE_CHAPTER, robj.Class.ZrodloDanychWzorca.ClassOfType.CID]
            else:
                robj.ZrodloDanychWzorca = [SHAPE_SOURCE_TABLE, robj.Class.ZrodloDanychWzorca.ClassOfType.CID]

        ashapesource = robj.ZrodloDanychWzorca.OID

        wxslchanged, wxslsochanged = 0, 0
        wquasarchanged, wquasarsochanged = 0, 0

        #obsluga SQLData,XSLData,XSLDataSO
        aquery = None
        if ashapesource == SHAPE_SOURCE_TABLE:
            if tobj:
                #pobranie/utworzenie SQLData
                if not wrozdzialcustomsql:
                    if aquery is None:
                        #print 'Create Shape SQL 1t:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.SQLData = aquery.SQLShapeString
                if not wrozdzialcustomsqlxml:
                    if aquery is None:
                        #print 'Create XML SQL 1t:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.SQLXMLData = aquery.SQLXMLString

                #zapamietanie SQLData
                if not wrozdzialcustomsql and self.SQLData:
                    robj.SQLData = self.SQLData

                #zapamietanie SQLXMLData
                if not wrozdzialcustomsqlxml and self.SQLXMLData:
                    robj.SQLXMLData = self.SQLXMLData

                #pobranie/utworzenie XSLData i XSLDataSO
                if wshowastable:
                    self.XSLData = tobj.ShapeXSLTable
                else:
                    self.XSLData = tobj.ShapeXSLTableList
                self.XSLDataSO = tobj.ShapeXSL
                if not wtablecustomxsl:
                    if aquery is None:
                        #print 'Create Shape SQL 2t:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    if wistableview or wshowastable:
                        bquery = self.GetChapterQuery(robj, tobj, 0, 0)
                    else:
                        bquery = aquery
                    self.XSLDataSO = bquery.XSLTransformString
                    wxslsochanged = 1
                    if wistableview:
                        self.XSLData = aquery.XSLTransformString
                        wxslchanged = 1
                    else:
                        self.XSLData = self.XSLDataSO

                #pobranie/utworzenie QuasarData i QuasarDataSO
                if wshowastable:
                    self.QuasarData = tobj.ShapeHandlebarsTable
                else:
                    self.QuasarData = tobj.ShapeHandlebarsTableList
                self.QuasarDataSO = tobj.ShapeHandlebars
                if not wtablecustomquasar:
                    if aquery is None:
                        #print 'Create Shape SQL 2t:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    if wistableview or wshowastable:
                        bquery = self.GetChapterQuery(robj, tobj, 0, 0)
                    else:
                        bquery = aquery
                    self.QuasarDataSO = bquery.QuasarString
                    wquasarsochanged = 1
                    if wistableview:
                        self.QuasarData = aquery.QuasarString
                        wquasarchanged = 1
                    else:
                        self.QuasarData = self.QuasarDataSO

                #zapamietanie XSLData/XSLDataSO
                if wxslchanged:
                    if wshowastable:
                        tobj.ShapeXSLTable = self.XSLData
                    else:
                        tobj.ShapeXSLTableList = self.XSLData
                if wxslsochanged:
                    tobj.ShapeXSL = self.XSLDataSO

                #zapamietanie QuasarData/QuasarDataSO
                if wquasarchanged:
                    if wshowastable:
                        tobj.ShapeHandlebarsTable = self.QuasarData
                    else:
                        tobj.ShapeHandlebarsTableList = self.QuasarData
                if wquasarsochanged:
                    tobj.ShapeHandlebars = self.QuasarDataSO

            else:
                pass
                #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID

        if ashapesource == SHAPE_SOURCE_CHAPTER:
            #pobranie/utworzenie SQLData
            if not wrozdzialcustomsql:
                if tobj:
                    if aquery is None:
                        #print 'Create Shape SQL 1r:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.SQLData = aquery.SQLShapeString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID
            else:
                self.SQLData = robj.SQLData

            #pobranie/utworzenie SQLXMLData
            if not wrozdzialcustomsqlxml:
                if tobj:
                    if aquery is None:
                        #print 'Create XML SQL 1r:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.SQLXMLData = aquery.SQLXMLString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID
            else:
                self.SQLXMLData = robj.SQLXMLData

            #zapamietanie SQLData
            if not wrozdzialcustomsql and self.SQLData:
                robj.SQLData = self.SQLData

            #zapamietanie SQLXMLData
            if not wrozdzialcustomsqlxml and self.SQLXMLData:
                robj.SQLXMLData = self.SQLXMLData

            #pobranie/utworzenie XSLData
            self.XSLData = robj.XSLData
            if not wcustomxsl:
                if tobj:
                    if aquery is None:
                        #print 'Create Shape SQL 2r:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.XSLData = aquery.XSLTransformString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID

            #pobranie/utworzenie QuasarData
            self.QuasarData = robj.HandlebarsData
            if not wcustomquasar:
                if tobj:
                    if aquery is None:
                        #print 'Create Shape SQL 2r:',robj.Naglowek
                        aquery = self.GetChapterQuery(robj, tobj, wistableview, wshowastable)
                    self.QuasarData = aquery.QuasarString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID

            #pobranie/utworzenie XSLDataSO
            self.XSLDataSO = robj.XSLDataSO
            if not wcustomxslso:
                if tobj:
                    aquery = self.GetChapterQuery(robj, tobj, 0, 0)
                    self.XSLDataSO = aquery.XSLTransformString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID

            #pobranie/utworzenie QuasarDataSO
            self.QuasarDataSO = robj.HandlebarsDataSO
            if not wcustomquasarso:
                if tobj:
                    aquery = self.GetChapterQuery(robj, tobj, 0, 0)
                    self.QuasarDataSO = aquery.QuasarString
                else:
                    pass
                    #print '*** Chapter without assigned table:',robj.Naglowek,robj.OID

            #zapamietanie XSLData/XSLDataSO
            if not wcustomxsl:
                robj.XSLData = self.XSLData
            if not wcustomxslso:
                robj.XSLDataSO = self.XSLDataSO

            #zapamietanie QuasarData/QuasarDataSO
            if not wcustomquasar:
                robj.HandlebarsData = self.QuasarData
            if not wcustomquasarso:
                robj.HandlebarsDataSO = self.QuasarDataSO

        #not self.ThisModels.Exists() - continue
        mupdate = 1
        if not self.ThisModels.Exists():
            mupdate = 0
        self.ThisModels.CreateModelByData('struktura', 'sqlshape', robj.IsCustomSQL, robj.SQLData, aupdate=mupdate)
        self.ThisModels.CreateModelByData('struktura', 'sqlxml', robj.IsCustomSQLXML, robj.SQLXMLData, aupdate=mupdate)
        vupdate = 1
        if not self.ThisViews.Exists():
            vupdate = 0
        self.ThisViews.CreateViewByData('dane', 'xsl', robj.IsCustomXSLSO, robj.XSLDataSO, aupdate=vupdate)
        self.ThisViews.CreateViewByData('tabela', 'xsl', robj.IsCustomXSL, robj.XSLData, aupdate=vupdate)
        self.ThisViews.CreateViewByData('lista', 'xsl', robj.IsCustomXSLList, robj.XSLDataList, aupdate=vupdate)
        self.ThisViews.CreateViewByData('dane', 'quasar', robj.IsCustomHandlebarsSO, robj.HandlebarsDataSO, aupdate=vupdate)
        self.ThisViews.CreateViewByData('tabela', 'quasar', robj.IsCustomHandlebars, robj.HandlebarsData, aupdate=vupdate)
        self.ThisViews.CreateViewByData('lista', 'quasar', robj.IsCustomHandlebarsList, robj.HandlebarsDataList, aupdate=vupdate)

        remark = """
      if tobj:
         if not wrozdzialcustomsql:
            print 'Create Shape SQL:',robj.Naglowek
            aquery=self.GetChapterQuery(robj,tobj,wistableview,wshowastable)
            robj.SQLData=aquery.SQLShapeString
            if not wcustomxsl:
               robj.XSLData=aquery.XSLTransformString
            if not wtablecustomxsl:
               if wistableview:
                  tobj.ShapeXSLTable=aquery.XSLTransformString
               else:
                  tobj.ShapeXSL=aquery.XSLTransformString
            else:
               self.XSLData=tobj.ShapeXSLTable
               self.XSLDataSO=tobj.ShapeXSL
            if ashapesource==SHAPE_SOURCE_TABLE:
               if wistableview:
                  if not self.XSLData:
                     self.XSLData=tobj.ShapeXSLTable
               else:
                  if not self.XSLData:
                     self.XSLData=tobj.ShapeXSL
                     self.XSLDataSO=self.XSLData
            elif ashapesource==SHAPE_SOURCE_CHAPTER:
               self.XSLData=robj.XSLData
               self.XSLDataSO=robj.XSLDataSO
         else:
            if ashapesource==SHAPE_SOURCE_TABLE:
               self.XSLData=tobj.ShapeXSLTable
               self.XSLDataSO=tobj.ShapeXSL
            elif ashapesource==SHAPE_SOURCE_CHAPTER:
               self.XSLData=robj.XSLData
               self.XSLDataSO=robj.XSLDataSO # bylo wylaczone
         if not self.XSLDataSO or not wcustomxsl:
            print 'Create Shape SQL SO:',robj.Naglowek
            aquery=self.GetChapterQuery(robj,tobj,0,0)
            self.XSLDataSO=aquery.XSLTransformString
            if not wcustomxsl:
               robj.XSLDataSO=self.XSLDataSO
"""
        mobj = None
        r1obj = robj.AsObject()
        while r1obj:
            mobj = r1obj.MetaTemplate
            if mobj:
                break
            r1obj = r1obj.NadRozdzial
        if not mobj:
            mobj = self.MetaTemplateObj
        self.TemplateCSS = 'template_%d.css' % self.TemplateObj.OID
        self.TemplateSearch = 'search_%d.asp' % self.TemplateObj.OID    #do usuniecia docelowo
        self.MetaAuthor, self.MetaDescription, self.MetaKeywords = '', '', ''    #'ICOR, application server, serwer aplikacyjny, application generator, object oriented database, '
        if mobj:
            self.MetaAuthor = mobj.Author
            self.MetaDescription = string.replace(string.replace(string.replace(mobj.Description, chr(10), ' '), chr(13), ''), '"', "'")
            self.MetaKeywords = string.replace(string.replace(string.replace(mobj.Keywords, chr(10), ' '), chr(13), ''), '"', "'")
        self.ProcessHeaderLines()
        l = []
        ehrobj = MCRMUtil.EventHelper(robj, 'ChapterEvents')
        self.OnASPPageTop = ICORUtil.GetTextAsHTMLText(ehrobj['OnASPPageTop'], repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter OnASPPageTop ' + str(robj.OID))
        self.OnASPPageHeader = ICORUtil.GetTextAsHTMLText(ehrobj['OnASPPageHeader'], repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter OnASPPageHeader ' + str(robj.OID))
        self.OnASPPageBefore = ICORUtil.GetTextAsHTMLText(ehrobj['OnASPPageBefore'], repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter OnASPPageBefore ' + str(robj.OID))
        self.OnASPPageAfter = ICORUtil.GetTextAsHTMLText(ehrobj['OnASPPageAfter'], repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter OnASPPageAfter ' + str(robj.OID))
        self.OnASPPageContent = ICORUtil.GetTextAsHTMLText(ehrobj['OnASPPageContent'], repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter OnASPPageContent ' + str(robj.OID))

        aPageTop = self.GetTemplateFieldValue(self.TemplateObj, 'PageTop1')
        #aPageLeft=self.TemplateObj.PageLeft
        #aPageContent=self.TemplateObj.PageContent
        #aPageRight=self.TemplateObj.PageRight
        #aPageBottom=self.TemplateObj.PageBottom
        #if aPageLeft!='' or aPageContent!='' or aPageRight!='' or aPageBottom!='':
        #   aPageTop=aPageTop+aPageLeft+aPageContent+aPageRight+aPageBottom
        #   self.TemplateObj.PageTop1=aPageTop
        #   self.TemplateObj.PageLeft=''
        #   self.TemplateObj.PageContent=''
        #   self.TemplateObj.PageRight=''
        #   self.TemplateObj.PageBottom=''
        #   lfields=['PageLeft','PageContent','PageRight','PageBottom','PageSearch']
        #   for afieldname in lfields:
        #      afield=self.TemplateObj.Class.FieldsByName(afieldname)
        #      afield.IsAliased='0'
        #      afield.IsInteractive='0'
        #      afield.WWWDefaultInput='0'

        if self.TemplateJinja:
            #print 'TemplateJinja 0:',len(aPageTop)
            aPageTop = self.TemplateJinja.Process('chapter_%d.asp' % robj.OID, aPageTop, repldict=self.repldict)
            #print 'TemplateJinja 1:',len(aPageTop)
        self.PageTop = ICORUtil.GetTextAsHTMLText(aPageTop, repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter PageTemplate ' + str(robj.OID))
        #      self.PageLeft=ICORUtil.GetTextAsHTMLText(self.TemplateObj.PageLeft,repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0)
        #      self.PageContent=ICORUtil.GetTextAsHTMLText(self.TemplateObj.PageContent,repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0)
        #      self.PageRight=ICORUtil.GetTextAsHTMLText(self.TemplateObj.PageRight,repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0)
        #      self.PageBottom=ICORUtil.GetTextAsHTMLText(self.TemplateObj.PageBottom,repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0)
        sheaderlines = ''
        for bmanual, bline in self.headerlines:
            if not bmanual:
                if self.PageTop.find(bline) < 0:
                    sheaderlines = sheaderlines + '\n' + bline
        sdoc = self.pagetemplatedoctype.get(self.TemplateObj.OID, '')
        if sdoc == '<!DOCTYPE html>':    #html5
            ametaencoding = '<meta charset="%s">' % (aDefaultEncoding, )
        else:
            ametaencoding = '<meta http-equiv="Content-Type" content="text/html; charset=%s">' % (aDefaultEncoding, )
        seffectscss = ''
        for aeffectskin in self.processedEffectsSkins_l:
            if aeffectskin.OnGetCSSSource:
                seffectscss = seffectscss + '\n' + aeffectskin.OnGetCSSSource

        spagecssjs = ''
        if self.processedCSSs_l:
            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'css/chapter_%d.css' % self.ThisChapter.OID, 'css', '\n'.join(self.processedCSSs_l), aencoding=aDefaultEncoding)
            self.ProcessEventsInternal('OnCMSWriteChapterCSS', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
            if awwwmenufile.Write():
                spagecssjs = '\n<link rel="stylesheet" type="text/css" href="css/chapter_%d.css">\n' % (self.ThisChapter.OID, )
        if self.processedScripts_l:
            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'js/chapter_%d.js' % self.ThisChapter.OID, 'js', '\n'.join(self.processedScripts_l), aencoding=aDefaultEncoding)
            self.ProcessEventsInternal('OnCMSWriteChapterJS', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
            if awwwmenufile.Write():
                spagecssjs = spagecssjs + '<script type="text/javascript" src="js/chapter_%d.js"></script>\n' % (self.ThisChapter.OID, )

        if self.TemplateXML.Variables.get('CustomHeadSection', '') != '1':
            #self.PageTop=re.sub('(?i)\<head.*?\>','<head>'+ametaencoding+sheaderlines+seffectscss+spagecssjs,self.PageTop)
            self.PageTop = re.sub('(?i)\<head\>', '<head>' + ametaencoding + sheaderlines + seffectscss + spagecssjs, self.PageTop)
        if sdoc and string.find(self.PageTop, '<!DOCTYPE') < 0:
            self.PageTop = sdoc + '\n' + self.PageTop
        self.PageTop = '<%%@ CodePage=%s LANGUAGE="VBSCRIPT" %%>\n' % (self.DefaultCodePage, ) + self.PageTop
        sbeforebody = ''
        for aeffect in self.processedEffects_l:
            aeffect.Process()
            if aeffect.InitScript:
                sbeforebody = sbeforebody + '\n' + aeffect.InitScript
        for aeffectskin in self.processedEffectsSkins_l:
            if aeffectskin.OnGetScriptSource:
                sbeforebody = sbeforebody + '\n' + aeffectskin.OnGetScriptSource
        if sbeforebody:
            #         self.PageBottom=re.sub('(?i)\<\/body\>',sbeforebody+'</body>',self.PageBottom)
            if self.TemplateXML.Variables.get('CustomBodySection', '') != '1':
                self.PageTop = re.sub('(?i)\<\/body\>', sbeforebody + '</body>', self.PageTop)
        if self.initScripts:
            sbeforebody = '\n'.join(self.initScripts)
            self.PageTop = re.sub('(?i)\<\/body\>', sbeforebody + '</body>', self.PageTop)
        if self.appScripts:
            sbeforebody = '\n'.join(self.appScripts)
            self.PageTop = re.sub('(?i)\<\/body\>', sbeforebody + '</body>', self.PageTop)
        l.append(self.PageTop)
        #      l.append(self.PageLeft)
        #      l.append(self.PageContent)
        #      l.append(self.PageRight)
        #      l.append(self.PageBottom)
        if self.XSLData is None:
            print robj.Naglowek, 'XSLData is None!!!!!!'
        atext = string.join(l, '')

        awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'chapter_' + str(robj.OID) + '.asp', 'html', atext, aencoding=aDefaultEncoding)
        aoldwwwmenufile = self.repldict.get('WWWMenuFile', None)
        self.repldict['WWWMenuFile'] = awwwmenufile
        #      ICORUtil.GetTextAsHTMLText(ehrobj['OnCMSWriteChapterText'],repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0,ascriptname='Chapter OnCMSWriteChapterText '+str(robj.OID))
        #      if awwwmenufile.AllowWrite:
        if 1:
            self.ProcessEventsInternal('OnCMSWriteChapterText', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
            if awwwmenufile.AllowWrite:
                self.WriteASP(awwwmenufile.FileName, awwwmenufile.Text, araw=1)
        self.repldict['WWWMenuFile'] = aoldwwwmenufile

        if wistableview:
            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'xsl/chapter_' + str(robj.OID) + '.xsl', 'xsl', self.XSLData, aencoding=aDefaultEncoding)
        else:
            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'xsl/chapter_' + str(robj.OID) + '.xsl', 'xsl', self.XSLDataSO, aencoding=aDefaultEncoding)
        self.ProcessEventsInternal('OnCMSWriteChapterXSLTable', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
        if aDefaultEncoding:
            awwwmenufile.Text = awwwmenufile.Text.replace('windows-1250', aDefaultEncoding)
        awwwmenufile.Write()

        if self.XSLDataSO:
            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'xsl/chapter_' + str(robj.OID) + '_so.xsl', 'xsl', self.XSLDataSO, aencoding=aDefaultEncoding)
            self.ProcessEventsInternal('OnCMSWriteChapterXSLSingle', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
            if aDefaultEncoding:
                awwwmenufile.Text = awwwmenufile.Text.replace('windows-1250', aDefaultEncoding)
            awwwmenufile.Write()

        if not self.pagetemplateoids.has_key(self.TemplateObj.OID):
            self.WriteMode = 'css'
            ljoids = self.GetTemplateLibs(self.TemplateObj)
            lcobj = []
            for toid in ljoids[::-1]:
                tobj = self.PageTemplateObj.Class[toid]
                cobj = tobj.PageCSSTemplate
                while cobj:
                    lcobj.append(cobj.AsObject())
                    cobj.Next()
            ltext = []
            for cobj in lcobj:
                lmedia = self.pagetemplatecssmedia.get(cobj.OID, ['all', ])
                ltext.append('\n@media %s {\n' % (string.join(lmedia, ',')))
                sc1 = cobj.CSSUser
                sc2 = cobj.CSSSystem
                if sc2 != '':
                    cobj.CSSUser = cobj.CSSUser + cobj.CSSSystem
                    cobj.CSSSystem = ''
                    lfields = ['CSSSystem', ]
                    for afieldname in lfields:
                        afield = cobj.Class.FieldsByName(afieldname)
                        afield.IsAliased = '0'
                        afield.IsInteractive = '0'
                        afield.WWWDefaultInput = '0'
                atext = ICORUtil.GetTextAsHTMLText(sc1 + '\n\n' + sc2, repldict=self.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Chapter CSS ' + str(robj.OID))
                ltext.append(atext)
                ltext.append('\n}\n')
                awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'css/style_%d.css' % cobj.OID, 'css', atext, aencoding=aDefaultEncoding)
                self.ProcessEventsInternal('OnCMSWriteCSSSingle', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
                awwwmenufile.Write()

            awwwmenufile = WWWMenuFile(self.WSBaseDirectory + 'css/template_%d.css' % self.TemplateObj.OID, 'css', '\n'.join(ltext), aencoding=aDefaultEncoding)
            self.ProcessEventsInternal('OnCMSWriteCSS', dd={'WWWMenuFile': awwwmenufile, 'Slimmer': Slimmer, })
            awwwmenufile.Write()

            #         self.WriteMode='search'
            #         fout=open(self.WSBaseDirectory+'search_%d.asp'%self.TemplateObj.OID,'w')
            #         atext=ICORUtil.GetTextAsHTMLText(self.TemplateObj.PageSearch,repldict=self.repldict,aengine=aICORDBEngine,aashtmlstring=0)
            #         if self.OptimizationLevel:
            #            atext=Slimmer.slimmer(atext,'html')
            #         fout.write(atext)
            #         fout.close()
            self.pagetemplateoids[self.TemplateObj.OID] = 1
        atimefinish = time.clock()
        self.ProcessEventsInternal('OnCMSWriteChapterAfter', dd={'ProcessingTime': atimefinish - atimestart, })
        if not anorecur:
            rrefs = robj.Class.PodRozdzialy.GetRefList(robj.OID)
            rrefs.sort(robj.Class.SGTabID)
            robj.Class.PodRozdzialy[robj.OID] = rrefs.AsString()
            probj = robj.PodRozdzialy
            while probj:
                self.WriteChapter(probj, acheckdisabled=acheckdisabled)
                probj.Next()
        self.ThisChapter = None
