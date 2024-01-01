from icorlib.icorinterface import *
from CLASSES_Library_NetBase_Utils_XMLUtil import *
from CLASSES_Library_ICORBase_Interface_ICORTextFile import TextFile
from CLASSES_Library_ICORBase_Interface_ICORSummary import DoSummaryLoad, DoSummarySave
import CLASSES_Library_ICORBase_Interface_ICORSecurity as ICORSecurity
#from xml.parsers import xmllib
import xmllib
import os
import string

MenuXMLException = 'MenuXMLException'


class XMLMenuImporter(xmllib.XMLParser):

    def __init__(self):
        xmllib.XMLParser.__init__(self)
        self.lines = []

    def Parse(self, amenu, fname):
        self.reset()
        self.wwwmenulist = [amenu, ]
        self.elements = {}
        self.elements['MENUSTRUCTURE'] = (self.start_MENUSTRUCTURE, self.end_MENUSTRUCTURE)
        self.elements['MENUITEM'] = (self.start_MENUITEM, self.end_MENUITEM)
        self.elements['SUBMENUS'] = (self.start_SUBMENUS, self.end_SUBMENUS)
        self.elements['MENUPAGEHTML'] = (self.start_MENUPAGEHTML, self.end_MENUPAGEHTML)
        self.elements['MENUPAGEHTMLLINE'] = (self.start_MENUPAGEHTMLLINE, self.end_MENUPAGEHTMLLINE)
        self.elements['MENUPAGEHTMLINFO'] = (self.start_MENUPAGEHTMLINFO, self.end_MENUPAGEHTMLINFO)
        self.elements['MENUPAGEHTMLINFOLINE'] = (self.start_MENUPAGEHTMLINFOLINE, self.end_MENUPAGEHTMLINFOLINE)
        self.elements['REPORTS'] = (self.start_REPORTS, self.end_REPORTS)
        self.elements['REPORTITEM'] = (self.start_REPORTITEM, self.end_REPORTITEM)
        self.elements['SUMMARIES'] = (self.start_SUMMARIES, self.end_SUMMARIES)
        self.elements['SUMMARYITEM'] = (self.start_SUMMARYITEM, self.end_SUMMARYITEM)
        self.afile = FilePathAsSystemPath(fname)
        fsize = os.path.getsize(self.afile)
        fin = TextFile(self.afile, 'r')
        i = 0
        try:
            s = fin.readline()
            while s != '':
                self.feed(s[:-1])
                i = i + 1
                if i >= 12:
                    i = 0
                    apos = fin.tell()
                    SetProgress(apos, fsize)
                s = fin.readline()
            self.close()
        finally:
            fin.close()
            SetProgress(0, 0)

    def start_MENUSTRUCTURE(self, attrs):
        pass

    def start_MENUITEM(self, attrs):
        wc, wn = attrs.has_key('Caption'), attrs.has_key('Name')
        if wc and not wn:
            acaption = GetXMLStringAsString(attrs['Caption'])
            aname = acaption
        elif not wc and wn:
            aname = GetXMLStringAsString(attrs['Name'])
            acaption = aname
        elif wc and wn:
            aname = GetXMLStringAsString(attrs['Name'])
            acaption = GetXMLStringAsString(attrs['Caption'])
        else:
            raise MenuXMLException, "MENUITEM doesn't has Caption or Name tag."
        if string.find(aname, '&#') >= 0:
            aname = GetXMLStringAsString(aname)
        if string.find(acaption, '&#') >= 0:
            acaption = GetXMLStringAsString(acaption)


#      aname,acaption='TEST11','TEST11'
        pmenu = self.wwwmenulist.pop()
        aaction = attrs.get('Action', '')
        bmenu = pmenu.NewMenu(aname=aname, acaption=acaption, aaction=aaction)
        la = ['ParamItem', 'ParamSubItem', 'ParamValue1', 'ParamValue2', 'ParamValue3', 'AsPageSubCaption', 'AsPageDescription', 'AsPageShortDescription', 'AsPageCaption', 'ConfirmHRef']
        for sfn in la:
            sfv = GetXMLStringAsString(attrs.get(sfn, ''))
            if sfv:
                mfield = bmenu.MenuClass.FieldsByName(sfn)
                if mfield:
                    mfield[bmenu.oid] = sfv
        if attrs.get('AccessLevel', ''):
            bmenu.AccessLevel = ICORSecurity.GetStringAsAccessLevelRefs(GetXMLStringAsString(attrs.get('AccessLevel', '')))
        if attrs.get('AccessLevelEdit', ''):
            bmenu.AccessLevelEdit = ICORSecurity.GetStringAsAccessLevelRefs(GetXMLStringAsString(attrs.get('AccessLevelEdit', '')))
        if attrs.get('AccessLevelStored', ''):
            bmenu.AccessLevelStored = ICORSecurity.GetStringAsAccessLevelRefs(GetXMLStringAsString(attrs.get('AccessLevelStored', '')))
        pmenu.AddChildMenu(bmenu)
        if attrs.has_key('worksheetqueryid'):
            bmenu.WorkSheetQueriesIDs = GetXMLStringAsString(attrs.get('worksheetqueryid', ''))
        self.wwwmenulist.append(pmenu)
        self.wwwmenulist.append(bmenu)

    def start_SUBMENUS(self, attrs):
        pass

    def end_SUBMENUS(self):
        pass

    def end_MENUITEM(self):
        #      print 'end_MENUITEM'
        self.wwwmenulist.pop()

    def end_MENUSTRUCTURE(self):
        pass

    def handle_data(self, data):
        self.lines.append(data)

    def start_MENUPAGEHTML(self, attrs):
        self.lines = []

    def end_MENUPAGEHTML(self):
        s = string.join(self.lines, '')
        if s:
            pmenu = self.wwwmenulist.pop()
            pmenu.PageHTML = s
            self.wwwmenulist.append(pmenu)
        self.lines = []

    def start_MENUPAGEHTMLLINE(self, attrs):
        pass

    def end_MENUPAGEHTMLLINE(self):
        self.lines.append('\n')

    def start_MENUPAGEHTMLINFO(self, attrs):
        self.lines = []

    def end_MENUPAGEHTMLINFO(self):
        s = string.join(self.lines, '')
        if s:
            pmenu = self.wwwmenulist.pop()
            pmenu.PageHTMLInfo = s
            self.wwwmenulist.append(pmenu)
        self.lines = []

    def start_MENUPAGEHTMLINFOLINE(self, attrs):
        pass

    def end_MENUPAGEHTMLINFOLINE(self):
        self.lines.append('\n')

    def start_REPORTS(self, attrs):
        pass

    def end_REPORTS(self):
        pass

    def start_REPORTITEM(self, attrs):
        pmenu = self.wwwmenulist.pop()
        sclass = pmenu.MenuClass.Report.ClassOfType
        soid = sclass.AddObject()
        sclass.ParentMenu[soid] = [pmenu.oid, pmenu.MenuClass.CID]
        sclass.Name[soid] = attrs.get('Name', '')
        sclass.PageMethod[soid] = attrs.get('PageMethod', '')
        sclass.PageMethodEvent[soid] = attrs.get('PageMethodEvent', '')
        pmenu.AddReport(soid)
        self.wwwmenulist.append(pmenu)

    def end_REPORTITEM(self):
        pass

    def start_SUMMARIES(self, attrs):
        pass

    def end_SUMMARIES(self):
        pass

    def start_SUMMARYITEM(self, attrs):
        pmenu = self.wwwmenulist.pop()
        sclass = pmenu.MenuClass.Summaries.ClassOfType
        soid = sclass.AddObject()
        sclass.ParentMenu[soid] = [pmenu.oid, pmenu.MenuClass.CID]
        sclass.CustomPageByMethod[soid] = attrs.get('CustomPageByMethod', '')
        sclass.DisableInHTMLReport[soid] = attrs.get('DisableInHTMLReport', '')
        sclass.Name[soid] = attrs.get('Name', '')
        sclass.Parameter[soid] = attrs.get('Parameter', '')
        sclass.ShowParameters[soid] = attrs.get('ShowParameters', '')
        bclass = aICORDBEngine.Classes[attrs.get('SummaryClass', '')]
        if bclass is not None:
            bsummoid = DoSummaryLoad(attrs.get('SummaryText', ''), ainteractive=0, ownerClass=bclass)
            if bsummoid >= 0:
                sclass.Summary[soid] = str(bsummoid)
            pmenu.AddSummary(soid, asumminfo=1, anocreatesummaryitem=1)
        else:
            print 'unknown summary for class:', attrs.get('SummaryClass', '')
        self.wwwmenulist.append(pmenu)

    def end_SUMMARYITEM(self):
        pass


class XMLMenuExporter:

    def __init__(self):
        pass

    def XMLExportSubItems(self, anode, afile, aheader=1):
        if aheader:
            afile.write('<?xml version="1.0" encoding="Windows-1250"?>\n\n')
            afile.write('<MENUSTRUCTURE>\n\n')
        for asubnode in anode.SubMenus:
            self.XMLExportSingleItem(asubnode, afile)
        if aheader:
            afile.write('\n</MENUSTRUCTURE>\n')

    def XMLExportSingleItem(self, anode, afile, alevel=0):
        aspc, schr, sma = '', '', ''
        if anode.Caption != anode.AsPageCaption:
            aspc = anode.AsPageCaption
        if anode.ConfirmHRef:
            schr = '1'
        if anode.Action != 'MenuAsPage':
            sma = anode.Action
        adict = {
            'AccessLevel': GetAsXMLString(ICORSecurity.GetAccessLevelRefsAsString(anode.AccessLevel)),
            'AccessLevelEdit': GetAsXMLString(ICORSecurity.GetAccessLevelRefsAsString(anode.AccessLevelEdit)),
            'AccessLevelStored': GetAsXMLString(ICORSecurity.GetAccessLevelRefsAsString(anode.AccessLevelStored)),
            'ParamItem': GetAsXMLString(anode.ParamItem),
            'ParamSubItem': GetAsXMLString(anode.ParamSubItem),
            'ParamValue1': GetAsXMLString(anode.ParamValue1),
            'ParamValue2': GetAsXMLString(anode.ParamValue2),
            'ParamValue3': GetAsXMLString(anode.ParamValue3),
            'AsPageSubCaption': GetAsXMLString(anode.AsPageSubCaption),
            'AsPageDescription': GetAsXMLString(anode.AsPageDescription),
            'AsPageShortDescription': GetAsXMLString(anode.AsPageShortDescription),
            'AsPageCaption': GetAsXMLString(aspc),
            'ConfirmHRef': schr,
            'Action': sma, }
        afile.write('%s<MENUITEM Caption="%s"' % ('  ' * alevel, GetAsXMLString(anode.Caption)))
        for akey, avalue in adict.items():
            if avalue:
                afile.write(' %s="%s"' % (akey, avalue))
        afile.write('>')
        wnl = 0
        s = anode.PageHTML
        if s:
            wnl = 1
            afile.write('\n%s<MENUPAGEHTML>\n' % ('  ' * (alevel + 1), ))
            sl = string.split(string.replace(s, chr(13), ''), '\n')
            for s in sl:
                afile.write('%s<MENUPAGEHTMLLINE>%s</MENUPAGEHTMLLINE>\n' % ('  ' * (alevel + 2), GetAsXMLString(s)))
            afile.write('%s</MENUPAGEHTML>' % ('  ' * (alevel + 1), ))
        s = anode.PageHTMLInfo
        if s:
            wnl = 1
            afile.write('\n%s<MENUPAGEHTMLINFO>\n' % ('  ' * (alevel + 1), ))
            sl = string.split(string.replace(s, chr(13), ''), '\n')
            for s in sl:
                afile.write('%s<MENUPAGEHTMLINFOLINE>%s</MENUPAGEHTMLINFOLINE>\n' % ('  ' * (alevel + 2), GetAsXMLString(s)))
            afile.write('%s</MENUPAGEHTMLINFO>' % ('  ' * (alevel + 1), ))
        if anode.Reports:
            wnl = 1
            afile.write('\n%s<REPORTS>\n' % ('  ' * (alevel + 1), ))
            while anode.Reports:
                afile.write('%s<REPORTITEM Name="%s" PageMethod="%s" PageMethodEvent="%s">\n' % ('  ' * (alevel + 2), GetAsXMLString(anode.Reports.Name[anode.Reports.OID]), GetAsXMLString(anode.Reports.PageMethod[anode.Reports.OID]), GetAsXMLString(anode.Reports.PageMethodEvent[anode.Reports.OID]), ))
                afile.write('%s</REPORTITEM>\n' % ('  ' * (alevel + 2), ))
                anode.Reports.Next()
            afile.write('%s</REPORTS>' % ('  ' * (alevel + 1), ))
        if anode.Summaries:
            wnl = 1
            afile.write('\n%s<SUMMARIES>\n' % ('  ' * (alevel + 1), ))
            while anode.Summaries:
                summoid = anode.Summaries.Summary[anode.Summaries.OID]
                tpath, summarytext = '', ''
                if summoid:
                    summoid = int(summoid)
                    sclass = aICORDBEngine.Classes['CLASSES_System_SummaryItem']
                    scid = sclass.OwnerCID.ValuesAsInt(summoid)
                    tclass = aICORDBEngine.Classes[scid]
                    if tclass is not None:
                        tpath = tclass.ClassPath
                        summarytext = DoSummarySave(summoid)
                if tpath:
                    afile.write('%s<SUMMARYITEM Name="%s" CustomPageByMethod="%s" Parameter="%s" DisableInHTMLReport="%d" ShowParameters="%d" SummaryClass="%s" SummaryText="%s">\n' %
                                ('  ' * (alevel + 2), GetAsXMLString(anode.Summaries.Name[anode.Summaries.OID]), GetAsXMLString(anode.Summaries.CustomPageByMethod[anode.Summaries.OID]), GetAsXMLString(anode.Summaries.Parameter[anode.Summaries.OID]), anode.Summaries.DisableInHTMLReport.ValuesAsInt(anode.Summaries.OID), anode.Summaries.ShowParameters.ValuesAsInt(anode.Summaries.OID), GetAsXMLString(tpath), GetAsXMLString(summarytext),
                                 ))
                    afile.write('%s</SUMMARYITEM>\n' % ('  ' * (alevel + 2), ))
                anode.Summaries.Next()
            afile.write('%s</SUMMARIES>' % ('  ' * (alevel + 1), ))
        if anode.SubMenus:
            wnl = 1
            afile.write('\n%s<SUBMENUS>\n' % ('  ' * (alevel + 1), ))
            for asubnode in anode.SubMenus:
                self.XMLExportSingleItem(asubnode, afile, alevel + 2)
            afile.write('%s</SUBMENUS>' % ('  ' * (alevel + 1), ))
        if wnl:
            afile.write('\n%s</MENUITEM>\n' % (('  ' * alevel), ))
        else:
            afile.write('</MENUITEM>\n')
