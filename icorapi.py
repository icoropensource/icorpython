import sys

try:
    import warnings
    warnings.filterwarnings('ignore', category=Warning, append=1)
except:
    pass

import icorexceptions
import icordbmain

import appplatform.startutil as startutil

aICORDB = icordbmain.ICORDBData()


def ClassExists(fparamI1, fparamI2):
    return aICORDB.struct.API_ClassExists(fparamI1, fparamI2)


def GetClassID(fparamI1, fparamS1):
    return aICORDB.struct.API_GetClassID(fparamI1, fparamS1)


def GetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, adefault=None):
    return aICORDB.struct.API_GetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, adefault=adefault)


def GetFieldValueInt(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueInt(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueFloat(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueFloat(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValuePyTime(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValuePyTime(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3)


def ValueExists(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_ValueExists(fparamI1, fparamI2, fparamS1, fparamI3)


def ObjectExists(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_ObjectExists(fparamI1, fparamI2, fparamI3)


def GetObjectCount(fparamI1, fparamI2):
    return aICORDB.struct.API_GetObjectCount(fparamI1, fparamI2)


def GetFirstObjectID(fparamI1, fparamI2):
    return aICORDB.struct.API_GetFirstObjectID(fparamI1, fparamI2)


def GetLastObjectID(fparamI1, fparamI2):
    return aICORDB.struct.API_GetLastObjectID(fparamI1, fparamI2)


def GetNextObjectID(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetNextObjectID(fparamI1, fparamI2, fparamI3)


def GetPrevObjectID(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetPrevObjectID(fparamI1, fparamI2, fparamI3)


def GetFirstFieldValueID(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_GetFirstFieldValueID(fparamI1, fparamI2, fparamS1)


def GetLastFieldValueID(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_GetLastFieldValueID(fparamI1, fparamI2, fparamS1)


def GetNextFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetNextFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3)


def GetPrevFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetPrevFieldValueID(fparamI1, fparamI2, fparamS1, fparamI3)


def GetNextFieldValue(fparamI1, fparamI2, fparamS1, fparamS2):
    return aICORDB.struct.API_GetFieldNextValue(fparamI1, fparamI2, fparamS1, fparamS2)


def GetPrevFieldValue(fparamI1, fparamI2, fparamS1, fparamS2):
    return aICORDB.struct.API_GetFieldPrevValue(fparamI1, fparamI2, fparamS1, fparamS2)


def GetNextFieldValueInt(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldNextValueInt(fparamI1, fparamI2, fparamS1, fparamI3)


def GetPrevFieldValueInt(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldPrevValueInt(fparamI1, fparamI2, fparamS1, fparamI3)


def GetObjectValue(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetObjectValue(fparamI1, fparamI2, fparamI3)


def GetObjectsValue(fparamI1, fparamI2, fields=None, autfconvert=1, aslist=0):
    return aICORDB.struct.API_GetObjectsValue(fparamI1, fparamI2, fields=fields, autfconvert=autfconvert, aslist=aslist)


def GetObjectIDByPosition(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetObjectIDByPosition(fparamI1, fparamI2, fparamI3)


def GetValueIDByPosition(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetValueIDByPosition(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldValueByPosition(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldValueByPosition(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldObjectsCount(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_GetFieldObjectsCount(fparamI1, fparamI2, fparamS1)


def IsObjectDeleted(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_IsObjectDeleted(fparamI1, fparamI2, fparamI3)


def GetFirstClass(fparamI1):
    return aICORDB.struct.API_GetFirstClass(fparamI1)


def GetNextClass(fparamI1, fparamI2):
    return aICORDB.struct.API_GetNextClass(fparamI1, fparamI2)


def FindValue(fparamI1, fparamI2, fparamS1, fparamS2):
    return aICORDB.struct.API_FindValue(fparamI1, fparamI2, fparamS1, fparamS2)


def FindValueMulti(UID, cid, values, mode=0):
    return aICORDB.struct.API_FindValueMulti(UID, cid, values, mode)


def FindValueBoolean(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_FindValueBoolean(fparamI1, fparamI2, fparamS1, fparamI3)


def FindValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9):
    return aICORDB.struct.API_FindValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)


def FindValueFloat(fparamI1, fparamI2, fparamS1, fparamD1):
    return aICORDB.struct.API_FindValueFloat(fparamI1, fparamI2, fparamS1, fparamD1)


def FindValueInteger(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_FindValueInteger(fparamI1, fparamI2, fparamS1, fparamI3)


def GetFieldOIDsBySearchValue(UID, cid, fname, value, acasesensitive=0, aregexp=0, aschema=None):
    return aICORDB.struct.API_GetFieldOIDsBySearchValue(UID, cid, fname, value, acasesensitive=acasesensitive, aregexp=aregexp, aschema=aschema)


def CompareOIDs(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4):
    return aICORDB.struct.API_CompareOIDs(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4)


def CompareOIDValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2):
    return aICORDB.struct.API_CompareOIDValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2)


def GetFieldsList(fparamI1, fparamI2):
    return aICORDB.struct.API_GetFieldsList(fparamI1, fparamI2)


def GetMethodsList(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetMethodsList(fparamI1, fparamI2, fparamI3)


def IsMethodInClass(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_IsMethodInClass(fparamI1, fparamI2, fparamS1)


def IsMethodInThisClass(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_IsMethodInThisClass(fparamI1, fparamI2, fparamS1)


def IsFieldInClass(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_IsFieldInClass(fparamI1, fparamI2, fparamS1)


def GetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3):
    return aICORDB.struct.API_GetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3)


def GetObjectModification(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_GetObjectModification(fparamI1, fparamI2, fparamI3)


def GetNextFreeObjectID(fparamI1, fparamI2, fparamI3, fparamI4):
    return aICORDB.struct.API_GetNextFreeObjectID(fparamI1, fparamI2, fparamI3, fparamI4)


def GetMethodInfo(UID, cid, amethodname):
    return aICORDB.struct.API_GetMethodInfo(UID, cid, amethodname)


def GetClassInfo(UID, cid):
    return aICORDB.struct.API_GetClassInfo(UID, cid)


def ExecuteMethod(fparamI1, fparamI2, fparamS1, fparamS2, fparamI3, fparamS3, fparamI4):
    return aICORDB.struct.API_ExecuteMethod(fparamI1, fparamI2, fparamS1, fparamS2, fparamI3, fparamS3, fparamI4)


def SetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetFieldValueDate(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetFieldValueDateTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetFieldValueTime(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetTestDecFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetTestDecFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetTestIncFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetTestIncFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetTestFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, fparamS3, amodification=None, adisablechangedevents=0):
    return aICORDB.struct.API_SetTestFieldValue(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamS2, fparamS3, amodification=amodification, adisablechangedevents=adisablechangedevents)


def SetClassLastModification(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9):
    return aICORDB.struct.API_SetClassLastModification(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)


def SetFieldLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9):
    return aICORDB.struct.API_SetFieldLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)


def SetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2):
    return aICORDB.struct.API_SetFieldModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamS2)


def SetMethodLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9):
    return aICORDB.struct.API_SetMethodLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9)


def SetObjectModification(fparamI1, fparamI2, fparamI3, fparamS1):
    return aICORDB.struct.API_SetObjectModification(fparamI1, fparamI2, fparamI3, fparamS1)


def SetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10):
    return aICORDB.struct.API_SetFieldValueLastModification(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9, fparamI10)


def SetObjectModified(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_SetObjectModified(fparamI1, fparamI2, fparamI3)


def SetClassProperty(fparamI1, fparamI2, fparamS1, fparamS2):
    return aICORDB.struct.API_SetClassProperty(fparamI1, fparamI2, fparamS1, fparamS2)


def SetFieldProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3):
    return aICORDB.struct.API_SetFieldProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3)


def SetMethodProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3):
    return aICORDB.struct.API_SetMethodProperty(fparamI1, fparamI2, fparamS1, fparamS2, fparamS3)


def CreateObjectByID(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_CreateObjectByID(fparamI1, fparamI2, fparamI3)


def AddObject(fparamI1, fparamI2):
    return aICORDB.struct.API_AddObject(fparamI1, fparamI2)


def DeleteObject(fparamI1, fparamI2, fparamI3):
    return aICORDB.struct.API_DeleteObject(fparamI1, fparamI2, fparamI3)


def ClearAllObjects(fparamI1, fparamI2):
    return aICORDB.struct.API_ClearAllObjects(fparamI1, fparamI2)


def ClearAllValues(fparamI1, fparamI2, fparamS1):
    return aICORDB.struct.API_ClearAllValues(fparamI1, fparamI2, fparamS1)


# -----------------
# field versions, deleted etc.


#OK - alldata
def GetFieldVersions(UID, cid, fname, oid):
    return aICORDB.struct.API_GetFieldVersions(UID, cid, fname, oid)


#OK - alldata
def GetFirstDeletedOffset(fparamI1, fparamI2, fparamS1):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetFirstDeletedOffset')


#OK - alldata
def GetDeletedObjectsList(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5, fparamI6, fparamI7, fparamI8, fparamI9):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetDeletedObjectsList')


#OK - alldata
def GetNextDeletedOffset(fparamI1, fparamI2, fparamS1, fparamI3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetNextDeletedOffset')


#OK - alldata
def GetRecLastModification(fparamI1, fparamI2, fparamS1, fparamI3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetRecLastModification')


#OK - alldata
def GetRecOID(fparamI1, fparamI2, fparamS1, fparamI3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetRecOID')


#OK - alldata
def GetRecOwnerID(fparamI1, fparamI2, fparamS1, fparamI3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetRecOwnerID')


#OK - alldata
def GetRecValueAsString(fparamI1, fparamI2, fparamS1, fparamI3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetRecValueAsString')


# -----------------


#OK - alldata
def DeleteVariable(fparamI1, fparamS1):
    if hasattr(sys, '__icorvariables'):
        dv = sys.__icorvariables
    else:
        dv = {}
        sys.__icorvariables = dv
    du = dv.get(fparamI1, {})
    if du.has_key(fparamS1):
        del du[fparamS1]
    dv[fparamI1] = du


#OK - alldata
def GetVariable(fparamI1, fparamS1):
    if hasattr(sys, '__icorvariables'):
        dv = sys.__icorvariables
    else:
        dv = {}
        sys.__icorvariables = dv
    du = dv.get(fparamI1, {})
    ret = du.get(fparamS1, '')
    dv[fparamI1] = du
    return ret


#OK - alldata
def SetVariable(fparamI1, fparamS1, fparamS2):
    if hasattr(sys, '__icorvariables'):
        dv = sys.__icorvariables
    else:
        dv = {}
        sys.__icorvariables = dv
    du = dv.get(fparamI1, {})
    du[fparamS1] = fparamS2
    dv[fparamI1] = du


########################## SKIP ###############################


def ImportModuleAsString(fparamI1, fparamS1):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ImportModuleAsString')


def ShellExecute(fparamI1, fparamS1, fparamS2, fparamS3):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ShellExecute')


def ExportModuleAsString(fparamI1, fparamS1, fparamS2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ExportModuleAsString')


def StatusInfo(fparamI1, fparamS1):
    print 'STATUS INFO: %s' % fparamS1
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: StatusInfo')


def SummaryEdit(fparamI1, fparamI2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SummaryEdit')


def CheckObjectBySummary(fparamI1, fparamI2, fparamI3, fparamI4, fparamI5):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: CheckObjectBySummary')


def ClearStdErr():
    pass
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ClearStdErr')


def ClearStdOut():
    pass
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ClearStdOut')


def DoEvents():
    pass
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: DoEvents')


def EditObject(fparamI1, fparamI2, fparamI3, fparamS1, fparamI4):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: EditObject')


def GetSystemID(fparamS1):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: GetSystemID')


def ICORSetClipboard(fparamS1):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: ICORSetClipboard')


def OnStdErrPrint(fparamI1, fparamS1, fparamI2):
    pass
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: OnStdErrPrint')


def OnStdOutPrint(fparamI1, fparamS1, fparamI2):
    pass
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: OnStdOutPrint')


def RepositoryChange(fparamI1, fparamS1, fparamI2, fparamI3, fparamS2, fparamS3, fparamS4):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: RepositoryChange')


def SelectClassFieldProperties(fparamI1, fparamI2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectClassFieldProperties')


def SelectElementDialog(fparamI1, fparamS1, fparamI2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectElementDialog')


def SelectFieldValues(fparamI1, fparamI2, fparamS1):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectFieldValues')


def SelectInEditor(fparamI1, fparamI2, fparamS1, fparamS2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectInEditor')


def SelectObjects(fparamI1, fparamI2, fparamS1, fparamI3, fparamI4):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectObjects')


def SelectObjectsFromDictionary(fparamI1, fparamI2, fparamS1, fparamS2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectObjectsFromDictionary')


def SelectSearchInClass(fparamI1, fparamI2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectSearchInClass')


def SelectSummaries(fparamI1, fparamI2):
    raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SelectSummaries')


def SetProgress(fparamI1, fparamI2, fparamI3):
    if fparamI3:
        v = 100.0 * fparamI2 / fparamI3
        print 'progress: %0.2f%%\r' % (v, ),
    else:
        print ' ' * 44
    #raise icorexceptions.ICORExceptionAPIObsolete('ICORAPITCP - function obsolete: SetProgress')
