# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil


def ParseProjectSecurityMap(atext):
    l = string.split(atext, '\n')
    ret = []
    for s in l:
        s = string.strip(s)
        if s[:1] == '#' or not s:
            continue
        apos = string.find(s, ';')
        if apos < 0:
            continue
        snum, sline = s[:apos], s[apos + 1:]
        try:
            anum = int(string.strip(snum))
        except:
            continue
        if anum < 0 or anum > 3999:
            continue
        ret.append([anum, string.strip(sline)])
    ret.sort()
    return ret


def GetUserACL(pobj, auid, asbitvector=0):
    dobj = pobj.SecurityMap.Dane
    if dobj is None:
        return ''
    l = ParseProjectSecurityMap(dobj)
    d = {}
    for apos, asname in l:
        d[asname] = apos
    uobj = aICORDBEngine.User[auid]
    abvector = ICORUtil.BitVector()
    if not uobj:
        if asbitvector:
            return abvector
        return ''
    gobj = uobj.Groups
    while gobj:
        sname = gobj.Name
        if d.has_key(sname):
            abvector[d[sname]] = 1
        gobj.Next()
    if asbitvector:
        return abvector
    return abvector.AsString()


def GetUserACLStrings(pobj, auid, auacl):
    l = ParseProjectSecurityMap(pobj.SecurityMap.Dane)
    d = {}
    for apos, asname in l:
        d[asname] = apos
    uobj = aICORDBEngine.User[auid]
    if not uobj:
        return ''
    abvector = ICORUtil.BitVector('0x' + auacl)
    ret = []
    gobj = uobj.Groups
    while gobj:
        sname = gobj.Name
        if d.has_key(sname):
            ret.append([sname, gobj.OID, abvector[d[sname]]])
        gobj.Next()
    ret.sort()
    return ret


def GetItemACLAsUserACL(arefs):
    ret = []
    gclass = aICORDBEngine.User.Groups.ClassOfType
    while arefs:
        sname = arefs.Name[arefs.OID]
        aoid = gclass.Name.Identifiers(sname)
        if aoid >= 0:
            ret.append(aoid)
        arefs.Next()
    return ret


def GetGroupsByACL(pobj, auacl):
    l = ParseProjectSecurityMap(pobj.SecurityMap.Dane)
    d = {}
    for apos, asname in l:
        d[apos] = asname
    abvector = ICORUtil.BitVector(auacl)
    glist = abvector.keys()
    ret = []
    for agid in glist:
        if d.has_key(agid):
            ret.append(d[agid])
    return ret


def GetTableBitVector(d, sobj):
    abvec = ICORUtil.BitVector()
    while sobj:
        sname = sobj.Name
        if d.has_key(sname):
            abvec[d[sname]] = 1
        sobj.Next()
    return abvec


def GetACLByOIDs(gclass, l, d):
    uacl = ICORUtil.BitVector()
    for xoid in l:
        if gclass.ObjectExists(xoid):
            s = gclass.Name[xoid]
            if d.has_key(s):
                uacl[d[s]] = 1
    return uacl


def GetTableACLs(pobj, tobj, auid, l1, l2):
    if type(tobj) == type(1):
        toid = tobj
        tobj = pobj.BazyZrodlowe
        tobj.SetByOID(toid)
        if not tobj:
            return None, None, None
    l = ParseProjectSecurityMap(pobj.SecurityMap.Dane)
    d = {}
    for apos, asname in l:
        d[asname] = apos
    abv_read = GetTableBitVector(d, tobj.AccessLevelView)
    abv_write = GetTableBitVector(d, tobj.AccessLevelEdit)
    abv_delete = GetTableBitVector(d, tobj.AccessLevelDelete)
    abv_useracl = GetUserACL(pobj, auid, asbitvector=1)
    if abv_useracl:
        abv_read = abv_read & abv_useracl
        abv_write = abv_write & abv_useracl
        abv_delete = abv_delete & abv_useracl
    baclread = ICORUtil.BitVector('0x' + l2[0])
    bacledit = ICORUtil.BitVector('0x' + l2[1])
    bacldelete = ICORUtil.BitVector('0x' + l2[2])
    baclread = (baclread | abv_read) ^ abv_read
    bacledit = (bacledit | abv_write) ^ abv_write
    bacldelete = (bacldelete | abv_delete) ^ abv_delete

    uobj = aICORDBEngine.User[auid]
    gclass = uobj.Groups.Class
    uaclread = GetACLByOIDs(gclass, l1[0], d)
    uacledit = GetACLByOIDs(gclass, l1[1], d)
    uacldelete = GetACLByOIDs(gclass, l1[2], d)
    if abv_read:
        uaclread = uaclread & abv_read
    if abv_write:
        uacledit = uacledit & abv_write
    if abv_delete:
        uacldelete = uacldelete & abv_delete

    baclread = baclread | uaclread
    bacledit = bacledit | uacledit
    bacldelete = bacldelete | uacldelete

    return baclread, bacledit, bacldelete


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    pobj = pclass[1]
    auacl = GetUserACL(pobj, 2055)
    print auacl
    print 'by acl:'
    ret = GetGroupsByACL(pobj, auacl)
    x1 = ICORUtil.BitVector(0x0101010101L)
    x2 = ICORUtil.BitVector(0x010201L)
    print x1 & x2
