# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_NetBase_WWW_HTML_Util_ASPIndent as ASPIndent
import cStringIO
import types
import appplatform.storageutil as storageutil


class MCRMItemBase:

    def __init__(self, acrm, agenerateenable=0):
        self.CRM = acrm
        self.GenerateEnable = agenerateenable
        self.DefaultEncoding = acrm.DefaultEncoding
        self.DefaultCodePage = acrm.DefaultCodePage
        self.IsCustomPage = 0
        self.InProcess = 0
        self._filedata = []
        self.evtOnASPWriteFile = None
        self.OnEventParams = None

    def OnWriteASPText(self, atext):
        return atext

    def WriteText(self, f, atext):
        if self.DefaultEncoding=='utf-8':
            atext=storageutil.UTF8_To_CP1250_Replace(atext)
        atext = self.OnWriteASPText(atext)
        #atext=storageutil.CP1250_To_UTF8(atext)
        if self.evtOnASPWriteFile is None:
            f.write(atext)
        else:
            self._filedata.append(atext)

    def FileClose(self, f):
        #      if self.DefaultEncoding=='utf-8':
        #         atext=XMLUtil.CP1250_To_UTF8(atext)
        if self.evtOnASPWriteFile is None:
            f.close()
        else:
            atext = ''.join(self._filedata)
            atext = self.evtOnASPWriteFile(atext, self.OnEventParams)
            f.write(atext)
            f.close()

    def WriteASPPageBegin(self, f, arefresh='', apage='', anobodytarget=0, aheadertext='', acompatibility='8'):
        atext = MHTMLSQLGenAspPage.GetASPPageBegin(self.CRM, arefresh, apage, anocss=self.IsCustomPage, anobodytarget=anobodytarget, aheadertext=aheadertext, aencoding=self.DefaultEncoding, acodepage=self.DefaultCodePage, acompatibility=acompatibility)
        self.WriteText(f, atext)

    def WriteASPPageEnd(self, f, fname):
        #atext = MHTMLSQLGenAspPage.GetASPPageEnd(self.CRM.SQLCreator, fname)
        atext = MHTMLSQLGenAspPage.GetASPPageEnd(None, fname)
        self.WriteText(f, atext)

    def WriteASP(self, fname, atext, arefresh='', apage='', araw=0, anobodytarget=0, aheadertext='', anocodepage=0, acompatibility='8', aonaspwritefile=None, aoneventparams=None):
        self._filedata = []
        self.evtOnASPWriteFile = aonaspwritefile
        self.OnEventParams = aoneventparams
        if isinstance(fname, types.StringTypes):
            fname = FilePathAsSystemPath(fname)
        if araw:
            f = ICORUtil.OpenText(fname, 'w', aencoding=self.DefaultEncoding)
        else:
            f = ICORUtil.OpenText(fname, 'w', aencoding=self.DefaultEncoding)
            #f=ASPIndent.ASPIndentedFile()
            #f.open(f1,fileclose=1)
        try:
            asig = '<%%@ CodePage=%s LANGUAGE="VBSCRIPT" %%>' % (self.DefaultCodePage)
            ssig1 = 'CodePage=%s' % (self.DefaultCodePage)
            ssigfind = 'CodePage='
            ssig2 = 'LANGUAGE="VBSCRIPT"'
            if not araw:
                self.WriteASPPageBegin(f, arefresh, apage, anobodytarget=anobodytarget, aheadertext=aheadertext, acompatibility=acompatibility)
            if type(atext) == type([]):
                if araw and not anocodepage and len(atext) > 0 and isinstance(atext[0], types.StringTypes):
                    if (atext[0].find(ssigfind) < 0) and (atext[0].find(ssig2) < 0):
                        atext[0] = asig + '\n' + atext[0]
                for s in atext:
                    if isinstance(s, types.StringTypes):
                        self.WriteText(f, s.replace(chr(13), ''))
                    elif hasattr(s, 'write'):
                        f2 = cStringIO.StringIO()
                        s.write(f2)
                        stext = f2.getvalue()
                        f2.close()
                        self.WriteText(f, stext)
                    elif hasattr(s, 'Write'):
                        f2 = cStringIO.StringIO()
                        s.Write(f2)
                        stext = f2.getvalue()
                        f2.close()
                        self.WriteText(f, stext)
                    self.WriteText(f, '\n')
            else:
                if araw and not anocodepage and atext.find(asig) < 0:
                    atext = asig + '\n' + atext
                self.WriteText(f, atext.replace(chr(13), ''))
            if not araw:
                self.WriteASPPageEnd(f, fname)
        finally:
            self.FileClose(f)


class SourceEventSection:

    def __init__(self, aevent, aobj):
        self.Event = aevent
        self.Obj = aobj.AsObject()
        self.OID = aobj.OID
        self.Group = aobj.Group
        self.Key = aobj.SectionKey
        self.Name = aobj.SectionName
        self.Text = aobj.SectionText
        self.Type = aobj.SectionType
        self.Description = aobj.Description

    def IsValid(self, agroup=None, atype=None, akey=None, aname=None):
        if agroup:
            if type(agroup) == type([]):
                if not self.Group in agroup:
                    return 0
            else:
                if self.Group != agroup:
                    return 0
        if atype:
            if type(atype) == type([]):
                if not self.Type in atype:
                    return 0
            else:
                if self.Type != atype:
                    return 0
        if akey:
            if type(akey) == type([]):
                if not self.Key in akey:
                    return 0
            else:
                if self.Key != akey:
                    return 0
        if aname:
            if type(aname) == type([]):
                if not self.Name in aname:
                    return 0
            else:
                if self.Name != aname:
                    return 0
        return 1

    def GetText(self, thisParam = None):
        if thisParam is None:
            thisParam = {}
        oevent = self.Event.ReplDictContainer.repldict.get('thisSection', None)
        oparam = self.Event.ReplDictContainer.repldict.get('thisParam', None)
        self.Event.ReplDictContainer.repldict['thisSection'] = self
        self.Event.ReplDictContainer.repldict['thisParam'] = thisParam
        atext = ICORUtil.GetTextAsHTMLText(self.Text, repldict=self.Event.ReplDictContainer.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='EventSection ' + str(self.OID) + ' ' + self.Group + ' ' + self.Key)
        if thisParam.has_key('_default'):
            thisParam[thisParam['_default']]=atext
        self.Event.ReplDictContainer.repldict['thisSection'] = oevent
        self.Event.ReplDictContainer.repldict['thisParam'] = oparam
        return atext


class SourceEvent:

    def __init__(self, aobj, acontext=None, arepldictcontainer=None):
        if not acontext:
            acontext = self
        self.Context = acontext
        if not arepldictcontainer:
            arepldictcontainer = self
            self.repldict = {}
        self.ReplDictContainer = arepldictcontainer
        self.OID = aobj.OID
        self.Name = aobj.EventKind.EventName
        self.Key = aobj.EventKey
        self.Source = aobj.EventSource
        self.Sections = []
        xobj = aobj.Sections
        while xobj:
            asection = SourceEventSection(self, xobj)
            self.Sections.append(asection)
            xobj.Next()

    def GetSections(self, agroup=None, atype=None, akey=None, aname=None):
        for asection in self.Sections:
            if asection.IsValid(agroup, atype, akey, aname):
                yield asection
