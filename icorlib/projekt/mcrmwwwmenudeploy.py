# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil


class DeployScenario(object):

    def __init__(self, astruct, dobj):
        self.WWWMenuStruct = astruct
        self.OID = dobj.OID
        self.Obj = dobj.AsObject()
        self.name = dobj.Nazwa
        self.mode = ''
        self.source = ''
        mobj = dobj.DeployMode
        if mobj:
            self.mode = mobj.TrybPublikacji
        sobj = dobj.DeploySource
        if sobj:
            self.source = sobj.Nazwa
        self.IsDisabled = dobj['SGIsDisabled', mt_Integer]
        self.SrcURI = dobj.SrcURI
        if self.source == 'filesystem':
            self.SrcURI = FilePathAsSystemPath(self.SrcURI)
        self.SrcBranch = dobj.SrcBranch
        self.SrcDir = dobj.SrcDir
        self.TargetDir = dobj.TargetDir
        self.URIUser = dobj.URIUser
        self.URIPassword = dobj.URIPassword


class JSLibManager(object):

    def __init__(self, astruct, dobj):
        self.WWWMenuStruct = astruct
        self.OID = dobj.OID
        self.Obj = dobj.AsObject()
        self.name = dobj.Nazwa
        self.description = dobj.Opis
        self.TargetDir = dobj.PodkatalogInstalacyjny
        self.kind = ''
        mobj = dobj.Rodzaj
        if mobj:
            self.kind = mobj.Nazwa
        self.Source = dobj.Skrypt
        self.IsDisabled = dobj['SGIsDisabled', mt_Integer]
        aoldrepldict = self.WWWMenuStruct.repldict
        self.WWWMenuStruct.repldict = self.WWWMenuStruct.GetReplDict()
        self.OnPageHeader = ICORUtil.GetTextAsHTMLText(dobj.OnPageHeader, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='JSLibManager.OnPageHeader ' + str(self.OID))
        self.OnPageBottom = ICORUtil.GetTextAsHTMLText(dobj.OnPageBottom, repldict=self.WWWMenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0, ascriptname='JSLibManager.OnPageBottom ' + str(self.OID))
        self.WWWMenuStruct.repldict = aoldrepldict
