# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mhtmlsqlgen2 as mhtmlsqlgen2
import icorlib.projekt.mhtmlsqlgenlib as mhtmlsqlgenlib
import icorlib.projekt.msqllib as msqllib
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.projekt.mcrmlib as MCRMLib
import icorlib.projekt.mcrmxmlinterface as MCRMXMLInterface
import icorlib.projekt.mhtmlsqlpivotgen as mhtmlsqlpivotgen
import icorlib.projekt.mcrmwwwmenulib as mwwwmenulib
import CLASSES_Library_NetBase_WWW_HTML_Tree_SimpleLinks_Main as SimpleHTMLTree
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icordbmain.adoutil as ADOLibInit
import icorlib.icorsecurity as ICORSecurity
import string
import random
import re
import os
import icordbmain.dbaccess as dbaccess
import appplatform.startutil as startutil


class TableLink:

    def __init__(self, asrctable, adsttableoid, asrcfield, adstfield, awwwdisabledtable, alinktabid, alinkconstraint, aoid=-1, aistableview=0, alinkname='', aLinkHrefCaptionNewItem='', acmsdisabledtable=0, aisextension=0, aisinternaltab=0, aidmodelxml=0, aislocationbackdisabled=0):
        self.OID = aoid
        self.SrcTable = asrctable
        self.DstTableOID = adsttableoid
        self.SrcFieldStr = asrcfield
        self.SrcField = string.split(asrcfield, ',')
        self.DstFieldStr = adstfield
        self.DstField = string.split(adstfield, ',')
        self.LinkFields = zip(self.SrcField, self.DstField)
        self.LinkName = alinkname
        self.WWWDisabledTable = awwwdisabledtable
        self.TabID = alinktabid
        self.LinkConstraint = alinkconstraint
        self.IsTableView = aistableview
        self.LinkHrefCaptionNewItem = aLinkHrefCaptionNewItem
        self.CMSDisabledTable = acmsdisabledtable
        self.IsExtension = aisextension
        self.IsInternalTab = aisinternaltab
        self.IDModelXML = aidmodelxml
        self.IsLocationBackDisabled = aislocationbackdisabled

    def __getattr__(self, name):
        if name == 'DstTable':
            return self.SrcTable.CRM.sourcetables[self.DstTableOID]

    def __repr__(self):
        return 'TableLink: %s[%s] --> %s[%s] (%d)' % (self.SrcTable, self.SrcFieldStr, self.DstTable, self.DstFieldStr, self.IsTableView)

    def __str__(self):
        return 'TableLink: %s[%s] --> %s[%s] (%d)' % (self.SrcTable, self.SrcFieldStr, self.DstTable, self.DstFieldStr, self.IsTableView)

    def GetModelXMLData(self):
        if not self.IDModelXML:
            return None
        adsttable = self.DstTable
        for axmldata in adsttable.xmldata:
            if axmldata.OID == self.IDModelXML:
                return axmldata
        return None

    def DumpAsXML(self, file, arecur, aindent=0, aaddobligatoryfields=0):
        alinkid = 'link_' + str(self.SrcTable.OID) + '_' + str(self.DstTableOID)
        if arecur.has_key(alinkid):
            return
        arecur[alinkid] = 1
        file.write('%s<TABLELINK srcoid="%d" dstoid="%d" srcfield="%s" dstfield="%s" linkconstraint="%s" istableview="%d" linkhrefcaptionnewitem="%s" isextension="%d" idmodelxml="%d" islocationbackdisabled="%d">\n' %
                   (' ' * aindent, self.SrcTable.OID, self.DstTableOID, self.SrcFieldStr, self.DstFieldStr, XMLUtil.GetAsXMLStringNoPL(self.LinkConstraint), self.IsTableView, XMLUtil.GetAsXMLStringNoPL(self.LinkHrefCaptionNewItem), self.IsExtension, self.IDModelXML, self.IsLocationBackDisabled))
        self.DstTable.DumpAsXML(file, arecur, aindent + 3, afromlinkid=self.SrcTable.OID, aaddobligatoryfields=aaddobligatoryfields)
        file.write('%s</TABLELINK>\n' % (' ' * aindent, ))
        del arecur[alinkid]


class SecurityDisabled:

    def __init__(self):
        self.OID = ''
        self.Nazwa = 'Disabled'
        self.AccessLevelDelete = '11:401:'
        self.AccessLevelEdit = '11:401:'
        self.AccessLevelFilesUpload = '11:401:'
        self.AccessLevelView = '11:401:'


class SecurityViewOnly:

    def __init__(self, aaccesslevelview=''):
        self.OID = ''
        self.Nazwa = 'ViewOnly'
        self.AccessLevelDelete = '11:401:'
        self.AccessLevelEdit = '11:401:'
        self.AccessLevelFilesUpload = '11:401:'
        self.AccessLevelView = aaccesslevelview


class SourceTable(MCRMLib.MCRMItemBase):

    def __repr__(self):
        return self.Nazwa

    def Process(self, bobj):
        import icorlib.projekt.mhtmlsqlgentable as MHTMLSQLGenTable
        if self.InProcess:
            return
        self.InProcess = 1
        self.Nazwa = bobj.Nazwa
        self.Name = self.Nazwa
        self.NazwaTabeli = bobj.NazwaTabeli
        self.Klucz = bobj.Klucz
        #      try:
        self.DataBaseName = startutil.GetStrEnv(bobj.Projekt.DBAccess.DataBaseName)
        self.DataBaseOwner = bobj.Projekt.DBAccess.DataBaseOwner
        #      except:
        #         self.DataBaseName=''
        #         self.DataBaseOwner=''
        self.TablePrefix = ''
        if self.DataBaseName:
            self.TablePrefix = self.DataBaseName + '.' + self.DataBaseOwner + '.'
        if not self.NazwaTabeli:
            self.NazwaTabeli = bobj.Nazwa
        self.NazwaObiektu = bobj.NazwaObiektu
        if not self.NazwaObiektu:
            self.NazwaObiektu = self.NazwaTabeli
        print 'Create source table: %s - %s.%s.%s' % (bobj.OID, self.DataBaseName, self.DataBaseOwner, self.Nazwa, )
        self.OID = bobj.OID
        self.ClassItem = bobj.Class
        self.IsVersionControl = bobj.Class.IsVersionControl.ValuesAsInt(bobj.OID)
        self.IsSecurityEnabled = bobj.Class.IsSecurityEnabled.ValuesAsInt(bobj.OID)
        self.SQLTable = self.CRM.SQLCreator.AddTable('BZR', bobj.OID, bobj.Nazwa, aisexternal=1, asingleobjectname=bobj.NazwaObiektu, ahasversions=self.IsVersionControl, aissecurityenabled=self.IsSecurityEnabled, adbname=self.DataBaseName, adbowner=self.DataBaseOwner, agenerateenable=self.GenerateEnable)
        self.VersionSQLTable = None
        if self.IsVersionControl:
            print '  Create version source table: %s - %s.%s.%s' % (bobj.OID, self.DataBaseName, self.DataBaseOwner, self.Nazwa, )
            self.VersionSQLTable = self.CRM.SQLCreator.AddTable('BZR_V', bobj.OID, bobj.Nazwa, aisexternal=1, asingleobjectname=bobj.NazwaObiektu, aisversioncontrol=1, aissecurityenabled=self.IsSecurityEnabled, adbname=self.DataBaseName, adbowner=self.DataBaseOwner, agenerateenable=self.GenerateEnable)
            self.SQLTable.VersionTable = self.VersionSQLTable
            self.VersionSQLTable.SQLBaseTable = self.SQLTable
        arepldict = {'aCRM': self.CRM, 'this': self}
        fobj = bobj.Pola
        while fobj:
            tobj = fobj.TypPolaDotyczy
            if not tobj:
                print '  *** %s.%s nie posiada typu! ***' % (self.SQLTable.NameSQL, fobj.Name)
            else:
                sprettyname = fobj.NazwaWidoczna
                if not sprettyname:
                    sprettyname = fobj.Nazwa
                dstobj = fobj.ZrodloDanychSlownika
                if dstobj:
                    adstoid = dstobj.OID
                else:
                    adstoid = -1
                aextdictconstraint = ICORUtil.GetTextAsHTMLText(fobj.ExtDictConstraint, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Table ExtDictConstraint: ' + str(self.OID))
                sobj = fobj.SGSortStyle
                if sobj:
                    asortstyle = sobj.Class.StyleID.ValuesAsInt(sobj.OID)
                else:
                    asortstyle = 0
                afield=self.SQLTable.AddField(fobj.NazwaID,tobj.Nazwa,tobj.Rozmiar,aprettyname=sprettyname, \
                   aisaliased=fobj.Class.SGIsAliased.ValuesAsInt(fobj.OID),aisinteractive=fobj.Class.SGIsInteractive.ValuesAsInt(fobj.OID), \
                   aissearch=fobj.Class.SGIsSearch.ValuesAsInt(fobj.OID),atabposition=fobj.Class.SGTabIndex.ValuesAsInt(fobj.OID),aisobligatory=fobj.Class.SGIsObligatory.ValuesAsInt(fobj.OID),aisindexed=fobj.Class.SGIsIndexed.ValuesAsInt(fobj.OID), afilter=tobj.Filtr,alowercase=tobj.Class.Lowercase.ValuesAsInt(tobj.OID),amask=tobj.Maska,anospace=tobj.Class.NoSpace.ValuesAsInt(tobj.OID),aregex=tobj.Regex,aunsigned=tobj.Class.Unsigned.ValuesAsInt(tobj.OID),auppercase=tobj.Class.Uppercase.ValuesAsInt(tobj.OID),anopastdate=tobj.Class.NiedopuszczalnaDataPrzeszla.ValuesAsInt(tobj.OID),adictsourcetable=adstoid,aminvalue=fobj.SGMinValue,amaxvalue=fobj.SGMaxValue,aisunique=fobj.Class.SGIsUnique.ValuesAsInt(fobj.OID),atypecaption=tobj.Caption,adictvalues=fobj.WartosciSlownika,atypedescription=tobj.Opis, \
                   atextcols=fobj.Class.TextCols.ValuesAsInt(fobj.OID),atextrows=fobj.Class.TextRows.ValuesAsInt(fobj.OID),atextnowrap=fobj.Class.TextNoWrap.ValuesAsInt(fobj.OID),aextdictconstraint=aextdictconstraint,asortstyle=asortstyle, \
                   aissingleviewhidden=fobj.Class.SGIsSingleViewHidden.ValuesAsInt(fobj.OID),aisdictviewhidden=fobj.Class.SGIsDictViewHidden.ValuesAsInt(fobj.OID),aisversioncontrol=fobj.Class.SGIsVersionControl.ValuesAsInt(fobj.OID),afieldvalues=fobj.WartosciPola,afieldnamedescription=fobj.OpisNazwy,afieldvaluedescription=fobj.OpisWartosci,afieldvaluedescription2=fobj.OpisWartosci2,afieldvaluepreviewlink=fobj.SGPreviewValueLink,
                   aisu2ulink=fobj.Class.SGIsU2ULink.ValuesAsInt(fobj.OID),adefaultvalue=fobj.DomyslnaWartosc,adefaultentry=fobj.DomyslnyWpis,
                   adisabledictshowallvalues=fobj.Class.SGDisableDictShowAllValues.ValuesAsInt(fobj.OID),
                   agroup=fobj.Grupa,acolorselectedvalue=fobj.KolorWartosciWybranej,acolorbackground=fobj.KolorTla,
                   amodelxmldataidview=fobj.Class.ModelXMLDataIDView.ValuesAsInt(fobj.OID),amodelxmldataidedit=fobj.Class.ModelXMLDataIDEdit.ValuesAsInt(fobj.OID)
                   )
                afield.CID = fobj.CID
                afield.OID = fobj.OID
                if self.IsVersionControl:
                    afield=self.VersionSQLTable.AddField(fobj.NazwaID,tobj.Nazwa,tobj.Rozmiar,aprettyname=sprettyname, \
                    aisaliased=fobj.Class.SGIsAliased.ValuesAsInt(fobj.OID),aisinteractive=fobj.Class.SGIsInteractive.ValuesAsInt(fobj.OID), \
                    aissearch=fobj.Class.SGIsSearch.ValuesAsInt(fobj.OID),atabposition=fobj.Class.SGTabIndex.ValuesAsInt(fobj.OID),aisobligatory=fobj.Class.SGIsObligatory.ValuesAsInt(fobj.OID),aisindexed=fobj.Class.SGIsIndexed.ValuesAsInt(fobj.OID), afilter=tobj.Filtr,alowercase=tobj.Class.Lowercase.ValuesAsInt(tobj.OID),amask=tobj.Maska,anospace=tobj.Class.NoSpace.ValuesAsInt(tobj.OID),aregex=tobj.Regex,aunsigned=tobj.Class.Unsigned.ValuesAsInt(tobj.OID),auppercase=tobj.Class.Uppercase.ValuesAsInt(tobj.OID),anopastdate=tobj.Class.NiedopuszczalnaDataPrzeszla.ValuesAsInt(tobj.OID),adictsourcetable=adstoid,aminvalue=fobj.SGMinValue,amaxvalue=fobj.SGMaxValue,aisunique=fobj.Class.SGIsUnique.ValuesAsInt(fobj.OID),atypecaption=tobj.Caption,adictvalues=fobj.WartosciSlownika,atypedescription=tobj.Opis, \
                    atextcols=fobj.Class.TextCols.ValuesAsInt(fobj.OID),atextrows=fobj.Class.TextRows.ValuesAsInt(fobj.OID),atextnowrap=fobj.Class.TextNoWrap.ValuesAsInt(fobj.OID),aextdictconstraint=aextdictconstraint,asortstyle=asortstyle, \
                    aissingleviewhidden=fobj.Class.SGIsSingleViewHidden.ValuesAsInt(fobj.OID),aisdictviewhidden=fobj.Class.SGIsDictViewHidden.ValuesAsInt(fobj.OID),aisversioncontrol=fobj.Class.SGIsVersionControl.ValuesAsInt(fobj.OID),afieldvalues=fobj.WartosciPola,afieldnamedescription=fobj.OpisNazwy,afieldvaluedescription=fobj.OpisWartosci,afieldvaluedescription2=fobj.OpisWartosci2,afieldvaluepreviewlink=fobj.SGPreviewValueLink,
                    aisu2ulink=fobj.Class.SGIsU2ULink.ValuesAsInt(fobj.OID),adefaultvalue=fobj.DomyslnaWartosc,adefaultentry=fobj.DomyslnyWpis,
                    adisabledictshowallvalues=fobj.Class.SGDisableDictShowAllValues.ValuesAsInt(fobj.OID),
                    agroup=fobj.Grupa,acolorselectedvalue=fobj.KolorWartosciWybranej,acolorbackground=fobj.KolorTla,
                    amodelxmldataidview=fobj.Class.ModelXMLDataIDView.ValuesAsInt(fobj.OID),amodelxmldataidedit=fobj.Class.ModelXMLDataIDEdit.ValuesAsInt(fobj.OID)
                    )
                    afield.CID = fobj.CID
                    afield.OID = fobj.OID
            fobj.Next()
        self.SourceTable = None
        self.SourceTableOID = -1
        dobj = bobj.Dotyczy
        if dobj:
            self.SQLTable.AddField('_Dotyczy', 'string', '44', aisindexed=1, adictsourcetable=dobj.OID)
            if self.IsVersionControl:
                self.VersionSQLTable.AddField('_Dotyczy', 'string', '44', aisindexed=1, adictsourcetable=dobj.OID)
            self.SourceTableOID = dobj.OID
        self.LinkTablesList = []
        self.TableLinks = []
        dobj = bobj.PolaczeniaDoTabel
        while dobj:
            atl = TableLink(self, dobj.DestinationTable.OID, dobj.SourceFieldID, dobj.DestinationFieldID, dobj.Class.WWWDisabledTable.ValuesAsInt(dobj.OID), dobj.Class.LinkTabID.ValuesAsInt(dobj.OID), dobj.LinkConstraint, aoid=dobj.OID, aistableview=dobj.Class.IsTableView.ValuesAsInt(dobj.OID), alinkname=dobj.LinkName, aLinkHrefCaptionNewItem=dobj.LinkHrefCaptionNewItem, acmsdisabledtable=dobj.Class.CMSDisabledTable.ValuesAsInt(dobj.OID),
                            aisextension=dobj.Class.IsExtension.ValuesAsInt(dobj.OID), aisinternaltab=dobj.Class.IsInternalTab.ValuesAsInt(dobj.OID), aidmodelxml=dobj.Class.ModelXMLDataID.ValuesAsInt(dobj.OID), aislocationbackdisabled=dobj.Class.IsLocationBackDisabled.ValuesAsInt(dobj.OID))
            self.TableLinks.append(atl)
            dobj.Next()
        self.Tabs = []
        self.TabsByID = {}
        self.TabsByIDSecurity = {}
        tobj = bobj.Zakladki
        while tobj:
            tid = tobj.Class.ZakladkaID.ValuesAsInt(tobj.OID)
            ts = tobj.Nazwa
            tav = tobj.Class.AccessLevelView[tobj.OID]
            self.Tabs.append([tid, ts, tav])
            self.TabsByID[tid] = ts
            self.TabsByIDSecurity[tid] = tav
            self.TabsByIDSecurity[str(tid)] = tav
            tobj.Next()
        self.Tabs.sort()
        self.DocumentsTabID = bobj.Class.DocumentsTabID.ValuesAsInt(bobj.OID)
        self.LinkedTablesTabID = bobj.Class.LinkedTablesTabID.ValuesAsInt(bobj.OID)
        self.AddedHTML = []
        hobj = bobj.AddedHTML
        while hobj:
            s = string.replace(hobj.AddHTML, chr(13), '')
            arepldict = {'aCRM': self.CRM, 'this': self, 'mhtmlsqlgen': MHTMLSQLGenTable, 'MHTMLSQLGenTable': MHTMLSQLGenTable}
            s = ICORUtil.GetTextAsHTMLText(s, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Table AddHTML: ' + str(self.OID) + ' ' + str(hobj.OID))
            i = hobj.Class.ZakladkaID.ValuesAsInt(hobj.OID)
            isinternal = hobj.Class.IsInternalTab.ValuesAsInt(hobj.OID)
            self.AddedHTML.append([i, s, isinternal, hobj.Nazwa])
            hobj.Next()
        self.AddedHTML.sort()
        self.xmldata = []
        xobj = bobj.XMLData
        while xobj:
            axmldata = XMLData(self.CRM)
            axmldata.Process(xobj, anamemodifier='BZR')
            self.xmldata.append(axmldata)
            xobj.Next()
        asql = self.SQLTable.GetDefaultSearchSQL(asqlversion=self.CRM.SQLVersion)
        self.DisableDefaultSearch = asql is None
        if self.IsVersionControl:
            self.VersionSQLTable.GetDefaultVersionSQL(self.SQLTable, self.CRM)
        self.NewsletterEnabled = bobj.Class.IsNewsletterEnabled.ValuesAsInt(bobj.OID)
        self.NewsletterOIDs = []
        nobj = bobj.ListaWysylkowa
        while nobj:
            self.NewsletterOIDs.append(nobj.OID)
            nobj.Next()
        self.ASPSourceOnBeforeShowOneTable = ''
        self.ASPSourceOnAfterShowOneTable = ''
        self.ASPSourceOnBeforeShowOne = ''
        self.ASPSourceShowBefore = ''
        self.ASPSourceShowFieldsBefore = ''
        self.ASPSourceShowFieldsStart = ''
        self.ASPSourceShowFields = ''
        self.ASPSourceShowFieldsAfter = ''
        self.ASPSourceShowAfter = ''
        self.ASPSourceSubmit = ''
        self.ASPSourceSubmitBefore = ''
        self.ASPSourcePreSubmitCheck = ''
        self.ASPSourceOnDelete = ''
        self.ASPSourceOnBeforeSheetShowOneTable = ''
        self.ASPSourceOnBeforeFieldsSheetShowOneTable = ''
        self.ASPSourceOnAfterFieldsSheetShowOneTable = ''
        self.ASPSourceOnAfterSheetShowOneTable = ''
        self.ASPSourceAfterCommit = ''
        self.ASPClientBeforeSubmit = ''
        self.ASPSourceOnBeforeGetData = ''
        self.ASPSourceOnAfterSearch = ''
        self.ASPSourceOnFilter = ''
        self.ASPSourceOnFieldValue = ''
        self.OnCMSBeforeSubmit = ''
        self.AccessLevelDelete = bobj.Class.AccessLevelDelete[bobj.OID]
        self.AccessLevelEdit = bobj.Class.AccessLevelEdit[bobj.OID]
        self.AccessLevelFilesUpload = bobj.Class.AccessLevelFilesUpload[bobj.OID]
        self.AccessLevelView = bobj.Class.AccessLevelView[bobj.OID]
        self.PluginSources = []
        self.bobj = bobj.AsObject()
        self.repldict = arepldict
        self.InProcess = 0
        self.IsWritten = 0

    def ProcessTableEvents(self):
        bobj = self.bobj
        arepldict = self.repldict
        eobj = bobj.TableEvents
        while eobj:
            aename = eobj.EventKind.EventName
            if not aename in ['OnSQLCreate']:
                self.__dict__[aename] = self.__dict__.get(aename, '') + ICORUtil.GetTextAsHTMLText(eobj.EventSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Table Event: ' + str(self.OID) + ' ' + aename + ' ' + str(eobj.OID)) + '\n'
            eobj.Next()

    def GetFieldEventsObj(self, afieldname):
        fobj = self.bobj.Pola
        while fobj:
            if fobj.NazwaID == afieldname:
                return fobj.FieldEvents
            fobj.Next()
        return None

    def GetFieldEventText(self, eobj):
        arepldict = self.repldict
        aolde = arepldict.get('thisEvent', None)
        aolds = arepldict.get('thisEventContext', None)
        arepldict['thisEvent'] = eobj
        arepldict['thisEventContext'] = 'Application'
        ret = ICORUtil.GetTextAsHTMLText(eobj.EventSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='TableField Event: ' + str(self.OID) + ' ' + eobj.EventKind.EventName + ' ' + str(eobj.OID))
        if aolde is None:
            del arepldict['thisEvent']
        else:
            arepldict['thisEvent'] = aolde
        if aolds is None:
            del arepldict['thisEventContext']
        else:
            arepldict['thisEventContext'] = aolds
        return ret

    def ProcessEvents(self, aeventname, aprocessxmldata):
        lret = []
        bobj = self.bobj
        arepldict = self.repldict
        eobj = bobj.TableEvents
        while eobj:
            aename = eobj.EventKind.EventName
            if aename == aeventname:
                btext = ICORUtil.GetTextAsHTMLText(eobj.EventSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='Table Event: ' + str(self.OID) + ' ' + aename + ' ' + str(eobj.OID))
                if btext:
                    lret.append(btext)
            eobj.Next()
        if aprocessxmldata:
            for axmldata in self.xmldata:
                btext = axmldata.ProcessEvents(aeventname)
                if btext:
                    lret.append(btext)
        return '\n'.join(lret)

    def DumpAsXML(self, file, arecur, aindent=0, afromlinkid=-1, aaddobligatoryfields=0):
        if arecur.has_key('_MAX_TABLE_RECUR'):
            atablerecurcnt = 0
            for akey in arecur.keys():
                if akey[:len('sourcetable_')] == 'sourcetable_':
                    atablerecurcnt = atablerecurcnt + 1
            if atablerecurcnt > arecur['_MAX_TABLE_RECUR']:
                return
        afirst = not aindent
        if afirst:
            self.CRM.DumpAsXMLStart(file)
            aindent = aindent + 3
        if arecur.has_key('sourcetable_' + str(self.OID)):
            return
        arecur['sourcetable_' + str(self.OID)] = 1
        file.write('%s<SOURCETABLE OID="%d" name="%s">\n' % (' ' * aindent, self.OID, self.Nazwa, ))
        self.SQLTable.DumpAsXML(file, arecur, aindent + 3, aaddobligatoryfields=aaddobligatoryfields)
        if self.SourceTableOID >= 0:
            self.SourceTable = self.CRM.sourcetables[self.SourceTableOID]
            file.write('%s<BASETABLE>\n' % (' ' * (aindent + 3), ))
            self.SourceTable.SQLTable.DumpAsXML(file, arecur, aindent + 6, aaddobligatoryfields=aaddobligatoryfields)
            file.write('%s</BASETABLE>\n' % (' ' * (aindent + 3), ))
        if self.TableLinks:
            w = 0
            for atl in self.TableLinks:
                if atl.DstTable.OID != afromlinkid:
                    if not w:
                        file.write('%s<TABLELINKS>\n' % (' ' * (aindent + 3), ))
                        w = 1
                    atl.DumpAsXML(file, arecur, aindent + 6, aaddobligatoryfields=aaddobligatoryfields)
            if w:
                file.write('%s</TABLELINKS>\n' % (' ' * (aindent + 3), ))
        file.write('%s</SOURCETABLE>\n' % (' ' * aindent, ))
        del arecur['sourcetable_' + str(self.OID)]
        if afirst:
            self.CRM.DumpAsXMLFinish(file)

    def OnASPWriteFile(self, atext, aoneventparams=None):
        if aoneventparams is None:
            aoneventparams = {}
        self.FileText = atext
        aoneventparams['thisItem'] = self
        aoneventparams['thisItemType'] = 'SourceTable'
        self.CRM.ProcessEvents('OnASPWriteFile', dd=aoneventparams)
        return self.FileText

    def WriteSinglePageView(self, asqltable, adirectory, stable, asecurity):
        import icorlib.projekt.mhtmlsqlgentable as MHTMLSQLGenTable
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage

        self.PageTabCnt = 0
        self.MHTMLSQLGenTable = MHTMLSQLGenTable
        apluginsources = self.CRM.pluginsources_tables.get(self.OID, [])
        if not apluginsources:
            apluginsources = [self.CRM, ]
        l = MHTMLSQLGenTable.SQLTableGetSelectSingleASP(asqltable, btable=stable, atabs=self.Tabs, afname=asqltable.NameFile + '_sot.asp', asecurity=asecurity, aTableLinks=self.TableLinks, aeventsrc=self, apluginsources=apluginsources)
        l.insert(0, MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, atableid=self.OID, anewsletters=self.NewsletterOIDs, atabid=self.Tabs[0][0], afiletype='sot'))
        if 0:
            l.insert(2, MHTMLSQLGenTable.SQLTableGetSelectAllDocumentsForCustomerASP(self, self.CRM.Table_DokumentyKontrahentow, atabid=self.DocumentsTabID))
        for i in range(len(self.LinkTablesList)):
            btable = self.LinkTablesList[i]
            if self.TabsByID.has_key(self.LinkedTablesTabID + i + 1):
                tid = self.LinkedTablesTabID + i + 1
            else:
                tid = self.LinkedTablesTabID
            if tid == self.Tabs[0][0]:
                l.insert(2, MHTMLSQLGenTable.SQLTableGetSelectAllLinkedTablesASP(self, btable.SQLTable, atabid=tid))
            else:
                l.insert(len(l) - 1, MHTMLSQLGenTable.SQLTableGetSelectAllLinkedTablesASP(self, btable.SQLTable, atabid=tid))
        for atablelink in self.TableLinks:
            if not atablelink.WWWDisabledTable:
                #            print 'Create forward table: %s'%atablelink.DstTable.Nazwa
                lret = mhtmlsqlgen2.GetSelectLinkedTable(atablelink, aeventsrc=self, asecurity=asecurity)
                if atablelink.TabID == self.Tabs[0][0]:
                    l.insert(2, lret[0])
                else:
                    l.insert(len(l) - 1, lret[0])
                l.insert(len(l) - 1, lret[1])
        aahtmlcnt = 0
        for tid, atext, isinternal, acaption in self.AddedHTML:
            if isinternal:
                l.insert(len(l) - 1, MHTMLSQLGenTable.GetSelectTextByTabID(self, atext, tid, isinternal, aahtmlcnt, acaption))
            else:
                if tid == self.Tabs[0][0]:
                    l.insert(2, MHTMLSQLGenTable.GetSelectTextByTabID(self, atext, tid, isinternal, aahtmlcnt, acaption))
                else:
                    l.insert(len(l) - 1, MHTMLSQLGenTable.GetSelectTextByTabID(self, atext, tid, isinternal, aahtmlcnt, acaption))
            aahtmlcnt = aahtmlcnt + 1


#      if self.NewsletterEnabled:
#         atabid=self.Tabs[0][0]
#         for anewsletter in self.CRM.newsletters.values():
#            l.insert(len(l)-1,MHTMLSQLGenTable.GetNewsletterNewElement(self,anewsletter,atabid))
#      if self.CRM.newsletters:
#         atabid=self.Tabs[0][0]
#         l.insert(len(l)-1,MHTMLSQLGenTable.GetNewsletterAbstractInfo(self,atabid))
        self.WriteASP(adirectory + asqltable.NameFile + '_sot.asp', l, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'sot'})
        #self.WriteASP(adirectory+asqltable.NameFile+'_so.asp',[MHTMLSQLGenTable.GetSingleObjectFramePage(self.Tabs,asqltable.NameFile+'_sot.asp',aeventsrc=self),],araw=1)

        if len(self.Tabs) <= 1:
            #$$ self.WriteASP(adirectory+asqltable.NameFile+'_so.asp',[MHTMLSQLGenTable.GetSingleObjectFramePageTabsOne(self.Tabs,asqltable.NameFile+'_sot.asp',aeventsrc=self),],araw=1,aonaspwritefile=self.OnASPWriteFile,aoneventparams={'thisFileType':'so'})
            self.WriteASP(adirectory + asqltable.NameFile + '_so.asp', [MHTMLSQLGenTable.GetSingleObjectFramePageTabs(self.Tabs, asqltable.NameFile + '_sot.asp', asqltable.NameFile + '_so.asp', aeventsrc=self, atitle=self.Nazwa, afiletype='so'), ], araw=0, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'so'})
        else:
            self.WriteASP(adirectory + asqltable.NameFile + '_so.asp', [MHTMLSQLGenTable.GetSingleObjectFramePageTabs(self.Tabs, asqltable.NameFile + '_sot.asp', asqltable.NameFile + '_so.asp', aeventsrc=self, atitle=self.Nazwa, afiletype='so'), ], araw=0, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'so'})

    def Write(self, adirectory):
        import icorlib.projekt.mhtmlsqlgentable as MHTMLSQLGenTable
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
        #      print '  Write source table: %s - %s.%s.%s'%(self.OID,self.DataBaseName,self.DataBaseOwner,self.Nazwa,)
        self.IsWritten = 1
        self.ProcessTableEvents()
        if self.SourceTableOID >= 0:
            self.SourceTable = self.CRM.sourcetables[self.SourceTableOID]
            stable = self.SourceTable.SQLTable
        else:
            stable = None
        for doid in self.CRM.sourcetables.keys():
            btable = self.CRM.sourcetables[doid]
            if btable.SourceTableOID == self.OID:
                self.LinkTablesList.append(btable)
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_sa.asp', MHTMLSQLGenTable.SQLTableGetSelectAllASP(self.SQLTable), aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'sa'})
        self.WriteSinglePageView(self.SQLTable, adirectory, stable, self)
        if self.IsVersionControl:
            atablesecurity = SecurityViewOnly(self.AccessLevelView)
            self.WriteSinglePageView(self.VersionSQLTable, adirectory, stable, atablesecurity)
        apluginsources = self.CRM.pluginsources_tables.get(self.OID, [])
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_au.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, atableid=self.OID, anorequestform=1, afiletype='au'), MHTMLSQLGenTable.SQLTableGetAddUpdateASP(self.SQLTable, self.SourceTable, aeventsrc=self, asecurity=self, apluginsources=apluginsources)], anobodytarget=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'au'})
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_gfv.asp', [mhtmlsqlgen2.SQLTableGetSingleFieldValue(self.SQLTable, self.CRM)], araw=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'gfv'})
        if self.SourceTable is not None:
            self.WriteASP(adirectory + self.SQLTable.NameFile + '_aun.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, self.OID, afiletype='aun'), MHTMLSQLGenTable.SQLTableSelectBaseTable(self.SourceTable.SQLTable, self.SQLTable)], aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'aun'})
        if not self.DisableDefaultSearch:
            self.WriteASP(adirectory + self.SQLTable.NameFile + '_sd.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, self.OID, afiletype='sd'), MHTMLSQLGenTable.SQLTableGetSearchDataASP(self.SQLTable)], aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'sd'})
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_dr.asp', MHTMLSQLGenTable.SQLTableDeleteRemoveSingleASP(self.SQLTable, asecurity=self, aeventsrc=self, apluginsources=apluginsources), aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'dr'})
        if self.CRM.SQLVersion >= 2005:
            amainoidfieldname = self.SQLTable.NameSQLID + '__OID'
        else:
            amainoidfieldname = '_OID'
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_sv.asp', [
            mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPageTitle1(),
            MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, self.OID, afiletype='sv'),
            mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPageTitle2(),
            mhtmlsqlgen2.SQLTableGetSearchDataASPAdvanced(self.SQLTable.NameFile, self.SQLTable.FieldsByTabID, self.SQLTable.GetStoredProcedure('DefaultSearch'), string.join(self.SQLTable.DefaultSQLQuery.ThisTable.SortedFields, ','), amainoidfieldname=amainoidfieldname, aprojectoid=self.CRM.OID, achaptertable=self.SQLTable.NameSQL, aaspsourceonbeforegetdata=self.ASPSourceOnBeforeGetData, aaspsourceonaftersearch=self.ASPSourceOnAfterSearch,
                                                          aaspsourceonfilter=self.ASPSourceOnFilter, aaspsourceonfieldvalue=self.ASPSourceOnFieldValue)], anobodytarget=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'sv'})
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_svf.asp', ['', mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPicker(self.SQLTable.NameFile, self.SQLTable.FieldsByTabID, self.SQLTable.GetStoredProcedure('DefaultSearch'), string.join(self.SQLTable.DefaultSQLQuery.ThisTable.SortedFields, ','))], aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'svf'})
        for axmldata in self.xmldata:
            axmldata.Write(adirectory, asourcetable=self)

        l = []
        l.append('-- Usuniecie tabeli')
        l.append(self.SQLTable.GetDropSQL())
        l.append('-- Utworzenie tabeli')
        l.append(self.SQLTable.GetCreateTableSQL())
        for aspname, asp in self.SQLTable.StoredProcedures.items():
            l.append('-- Procedura wbudowana: ' + aspname + ' - usuniecie')
            l.append(asp.TextDrop)
            l.append('-- Procedura wbudowana: ' + aspname + ' - utworzenie')
            l.append(asp.Text)
        if self.VersionSQLTable is not None:
            l.append('-- Usuniecie tabeli wersyjnej')
            l.append(self.VersionSQLTable.GetDropSQL())
            l.append('-- Utworzenie tabeli wersyjnej')
            l.append(self.VersionSQLTable.GetCreateTableSQL())
            for aspname, asp in self.VersionSQLTable.StoredProcedures.items():
                l.append('-- Procedura wbudowana: ' + aspname + ' - usuniecie')
                l.append(asp.TextDrop)
                l.append('-- Procedura wbudowana: ' + aspname + ' - utworzenie')
                l.append(asp.Text)
        asql = string.join(l, '\n\nGO\n\n')
        self.ClassItem.SQLSource[self.OID] = asql


class SimpleTableEditor(MCRMLib.MCRMItemBase):

    def Process(self, aname, atable, aallowedit=0, aallowdelete=0, asetfieldisaliased=0):
        self.Nazwa = aname
        self.SQLTable = atable
        self.IsAllowEdit = aallowedit
        self.IsAllowDelete = aallowdelete
        if asetfieldisaliased:
            for afield in self.SQLTable.FieldsByTabID:
                if afield.Name[:1] != '_':
                    afield.IsAliased = 1

    def OnASPWriteFile(self, atext, aoneventparams=None):
        if aoneventparams is None:
            aoneventparams = {}
        self.FileText = atext
        aoneventparams['thisItem'] = self
        aoneventparams['thisItemType'] = 'SimpleTableEditor'
        self.CRM.ProcessEvents('OnASPWriteFile', dd=aoneventparams)
        return self.FileText

    def Write(self, adirectory):
        import icorlib.projekt.mhtmlsqlgentable as MHTMLSQLGenTable
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_au.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Nazwa, self.CRM, anorequestform=1, afiletype='simpleau'), MHTMLSQLGenTable.SQLTableGetAddUpdateASP(self.SQLTable)], anobodytarget=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'au'})
        self.WriteASP(adirectory + self.SQLTable.NameFile + '_sa.asp', MHTMLSQLGenTable.SQLTableGetSelectAllASP(self.SQLTable), aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'sa'})


class PageHTML(MCRMLib.MCRMItemBase):

    def __repr__(self):
        return self.Title

    def Process(self, jobj, arepldict={}, anamemodifier=''):
        self.Title = jobj.PageTitle
        self.OID = jobj.OID
        if anamemodifier:
            anamemodifier = anamemodifier + '_'
        self.PageFile = 'page_' + anamemodifier + str(self.OID) + '.asp'
        arepldict['aCRM'] = self.CRM
        arepldict['this'] = self
        self.IsPreprocessingDisabled = jobj.Class.IsPreprocessingDisabled.ValuesAsInt(jobj.OID)
        if self.IsPreprocessingDisabled:
            s = jobj.AddHTML
        else:
            s = ICORUtil.GetTextAsHTMLText(jobj.AddHTML, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='PageHTML: ' + str(self.OID))
        self.PageHTML = s
        self.IsCustomPage = jobj.Class.IsCustomPage.ValuesAsInt(jobj.OID)
        self.IsRawPage = jobj.Class.IsRawPage.ValuesAsInt(jobj.OID)
        self.AccessLevelView = jobj.Class.AccessLevelView[jobj.OID]
        self.NoCodePage = 0
        if self.IsPreprocessingDisabled and self.IsCustomPage and self.IsRawPage:
            self.NoCodePage = 1

    def OnASPWriteFile(self, atext, aoneventparams=None):
        if aoneventparams is None:
            aoneventparams = {}
        self.FileText = atext
        aoneventparams['thisItem'] = self
        aoneventparams['thisItemType'] = 'PageHTML'
        self.CRM.ProcessEvents('OnASPWriteFile', dd=aoneventparams)
        return self.FileText

    def Write(self, adirectory):
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
        if self.IsCustomPage:
            l = [self.PageHTML, ]
        else:
            l = [MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, anorequestform=1, afiletype='pagehtml'), self.PageHTML]
        self.WriteASP(adirectory + self.PageFile, l, araw=self.IsRawPage, anocodepage=self.NoCodePage, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': ''})


class UserTSQL(MCRMLib.MCRMItemBase):

    def __repr__(self):
        return self.Name

    def Process(self, jobj, arepldict={}):
        self.Name = jobj.Nazwa
        self.OID = jobj.OID
        self.ExecuteNow = jobj.Class.ExecuteNow.ValuesAsInt(jobj.OID)
        arepldict['aCRM'] = self.CRM
        arepldict['this'] = self
        self.PageHTML = ICORUtil.GetTextAsHTMLText(jobj.SQLSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='UserTSQL: ' + str(self.OID))

    def Write(self, afile):
        afile.write('\n-- START  -- USER TSQL: %s [%d]\n' % (self.Name, self.OID))
        afile.write('\nGO\n')
        afile.write(self.PageHTML)
        afile.write('\n-- FINISH -- USER TSQL: %s [%d]\n' % (self.Name, self.OID))


class SearchAction:

    def __init__(self, axmldata, aobj):
        self.OID = aobj.OID
        self.Name = aobj.Nazwa
        self.XMLData = axmldata
        self.Parameters = ICORUtil.ParseVars(aobj.Parametry, {})
        self.OnBeforeIteration = aobj.OnBeforeIteration
        self.OnIteration = aobj.OnIteration
        self.OnAfterIteration = aobj.OnAfterIteration

    def Process(self):
        arepldict = {}
        arepldict['aCRM'] = self.XMLData.CRM
        arepldict['this'] = self.XMLData
        arepldict['ActionOID'] = self.OID
        arepldict['ActionName'] = self.Name
        self.OnBeforeIteration = ICORUtil.GetTextAsHTMLText(self.OnBeforeIteration, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SearchAction OnBeforeIteration: ' + str(self.OID))
        self.OnIteration = ICORUtil.GetTextAsHTMLText(self.OnIteration, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SearchAction OnIteration: ' + str(self.OID))
        self.OnAfterIteration = ICORUtil.GetTextAsHTMLText(self.OnAfterIteration, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='SearchAction OnAfterIteration: ' + str(self.OID))


class XMLData(MCRMLib.MCRMItemBase):

    def __repr__(self):
        return 'XMLData: %s [%d]' % (self.Title, self.OID)

    def Process(self, jobj, anamemodifier=''):
        self.Title = jobj.Name
        self.OID = jobj.OID
        self.TableOID = jobj.Dotyczy.OID
        self.AutoGenerate = jobj.Class.AutoGenerate.ValuesAsInt(jobj.OID)
        if anamemodifier:
            anamemodifier = anamemodifier + '_'
        arepldict = {}
        arepldict['aCRM'] = self.CRM
        arepldict['this'] = self
        self.bobj = jobj.AsObject()
        self.repldict = arepldict
        self.ASPSourceOnBeforeGetData = ''
        self.ASPSourceOnFilter = ''
        self.ASPSourceOnFieldValue = ''
        self.ASPSourceOnAfterSearch = ''
        self.PageFile = 'xmldata_' + anamemodifier + str(self.OID)
        self.XMLSource = jobj.XMLSource
        l = re.findall('<XMLPARAM +key="(.+?)" +value="(.+?)"', self.XMLSource)
        self.XMLParams = {}
        for akey, avalue in l:
            self.XMLParams[akey] = avalue
        self.AccessLevelView = jobj.Class.AccessLevelView[jobj.OID]
        self.IsObjectMenu = jobj.Class.IsObjectMenu.ValuesAsInt(jobj.OID)
        self.SearchActions = []
        sobj = jobj.SearchActions
        while sobj:
            asaction = SearchAction(self, sobj)
            self.SearchActions.append(asaction)
            sobj.Next()

    def HasEvent(self, aname):
        eobj = self.bobj.Events
        while eobj:
            if eobj.EventKind.EventName == aname:
                return 1
            eobj.Next()
        return 0

    def GetFieldEventsObj(self, afieldname):
        atable = self.CRM.sourcetables[self.TableOID]
        return atable.GetFieldEventsObj(afieldname)

    def GetFieldEventText(self, eobj):
        atable = self.CRM.sourcetables[self.TableOID]
        return atable.GetFieldEventText(eobj)

    def ProcessXMLDataEvents(self):
        bobj = self.bobj
        arepldict = self.repldict
        eobj = bobj.Events
        while eobj:
            aename = eobj.EventKind.EventName
            if not aename in ['OnSQLCreate']:
                atext = ICORUtil.GetTextAsHTMLText(eobj.EventSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='XMLData: ' + str(self.OID) + ' ' + aename + ' ' + str(eobj.OID))
                self.__dict__[aename] = atext
            eobj.Next()
        atable = self.CRM.sourcetables[self.TableOID]
        for aename in ['ASPSourceSubmitBefore', ]:
            self.__dict__[aename] = self.__dict__.get(aename, '') + '\n' + atable.__dict__.get(aename, '')

    def ProcessEvents(self, aeventname, akey='', aeventcontext='', anowrite=0):
        bobj = self.bobj
        arepldict = self.repldict
        write = None
        if aeventcontext:
            arepldict = aeventcontext.repldict
            oldxmldata = arepldict.get('aXMLData', None)
            arepldict['aXMLData'] = self
            if arepldict.has_key('Response') and not anowrite:
                write = arepldict['Response'].write
        eobj = bobj.Events
        lret = []
        while eobj:
            aename = eobj.EventKind.EventName
            if (aename == aeventname) and (eobj.EventKey == akey):
                oevent = arepldict.get('thisEvent', None)
                aevent = MCRMLib.SourceEvent(eobj, acontext=self, arepldictcontainer=arepldict)
                arepldict['thisEvent'] = aevent
                btext = ICORUtil.GetTextAsHTMLText(eobj.EventSource, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='XMLData: ' + str(self.OID) + ' ' + aename + ' ' + str(eobj.OID))
                arepldict['thisEvent'] = oevent
                if btext:
                    lret.append(btext)
                    if write is not None:
                        write(btext)
            eobj.Next()
        if aeventcontext:
            arepldict['aXMLData'] = oldxmldata
        return '\n'.join(lret)

    def Parse(self, anoassql=0, queryparams=None):
        l = re.findall('<XMLLOAD +key="(.+?)"', self.XMLSource)
        for akey in l:
            self.CRM.ProcessEvents('OnTableXMLLoad', akey=akey, dd={'XMLData': self})
        self.Parser = MCRMXMLInterface.ICORXMLCRMQueryDefinitionParser(self.CRM, queryparams=queryparams)
        self.Parser.Parse(self.XMLSource)
        #      if self.Parser.querysql.IsPivot:
        #         self.Parser.querysql.Top=40000 #$$$$$$
        #      else:
        #         self.Parser.querysql.Top=10000 #$$$$$$
        if not anoassql:
            self.Parser.AsSQL()
        atable = self.CRM.sourcetables[self.TableOID]
        self.SQLTable = atable.SQLTable
        self.ProcessXMLDataEvents()

    def OnASPWriteFile(self, atext, aoneventparams=None):
        if aoneventparams is None:
            aoneventparams = {}
        self.FileText = atext
        aoneventparams['thisItem'] = self
        aoneventparams['thisItemType'] = 'XMLData'
        self.CRM.ProcessEvents('OnASPWriteFile', dd=aoneventparams)
        return self.FileText

    def Write(self, adirectory, aoverrideautogenerate=0, asourcetable=None):
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
        if not self.AutoGenerate and not aoverrideautogenerate:
            return
        print 'Parse & generate XML Data: %s - %s' % (self.OID, self.Title)
        self.Parse()
        if self.Parser.querysql.OutputType == 'owc pivot':
            self.WriteASP(adirectory + self.PageFile + '.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, self.TableOID, afiletype='xmlpivot'), mhtmlsqlpivotgen.GetMainPivotPage(self, self.Parser.querysql)], aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'pivot'})
            self.WriteASP(adirectory + self.PageFile + '_xr.asp', [mhtmlsqlpivotgen.GetXMLRecordsetPage(self, self.Parser.querysql), ], araw=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'pivot_xr'})
        elif self.Parser.querysql.OutputType == 'search form' and asourcetable is not None:
            axproc = asourcetable.SQLTable.GetDefaultSearchSQL(self.PageFile, self.Parser.querysql, asqlversion=self.CRM.SQLVersion)
            if axproc is not None:
                if asourcetable is not None:
                    aownerfilename = asourcetable.SQLTable.NameFile
                else:
                    aownerfilename = ''
                #string.join(self.Parser.querysql.OrderByList,',')
                atree = SimpleHTMLTree.SimpleLinksHTMLTree(acaption=self.Title)
                self.Parser.querysql.ProcessHTMLTree(atree.RootNode)
                self.SourceTable = asourcetable
                for asaction in self.SearchActions:
                    asaction.Process()
                self.WriteASP(adirectory + self.PageFile + '_sv.asp', [
                    mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPageTitle1(),
                    MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, self.TableOID, afiletype='xmlsv'),
                    mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPageTitle2(),
                    mhtmlsqlgen2.SQLTableGetSearchDataASPAdvanced(self.PageFile, self.Parser.querysql.FieldsList, axproc, asortedfields='', aownerfilename=aownerfilename, amainoidfieldname=self.Parser.querysql.Tables[0].Fields['_OID'].UniqueName, aurlparams=self.Parser.querysql.URLParams, amarkergroups=self.Parser.querysql.MarkerGroups, aquerysql=self.Parser.querysql, asearchactions=self.SearchActions, aprojectoid=self.CRM.OID,
                                                                  achaptertable=self.Parser.querysql.Tables[0].NameSQL, aaspsourceonbeforegetdata=self.ASPSourceOnBeforeGetData, aaspsourceonaftersearch=self.ASPSourceOnAfterSearch, aaspsourceonfilter=self.ASPSourceOnFilter, aaspsourceonfieldvalue=self.ASPSourceOnFieldValue), '\n%>\n', '', '\n<%\n'], anobodytarget=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'search_sv'})
                self.WriteASP(adirectory + self.PageFile + '_svf.asp', ['', mhtmlsqlgen2.SQLTableGetSearchDataASPAdvancedPicker(self.PageFile, self.Parser.querysql.FieldsList, axproc, asortedfields='', aownerfilename=aownerfilename, amainoidfieldname=self.Parser.querysql.Tables[0].Fields['_OID'].UniqueName, aurlparams=self.Parser.querysql.URLParams, amarkergroups=self.Parser.querysql.MarkerGroups)], aonaspwritefile=self.OnASPWriteFile,
                              aoneventparams={'thisFileType': 'search_svf'})

                if self.Parser.querysql.IsEditor:
                    import icorlib.projekt.mhtmlsqlgentable as MHTMLSQLGenTable
                    self.Parser.querysql.Tables[0].NameFileSubmit = self.PageFile
                    self.WriteASP(adirectory + self.PageFile + '_au.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, self.TableOID, anorequestform=1, afiletype='xmlau'), MHTMLSQLGenTable.SQLTableGetAddUpdateASP(self.Parser.querysql.Tables[0], aeventsrc=self)], anobodytarget=1, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': 'search_au'})
        elif self.Parser.querysql.OutputType == 'owc chart':
            pass
        else:
            l = [MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, self.TableOID, afiletype='xml'), self.Parser.querysql.AsASP()]
            self.WriteASP(adirectory + self.PageFile + '.asp', l, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': ''})


class ContainerHTML(MCRMLib.MCRMItemBase):

    def __repr__(self):
        return self.Title

    def Process(self, atitle, apage, aitems, afunction, aitemsortfield='', araw=0, anocodepage=0, acompatibility='8'):
        self.Title = atitle
        self.Page = apage
        if aitemsortfield:
            l = []
            for aitem in aitems:
                l.append([getattr(aitem, aitemsortfield), aitem])
            l.sort()
            self.Items = []
            for s, v in l:
                self.Items.append(v)
        else:
            self.Items = aitems
        self.Function = afunction
        self.Raw = araw
        self.NoCodePage = anocodepage
        self.Compatibility = acompatibility

    def OnASPWriteFile(self, atext, aoneventparams=None):
        if aoneventparams is None:
            aoneventparams = {}
        self.FileText = atext
        aoneventparams['thisItem'] = self
        aoneventparams['thisItemType'] = 'ContainerHTML'
        self.CRM.ProcessEvents('OnASPWriteFile', dd=aoneventparams)
        return self.FileText

    def Write(self, adirectory, anorequestform=0):
        import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
        l = []
        if self.Title:
            l.append(MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM, anorequestform=anorequestform, afiletype='containerhtml'))
        l.append(apply(self.Function, (self, )))
        self.WriteASP(adirectory + self.Page + '.asp', l, araw=self.Raw, anocodepage=self.NoCodePage, acompatibility=self.Compatibility, aonaspwritefile=self.OnASPWriteFile, aoneventparams={'thisFileType': ''})


class LazyOIDDictOnClass:

    def __init__(self, acrm, aclass, aicorclass):
        self.CRM = acrm
        self.BaseClass = aclass
        self.ICORClass = aicorclass
        self.dict = {}

    def items(self):
        return self.dict.items()

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def has_key(self, key):
        return self.dict.has_key(key)

    def get(self, key, defvalue=None):
        if self.dict.has_key(key):
            return self.dict[key]
        return defvalue

    def __getitem__(self, key):
        if not self.dict.has_key(key):
            #         print 'lazy getitem:',key
            aitem = self.BaseClass(self.CRM)
            aobj = self.ICORClass[key]
            self.dict[key] = aitem
            #         print 'lazy before process',key
            aitem.Process(aobj)


#         print 'lazy after process',key
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value


class AddInTemplate:

    def __init__(self, aaddin, aobj):
        self.AddIn = aaddin
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.Events = []
        self.EventsDict = {}
        eobj = aobj.AddInTemplateEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, aevent.Key)
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()
        self.AddInTemplateVars = ICORUtil.ParseVars(aobj.AddInTemplateVars, {})
        self.thisEventName, self.thisEventKey = '', ''
        self.aIsDerived = None

    def IsDerived(self):
        if self.aIsDerived is None:
            self.aIsDerived = 0
            for aevent in self.AddIn.Events:
                if aevent.Name == self.thisEventName and aevent.Key == self.thisEventKey:
                    self.aIsDerived = 1
                    break
        return self.aIsDerived

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        write = None
        if self.AddIn.Project.repldict.has_key('Response'):
            write = self.AddIn.Project.repldict['Response'].write
        repldict = self.AddIn.Project.repldict
        otemplate = repldict.get('AddInTemplate', None)
        repldict['AddInTemplate'] = self
        for aevent in self.EventsDict.get((aeventname, akey), []):
            self.thisEventName, self.thisEventKey = aeventname, akey
            #print 'ADDINTEMPLATEEVENT'
            #ICORUtil.dumpstack()
            #print 'ReplDict:'
            #import pprint
            #pprint.pprint(repldict,indent=4)
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='AddInTemplateEvent ' + str(self.OID) + ' ' + aeventname + ' ' + str(aevent.OID))
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        repldict['AddInTemplate'] = otemplate
        return '\n'.join(lret)


class AddIn:

    def __init__(self, aproject, aobj):
        self.Project = aproject
        self.OID = aobj.OID
        self.Obj = aobj.AsObject()
        self.Nazwa = aobj.Nazwa
        self.IsDisabled = aobj['SGIsDisabled', mt_Integer]
        dtvars = {}
        self.AddInTemplates = []
        tobj = aobj.AddInTemplate
        while tobj:
            atemplate = AddInTemplate(self, tobj)
            self.AddInTemplates.append(atemplate)
            dtvars.update(atemplate.AddInTemplateVars)
            tobj.Next()
        self.Events = []
        self.EventsDict = {}
        eobj = aobj.AddInEvents
        while eobj:
            aevent = MCRMLib.SourceEvent(eobj)
            self.Events.append(aevent)
            ek = (aevent.Name, aevent.Key)
            lk = self.EventsDict.get(ek, [])
            lk.append(aevent)
            self.EventsDict[ek] = lk
            eobj.Next()
        self.AddInVars = ICORUtil.ParseVars(aobj.AddInVars, dtvars)
        self.AccessLevelView = aobj.Class.AccessLevelView[aobj.OID]

    def CheckEvents(self, aeventname, akey=''):
        if self.IsDisabled:
            return 0
        for atemplate in self.AddInTemplates:
            if atemplate.EventsDict.has_key((aeventname, akey)):
                return 1
        if self.EventsDict.has_key((aeventname, akey)):
            return 1
        return 0

    def ProcessEvents(self, aeventname, akey='', aeventcontext=''):
        lret = []
        if self.IsDisabled:
            return ''
        aoldaddin = self.Project.repldict.get('AddIn', None)
        self.Project.repldict['AddIn'] = self
        aoldeventcontext = self.Project.repldict.get('EventContext', None)
        self.Project.repldict['EventContext'] = aeventcontext
        for atemplate in self.AddInTemplates:
            atext = atemplate.ProcessEvents(aeventname, akey=akey, aeventcontext=aeventcontext)
            if atext:
                lret.append(atext)
        write = None
        if self.Project.repldict.has_key('Response'):
            write = self.Project.repldict['Response'].write
        for aevent in self.EventsDict.get((aeventname, akey), []):
            atext = ICORUtil.GetTextAsHTMLText(aevent.Source, repldict=self.Project.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='AddInEvent ' + str(self.OID) + ' ' + aeventname + ' ' + str(aevent.OID))
            if atext:
                lret.append(atext)
                if write is not None:
                    write(atext)
        self.Project.repldict['AddIn'] = aoldaddin
        self.Project.repldict['EventContext'] = aoldeventcontext
        return '\n'.join(lret)


class MCRM:

    def __init__(self, aproject, acreatetables=0, abasenamemodifier='', alogger=None):
        self.Project = aproject
        self.CRM = self
        self.sourcetables = None
        self.addins = []
        self.usertsql = []
        self.pages = {}
        self.containers = []
        self.wwwmenustruct = []
        self.newsletters = {}
        self.newsletter_elements = {}
        self.newsletter_categories = {}
        self.pluginsources_tables = {}
        self.createtables = acreatetables
        self.BaseNameModifier = abasenamemodifier
        self.BaseDirectory = '///'
        self.Logger = alogger
        self.Dist_Mode = startutil.appconfig.Dist_Mode

        self.MCRMLib = MCRMLib

        self.ContainerHTML = ContainerHTML
        self.SimpleTableEditor = SimpleTableEditor

    def __repr__(self):
        return 'MCRM'

    def Process(self, pobj, abasedirectory):
        self.PreProcess(pobj, abasedirectory)
        self.ProcessBazyZrodlowe(pobj.BazyZrodlowe)
        self.ProcessPages(pobj.PagesHTML)
        self.ProcessUserTSQL(pobj.UserTSQL)
        self.ProcessWWWMenuStruct(pobj.WWWMenuStruct)

    def EnsureDir(self, adir):
        if not os.path.exists(adir):
            print 'make dir:', adir
            os.makedirs(adir)

    def PreProcess(self, pobj, abasedirectory):
        self.OID = pobj.OID
        self.Obj = pobj.AsObject()
        self.IsDisabled = pobj['SGIsDisabled']
        self.sourcetables = LazyOIDDictOnClass(self, SourceTable, pobj.Class.BazyZrodlowe.ClassOfType)
        self.AppPath = pobj.AppPath
        if self.AppPath[-1:] != '/':
            self.AppPath = self.AppPath + '/'
        self.IncPath = re.sub('[^\\\/]+', '..', self.AppPath) + 'inc/'
        if abasedirectory[-1:] != '/':
            abasedirectory = abasedirectory + '/'
        abasedirectory = string.replace(abasedirectory, '\\', '/')
        self.BaseDirectory = FilePathAsSystemPath(abasedirectory)
        self.WWWDataPath = FilePathAsSystemPath(pobj.WWWDataPath)
        self.WWWDataPath = ICORUtil.GetProperPath(self.WWWDataPath)
        self.WWWDataPathScan = FilePathAsSystemPath(pobj.WWWDataPathScan)
        self.WWWDataPathScan = ICORUtil.GetProperPath(self.WWWDataPathScan)
        if not self.WWWDataPathScan:
            self.WWWDataPathScan = self.WWWDataPath
        self.WWWDataPathUserFiles = FilePathAsSystemPath(pobj.WWWDataPathUserFiles, aslash='/')
        self.WWWDataPathUserImages = FilePathAsSystemPath(pobj.WWWDataPathUserImages, aslash='/')

        self.EnsureDir(self.BaseDirectory)    #%ICOR%\wwwroot\appdata\<project>\crm\
        self.EnsureDir(os.path.join(self.BaseDirectory, '..', 'inc'))
        for asubdir in ['CDN', 'deploy', 'HTTPFiles', 'HTTPFilesDeleted', 'HTTPImages', 'jslibmanager', 'SQLFiles', 'SQLFilesDeleted', 'SQLFilesNew', 'SQLImages', 'WWWStruct', ]:
            self.EnsureDir(os.path.join(self.WWWDataPath, asubdir))    #%ICOR%/WWWData/<project>/
            if self.WWWDataPath != self.WWWDataPathScan:
                self.EnsureDir(os.path.join(self.WWWDataPathScan, asubdir))    #%ICOR%/WWWData/<project>/

        self.CDN_ExternalWWWAddress = ''
        self.CDN_FTPServer = ''
        self.CDN_FTPBasePath = ''
        self.CDN_FTPUser = ''
        self.CDN_FTPPassword = ''
        self.CDN_ServerType = ''
        self.CDN_SMBBasePath = ''
        cobj = pobj.CDNServers
        if cobj:
            if not cobj['SGIsDisabled']:
                self.CDN_ExternalWWWAddress = ICORUtil.GetProperPath(cobj.AdresZewnetrznyWWW)
                self.CDN_FTPServer = cobj.AdresFTP
                self.CDN_FTPBasePath = ICORUtil.GetProperPath(cobj.FTPBasePath)
                self.CDN_FTPUser = cobj.FTPUser
                self.CDN_FTPPassword = cobj.FTPPassword
                self.CDN_ServerType = cobj.SerwerCDN.Nazwa
                self.CDN_SMBBasePath = ICORUtil.GetProperPath(cobj.SMBBasePath)

        if pobj.HTTPServerParameters:
            self.HTTPServerAddress = pobj.HTTPServerParameters.HTTPAddress
            l = string.split(self.HTTPServerAddress, '//')
            self.HTTPServerProtocol = l[0] + '//'
            tobj = pobj.HTTPServerParameters.ServerType
            if tobj:
                self.HTTPServerName = tobj.Name
                self.HTTPServerVersion = tobj.Version
            else:
                self.HTTPServerName, self.HTTPServerVersion = 'IIS', '7'
        else:
            self.HTTPServerAddress = 'http://127.0.0.1'
            self.HTTPServerProtocol = 'http://'
            self.HTTPServerName, self.HTTPServerVersion = 'IIS', '7'
        self.repldict = None

        self.ProjectVars = ICORUtil.ParseVars(self.Obj.ProjectVars, {'aCgiScriptPath': '', 'aExternalDictMaxItemsCount': '300', 'aMSSQLVersion': '2008', 'aSQLScriptsCreate': '0'})
        self.SQLVersion = int(self.ProjectVars.get('aMSSQLVersion', '2008'))
        self.DefaultEncoding = self.ProjectVars.get('aDefaultEncoding', 'utf-8').lower()
        self.DefaultCodePage = self.ProjectVars.get('aDefaultCodePage', '65001')
        self.ConnectionString = dbaccess.GetConnectionString(pobj.DBAccess)
        self.DataBaseName = startutil.GetStrEnv(pobj.DBAccess.DataBaseName)
        self.DataBaseOwner = pobj.DBAccess.DataBaseOwner
        self.SQLCreator = msqllib.SQLCreator(self.Project, self.ConnectionString, abasenamemodifier=self.BaseNameModifier, acrm=self, asqlversion=self.SQLVersion)
        self.InitContainers()
        self.ProcessAddIns(pobj.AddIns)
        self.ProcessEvents('OnProjectInit', 'system')
        self.ProcessEvents('OnProjectInit', 'database')
        self.ProcessEvents('OnProjectInit', 'tables')
        self.ProcessEvents('OnProjectInit')

    def ProcessAddIns(self, uobj):
        while uobj:
            aaddin = AddIn(self, uobj)
            self.addins.append(aaddin)
            uobj.Next()

    def ProcessBazyZrodlowe(self, bobj, agenerateenable=0):
        while bobj:
            if not self.sourcetables.has_key(bobj.OID):
                astable = SourceTable(self, agenerateenable=agenerateenable)
                astable.Process(bobj)
                self.sourcetables[bobj.OID] = astable
            bobj.Next()

    def ProcessBazyZrodloweByList(self, tlist, agenerateenable=0):
        tclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
        for toid in tlist:
            bobj = tclass[toid]
            if not self.sourcetables.has_key(bobj.OID):
                astable = SourceTable(self, agenerateenable=agenerateenable)
                astable.Process(bobj)
                self.sourcetables[bobj.OID] = astable

    def ProcessPages(self, pobj):
        while pobj:
            apage = PageHTML(self)
            apage.Process(pobj)
            self.pages[pobj.OID] = apage
            pobj.Next()

    def ProcessUserTSQL(self, sobj):
        while sobj:
            ausql = UserTSQL(self)
            ausql.Process(sobj)
            self.usertsql.append(ausql)
            sobj.Next()

    def GetTableXMLDataByID(self, aid, anoparse=0, queryparams=None):
        xclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Slownik_XMLData_TableXMLData']
        if not xclass.ObjectExists(aid):
            return None
        xobj = xclass[aid]
        axmldata = XMLData(self)
        axmldata.Process(xobj, anamemodifier='BZR')
        if not anoparse:
            axmldata.Parse(queryparams=queryparams)
        return axmldata

    def ProcessWWWMenuStruct(self, sobj, asingle=0, awritedisabled=0):
        while sobj:
            if not sobj['SGIsDisabled']:
                awwwmenustruct = mwwwmenulib.WWWMenuStruct(self)
                awwwmenustruct.Process(sobj, awritedisabled=awritedisabled)
                self.wwwmenustruct.append(awwwmenustruct)
            else:
                print '*** WWWMenustruct is disabled: ' + str(sobj.OID)
            if asingle:
                break
            sobj.Next()

    def InitContainers(self):
        pass

    def CreateTables(self, asqldir='', aservercreate=0, acreatesp=0, acreatevar=0, adisablechaptercreate=0, aDisableGenerateDependentTables=0):
        lstoredprocedures = []
        laddedsql = [mhtmlsqlgenlib.GetSQLSP_GetUpdateRandomIDByLen(), ]
        self.SQLCreator.WriteTableDefinitions(asqldir, ausertsql=self.usertsql, lstoredprocedures=lstoredprocedures, laddedsql=laddedsql, aservercreate=aservercreate, aprojectname=self.Project, aDisableGenerateDependentTables=aDisableGenerateDependentTables)
        if self.usertsql:
            for autsql in self.usertsql:
                if autsql.ExecuteNow and not aservercreate:
                    self.SQLCreator.ExecuteServerSQLCommand(autsql.PageHTML, isafile=0)
        if acreatesp:
            for atext in lstoredprocedures:
                self.SQLCreator.ExecuteServerSQLCommand(atext, isafile=0)
            for aid, astable in self.sourcetables.items():
                astable.ProcessEvents('OnSQLCreate', 1)
            for awwwmenustruct in self.wwwmenustruct:
                awwwmenustruct.ProcessEvents('OnCMSSQLCreate')
            self.ProcessEvents('OnProjectSQLCreate')
        if acreatevar and not adisablechaptercreate:
            for awwwmenustruct in self.wwwmenustruct:
                if not awwwmenustruct.WriteDisabled and awwwmenustruct.Table_ChaptersID.Values:
                    self.SQLCreator.ExecuteServerSQLCommand(awwwmenustruct.Table_ChaptersID.GetTruncateSQL(), isafile=0)
                    self.SQLCreator.ExecuteServerSQLCommand(awwwmenustruct.Table_ChaptersID.GetCreateTableSQL(ainsertvaluesonly=1, acreateifnotexists=1), isafile=0)

    def GetNewCRMItem(self):
        aitem = MCRMLib.MCRMItemBase(self)
        return aitem

    def DumpAsXMLStart(self, file, aencoding=''):
        if aencoding == '':
            aencoding = self.DefaultEncoding
        if aencoding:
            file.write('<?xml version="1.0" encoding="%s"?>\n\n' % aencoding)
        file.write('<ICORCRMTEMPLATE outputtype="">\n')

    def DumpAsXMLFinish(self, file):
        file.write('</ICORCRMTEMPLATE>\n')

    def ProcessCMSEvents(self, aeventname, dd=None, akey=''):
        ret = ''
        for awwwmenustruct in self.wwwmenustruct:
            ret = ret + awwwmenustruct.ProcessEventsInternal(aeventname, dd, akey)
        return ret

    def AddInTemplateExists(self, atemplatename):
        for aaddin in self.addins:
            if not aaddin.IsDisabled:
                for aaddintemplate in aaddin.AddInTemplates:
                    if aaddintemplate.Nazwa == atemplatename:
                        return 1
        return 0

    def ProcessEvents(self, aeventname, akey='', dd=None, arepldict=None):
        lret = []
        wd = 0
        for aaddin in self.addins:
            if aaddin.CheckEvents(aeventname, akey):
                if not wd:
                    orepldict = self.repldict
                    if arepldict:
                        self.repldict = arepldict
                    if self.repldict is None:
                        self.repldict = {'this': self, 're': re, 'os': os, 'string': string, 'ICORUtil': ICORUtil, 'ADOLibInit': ADOLibInit, 'FilePathAsSystemPath': FilePathAsSystemPath, 'XMLUtil': XMLUtil, 'ICORSecurity': ICORSecurity, 'MCRMLib': MCRMLib}
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

    def ProcessEventsInternal(self, aeventname, dd=None, akey='', arepldict=None):
        return self.ProcessEvents(aeventname, akey, dd, arepldict)

    def Write(self, adisablechaptercreate=0, aDisableGenerateDependentTables=0):
        w = 1
        while w:
            w = 0
            for aid, astable in self.sourcetables.items():
                if not astable.IsWritten:
                    wt = 1
                    if aDisableGenerateDependentTables and not astable.GenerateEnable:
                        wt = 0
                    if wt:
                        w = 1
                        astable.Write(self.BaseDirectory)
        for awwwmenustruct in self.wwwmenustruct:
            awwwmenustruct.Write(self.BaseDirectory, adisablechaptercreate=adisablechaptercreate)
        for aid, apage in self.pages.items():
            apage.Write(self.BaseDirectory)
        for acontainer in self.containers:
            acontainer.Write(self.BaseDirectory)
        self.ProcessEvents('OnProjectWrite')
