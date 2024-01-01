# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.icorsecurity as ICORSecurity


def IsVisibleByProfile(aclass, aoid, uid):
    arefs = aclass.Profile.GetRefList(aoid)
    if not arefs.IsEmpty():
        if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
            return 0
    arefs = aclass.AccessLevel.GetRefList(aoid)
    ret = ICORSecurity.CheckAccessLevelForUser(arefs, uid)
    return ret


def DoWhatsNew(amenu, file):
    aclass = aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Dictionary_WhatsNewItem']
    aoid = aclass.Date.GetLastValueID()
    while aoid >= 0:
        if IsVisibleByProfile(aclass, aoid, amenu.uid):
            file.write('<h3><font color="green">%s</font> <font color="navy">%s</font></h3>' % (aclass.Date[aoid], aclass.Caption[aoid]))
            file.write('<p>%s</p><hr>' % (aclass.Description[aoid]))
        aoid = aclass.Date.GetPrevValueID(aoid)


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
