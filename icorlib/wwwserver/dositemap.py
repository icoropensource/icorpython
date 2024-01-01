# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from CLASSES_Library_NetBase_WWW_Server_DoSummaryExecute import GenerateSummaryExecute
import re
import types


class ICORWWWServer:

    def __init__(self, aname='Default'):
        self.srvclass = aICORDBEngine.Classes['CLASSES\Library\NetBase\WWW\Server']
        self.OID = self.srvclass.Name.Identifiers(aname)
        if self.OID < 0:
            raise exception, 'Bad server name!'
        self.indent = '&nbsp;' * 8
        self.toclist = [1]
        self.Pattern = None

    def Generate(self, afile, amenu, atext='', areport=0, ashowinfo=0, ashowfromrootmenu=0, ashowasmsword=0, afirsttocnumber=None, ashownotvisible=0, ashowprobablynotvisible=0, adonotshowreportdisabled=0):
        self.UID = amenu.uid
        self.FirstTOCNumber = afirsttocnumber
        self.ShowFromRootMenu = ashowfromrootmenu
        self.ShowNotVisible = ashownotvisible
        self.ShowProbablyNotVisible = ashowprobablynotvisible
        self.DoNotShowReportDisabled = adonotshowreportdisabled
        self.file = afile
        if atext:
            self.Pattern = re.compile(atext, re.I)
        self.Report = areport
        self.ShowInfo = ashowinfo
        self.ShowAsMSWord = ashowasmsword
        if not self.Report:
            self.file.write('<font size="-2">')

        if self.FirstTOCNumber == 0:
            self.TOCSearched = 0
        elif self.FirstTOCNumber is not None:
            self.toclist = [self.FirstTOCNumber]
            self.TOCSearched = 1
        else:
            self.TOCSearched = 1

        if self.ShowFromRootMenu:
            self.srvclass.Menu.ForEachRefObject(self.PrepareTOCList, self.OID, amenu.oid)
            self.GenerateMenuItem(self.srvclass.Menu.ClassOfType, amenu.oid, 0)
        else:
            self.srvclass.Menu.ForEachRefObject(self.GenerateMenuItem, self.OID, 0)
        if not self.Report:
            self.file.write('</font>')

    def GetToc(self):
        if self.FirstTOCNumber is not None:
            sl = []
            for aid in self.toclist:
                if isinstance(aid, types.StringTypes):
                    sl.append(aid)
                else:
                    sl.append(str(aid))
            return string.join(sl, '.')
        return ''

    def PrepareTOCList(self, aclass, aoid, coid):
        if self.TOCSearched:
            return
        if aoid == coid:
            self.TOCSearched = 1
            return
        amenu = ICORWWWMenuItem(0, aoid)
        if not amenu.IsVisibleByProfile(self.UID):
            return
        if self.DoNotShowReportDisabled:
            if amenu.DisableInReport:
                return
        if aclass.SubMenu[aoid] != '':
            self.toclist.append(1)
            aclass.SubMenu.ForEachRefObject(self.PrepareTOCList, aoid, coid)
            self.toclist.pop()
        x = self.toclist.pop()
        self.toclist.append(x + 1)

    def GenerateMenuItem(self, aclass, aoid, alevel):
        amenu = ICORWWWMenuItem(0, aoid)
        if not amenu.IsVisibleByProfile(self.UID):
            return
        if self.DoNotShowReportDisabled:
            if amenu.DisableInReport:
                return
        acaption = amenu.Caption

        w = 1
        if self.Pattern:
            aindent = ''
            if not self.Pattern.search(acaption):
                w = 0
        elif self.Report:
            w = 2
            aindent = ''
        elif self.ShowNotVisible or self.ShowProbablyNotVisible:
            aindent = ''
            w = 3
            sref = amenu.Summaries
            while sref:
                if sref.CustomPageByMethod[sref.OID] != '':
                    w = 4
                    break
                sref.Next()
            if not w:
                sref = amenu.Reports
                while sref:
                    if sref.PageMethod[sref.OID] != '':
                        w = 4
                        break
                    sref.Next()
        else:
            aindent = self.indent * alevel

        if w == 1:
            self.file.write('<span style="WHITE-SPACE:nowrap;">%s<a class=reflistoutnavy HREF="%s" ' % (aindent, amenu.GetMenuRef()))
            self.file.write('>%s %s</a></span><br>\n' % (self.GetToc(), acaption))
        elif w == 2:
            self.file.write('<h1>%s %s</h1>\n' % (self.GetToc(), acaption))
            if self.ShowInfo:
                if amenu.AsPageCaption:
                    self.file.write('<center><P><b>%s</b></P></center>\n' % amenu.AsPageCaption)
                if amenu.AsPageSubCaption:
                    self.file.write('<center><P><i><small>%s</small></i></P></center>\n' % amenu.AsPageSubCaption)
                s = amenu.AsPageDescription
                if s:
                    self.file.write('<p><i>%s</i></p><br>\n' % s)
                self.file.write(amenu.PageHTMLInfo)
            else:
                self.file.write(amenu.PageHTML)
                self.ProcessMenuAttributes(amenu)
        elif w == 3:
            self.file.write('<span style="WHITE-SPACE:nowrap;">%s<a class=reflistoutnavy HREF="%s" ' % (aindent, amenu.GetMenuRef()))
            self.file.write('>%s %s</a></span><br>\n' % (self.GetToc(), acaption))
        elif w == 4:
            self.file.write('<span style="WHITE-SPACE:nowrap;">%s<font size="+1"><b><a class=reflistoutnavy HREF="%s" ' % (aindent, amenu.GetMenuRef()))
            self.file.write('>%s %s</a></b></font></span><br>\n' % (self.GetToc(), acaption))
        if aclass.SubMenu[aoid] != '':
            self.toclist.append(1)
            aclass.SubMenu.ForEachRefObject(self.GenerateMenuItem, aoid, alevel + 1)
            self.toclist.pop()
        x = self.toclist.pop()
        if type(x) != type(1):
            self.toclist.append(x)
        else:
            self.toclist.append(x + 1)

    def ProcessMenuAttributes(self, amenu):
        formdict = {}
        if self.ShowAsMSWord:
            formdict['MIMEWord'] = '1'
        formdict['SimpleSummary'] = '1'
        sref = amenu.Summaries
        while sref:
            soid = sref.Summary[sref.OID]
            try:
                soid = int(soid)
            except:
                soid = -1
            if soid >= 0:
                GenerateSummaryExecute(self.file, soid, formdict)

            wref = sref.WorksheetQueries.GetRefList(sref.OID)
            while wref:
                self.file.write(wref.Class.TextAsHTML[wref.OID])
                wref.Next()

            if not self.ShowAsMSWord:
                mname = sref.CustomPageByMethod[sref.OID]
                if mname != '':
                    mname = mname.replace('\\', '_')
                    mname = mname.replace('/', '_')
                    pagemethod = __import__(mname)
                    pageevent = getattr(pagemethod, 'DoCustomPageByMethod')
                    aparam = sref.Parameter[sref.OID]
                    if pageevent is not None:
                        apply(pageevent, (self.file, amenu, amenu.uid, aparam))
            sref.Next()


def DoSiteMap(amenu, file):
    aserver = ICORWWWServer()
    aserver.Generate(file, amenu, afirsttocnumber=1)


def DoSearchMenu(amenu, atext, file):
    aserver = ICORWWWServer()
    aserver.Generate(file, amenu, atext)


def DoReportMenu(amenu, file, ashowinfo, ashowasmsword, afirsttocnumber):
    aserver = ICORWWWServer()
    print 'ashowasmsword', ashowasmsword
    aserver.Generate(file, amenu, '', 1, ashowinfo, ashowfromrootmenu=1, ashowasmsword=ashowasmsword, afirsttocnumber=afirsttocnumber, adonotshowreportdisabled=1)


def DoSiteMapReportNonVisibleMenus(amenu, file):
    aserver = ICORWWWServer()
    aserver.Generate(file, amenu, ashowfromrootmenu=1, afirsttocnumber=1, ashownotvisible=1, ashowprobablynotvisible=1, adonotshowreportdisabled=1)


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
