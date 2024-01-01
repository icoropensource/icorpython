# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.icorsecurity as ICORSecurity
import string
import cStringIO


def GetSheetsInfo(vclass):
    srefs = vclass.EditorSheets
    sheetsinfo = {}
    i = 0
    while srefs.position >= 0:
        sheetsinfo[i] = [srefs.Name[srefs.OID], [], srefs.WWWDisabled.ValuesAsInt(srefs.OID)]
        i = i + 1
        srefs.Next()
    if sheetsinfo == {}:
        sheetsinfo[0] = [vclass.NameOfClass, [], 0]

    def ffunc(aclass, afield, sheetsinfo):
        if afield.WWWDisabled:
            return
        fsi = int(afield.FieldSheetID)
        fti = int(afield.FieldTabIndex)
        if not sheetsinfo.has_key(fsi):
            fsi = 0
        s = afield.FieldNameAsDisplayed
        if s == '':
            s = afield.Name
        sheetsinfo[fsi][1].append([fti, s, afield])

    vclass.ForEachField(ffunc, sheetsinfo)
    for akey in sheetsinfo.keys():
        afields = sheetsinfo[akey][1]
        afields.sort()
        sheetsinfo[akey][1] = afields
    return sheetsinfo


def ProcessObjectEdit(f, eclass, OID, UID, brcid=-1, broid=-1):
    w = eclass.ObjectExists(OID)
    aobj = eclass[OID]
    if w and not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', UID):
        w = 0
    if not w:
        f.write("""
<h2><font color="red">Brak uprawnień do tej pozycji</font></h2>
<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:history.back();"> Powrót </button>
""")
        return

    import CLASSES_Library_NetBase_WWW_Server_DoSheetGet
    CLASSES_Library_NetBase_WWW_Server_DoSheetGet.DoSheetGet(f, eclass.CID, OID, -1, UID, brcid, broid)
    return

    sheetsinfo = GetSheetsInfo(eclass)
    #   WriteHeader(f,eclass,sheetsinfo,OID)
    vkeys = sheetsinfo.keys()
    vkeys.sort()

    apanes = '100%%'
    if len(vkeys) > 1:
        apanes = apanes + ',0' * (len(vkeys) - 1)
    f.write("""
<frameset name="FRAMEOBJECTS" id="FRAMEOBJECTS" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="64,*">
  <frame name="OBJECTEDITMAIN" id="OBJECTEDITMAIN" scrolling="no" noresize src="icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=-1" frameborder="0" marginheight="0" marginwidth="0">
  <frameset name="FRAMEPANES" id="FRAMEPANES" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="%s">
""" % (eclass.CID, OID, apanes))
    for i in range(len(vkeys)):
        if not i:
            f.write('   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize src="icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=0&brCID=%d&brOID=%d" frameborder="0" marginheight="0" >\n' % (i, i, eclass.CID, OID, brcid, broid))
        else:
            f.write('   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize frameborder="0" marginheight="0" >\n' % (i, i))
    f.write('</frameset></frameset>\n')


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    print 'aaaaaa'
    aclass = aICORDBEngine.Classes[CID]
    if Value == '':
        return 'Error!'
    acid = int(Value)
    eclass = aICORDBEngine.Classes[acid]
    f = cStringIO.StringIO()
    ProcessObjectEdit(f, eclass, OID, UID)
    return f.getvalue()
