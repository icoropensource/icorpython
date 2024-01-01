# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.icorsecurity as ICORSecurity
import icorlib.wwwserver.icorwwwinterface as ICORWWWInterface


class EventHelper:

    def __init__(self, aobj, aeventfieldname, aeventkindfieldname='EventKind', aeventsourcefieldname='EventSource'):
        self.Obj = aobj
        self.EventsObj = aobj.GetFieldValue(aeventfieldname)
        self.EventKindFieldName = aeventkindfieldname
        self.EventSourceFieldName = aeventsourcefieldname

    def __getitem__(self, aname, asingle=1):
        ret = ''
        lret = []
        eobj = self.EventsObj.AsObject()
        while eobj:
            kobj = eobj.GetFieldValue(self.EventKindFieldName)
            if kobj:
                if kobj.EventName == aname:
                    ret = eobj.GetFieldValue(self.EventSourceFieldName)
                    if asingle:
                        return ret
                    lret.append(ret)
            eobj.Next()
        if asingle:
            return ret
        return lret

    def __setitem__(self, aname, avalue):
        pass


def GetCRMByItem(pobj):
    import icorlib.projekt.mcrmbase as mcrmbase
    acrm = mcrmbase.MCRM(pobj.Nazwa, acreatetables=0, abasenamemodifier=pobj.BaseNameModifier)
    adir = FilePathAsSystemPath(ICORWWWInterface.aICORWWWServerInterface.AppPath) + pobj.AppPath
    acrm.PreProcess(pobj, adir)
    return acrm


_CRM_CACHE = {}


def CRMByUserIterator(buid):
    asecprofile = ICORSecurity.ICORSecurityProfile()
    asecprofile.SetByUser(buid)
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    pobj = pclass.GetFirstObject()
    while pobj:
        if pobj['SGIsDisabled']:
            pobj.Next()
            continue
        parefs = ICORSecurity.GetRecursiveAccessLevelRefs(pobj, 'AccessLevelView')
        if asecprofile.CheckAccessByRefs(parefs):
            if not _CRM_CACHE.has_key(pobj.OID):
                _CRM_CACHE[pobj.OID] = GetCRMByItem(pobj)
            acrm = _CRM_CACHE[pobj.OID]
            yield acrm
        pobj.Next()


def CRMByAllIterator():
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    pobj = pclass.GetFirstObject()
    while pobj:
        if pobj['SGIsDisabled']:
            pobj.Next()
            continue
        if not _CRM_CACHE.has_key(pobj.OID):
            _CRM_CACHE[pobj.OID] = GetCRMByItem(pobj)
        acrm = _CRM_CACHE[pobj.OID]
        yield acrm
        pobj.Next()


PATT_SESSION = re.compile('((?<!\w)session\s*?\()', re.I + re.M)


def ChangeDessionRepl(m):
    return 'Dession('


def ChangeDession(atext):
    ret = PATT_SESSION.sub(ChangeDessionRepl, atext)
    return ret
