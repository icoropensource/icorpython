# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mhtmlsqlgenwizards as MHTMLSQLGenWizards
import icorlib.projekt.mhtmlsqlgenasppage as MHTMLSQLGenAspPage
import icorlib.projekt.mcrmlib as MCRMLib
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil


class WizardStep:

    def __init__(self, awizard, sobj):
        self.OID = sobj.OID
        self.Wizard = awizard
        self.Title = sobj.Nazwa
        self.NameFile = 'wizard_' + str(self.Wizard.OID) + '_' + str(self.OID)
        self.SQLTable = self.Wizard.CRM.SQLCreator.AddTable('WSTP', self.OID, atablecaption=awizard.Title + ' (' + self.Title + ')')
        arepldict = {'aCRM': self.Wizard.CRM, 'this': self}
        fobj = sobj.Pola
        while fobj:
            tobj = fobj.TypPola
            if not tobj:
                print '  *** %s.%s nie posiada typu! ***' % (self.SQLTable.NameSQL, fobj.Nazwa)
            else:
                dstobj = fobj.ZrodloDanychSlownika
                if dstobj:
                    adstoid = dstobj.OID
                else:
                    adstoid = -1
                s1obj = fobj.SGSortStyle
                if s1obj:
                    asortstyle = s1obj.Class.StyleID.ValuesAsInt(s1obj.OID)
                else:
                    asortstyle = 0
                aextdictconstraint = ICORUtil.GetTextAsHTMLText(fobj.ExtDictConstraint, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)
                self.SQLTable.AddField(fobj.NazwaID,tobj.Nazwa,tobj.Rozmiar,aprettyname=fobj.Nazwa,aisaliased=fobj.Class.SGIsAliased.ValuesAsInt(fobj.OID),aissearch=fobj.Class.SGIsSearch.ValuesAsInt(fobj.OID),adictvalues=fobj.WartosciSlownika,atabposition=fobj.Class.SGTabIndex.ValuesAsInt(fobj.OID),aisobligatory=fobj.Class.SGIsObligatory.ValuesAsInt(fobj.OID),aisindexed=fobj.Class.SGIsIndexed.ValuesAsInt(fobj.OID), afilter=tobj.Filtr,alowercase=tobj.Class.Lowercase.ValuesAsInt(tobj.OID),amask=tobj.Maska,anospace=tobj.Class.NoSpace.ValuesAsInt(tobj.OID),aregex=tobj.Regex,aunsigned=tobj.Class.Unsigned.ValuesAsInt(tobj.OID),auppercase=tobj.Class.Uppercase.ValuesAsInt(tobj.OID),adescription=fobj.Opis,anopastdate=tobj.Class.NiedopuszczalnaDataPrzeszla.ValuesAsInt(tobj.OID),aisinteractive=fobj.Class.SGIsInteractive.ValuesAsInt(fobj.OID),adictsourcetable=adstoid,aminvalue=fobj.SGMinValue,amaxvalue=fobj.SGMaxValue, \
                aisunique=fobj.Class.SGIsUnique.ValuesAsInt(fobj.OID),atypecaption=tobj.Caption,
                atextcols=fobj.Class.TextCols.ValuesAsInt(fobj.OID),atextrows=fobj.Class.TextRows.ValuesAsInt(fobj.OID),atextnowrap=fobj.Class.TextNoWrap.ValuesAsInt(fobj.OID),aextdictconstraint=aextdictconstraint,asortstyle=asortstyle, \
                aissingleviewhidden=fobj.Class.SGIsSingleViewHidden.ValuesAsInt(fobj.OID),aisdictviewhidden=fobj.Class.SGIsDictViewHidden.ValuesAsInt(fobj.OID))
            fobj.Next()
        self.SQLTable.AddField('_KreatorID', 'string', '44', aisindexed=1)
        self.SQLTable.AddField('_KreatorOID', 'string', '44', aisindexed=1)
        self.SQLTable.AddField('_Dotyczy', 'string', '44', aisindexed=1)
        self.ASPSourceShowBefore = sobj.ASPSourceShowBefore
        self.ASPSourceShowFieldsBefore = sobj.ASPSourceShowFieldsBefore
        self.ASPSourceShowFields = sobj.ASPSourceShowFields
        self.ASPSourceShowFieldsAfter = sobj.ASPSourceShowFieldsAfter
        self.ASPSourceShowAfter = sobj.ASPSourceShowAfter
        self.ASPSourceSubmit = sobj.ASPSourceSubmit

    def DumpAsXML(self, file, arecur, aindent=0):
        if arecur.has_key('wizardstep_' + str(self.OID)):
            return
        arecur['wizardstep_' + str(self.OID)] = 1
        file.write('%s<WIZARDSTEP OID="%d" name="%s">\n' % (' ' * aindent, self.OID, self.Title, ))
        self.SQLTable.DumpAsXML(file, arecur, aindent + 3)
        file.write('%s</WIZARDSTEP>\n' % (' ' * aindent, ))
        del arecur['wizardstep_' + str(self.OID)]


class Wizard(MCMRLib.MCRMItemBase):

    def Process(self, wobj):
        self.OID = wobj.OID
        self.Title = wobj.Nazwa
        sobj = wobj.Etapy
        self.steps = []
        self.NewPage = ''
        self.NameFile = 'WIZARDPAGE_' + str(self.OID)
        while sobj:
            astep = WizardStep(self, sobj)
            if not self.NewPage:
                self.NewPage = astep.NameFile
            self.steps.append(astep)
            sobj.Next()
        s = wobj.ASPSourceOnDelete
        if s:
            arepldict = {}
            arepldict['aCRM'] = self.CRM
            arepldict['this'] = self
            s = ICORUtil.GetTextAsHTMLText(s, repldict=arepldict, aengine=aICORDBEngine)
        self.ASPSourceOnDelete = s
        self.AccessLevelView = wobj.Class.AccessLevelView[wobj.OID]

    def Write(self, adirectory):
        self.WriteASP(adirectory + self.NameFile + '.asp', [MHTMLSQLGenAspPage.GetPageTitle(self.Title, self.CRM), MHTMLSQLGenWizards.GetWizardMainPage(self, self.CRM.Table_Kreator)])
        i = 0
        while i < len(self.steps):
            astep = self.steps[i]
            nextstep, prevstep = astep, astep
            if i > 0:
                prevstep = self.steps[i - 1]
            if i < (len(self.steps) - 1):
                nextstep = self.steps[i + 1]
            self.WriteASP(adirectory + astep.NameFile + '.asp', [MHTMLSQLGenAspPage.GetPageTitle(astep.Title, self.CRM), MHTMLSQLGenWizards.GetWizardStepPage(self, astep, prevstep, nextstep, self.CRM.Table_DokKreator, self.CRM.Table_Kreator)])
            self.WriteASP(adirectory + astep.SQLTable.NameFile + '_so.asp', [MHTMLSQLGenAspPage.GetPageTitle(astep.Title, self.CRM), MHTMLSQLGenWizards.GetWizardStepShowOnePage(self, astep, prevstep, nextstep, self.CRM.Table_DokKreator)])
            i = i + 1

    def DumpAsXML(self, file, arecur, aindent=0):
        if arecur.has_key('wizard_' + str(self.OID)):
            return
        arecur['wizard_' + str(self.OID)] = 1
        file.write('%s<WIZARD OID="%d" name="%s">\n' % (' ' * aindent, self.OID, self.Title, ))
        for astep in self.steps:
            astep.DumpAsXML(file, arecur, aindent + 3)
        file.write('%s</WIZARD>\n' % (' ' * aindent, ))
        del arecur['wizard_' + str(self.OID)]
