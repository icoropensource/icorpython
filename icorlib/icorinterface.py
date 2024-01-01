import sys
try:
    import ICORDelphi
    icorapi = ICORDelphi
    ICOR_EXECUTE_EXTERNAL = 0
except:
    import icorapi
    ICOR_EXECUTE_EXTERNAL = 1
import string
import struct
import types
import time
import re
import hashlib
import locale

import icorstorage

try:
    import warnings
    warnings.filterwarnings('ignore', category=Warning, append=1)
except:
    pass

__version__ = 1, 4, 76, 0


class ICORException(Exception):

    def __init__(self, errmsg=''):
        Exception.__init__(self, errmsg)


# stale ikon dla MessageDialog
mtWarning, mtError, mtInformation, mtConfirmation, mtCustom = 0, 1, 2, 3, 4

#stale przyciskow dla MessageDialog
mbYes, mbNo, mbOK, mbCancel, mbAbort, mbRetry, mbIgnore, mbAll, mbHelp = 1, 2, 4, 8, 16, 32, 64, 128, 256
mbYesNoCancel = mbYes | mbNo | mbCancel
mbOkCancel = mbOK | mbCancel
mbAbortRetryIgnore = mbAbort | mbRetry | mbIgnore

#stale powrotu z MessageDialog
mrNone, mrOk, mrCancel, mrAbort, mrRetry, mrIgnore, mrYes, mrNo = 0, 1, 2, 3, 4, 5, 6, 7
mrAll = mrNo + 1

FALSE_STRING = 'False'
TRUE_STRING = 'True'

d_FieldEditor={
   0:'None',1:'String',2:'Integer',3:'Float',4:'EFloat',5:'Date',6:'Time',7:'DateTime',8:'Bool',9:'Currency',
   100:'Repository',101:'Class',102:'ClassField',103:'ClassMethod',104:'FieldValues',105:'MethodName',106:'ObjectsList',107:'Summary',108:'ObjectsView',
   201:'File',202:'Directory',203:'URL',10:'Password',204:'HTML',205:'Worksheet',206:'XML',207:'SourceCode',
} # yapf: disable

def find_in_locals(aname, adefault):
    f = sys._getframe().f_back
    while f is not None:
        if f.f_locals.has_key(aname):
            return f.f_locals[aname]
        f = f.f_back
    return adefault


def get_caller_names(adepth=0):
    ret = []
    f = sys._getframe().f_back
    acnt = 0
    while f is not None:
        aname = f.f_code.co_name
        if adepth and acnt == adepth:
            return aname
        ret.append(aname)
        f = f.f_back
        acnt = acnt + 1
    return ret


def GetUID():
    #  return 0
    return find_in_locals('UID', -1)


def MessageDialog(acaption, aicon=mtInformation, abuttons=mbOkCancel):
    return aICORDBEngine.icorapi.MessageShow(GetUID(), acaption, aicon, abuttons)


def ClearStdOut():
    return aICORDBEngine.icorapi.ClearStdOut()


def ClearStdErr():
    return aICORDBEngine.icorapi.ClearStdErr()


def InfoStatus(astr):
    return aICORDBEngine.icorapi.StatusInfo(GetUID(), astr)


def DoEvents():
    if ICOR_EXECUTE_EXTERNAL:
        time.sleep(0.001)
    else:
        aICORDBEngine.icorapi.DoEvents()


def SetProgress(apos, amax):
    return aICORDBEngine.icorapi.SetProgress(GetUID(), apos, amax)


def ExecuteShellCommand(afilename, amode='Shell', await=0, mSec=None, akill=0):    #Shell, Process, ProcessNoWindow
    ret = aICORDBEngine.icorapi.ShellExecute(GetUID(), afilename, amode, '')
    if await and amode in ['Process', 'ProcessNoWindow']:
        try:
            import win32event
            if mSec is None:
                mSec = win32event.INFINITE
            status = win32event.WaitForSingleObject(ret, mSec)
            if status != win32event.WAIT_OBJECT_0 and akill:
                import win32process
                win32process.TerminateProcess(ret, 0)
                time.sleep(0.01)
        except:
            pass
    return ret


def FilePathAsSystemPath(afilepath, aslash=r'\\'):
    sibd = aICORDBEngine.Variables['_ICOR_BASE_DIR']
    if not sibd:
        sibd = aICORDBEngine.icorapi.startutil.appconfig.ICORBaseDir
        if not sibd:
            raise ICORException('Bad ICOR Base dir')
    s = ReplaceStrStr(afilepath, '%ICOR%', sibd)
    s = re.sub(r'[/\\]', aslash, s)
    return s


def Destruct(obj):
    if type(obj) == types.InstanceType:
        for k in obj.__dict__.keys():
            obj.__dict__[k] = None


def ReplaceStr(str1, str2, pos, len=1):
    return str1[:pos] + str2 + str1[pos + len:]


def ReplaceStrStr(str1, str2, str3):
    pos = string.find(str1, str2)
    if pos >= 0:
        return str1[:pos] + str3 + str1[pos + len(str2):]
    return str1


_aidentifierpattern = re.compile('^[A-Z][a-zA-Z0-9]*$')


def IsIdentifier(aname):
    if _aidentifierpattern.search(aname):
        return 1
    return 0


def str2bool(s):
    if isinstance(s, types.StringTypes):
        if s.lower() in ['true', '1', 'on', 'yes', 'prawda', 'tak', 't', 'y']:
            return 1
    try:
        i = int(s)
        if i > 0:
            return 1
    except:
        return 0
    return 0


def str2fmtstr(fmt, v):
    if not fmt:
        if not isinstance(v, types.StringTypes):
            return str(v)
        return v
    fmt = fmt.replace('%%', '$$_$$')
    s = locale.format_string(fmt, v, 1)
    s = s.replace('$$_$$', '%')
    return s


MAX_ICOR_SYSTEM_TYPE = 255

STARTUP_CLASS_LOCATION = 'CLASSES\System\Startup'
USER_CLASS_LOCATION = 'CLASSES\System\User'
USER_PROFILE_CLASS_LOCATION = 'CLASSES\System\UserProfile'
QUEUED_PARAMETERS_CLASS_LOCATION = 'CLASSES\System\SystemDictionary\External\DaemonParameters'
QUEUED_METHODS_SINGLE_CALL = ['CLASSES_Library_NetBase_WWW_Administration_Security_DoWWWClearCache', ]

#_FieldLastValue         - przy validacji wartosci pol - stara wartosc pola edycyjnego
#_FieldNewValue          - przy validacji wartosci pol - nowa wartosc pola edycyjnego
#_Interactive            - oznacza, ze metoda jest wywolywana z trybu interaktywnego [0,1]
#_ReturnCode             - wartosc typu Int, oznaczajaca rozne statusy powrotu

#_FieldDateTime          - podczas ustalania wartosci pol wirtualnych
#_FieldValue             - podczas pobierania wartosci pol wirtualnych

#_AllowObjectDelete      - przed kasowaniem jest szansa na sprawdzenie np. RefCount

#_AllowFieldImport       - podczas importowania danych zezwala lub nie na aktualizacje danych
#_FieldImportValue       - nowa wartosc importowana
#_FieldImportDate        - data i czas zmiany tej wartosci

#_ObjectID               - identyfikator obiektu dla klas wirtualnych
#_ObjectsCount           - ilosc obiektow dla klas wirtualnych


class ICORVariables:

    def __init__(self, aengine):
        self.__dict__['aICORDBEngine'] = aengine

    def __getattr__(self, name):
        return self.__dict__['aICORDBEngine'].icorapi.GetVariable(GetUID(), name)

    def __setattr__(self, name, value):
        return self.__dict__['aICORDBEngine'].icorapi.SetVariable(GetUID(), name, value)

    def __getitem__(self, key):
        return self.__dict__['aICORDBEngine'].icorapi.GetVariable(GetUID(), key)

    def __setitem__(self, key, value):
        return self.__dict__['aICORDBEngine'].icorapi.SetVariable(GetUID(), key, value)


class ICORUserVars:

    def __init__(self):
        self.vars = {}

    def __getitem__(self, key):
        if self.vars.has_key(key):
            return self.vars[key]
        if not isinstance(key, types.StringTypes):
            auid, akey = key
            uclass = aICORDBEngine.User
            if not uclass.ObjectExists(auid):
                return None
            uobj = uclass[auid]
            vobj = uobj.UserVariables
            while vobj:
                self.vars[(auid, vobj.Name)] = vobj.Value
                vobj.Next()
            if self.vars.has_key(key):
                return self.vars[key]
        return None

    def __setitem__(self, key, value):
        self.vars[key] = value
        return

    def Delete(self, key):
        if self.vars.has_key(key):
            del self.vars[key]
        return

    def KeyExists(self, key):
        return self.vars.has_key(key)


#stale dla typow podstawowych
mt_Integer, mt_Double, mt_DateTime, mt_Boolean, mt_String = 0x20, 0x40, 0x60, 0x70, 0x90
mt_Bool, mt_Date, mt_Time = 0x70, 0x60, 0x60
mt_Memo = 0x91
mt_Any = -1

#stale dla trybow dostepu do pola
FA_Public, FA_Private, FA_Protected = 0, 1, 2

#stale dla operatorow (np. funkcjach SetTest*Value)
cv_eq, cv_le, cv_ge, cv_not = 1, 2, 4, 8
cv_neq, cv_nle, cv_nge, cv_leeq, cv_geeq, cv_nleeq, cv_ngeeq = cv_not + cv_eq, cv_not + cv_le, cv_not + cv_ge, cv_eq + cv_le, cv_eq + cv_ge, cv_not + cv_eq + cv_le, cv_not + cv_eq + cv_ge

START_DATE_TIME = (1899, 12, 30, 0, 0, 0, 0)
START_DATE_TIME_L = [1899, 12, 30, 0, 0, 0, 0]
START_DATE_TIME_STR = '1899-12-30 00:00:00'


class ICORFieldDefinition:

    def __init__(self, afname="", aftypeid=mt_String):
        self.FName, self.FTypeID, self.FValue, self.FDefaultValue, self.FAccess = afname, aftypeid, "", "", FA_Public
        self.FInteractive, self.FObligatory, self.FContainerType = 1, 0, 0
        self.FIndexed, self.FFastIndexed, self.FAlias = 0, 0, 1
        self.FVirtual, self.FCached = 0, 0
        self.FOwnerCID = -1

    def __repr__(self):
        s = """FName=%s, FTypeID=%s, FValue=%s,FDefaultValue=%s,FAccess=%s
FInteractive=%s, FObligatory=%s, FContainerType=%s
FIndexed=%s, FFastIndexed=%s, FAlias=%s
FVirtual=%s, FCached=%s
""" % (self.FName, str(self.FTypeID), self.FValue, self.FDefaultValue, str(self.FAccess), str(self.FInteractive), str(self.FObligatory), str(self.FContainerType), str(self.FIndexed), str(self.FFastIndexed), str(self.FAlias), str(self.FVirtual), str(self.FCached))
        return s


class ICORMethodDefinition:

    def __init__(self, amname=""):
        self.MName, self.MDescription, self.MAccess, self.MLanguage, self.MIsParallel = amname, "", FA_Public, 'Python', 0

    def __repr__(self):
        s = "MName=%s, MLanguage=%s, MDescription=%s, MAccess=%s, MIsParallel=%d" % (self.MName, self.MLanguage, self.MDescription, str(self.MAccess), self.MIsParallel)
        return s


class ICORDBFieldItem:

    def __init__(self, CID, FName):
        self.__dict__['_FieldProperties'] = {}
        self.CID = CID
        self.FName = FName
        self.Name = FName

    def __getattr__(self, name):
        if self.__dict__['_FieldProperties'].has_key(name):
            return self.__dict__['_FieldProperties'][name]
        if name == 'FOID':
            ret = aICORDBEngine.Classes.MetaField.aIDClassField.Identifiers(str(self.CID) + '_' + self.FName)
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldTypeID':
            ret = aICORDBEngine.Classes.MetaField.aFieldTypeID[self.FOID]
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldTID':
            ret = int(aICORDBEngine.Classes.MetaField.aFieldTypeID.Values(self.FOID))
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'ClassOfType':
            acid = self.FieldTID
            if acid <= MAX_ICOR_SYSTEM_TYPE:
                return None
            return aICORDBEngine.Classes[acid]
        battrs = ['IsAliased', 'IsContainer', 'IsVirtual', 'IsCached', 'IsFastIndexed', 'IsIndexed', 'IsInteractive', 'IsObligatory', 'IsReadOnly', 'IsReportProtected', ]
        if name in battrs:
            mfield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            return str(str2bool(mfield[self.FOID]))
        battrs_i = ['WWWDisabled', 'WWWSingleValue', 'WWWDefaultInput', 'WWWDefaultCheck', 'WWWUpdateRefs', 'WWWBackRefField', 'WWWLowercase', 'WWWUppercase', 'WWWNoSpace', 'WWWUnsigned', 'WWWUnique', 'WWWTreeRecur', 'WWWTreeRecurObjects', 'WWWSortable']
        if name in battrs_i:
            afield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            ret = int(afield.ValuesAsInt(self.FOID) > 0)
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        cattrs = ['FieldTypeID', 'FieldAccess', 'FieldDescription', 'FieldNameAsDisplayed', 'FieldFormat', 'FID', 'Alignment', 'FieldPosition', 'FieldLVColWidth', 'FieldLeft', 'FieldTop', 'FieldWidth', 'FieldHeight', 'FieldNamePosition', 'FieldDefaultDblClickAction', 'FieldSheetID', 'FieldTabIndex', 'FieldOwnerClassID', 'WWWFilter', 'WWWMask', 'WWWRegex', 'WWWMinValue', 'WWWMaxValue', 'WWWDefaultValue']
        if name in cattrs:
            mfield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            ret = mfield[self.FOID]
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        dattrs_e = {'FieldValueAsString': 'aFieldValue', 'FieldDefaultValueAsString': 'aFieldDefaultValue', }
        if name in dattrs_e:
            mfield = aICORDBEngine.Classes.MetaField.FieldsByName(dattrs_e[name])
            ret = mfield[self.FOID]
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        dattrs_dv = {'AllowRead': '1', 'AllowWrite': '1', }
        if name in dattrs_dv:
            ret = dattrs_dv[name]
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldPath':
            aclass = aICORDBEngine.Classes[self.CID]
            ret = aclass.ClassPath + '\\' + self.FName
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldType':
            ret = aICORDBEngine.Classes.GetTypeByTypeID(self.FieldTID)
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'LastModified':
            mfield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            return mfield.ValuesAsDateTime(self.FOID)
        if name == 'AlignmentStd':
            mfield = aICORDBEngine.Classes.MetaField.aFieldAlignment
            avalue = mfield.ValuesAsInt(self.FOID)
            if not avalue:
                if self.FieldTID in [mt_Integer, mt_Double, mt_DateTime]:
                    avalue = 1    #taRightJustify
                else:
                    avalue = 0    #taLeftJustify
            elif avalue == 1:
                avalue = 0    #taLeftJustify
            elif avalue == 2:
                avalue = 2    #taCenter
            elif avalue == 3:
                avalue = 1    #taRightJustify
            else:
                avalue = 0
            ret = str(avalue)
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldEditor':
            mfield = aICORDBEngine.Classes.MetaField.aFieldEditor
            aeditor = mfield.ValuesAsInt(self.FOID)
            if self.FieldTID == mt_DateTime and aeditor <= 0:
                aeditor = 7
            elif self.FieldTID == mt_Bool:
                aeditor = 8
            ret = d_FieldEditor.get(aeditor, 'None')
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'ClassItem':
            return aICORDBEngine.Classes[self.CID]
        if name == 'IsMemo':
            ret = int(self.FieldTypeID == str(mt_String) and self.IsContainer == '1')
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldAccessI':
            ret = FA_Public
            s = self.FieldAccess
            if s == 'Public':
                ret = FA_Public
            if s == 'Private':
                ret = FA_Private
            if s == 'Protected':
                ret = FA_Protected
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name == 'FieldCreated':
            ret = aICORDBEngine.Classes.MetaField.aFieldName.GetValueLastModified(self.FOID)
            self.__dict__['_FieldProperties'][name] = ret
            return ret
        if name in ['AllowReadGroups', 'AllowWriteGroups', 'WWWMenuImageField', 'WWWMenuImageClosedField']:
            afield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            return afield.GetRefList(self.FOID)
        return getattr(__builtins__, name)

    def __setattr__(self, name, value):
        if self.__dict__['_FieldProperties'].has_key(name):
            del self.__dict__['_FieldProperties'][name]
        attrs=('FieldValueAsString','FieldDefaultValueAsString','FieldDescription', \
           'FieldNameAsDisplayed','FieldFormat','IsReportProtected','IsAliased','IsObligatory','IsInteractive','IsVirtual','IsCached',\
           'FieldAccessI', \
           'Alignment','FieldEditor', \
           'FieldPosition','FieldLVColWidth','FieldLeft','FieldTop','FieldWidth','FieldHeight','FieldNamePosition','FieldDefaultDblClickAction','FieldSheetID','FieldTabIndex',\
           'IsReadOnly') # yapf: disable
        if name in attrs:
            if name == 'FieldAccessI':
                name = 'FieldAccess'
                if value == FA_Public:
                    value = 'Public'
                elif value == FA_Private:
                    value = 'Private'
                elif value == FA_Protected:
                    value = 'Protected'
                else:
                    value = 'Public'
            return aICORDBEngine.icorapi.SetFieldProperty(GetUID(), self.CID, self.FName, name, value)
        if name in ['WWWDisabled', 'WWWSingleValue', 'WWWDefaultInput', 'WWWDefaultCheck', 'WWWUpdateRefs', 'WWWBackRefField', 'WWWLowercase', 'WWWUppercase', 'WWWNoSpace', 'WWWUnsigned', 'WWWFilter', 'WWWMask', 'WWWRegex', 'WWWMinValue', 'WWWMaxValue', 'WWWDefaultValue', 'WWWUnique', 'WWWTreeRecur', 'WWWTreeRecurObjects', 'WWWMenuImageField', 'WWWMenuImageClosedField', 'WWWSortable']:
            afield = aICORDBEngine.Classes.MetaField.FieldsByName('a' + name)
            if not isinstance(value, types.StringTypes):
                value = str(value)
            afield[self.FOID] = value
            return
        self.__dict__[name] = value

    def __setitem__(self, key, value):
        return self.SetValues(key, value)

    def __repr__(self):
        return self.Name

    def __iter__(self):
        from icorlib.icoriterators import FieldOIDIterator
        return FieldOIDIterator(self)

    def ClearAllValues(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.ClearAllValues(UID, self.CID, self.FName)

    def DeleteValueByID(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return -1

    def GetFirstValueID(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFirstFieldValueID(UID, self.CID, self.FName)

    def GetNextValueID(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextFieldValueID(UID, self.CID, self.FName, aid)

    def GetLastValueID(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetLastFieldValueID(UID, self.CID, self.FName)

    def GetPrevValueID(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetPrevFieldValueID(UID, self.CID, self.FName, aid)

    def GetNextValue(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextFieldValue(UID, self.CID, self.FName, value)

    def GetPrevValue(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetPrevFieldValue(UID, self.CID, self.FName, value)

    def GetNextValueInt(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextFieldValueInt(UID, self.CID, self.FName, value)

    def GetPrevValueInt(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetPrevFieldValueInt(UID, self.CID, self.FName, value)

    def GetValueIDByPosition(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetValueIDByPosition(UID, self.CID, self.FName, aid)

    def CompareOIDs(self, aoid1, aoid2, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.CompareOIDs(UID, self.CID, self.FName, aoid1, aoid2)

    def CompareOIDValue(self, aoid, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if isinstance(avalue, types.StringTypes):
            return aICORDBEngine.icorapi.CompareOIDValue(UID, self.CID, self.FName, aoid, avalue)
        else:
            v = self.ValuesAsComp(aoid, UID=UID)
            if v > avalue:
                return 1
            elif v < avalue:
                return -1
            return 0

    def ValueExists(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.ValueExists(UID, self.CID, self.FName, aid)

    def ObjectsCount(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldObjectsCount(UID, self.CID, self.FName)

    def Identifiers(self, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if isinstance(avalue, types.StringTypes):
            return aICORDBEngine.icorapi.FindValue(UID, self.CID, self.FName, avalue)
        elif type(avalue) == type(1):
            if self.FieldTID == mt_Bool:
                return aICORDBEngine.icorapi.FindValueBoolean(UID, self.CID, self.FName, avalue)
            return aICORDBEngine.icorapi.FindValueInteger(UID, self.CID, self.FName, avalue)
        elif type(avalue) == type(1.0):
            return aICORDBEngine.icorapi.FindValueFloat(UID, self.CID, self.FName, avalue)
        elif type(avalue) == type(()) or type(avalue) == type([]):
            if len(avalue) == 3:
                y, m, d = avalue
                h, mm, s, ms = 0, 0, 0, 0
            else:
                y, m, d, h, mm, s, ms = avalue
            return aICORDBEngine.icorapi.FindValueDateTime(UID, self.CID, self.FName, y, m, d, h, mm, s, ms)
        return aICORDBEngine.icorapi.FindValue(UID, self.CID, self.FName, str(avalue))

    def GetDefaultValue(self, asstring=0):
        if self.Name == 'aFieldTypeID':    # and (self.CID=='CLASSES_System_ICORClass'):
            atype = mt_Integer
        else:
            atype = self.FieldTID
        if atype <= MAX_ICOR_SYSTEM_TYPE:
            if atype is None or atype in [mt_String, mt_Memo]:
                return ''
            elif atype in [mt_Integer, mt_Boolean]:
                if asstring:
                    return '0'
                return 0
            elif atype in [mt_Double]:
                if asstring:
                    return '0.0'
                return 0.0
            elif atype == mt_DateTime:
                if asstring:
                    return START_DATE_TIME_STR
                return START_DATE_TIME
        return ''

    def Values(self, aid, aasstring=1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if ICOR_EXECUTE_EXTERNAL:
            adefault = self.GetDefaultValue(asstring=1)
            return aICORDBEngine.icorapi.GetFieldValue(UID, self.CID, self.FName, aid, adefault=adefault)
        return aICORDBEngine.icorapi.GetFieldValue(UID, self.CID, self.FName, aid)

    __getitem__ = Values
    ValuesAsString = Values

    def ValuesAsDateTime(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldValueDateTime(UID, self.CID, self.FName, aid)

    def ValuesFmt(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ft = self.FieldTID
        if (ft in [mt_Boolean, mt_DateTime, ]) or not self.FieldFormat:
            return self.Values(aid, UID=UID)
        elif ft == mt_Integer:
            return str2fmtstr(self.FieldFormat, self.ValuesAsComp(aid, UID=UID))
        elif ft == mt_Double:
            return str2fmtstr(self.FieldFormat, self.ValuesAsComp(aid, UID=UID))
        return self.Values(aid, UID=UID)

    def ValuesAsInt(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = self.Values(aid, aasstring=0, UID=UID)
        if not ret:
            return 0
        if (self.FieldTID == mt_Boolean) and (isinstance(ret, types.StringTypes)):
            ret = str2bool(ret)
        return int(ret)

    def ValuesAsFloat(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = self.Values(aid, aasstring=0, UID=UID)
        if not ret:
            return 0.0
        return float(ret)

    def ValuesAsPyTime(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        x = self.ValuesAsTime(aid, UID=UID)
        return time.mktime(x)

    def ValuesAsDate(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        x = self.ValuesAsDateTime(aid, UID=UID)
        return tuple(x[:3])

    def ValuesAsTime(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        x = self.ValuesAsDateTime(aid, UID=UID)
        return tuple(x[3:])

    def ValuesByPosition(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldValueByPosition(UID, self.CID, self.FName, aid)

    def ValuesAsComp(self, aid, ajsonfriendly=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ft = self.FieldTID
        if ft == mt_Boolean:
            return self.ValuesAsInt(aid, UID=UID) > 0
        elif ft == mt_Integer:
            return self.ValuesAsInt(aid, UID=UID)
        elif ft == mt_String:
            return self.Values(aid, UID=UID)
        elif ft == mt_DateTime:
            ret = self.ValuesAsDateTime(aid, UID=UID)
            if ajsonfriendly:
                ret = '%04d-%02d-%02d %02d:%02d:%02d' % (ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
            return ret
        elif ft == mt_Double:
            return self.ValuesAsFloat(aid, UID=UID)
        return self.Values(aid, UID=UID)

    def SetValuesAsString(self, aid, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.SetFieldValue(UID, self.CID, self.FName, aid, avalue)

    def SetValuesAsPyTime(self, aid, avalue, UID=-1):
        return -1

    def SetValuesAsDate(self, aid, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d = value
        return aICORDBEngine.icorapi.SetFieldValueDate(UID, self.CID, self.FName, aid, y, m, d)

    def SetValuesAsTime(self, aid, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        h, m, s, ms = value
        return aICORDBEngine.icorapi.SetFieldValueTime(UID, self.CID, self.FName, aid, h, m, s, ms)

    def SetValuesAsDateTime(self, aid, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = value
        return aICORDBEngine.icorapi.SetFieldValueDateTime(UID, self.CID, self.FName, aid, y, m, d, h, mm, s, ms)

    def SetValues(self, aid, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if not isinstance(avalue, types.StringTypes):
            ftid = self.FieldTID
            if ftid > MAX_ICOR_SYSTEM_TYPE:
                if type(avalue) == type([]):
                    if avalue:
                        if type(avalue[0]) == type(1):
                            avalue = string.join(map(repr, avalue) + [''], ':')
                        else:
                            avalue = string.join(map(lambda x: str(x[0]) + ':' + str(x[1]) + ':', avalue), '')
                    else:
                        avalue = ''
                elif hasattr(avalue, 'AsString'):
                    avalue = avalue.AsString()
                else:
                    return 0
            elif ftid in [mt_Integer, mt_Double, mt_Boolean, mt_Bool]:
                avalue = str(avalue)
            elif ftid in [mt_DateTime, mt_Date, mt_Time]:
                if len(avalue) == 3:
                    return self.SetValuesAsDate(aid, avalue, UID=UID)
                elif len(avalue) == 4:
                    return self.SetValuesAsTime(aid, avalue, UID=UID)
                else:
                    return self.SetValuesAsDateTime(aid, avalue, UID=UID)
        return aICORDBEngine.icorapi.SetFieldValue(UID, self.CID, self.FName, aid, avalue)

    def SetTestValues(self, aid, aoperator, atestvalue, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if not isinstance(atestvalue, types.StringTypes):
            atestvalue = str(atestvalue)
        if not isinstance(avalue, types.StringTypes):
            avalue = str(avalue)
        return aICORDBEngine.icorapi.SetTestFieldValue(UID, self.CID, self.FName, aid, aoperator, atestvalue, avalue)

    def SetTestIncValues(self, aid, aoperator, atestvalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.FieldTID != mt_Integer:
            return 0
        if not isinstance(atestvalue, types.StringTypes):
            atestvalue = str(atestvalue)
        return aICORDBEngine.icorapi.SetTestIncFieldValue(UID, self.CID, self.FName, aid, aoperator, atestvalue)

    def SetTestDecValues(self, aid, aoperator, atestvalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.FieldTID != mt_Integer:
            return 0
        if not isinstance(atestvalue, types.StringTypes):
            atestvalue = str(atestvalue)
        return aICORDBEngine.icorapi.SetTestDecFieldValue(UID, self.CID, self.FName, aid, aoperator, atestvalue)

    def GetFieldModification(self, aid, UID=-1):    # as string
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldModification(UID, self.CID, self.FName, aid)

    def SetFieldModification(self, aid, avalue, UID=-1):    #as string
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.SetFieldModification(UID, self.CID, self.FName, aid, avalue)

    def GetLastModified(self, UID=-1):    #as tuple
        if UID == -1:
            del UID
            UID = GetUID()
        return self.LastModified

    def SetLastModified(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = value
        return aICORDBEngine.icorapi.SetFieldLastModification(UID, self.CID, self.FName, y, m, d, h, mm, s, ms)

    def GetValueLastModified(self, aoid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldValueLastModification(UID, self.CID, self.FName, aoid)

    def SetValueLastModified(self, aoid, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = value
        return aICORDBEngine.icorapi.SetFieldValueLastModification(UID, self.CID, self.FName, aoid, y, m, d, h, mm, s, ms)

    def GetFieldVersions(self, aoid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFieldVersions(UID, self.CID, self.FName, aoid)

    def GetFirstDeletedOffset(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFirstDeletedOffset(UID, self.CID, self.FName)

    def GetNextDeletedOffset(self, aoffset, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextDeletedOffset(UID, self.CID, self.FName, aoffset)

    def GetRecValueAsString(self, aoffset, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetRecValueAsString(UID, self.CID, self.FName, aoffset)

    def GetRecLastModification(self, aoffset, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetRecLastModification(UID, self.CID, self.FName, aoffset)

    def GetRecOID(self, aoffset, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetRecOID(UID, self.CID, self.FName, aoffset)

    def AddRefs(self, aid, lrefs, asortedreffield=None, adescending=0, dosort=0, aremoveexisting=0, ainsertifnotexists=0, ainsertbefore=None, ainsertafter=None, UID=-1):
        from icorlib.icoriterators import FieldRefIterator
        if UID == -1:
            del UID
            UID = GetUID()
        if asortedreffield is None:
            if len(lrefs) > 0:
                if (ainsertbefore is None) and (ainsertafter is None):
                    if type(lrefs[0]) == type(1):
                        ss = string.join(map(repr, lrefs) + [''], ':')
                    else:
                        ss = string.join(map(lambda x: str(x[0]) + ':' + str(x[1]), lrefs), ':')
                    if ss and ss[-1:] != ':':
                        ss = ss + ':'
                    if not aremoveexisting:
                        arefs = self.GetRefList(aid, UID=UID)
                        brefs = FieldRefIterator(ss)
                        arefs.AddRefs(brefs)
                        return self.SetValues(aid, arefs.AsString(), UID=UID)
                    else:
                        return self.SetValues(aid, ss, UID=UID)
                else:
                    amidpos = 0
                    if ainsertbefore:
                        boid, bcid = ainsertbefore
                    else:
                        boid, bcid = ainsertafter
                        amidpos = 1
                    arefs = self.GetRefList(aid, UID=UID)
                    if aremoveexisting:
                        if type(lrefs[0]) == type(1):
                            i = 0
                            while i < len(lrefs):
                                aoid, acid = lrefs[i], lrefs[i + 1]
                                arefs.DelRef(aoid, acid)
                                i = i + 2
                        else:
                            for aoid, acid in lrefs:
                                arefs.DelRef(aoid, acid)
                    pos, find = arefs.FindRef(boid, bcid)
                    if type(lrefs[0]) == type(1):
                        i = 0
                        while i < len(lrefs):
                            aoid, acid = lrefs[i], lrefs[i + 1]
                            arefs.InsertRef(pos + amidpos, aoid, acid)
                            if find:
                                pos = pos + 1
                            i = i + 2
                    else:
                        for aoid, acid in lrefs:
                            arefs.InsertRef(pos + amidpos, aoid, acid)
                            if find:
                                pos = pos + 1
                    return self.SetValues(aid, arefs.AsString(), UID=UID)
        else:
            if len(lrefs) > 0:
                arefs = self.GetRefList(aid, UID=UID)
                if dosort:
                    arefs.sort(asortedreffield)
                    if adescending:
                        arefs.reverse()
                if type(lrefs[0]) == type(1):
                    i = 0
                    while i < len(lrefs):
                        aoid, acid = lrefs[i], lrefs[i + 1]
                        if ainsertifnotexists:
                            if not arefs.RefExists(aoid, acid):
                                arefs.InsertRefEx(asortedreffield, aoid, acid, adescending)
                        else:
                            if aremoveexisting:
                                arefs.DelRef(aoid, acid)
                            arefs.InsertRefEx(asortedreffield, aoid, acid, adescending)
                        i = i + 2
                else:
                    for aoid, acid in lrefs:
                        if ainsertifnotexists:
                            if not arefs.RefExists(aoid, acid):
                                arefs.InsertRefEx(asortedreffield, aoid, acid, adescending)
                        else:
                            if aremoveexisting:
                                arefs.DelRef(aoid, acid)
                            arefs.InsertRefEx(asortedreffield, aoid, acid, adescending)
                return self.SetValues(aid, arefs.AsString(), UID=UID)

    def DeleteRefs(self, aid, lrefs=None, aobjectdelete=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if lrefs is None:
            lrefs = []
        if lrefs:
            if type(lrefs[0]) == type(1):
                l = []
                i = 0
                while i < len(lrefs):
                    aoid, acid = lrefs[i], lrefs[i + 1]
                    l.append([aoid, acid])
                    i = i + 2
                lrefs = l
        arefs = self.GetRefList(aid, UID=UID)
        while arefs.position >= 0:
            if not arefs.Class.ObjectExists(arefs.OID, UID=UID):
                lrefs.append([arefs.OID, arefs.CID])
            arefs.Next()
        arefs.First()
        for aoid, acid in lrefs:
            if aobjectdelete:
                arefs.Class.DeleteObject(aoid, UID=UID)
            arefs.DelRef(aoid, acid)
        return self.SetValues(aid, arefs.AsString(), UID=UID)

    def GetRefList(self, aid, UID=-1):
        from icorlib.icoriterators import FieldRefIterator
        if UID == -1:
            del UID
            UID = GetUID()
        arefs = FieldRefIterator(self.Values(aid, UID=UID))
        arefs.RefField = self
        arefs.RefOID = aid
        return arefs

    def SetRefList(self, aid, areflist, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.SetValues(aid, areflist.AsString(), UID=UID)    # as string

    def GetRefObject(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        arefs = self.GetRefList(aid, UID=UID)
        return arefs.AsObject()

    def GetRefOIDsByValues(self, afieldname, lvalues, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = []
        afield = self.ClassOfType.FieldsByName(afieldname, UID=UID)
        for avalue in lvalues:
            roid = afield.Identifiers(avalue, UID=UID)
            if roid >= 0:
                ret.append(roid)
        return ret

    def ForEachRefObject(self, afunc, aid, *parms):
        from icorlib.icoriterators import ForEachRefObjectParms
        ForEachRefObjectParms(self, aid, afunc, parms)

    def DeleteReferencedObjects(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        arefs = self.GetRefList(aid, UID=UID)
        self.SetValues(aid, '', UID=UID)
        while arefs.position >= 0:
            arefs.Class.DeleteObject(arefs.OID, UID=UID)
            arefs.Next()
        return -1

    def UpdateReferencedObjects(self, aid, fname='', adeleterefs=0, aupdaterefs=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if not fname:
            afields = self.ClassOfType.GetFieldsList(UID=UID)
            for fname in afields:
                bfield = self.ClassOfType.FieldsByName(fname, UID=UID)
                if bfield.ClassOfType is not None:
                    if bfield.ClassOfType.CID == self.CID:
                        afield = bfield
                        break
        if isinstance(fname, types.StringTypes):
            afield = self.ClassOfType.FieldsByName(fname, UID=UID)
        else:
            afield = fname
        if afield is None:
            return None
        arefs = self.GetRefList(aid, UID=UID)
        if adeleterefs:
            sref = ''
        else:
            sref = str(aid) + ':' + str(self.CID) + ':'
        while arefs.position >= 0:
            if aupdaterefs:
                brefs = afield.GetRefList(arefs.OID, UID=UID)
                w = brefs.RefExists(aid, self.CID)
                if adeleterefs:
                    if w:
                        brefs.DelRef(aid, self.CID)
                        afield[arefs.OID] = brefs.AsString()
                else:
                    if not w:
                        brefs.AddRef(aid, self.CID)
                        afield[arefs.OID] = brefs.AsString()
            else:
                afield[arefs.OID] = sref
            arefs.Next()
        return afield

    def ForEachValueByRange(self, afunc, akey1, akey2, *parms):
        from icorlib.icorsearch import ForEachValueByRangeParms
        ForEachValueByRangeParms(self, afunc, akey1, akey2, parms)

    def ForEachValueByPattern(self, afunc, akey1, apattern, *parms):
        from icorlib.icorsearch import ForEachValueByPatternParms
        ForEachValueByPatternParms(self, afunc, akey1, apattern, parms)

    def GetFieldOIDsBySearchValue(self, value, acasesensitive=0, aregexp=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return icorapi.GetFieldOIDsBySearchValue(UID, self.CID, self.FName, value, acasesensitive=acasesensitive, aregexp=aregexp)

    def GetFieldDefinition(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aftid = int(self.FieldTypeID)
        fdi = ICORFieldDefinition(self.FName, aftid)
        fdi.FAccess = self.FieldAccessI
        fdi.FInteractive = int(self.IsInteractive)
        fdi.FObligatory = int(self.IsObligatory)
        fdi.FContainerType = int(self.IsContainer)
        fdi.FIndexed = int(self.IsIndexed)
        fdi.FFastIndexed = int(self.IsFastIndexed)
        fdi.FAlias = int(self.IsAliased)
        fdi.FVirtual = int(self.IsVirtual)
        fdi.FCached = int(self.IsCached)
        return fdi

    def SelectValues(self, acaption='', adisabletoolbar=0, adisableediting=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.ClassOfType is None:
            return aICORDBEngine.icorapi.SelectFieldValues(UID, self.CID, self.FName)
        return self.ClassOfType.SelectObjects(acaption=acaption, adisabletoolbar=adisabletoolbar, adisableediting=adisableediting)

    def SelectInRepository(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aICORDBEngine.icorapi.RepositoryChange(UID, 'FieldSelect', -1, -1, self.FieldPath, '', '')


class ICORDBMethodItem:

    def __init__(self, CID, Name):
        self.__dict__['_MethodProperties'] = {}
        self.CID = CID
        self.Name = Name

    def __getattr__(self, name):
        if self.__dict__['_MethodProperties'].has_key(name):
            return self.__dict__['_MethodProperties'][name]
        if name == 'MOID':
            s = str(self.BaseCID) + '_' + self.Name
            ret = aICORDBEngine.Classes.MetaMethod.aIDClassMethod.Identifiers(s)
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        cattrs = ['MethodDescription', 'MethodText', 'Language', 'WWWDescription']
        if name in cattrs:
            mfield = aICORDBEngine.Classes.MetaMethod.FieldsByName('a' + name)
            ret = mfield[self.MOID]
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        if name == 'MethodPath':
            aclass = aICORDBEngine.Classes[self.BaseCID]
            ret = aclass.ClassPath + '\\' + self.Name
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        if name == 'MethodPathImport':
            aclass = aICORDBEngine.Classes[self.BaseCID]
            ret = aclass.ClassPathImport + '_' + self.Name
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        battrs = ['IsMenuHidden', ]
        if name in battrs:
            mfield = aICORDBEngine.Classes.MetaMethod.FieldsByName('a' + name)
            ret = str(str2bool(mfield[self.MOID]))
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        iattrs = ['IsParallel', 'IsQueued', 'WWWMethod', 'WWWConfirmExecute']
        if name in iattrs:
            mfield = aICORDBEngine.Classes.MetaMethod.FieldsByName('a' + name)
            ret = str2bool(mfield[self.MOID])
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        dzattrs = ['MID', ]
        if name in dzattrs:
            mfield = aICORDBEngine.Classes.MetaMethod.FieldsByName('a' + name)
            ret = mfield[self.MOID]
            if not ret:
                ret = '0'
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        if name == 'LastModified':
            mfield = aICORDBEngine.Classes.MetaMethod.FieldsByName('a' + name)
            return mfield.ValuesAsDateTime(self.MOID)
        dattrs_dv = {'MethodAccess': '0', }
        if name in dattrs_dv:
            ret = dattrs_dv[name]
            self.__dict__['_MethodProperties'][name] = ret
            return ret

        if name == 'BaseCID':
            aclass = aICORDBEngine.Classes[self.CID]
            aname = self.Name
            ret = -1
            while aclass is not None:
                if aclass.IsMethodInThisClass(aname):
                    ret = aclass.CID
                    break
                aclass = aclass.Inherited
            self.__dict__['_MethodProperties'][name] = ret
            return ret
        xattrs = ['Modified', 'AllowRead', 'AllowWrite', ]
        if name == 'MethodAccessI':
            s = self.MethodAccess
            if s == 'Public' or s == '0':
                return FA_Public
            if s == 'Private' or s == '1':
                return FA_Private
            if s == 'Protected' or s == '2':
                return FA_Protected
            return FA_Public
        if name == 'AllowReadGroups':
            return aICORDBEngine.Classes.MetaMethod.aAllowReadGroups.GetRefList(self.MOID)
        if name == 'AllowWriteGroups':
            return aICORDBEngine.Classes.MetaMethod.aAllowWriteGroups.GetRefList(self.MOID)
        if name == 'WWWMenuImageLink':
            return aICORDBEngine.Classes.MetaMethod.aWWWMenuImageLink.GetRefList(self.MOID)
        return getattr(__builtins__, name)

    def __setattr__(self, name, value):
        attrs = ('MethodDescription', 'MethodAccess', 'MethodText', 'IsMenuHidden', 'Language', 'WWWDescription')
        if name in attrs:
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        elif name == 'MethodAccessI':
            name = 'MethodAccess'
            if value == FA_Public:
                value = 'Public'
            elif value == FA_Private:
                value = 'Private'
            elif value == FA_Protected:
                value = 'Protected'
            else:
                value = 'Public'
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        elif name == 'IsParallel':
            if type(value) == type(1):
                value = str(value)
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        elif name == 'IsQueued':
            if type(value) == type(1):
                value = str(value)
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        elif name == 'WWWMethod':
            if type(value) == type(1):
                value = str(value)
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        elif name == 'WWWConfirmExecute':
            if type(value) == type(1):
                value = str(value)
            return aICORDBEngine.icorapi.SetMethodProperty(GetUID(), self.CID, self.Name, name, value)
        else:
            self.__dict__[name] = value

    def __repr__(self):
        return self.Name

    def Execute(self, FieldName='', OID=-1, Value='', UID=-1, anostringvalue=0, aqueued=0, ainternalexecute=0, alogger=None, acontext=None, apriority='N03'):
        if UID == -1:
            del UID
            UID = GetUID()
        if alogger:
            alogger(msg='  execute: %d %s q:%d p:%d' % (self.CID, self.Name, self.IsQueued, self.IsParallel))
        if aqueued or self.IsQueued or self.IsParallel:
            if alogger:
                alogger(msg='    execute 1: %d %s' % (self.CID, self.Name, ))
            aICORDBEngine.SysBase.AddExecutorMethod(self.CID, self.Name, FieldName, OID, Value, UID, self.IsParallel, self.IsQueued, apriority)
            if 0:
                apclass = aICORDBEngine.Classes.ClassQueuedParameters
                mname = self.MethodPath.replace('\\', '_')
                mname = mname.replace('/', '_')
                if mname in QUEUED_METHODS_SINGLE_CALL:
                    apoid = apclass.Name.Identifiers(mname, UID=UID)
                    if apoid >= 0:
                        return
                apoid = apclass.AddObject(UID=UID)
                apclass.BCID[apoid] = self.CID
                apclass.BFieldName[apoid] = FieldName
                apclass.BOID[apoid] = OID
                apclass.BUID[apoid] = UID
                apclass.MOID[apoid] = self.MOID
                apclass.MIsParallel[apoid] = self.IsParallel
                apclass.MIsQueued[apoid] = self.IsQueued
                apclass.BValue[apoid] = Value
                dt = time.localtime(time.time())
                apclass.BEventTime.SetValuesAsDateTime(apoid, (dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], 0), UID=UID)
                apclass.Name[apoid] = mname
                apclass.Status[apoid] = 'Ready'
        elif not ainternalexecute and self.Language == 'Python':
            if alogger:
                alogger(msg='    execute 2: %d %s' % (self.CID, self.Name, ))
            mname = self.MethodPath.replace('\\', '_')
            mname = mname.replace('/', '_')
            amethod = __import__(mname)
            if acontext is None:
                acontext = {}
            amethod.CONTEXT = acontext
            ret = None
            if hasattr(amethod, 'ICORMain'):
                ret = amethod.ICORMain(self.CID, FieldName, OID, Value, UID)
            return ret
        else:
            if alogger:
                alogger(msg='    execute 3: %d %s' % (self.CID, self.Name, ))
            return aICORDBEngine.icorapi.ExecuteMethod(UID, self.CID, self.Name, FieldName, OID, Value, anostringvalue)

    __call__ = Execute

    def GetMethodDefinition(self):
        mdi = ICORMethodDefinition(self.Name)
        mdi.MDescription = self.MethodDescription
        mdi.MAccess = self.MethodAccessI
        mdi.MIsParallel = self.IsParallel
        return mdi

    def AsModule(self):
        mname = self.MethodPath.replace('\\', '_')
        mname = mname.replace('/', '_')
        return __import__(mname)

    def GetLastModified(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.LastModified

    def SetLastModified(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = value
        return aICORDBEngine.icorapi.SetMethodLastModification(UID, self.CID, self.Name, y, m, d, h, mm, s, ms)

    def SelectInRepository(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aICORDBEngine.icorapi.RepositoryChange(UID, 'MethodSelect', -1, -1, self.MethodPath, '', '')

    def SelectInEditor(self, aline='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aICORDBEngine.icorapi.SelectInEditor(UID, self.CID, self.Name, aline)


class ICORDBClassItem:

    def __init__(self, CID):
        self.__dict__['_ClassProperties'] = {}
        self.CID = CID
        self.Fields = {}
        self.Methods = {}
        self._MethodNames = {}
        self._FieldNames = {}

    def __getattr__(self, name):
        if self.__dict__['_ClassProperties'].has_key(name):
            return self.__dict__['_ClassProperties'][name]
        cattrs = ['ClassDescription', 'ClassColIDWidth', 'ClassFormLeft', 'ClassFormTop', 'ClassFormWidth', 'ClassFormHeight', 'ClassFieldsHidden', 'BaseCID', 'BasePath']
        if name in cattrs:
            mfield = aICORDBEngine.Classes.MetaClass.FieldsByName('a' + name)
            ret = mfield[self.CID]
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        bsattrs = ['IsSystem', 'IsVirtual', 'ReportClass', 'IsReadOnly']
        if name in bsattrs:
            mfield = aICORDBEngine.Classes.MetaClass.FieldsByName('a' + name)
            ret = str(str2bool(mfield[self.CID]))
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        if name == 'NameOfClass':
            ret = aICORDBEngine.Classes.MetaClass.aClassName[self.CID]
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        if name == 'ClassPath':
            ret = self.BasePath + '\\' + self.NameOfClass
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        if name == 'ClassPathImport':
            bpath = self.BasePath
            bpath = bpath.replace('\\', '_')
            bpath = bpath.replace('/', '_')
            ret = bpath + '_' + self.NameOfClass
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        dattrs_dv = {'AllowRead': '1', 'AllowWrite': '1', }
        if name in dattrs_dv:
            ret = dattrs_dv[name]
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        if name == 'LastModified':
            mfield = aICORDBEngine.Classes.MetaClass.FieldsByName('a' + name)
            ret = mfield.ValuesAsDateTime(self.CID)
            return ret
        if name == 'Inherited':
            acid = int(self.BaseCID)
            if acid > MAX_ICOR_SYSTEM_TYPE:
                return self.Classes.GetClassByID(acid)
            else:
                return None
        elif name in ['EditorSheets', 'AllowReadGroups', 'AllowWriteGroups', 'WWWMenuImageClass', 'WWWMenuImageClosedClass', 'WWWMenuImageObject', 'WWWMenuImageClosedObject']:
            afield = self.Classes.MetaClass.FieldsByName('a' + name)
            return afield.GetRefList(self.CID)
        elif name == 'WWWDescription':
            ret = self.Classes.MetaClass.aWWWDescription[self.CID]
            if not ret:
                ret = self.NameOfClass
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name == 'ClassCreated':
            ret = aICORDBEngine.Classes.MetaClass.aClassName.GetValueLastModified(self.CID)
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name in ['WWWMaxColDictDescription', ]:
            afield = self.Classes.MetaClass.FieldsByName('a' + name)
            ret = afield.ValuesAsInt(self.CID)
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name in ['WWWDisableDescription', 'WWWJumpToBackRefObject']:
            afield = self.Classes.MetaClass.FieldsByName('a' + name)
            ret = 0
            if afield.ValuesAsInt(self.CID) > 0:
                ret = 1
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name in ['WWWEditPageTopHTML', 'WWWEditPageBottomHTML']:
            afield = self.Classes.MetaClass.FieldsByName('a' + name)
            return afield.GetRefList(self.CID).AsObject()
        elif name == 'FieldsAsColumns':
            ret = []
            flist = self.GetFieldsList()
            for afname in flist:
                afield = self.FieldsByName(afname)
                if afield.IsAliased != '1' or afield.IsInteractive != '1':
                    continue
                try:
                    ret.append([int(afield.FieldPosition), afield])
                except:
                    print '$$$', 'fieldposition', self.CID, afname, afield.FOID
                    raise
            ret.sort()
            ret = map(lambda x: x[1], ret)
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name == 'BackRefFields':
            ret = []
            afields = self.GetFieldsList()
            for afname in afields:
                afield = self.FieldsByName(afname)
                if afield.WWWBackRefField:
                    ret.append(afield)
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        elif name == 'UpdateRefFields':
            ret = []
            afields = self.GetFieldsList()
            for afname in afields:
                afield = self.FieldsByName(afname)
                if afield.WWWUpdateRefs:
                    ret.append(afield)
            self.__dict__['_ClassProperties'][name] = ret
            return ret
        ret = self.FieldsByName(name)
        if ret:
            return ret
        if self.IsMethodInClass(name) == 1:
            return self.MethodsByName(name)

    def __setattr__(self, name, value):
        attrs=('ClassDescription','IsSystem','IsVirtual', \
           'ClassColIDWidth','ClassFormLeft','ClassFormTop', \
           'ClassFormWidth','ClassFormHeight','ClassFieldsHidden', \
           'ReportClass','IsReadOnly')
        if name in attrs:
            return aICORDBEngine.icorapi.SetClassProperty(GetUID(), self.CID, name, value)
        elif name in ['WWWDescription', 'WWWDisableDescription', 'WWWJumpToBackRefObject', 'WWWEditPageTopHTML', 'WWWEditPageBottomHTML', 'WWWMaxColDictDescription', 'WWWMenuImageClass', 'WWWMenuImageClosedClass', 'WWWMenuImageObject', 'WWWMenuImageClosedObject']:
            afield = self.Classes.MetaClass.FieldsByName('a' + name)
            afield[self.CID] = value
        else:
            self.__dict__[name] = value

    def __getitem__(self, oid):
        return ICORDBObject(oid, self)

    def __repr__(self):
        return self.NameOfClass

    def __iter__(self):
        from icorlib.icoriterators import ClassOIDIterator
        return ClassOIDIterator(self)

    def GetLastModified(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.LastModified

    def SetLastModified(self, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = value
        return aICORDBEngine.icorapi.SetClassLastModification(UID, self.CID, y, m, d, h, mm, s, ms)

    def AddClass(self, aname, acid=-1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.Classes.AddClass(self.CID, aname, acid, UID=UID)

    def ClearAllObjects(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.ClearAllObjects(UID, self.CID)

    def IsFieldInClass(self, fname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = self._FieldNames.get(fname, None)
        if ret is None:
            ret = 0
            if fname in self.GetFieldsList(UID=UID):
                ret = 1
            self._FieldNames[fname] = ret
        return ret

    def ClearStructInfo(self, afull=0):
        if afull:
            self.__dict__['_ClassProperties'] = {}
            return
        name = '_GetFieldsList'
        if self.__dict__['_ClassProperties'].has_key(name):
            del self.__dict__['_ClassProperties'][name]
        name = '_GetMethodsList'
        if self.__dict__['_ClassProperties'].has_key(name):
            del self.__dict__['_ClassProperties'][name]

    def AddField(self, afielddef, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        tfield = self.FieldsByName(afielddef.FName)
        if tfield is not None:
            print 'Pole', afielddef.FName, 'juz istnieje'
            return None
        if self._FieldNames.has_key(afielddef.FName):
            del self._FieldNames[afielddef.FName]
        aoid = self.Classes.MetaField.AddObject(UID=UID)
        self.Classes.MetaClass.aFields[self.CID] = self.Classes.MetaClass.aFields[self.CID] + str(aoid) + ':' + str(self.Classes.MetaField.CID) + ':'
        self.Classes.MetaField.aIDClassField[aoid] = str(self.CID) + '_' + afielddef.FName
        self.Classes.MetaField.aFieldName[aoid] = afielddef.FName
        self.Classes.MetaField.aFieldNameAsDisplayed[aoid] = afielddef.FName
        if afielddef.FOwnerCID < 0:
            afielddef.FOwnerCID = self.CID
        self.Classes.MetaField.aFieldOwnerClassID[aoid] = str(afielddef.FOwnerCID)
        self.Classes.MetaField.aFieldTypeID[aoid] = str(afielddef.FTypeID)
        self.Classes.MetaField.aFieldPosition[aoid] = '0'
        self.Classes.MetaField.aFieldNamePosition[aoid] = '0'
        self.Classes.MetaField.aFieldSheetID[aoid] = '0'
        self.Classes.MetaField.aFieldDefaultDblClickAction[aoid] = '0'
        self.Classes.MetaField.aFieldLVColWidth[aoid] = '-1'
        self.Classes.MetaField.aFieldLeft[aoid] = '-1'
        self.Classes.MetaField.aFieldTop[aoid] = '-1'
        self.Classes.MetaField.aFieldWidth[aoid] = '-1'
        self.Classes.MetaField.aFieldHeight[aoid] = '-1'
        self.Classes.MetaField.aFieldTabIndex[aoid] = '-1'
        self.Classes.MetaField.aFieldAccess[aoid] = str(afielddef.FAccess)
        self.Classes.MetaField.aIsInteractive[aoid] = str(afielddef.FInteractive)
        self.Classes.MetaField.aIsContainer[aoid] = str(afielddef.FContainerType)
        self.Classes.MetaField.aIsObligatory[aoid] = str(afielddef.FObligatory)
        self.Classes.MetaField.aIsIndexed[aoid] = str(afielddef.FIndexed)
        self.Classes.MetaField.aIsAliased[aoid] = str(afielddef.FAlias)
        self.Classes.MetaField.aIsFastIndexed[aoid] = str(afielddef.FFastIndexed)
        self.Classes.MetaField.aIsVirtual[aoid] = str(afielddef.FVirtual)
        self.Classes.MetaField.aIsCached[aoid] = str(afielddef.FCached)
        #      if afielddef.FOwnerCID==self.CID:
        self.ClearStructInfo()
        aICORDBEngine.icorapi.RepositoryChange(UID, 'FieldAdd', self.CID, -1, afielddef.FName, '', '')
        clist = self.GetInheritedClassesList()
        for acid in clist:
            aci = self.Classes[acid]
            if aci is not None:
                aci.AddField(afielddef, UID=UID)
        return self.FieldsByName(afielddef.FName, UID=UID)

    def DeleteField(self, fname, aownercid='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        afield = self.FieldsByName(fname, UID=UID)
        if afield is None:
            return -1
        if not aownercid:
            aownercid = afield.FieldOwnerClassID
        if afield.FieldOwnerClassID != aownercid:
            return -1
        del self.Fields[fname]
        aidf = str(self.CID) + '_' + fname
        foid = self.Classes.MetaField.aIDClassField.Identifiers(aidf, UID=UID)
        if foid >= 0:
            arefs = self.Classes.MetaClass.aFields.GetRefList(self.CID, UID=UID)
            arefs.DelRef(foid)
            self.Classes.MetaClass.aFields[self.CID] = arefs.AsString()
            aICORDBEngine.icorapi.RepositoryChange(UID, 'FieldDelete', self.CID, -1, fname, '', '')
            self.Classes.MetaField.DeleteObject(foid, UID=UID)
        self.ClearStructInfo()
        clist = self.GetInheritedClassesList(UID=UID)
        for acid in clist:
            aci = self.Classes[acid]
            if aci is not None:
                aci.DeleteField(fname, aownercid, UID=UID)
        return -1

    def CopyField(self, aCID, aFName, copyvalues=0, afieldtype=-1, anewname='', aownercid=-1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        bclass = self.Classes[aCID]
        if bclass is None:
            print 'Klasa zrodlowa nie istnieje!'
            return None
        bfield = bclass.FieldsByName(aFName, UID=UID)
        if bfield is None:
            print 'Pole zrodlowe nie istnieje!'
            return None
        if anewname == '':
            afi = self.FieldsByName(aFName, UID=UID)
        else:
            afi = self.FieldsByName(anewname, UID=UID)
        if afi is None:
            fdi = bfield.GetFieldDefinition(UID=UID)
            if anewname != '':
                fdi.FName = anewname
            if afieldtype >= 0:
                fdi.FTypeID = afieldtype
            if aownercid != -1:
                fdi.FOwnerCID = aownercid
            afi = self.AddField(fdi, UID=UID)
        if afi is not None:
            attrs=('FieldValueAsString','FieldDefaultValueAsString','FieldDescription', \
               'FieldNameAsDisplayed','FieldFormat','IsReportProtected','IsAliased','IsObligatory','IsVirtual','IsCached',\
               'FieldAccess','Alignment','FieldEditor', \
               'FieldPosition','FieldLVColWidth','FieldLeft','FieldTop','FieldWidth','FieldHeight','FieldNamePosition','FieldDefaultDblClickAction','FieldSheetID','FieldTabIndex',\
               'IsReadOnly') # yapf: disable
            for attr in attrs:
                s = bfield.__getattr__(attr)
                afi.__setattr__(attr, s)
        if copyvalues and afi is not None:
            aoid = bfield.GetFirstValueID(UID=UID)
            while aoid >= 0:
                if not self.ObjectExists(aoid, UID=UID):
                    self.CreateObjectByID(aoid, UID=UID)
                mdate = bfield.GetValueLastModified(aoid, UID=UID)
                if afieldtype > MAX_ICOR_SYSTEM_TYPE:
                    aref = bfield.GetRefList(aoid, UID=UID)
                    s = ''
                    while aref.position >= 0:
                        s = s + str(aref.OID) + ':' + str(afieldtype) + ':'
                        aref.Next()
                    afi[aoid] = s
                else:
                    afi[aoid] = bfield[aoid]
                afi.SetValueLastModified(aoid, mdate, UID=UID)
                aoid = bfield.GetNextValueID(aoid, UID=UID)
        self.ClearStructInfo()
        return afi

    def FieldsByName(self, fname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Fields.has_key(fname):
            return self.Fields[fname]
        elif self.IsFieldInClass(fname, UID=UID):
            afield = ICORDBFieldItem(self.CID, fname)
            self.Fields[fname] = afield
            return afield
        return None

    def GetFieldsList(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        name = '_GetFieldsList'
        if self.__dict__['_ClassProperties'].has_key(name):
            return self.__dict__['_ClassProperties'][name]
        s = aICORDBEngine.icorapi.GetFieldsList(UID, self.CID)
        ret = string.split(s, ':')[:-1]
        self.__dict__['_ClassProperties'][name] = ret
        return ret

    def GetFieldsByTabID(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        lfields = self.GetFieldsList(UID=UID)
        return lfields

    def FieldsIterator(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        lfields = self.GetFieldsList(UID=UID)
        for afieldname in lfields:
            afield = self.FieldsByName(afieldname, UID=UID)
            yield afield

    def GetMethodsList(self, ainherited=1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        name = '_GetMethodsList'
        if self.__dict__['_ClassProperties'].has_key(name):
            return self.__dict__['_ClassProperties'][name]
        s = aICORDBEngine.icorapi.GetMethodsList(UID, self.CID, ainherited)
        ret = string.split(s, ':')[:-1]
        self.__dict__['_ClassProperties'][name] = ret
        return ret

    def MethodsIterator(self, ainherited=1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        lmethods = self.GetMethodsList(ainherited, UID=UID)
        for amethodname in lmethods:
            amethod = self.MethodsByName(amethodname, UID=UID)
            yield amethod

    def GetInheritedClassesList(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        arefs = self.Classes.MetaClass.aDerivedClasses.GetRefList(self.CID, UID=UID)
        return arefs.AsListOID()

    def GetInheritedClassesListStr(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        arefs = self.Classes.MetaClass.aDerivedClasses.GetRefList(self.CID, UID=UID)
        return arefs.AsStringOID()

    def GetDerivedClass(self, apath):
        return self.Classes[self.ClassPath + '\\' + apath]

    def AddMethod(self, amethoddef, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if not IsIdentifier(amethoddef.MName):
            print 'Zla nazwa metody:', amethoddef.MName
            return None
        if self.IsMethodInThisClass(amethoddef.MName):
            print 'Metoda juz istnieje:', amethoddef.MName
            return None
        aoid = self.Classes.MetaMethod.AddObject(UID=UID)
        self.Classes.MetaClass.aMethods[self.CID] = self.Classes.MetaClass.aMethods[self.CID] + str(aoid) + ':' + str(self.Classes.MetaMethod.CID) + ':'
        self.Classes.MetaMethod.aIDClassMethod[aoid] = str(self.CID) + '_' + amethoddef.MName
        self.Classes.MetaMethod.aMethodName[aoid] = amethoddef.MName
        self.Classes.MetaMethod.aMethodDescription[aoid] = amethoddef.MDescription
        self.Classes.MetaMethod.aMethodAccess[aoid] = str(amethoddef.MAccess)
        self.Classes.MetaMethod.aLanguage[aoid] = amethoddef.MLanguage
        self.Classes.MetaMethod.aIsParallel[aoid] = str(amethoddef.MIsParallel)
        self.ClearStructInfo()
        aICORDBEngine.icorapi.RepositoryChange(UID, 'MethodAdd', self.CID, -1, amethoddef.MName, '', '')
        return self.MethodsByName(amethoddef.MName, UID=UID)

    def DeleteMethod(self, mname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Methods.has_key(mname):
            del self.Methods[mname]
        aidm = str(self.CID) + '_' + mname
        moid = self.Classes.MetaMethod.aIDClassMethod.Identifiers(aidm, UID=UID)
        if moid >= 0:
            arefs = self.Classes.MetaClass.aMethods.GetRefList(self.CID, UID=UID)
            arefs.DelRef(moid)
            self.Classes.MetaClass.aMethods[self.CID] = arefs.AsString()
            self.ClearStructInfo()
            aICORDBEngine.icorapi.RepositoryChange(UID, 'MethodDelete', self.CID, -1, mname, '', '')
            self.Classes.MetaMethod.DeleteObject(moid, UID=UID)
        return -1

    def CopyMethod(self, aCID, aMName, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        bclass = self.Classes[aCID]
        if bclass is None:
            print 'Klasa zrodlowa nie istnieje!'
            return None
        bmethod = bclass.MethodsByName(aMName, UID=UID)
        if bmethod is None:
            print 'Metoda zrodlowa nie istnieje!'
            return None
        if self.IsMethodInThisClass(aMName, UID=UID):
            ami = self.MethodsByName(aMName, UID=UID)
        else:
            mdi = bmethod.GetMethodDefinition()
            ami = self.AddMethod(mdi, UID=UID)
        ami.MethodText = bmethod.MethodText
        return ami

    def MethodsByName(self, mname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Methods.has_key(mname):
            return self.Methods[mname]
        elif self.IsMethodInClass(mname, UID=UID):
            amethod = ICORDBMethodItem(self.CID, mname)
            self.Methods[mname] = amethod
            return amethod
        return None

    def IsMethodInClass(self, mname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = self._MethodNames.get(mname, None)
        if ret is None:
            ret = 0
            if aICORDBEngine.icorapi.IsMethodInClass(UID, self.CID, mname) > 0:
                ret = 1
            self._MethodNames[mname] = ret
        return ret

    def IsMethodInThisClass(self, mname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.IsMethodInThisClass(UID, self.CID, mname) > 0

    def NewObject(self, arefobject=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        oid = self.AddObject(UID=UID)
        return ICORDBObject(oid, self)

    def AddObject(self, arefobject=None, arangeobject=None, anocreate=0, aoidrangesobj=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if type(arefobject) == type(1):
            arefobject = ICORDBObject(arefobject, self)
        if arefobject:
            if arefobject.CID == self.CID:
                amethod = self.MethodsByName('OnObjectAdd', UID=UID)
                if amethod is not None:
                    soid = amethod.Execute(OID=arefobject.OID, Value='internal', UID=UID)
                    try:
                        aoid = int(soid)
                        if aoid >= 0:
                            if not anocreate:
                                self.CreateObjectByID(aoid, UID=UID)
                            return aoid
                    except:
                        pass
            aoidranges = arefobject.GetOIDRanges()
            if aoidranges:
                for aidmin, aidmax in aoidranges:
                    aoid = self.GetNextFreeObjectID(aidmin, aidmax, UID=UID)
                    if aoid >= 0:
                        if not anocreate:
                            self.CreateObjectByID(aoid, UID=UID)
                        return aoid
                return -1
        if aoidrangesobj:
            while aoidrangesobj:
                aidmin, aidmax = aoidrangesobj['IDMin'], aoidrangesobj['IDMax']
                aoid = self.GetNextFreeObjectID(aidmin, aidmax, UID=UID)
                if aoid >= 0:
                    if not anocreate:
                        self.CreateObjectByID(aoid, UID=UID)
                    return aoid
                aoidrangesobj.Next()
            return -1
        if arangeobject:
            boid = arangeobject.OID
            aclass = aICORDBEngine.User.OIDRange.ClassOfType
            aobj = aclass.GetFirstObject(UID=UID)
            aidmin, aidmax = -1, -1
            while aobj:
                amin, amax = aobj['IDMin'], aobj['IDMax']
                if boid >= amin and boid <= amax:
                    aidmin, aidmax = amin, amax
                    break
                aobj.Next()
            if aidmin >= 0:
                aoid = self.GetNextFreeObjectID(aidmin, aidmax, UID=UID)
                if aoid >= 0:
                    if not anocreate:
                        self.CreateObjectByID(aoid, UID=UID)
                    return aoid
        if not anocreate:
            ret = aICORDBEngine.icorapi.AddObject(UID, self.CID)
        else:
            ret = self.GetNextFreeObjectID(0, 2000000000, UID=UID)
        return ret

    def CreateObjectByID(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aICORDBEngine.icorapi.CreateObjectByID(UID, self.CID, aid)
        return aid

    def GetNextFreeObjectID(self, aidmin, aidmax, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextFreeObjectID(UID, self.CID, aidmin, aidmax)

    def DeleteObject(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if type(aid) == type([]):
            ret = 0
            acid = self.CID
            for bid in aid:
                ret = aICORDBEngine.icorapi.DeleteObject(UID, acid, bid)
            return ret
        return aICORDBEngine.icorapi.DeleteObject(UID, self.CID, aid)

    def ObjectsCount(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetObjectCount(UID, self.CID)

    def ObjectExists(self, aoid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.ObjectExists(UID, self.CID, aoid) >= 0

    def IsObjectDeleted(self, aoid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.IsObjectDeleted(UID, self.CID, aoid) >= 0

    def GetDeletedObjectsList(self, afromdate, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        y, m, d, h, mm, s, ms = afromdate
        s = aICORDBEngine.icorapi.GetDeletedObjectsList(UID, self.CID, y, m, d, h, mm, s, ms)
        alist = string.split(s, ':')
        k = 0
        while k < len(alist):
            if alist[k] != '':
                try:
                    alist[k] = int(alist[k])
                except:
                    pass
            k = k + 1
        return alist[:-1]

    def GetObjectIDByPosition(self, apos, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetObjectIDByPosition(UID, self.CID, apos)

    def GetObjectsInRange(self, aoidfrom, aoidto, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        l = []
        hi = self.ObjectsCount(UID=UID)
        if not hi:
            return l
        lo = 0
        while lo < hi:
            mid = (lo + hi) / 2
            aoid = self.GetObjectIDByPosition(mid, UID=UID)
            if aoid < aoidfrom:
                lo = mid + 1
            else:
                hi = mid
        aoid = self.GetObjectIDByPosition(lo, UID=UID)
        while aoid >= 0 and aoid >= aoidfrom and aoid < aoidto:
            l.append(aoid)
            aoid = self.NextObject(aoid, UID=UID)
        return l

    def GetFirstObject(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if afield is None:
            return ICORDBObject(self.FirstObject(UID=UID), self)
        else:
            if isinstance(afield, types.StringTypes):
                return ICORDBObject(self.FieldsByName(afield, UID=UID).GetFirstValueID(UID=UID), self)
            return ICORDBObject(afield.GetFirstValueID(UID=UID), self)

    def GetLastObject(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if afield is None:
            return ICORDBObject(self.LastObject(UID=UID), self)
        else:
            if isinstance(afield, types.StringTypes):
                return ICORDBObject(self.FieldsByName(afield, UID=UID).GetLastValueID(UID=UID), self)
            return ICORDBObject(afield.GetLastValueID(UID=UID), self)

    def FirstObject(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetFirstObjectID(UID, self.CID)

    def LastObject(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetLastObjectID(UID, self.CID)

    def NextObject(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetNextObjectID(UID, self.CID, aid)

    def PrevObject(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetPrevObjectID(UID, self.CID, aid)

    def GetObjectValue(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetObjectValue(UID, self.CID, aid)

    def SetObjectModified(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.SetObjectModified(UID, self.CID, aid)

    def GetObjectModification(self, aid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.GetObjectModification(UID, self.CID, aid)

    def SetObjectModification(self, aid, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.SetObjectModification(UID, self.CID, aid, avalue)

    def GetObjectValue(self, aid):
        return aICORDBEngine.icorapi.GetObjectValue(GetUID(), self.CID, aid)

    def GetObjectsValue(self, fields=None, autfconvert=1, aslist=0):
        return aICORDBEngine.icorapi.GetObjectsValue(GetUID(), self.CID, fields=fields, autfconvert=autfconvert, aslist=aslist)

    def Identifiers(self, avalue, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.FindValueMulti(UID, self.CID, avalue)

    def ForEachObject(self, afunc, *parms):
        from icorlib.icoriterators import ForEachObjectParms
        ForEachObjectParms(self, afunc, parms)

    def ForEachDerivedClass(self, afunc, *parms):
        from icorlib.icoriterators import ForEachClassParms
        ForEachClassParms(afunc, self, parms)

    def ForEachField(self, afunc, *parms):
        from icorlib.icoriterators import ForEachFieldParms
        ForEachFieldParms(afunc, self, parms)

    def ForEachMethod(self, afunc, *parms):
        from icorlib.icoriterators import ForEachMethodParms
        ForEachMethodParms(afunc, self, parms)

    def GetReferencingFields(self, UID=-1):
        from icorlib.icorsearch import ICORRepositorySearch
        if UID == -1:
            del UID
            UID = GetUID()
        ret = []
        mclass = self.Classes.MetaField
        loids = mclass.Identifiers({'aFieldTypeID': str(self.CID)})
        for aoid in loids:
            bcid = mclass.aFieldOwnerClassID.ValuesAsComp(aoid, UID=UID)
            bname = mclass.aFieldName.ValuesAsComp(aoid, UID=UID)
            bclass = self.Classes[bcid]
            bfield = bclass.FieldsByName(bname, UID=UID)
            ret.append(bfield)
        return ret

    def GetWWWMenuRefs(self):
        return self.Classes.MetaClass.aWWWMenu.GetRefList(self.CID)

    def EditObject(self, aid, acaption='', atoolbar=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return aICORDBEngine.icorapi.EditObject(UID, self.CID, aid, acaption, atoolbar)

    def SelectObjects(self, acaption='', adisabletoolbar=1, adisableediting=1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        from icorlib.icoriterators import FieldRefIterator
        return FieldRefIterator(aICORDBEngine.icorapi.SelectObjects(UID, self.CID, acaption, adisabletoolbar, adisableediting))

    def SelectObjectsFromDictionary(self, arefs=None, acaption='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if arefs:
            if isinstance(arefs, types.StringTypes):
                s = arefs
            else:
                s = arefs.AsString()
        else:
            s = ''
        from icorlib.icoriterators import FieldRefIterator
        return FieldRefIterator(aICORDBEngine.icorapi.SelectObjectsFromDictionary(UID, self.CID, s, acaption))

    def SelectSummaries(self):
        return aICORDBEngine.icorapi.SelectSummaries(GetUID(), self.CID)

    def SelectSearchInClass(self):
        return aICORDBEngine.icorapi.SelectSearchInClass(GetUID(), self.CID)

    def SelectClassFieldProperties(self):
        return aICORDBEngine.icorapi.SelectClassFieldProperties(GetUID(), self.CID)

    def SelectInRepository(self):
        aICORDBEngine.icorapi.RepositoryChange(GetUID(), 'ClassSelect', -1, -1, self.ClassPath, '', '')

    def SelectInStructure(self):
        aICORDBEngine.icorapi.RepositoryChange(GetUID(), 'ClassSelectInStructure', self.CID, -1, '', '', '')


class ICORDBClasses:

    def __init__(self):
        self.classes = {}
        self._GetClassIDs = {}
        self._MetaClass = None
        self._MetaField = None
        self._MetaMethod = None
        self._ClassQueuedParameters = None

    def __getattr__(self, name):
        if name == 'MetaClass':
            if self._MetaClass is None:
                self._MetaClass = self.GetClassByName('CLASSES/System/ICORClass')
            return self._MetaClass
        if name == 'MetaField':
            if self._MetaField is None:
                self._MetaField = self.GetClassByName('CLASSES/System/ICORField')
            return self._MetaField
        if name == 'MetaMethod':
            if self._MetaMethod is None:
                self._MetaMethod = self.GetClassByName('CLASSES/System/ICORMethod')
            return self._MetaMethod
        if name == 'ClassQueuedParameters':
            if self._ClassQueuedParameters is None:
                self._ClassQueuedParameters = self.GetClassByName(QUEUED_PARAMETERS_CLASS_LOCATION)
            return self._ClassQueuedParameters
        return getattr(__builtins__, name)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getitem__(self, key):
        if type(key) == types.InstanceType:
            return key
        if isinstance(key, types.StringTypes):
            aid = self.GetClassByName(key)
        else:
            aid = self.GetClassByID(key)
        return aid

    def AddClass(self, abasecid, aname, acid=-1, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aclass = self.GetClassByID(acid, UID=UID)
        if aclass is not None:
            print 'Klasa juz istnieje:', acid
            return aclass    # klasa juz istnieje
        if not IsIdentifier(aname):
            print 'Zla nazwa klasy:', aname
            return None    # niepoprawna nazwa klasy
        abaseclass = self.GetClassByID(abasecid, UID=UID)
        w = 1
        s = aname.lower()
        clist = abaseclass.GetInheritedClassesList(UID=UID)
        for icid in clist:
            dclass = self.GetClassByID(icid, UID=UID)
            if dclass is not None:
                s1 = dclass.NameOfClass.lower()
                if s1 == s:
                    w = 0
                    break
        if not w:
            print 'Klasa pochodna o takiej nazwie juz istnieje:', aname
            return None
        if abaseclass.AllowWrite == '0':
            print 'Brak dostepu do klasy bazowej:', abasecid
            return None
        if acid >= 0:
            self.MetaClass.CreateObjectByID(acid, UID=UID)
            aoid = acid
        else:
            aoid = self.MetaClass.AddObject(UID=UID)
        self.MetaClass.aClassName[aoid] = aname
        self.MetaClass.aClassDescription[aoid] = aname
        self.MetaClass.aBasePath[aoid] = abaseclass.ClassPath
        self.MetaClass.aCID[aoid] = str(aoid)
        self.MetaClass.aBaseCID[aoid] = str(abaseclass.CID)
        self.MetaClass.aClassColIDWidth[aoid] = '60'
        self.MetaClass.aClassFormLeft[aoid] = '-1'
        self.MetaClass.aClassFormTop[aoid] = '-1'
        self.MetaClass.aClassFormWidth[aoid] = '-1'
        self.MetaClass.aClassFormHeight[aoid] = '-1'
        self.MetaClass.aReportClass[aoid] = abaseclass.ReportClass
        self.MetaClass.aIsSystem[aoid] = abaseclass.IsSystem
        self.MetaClass.aIsVirtual[aoid] = '0'
        self.MetaClass.aDerivedClasses[abaseclass.CID] = self.MetaClass.aDerivedClasses[abaseclass.CID] + str(aoid) + ':' + str(self.MetaClass.CID) + ':'
        aclass = self.GetClassByID(aoid, UID=UID)
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassAdd', aoid, -1, '', '', '')
        if aclass is None:
            print 'Blad podczas tworzenia klasy:', aoid, 'pochodnej od klasy:', abasecid
            return None    # jakis blad podczas pobierania juz utworzonej klasy

        def cffunc(bclass, afield, aclass):
            aclass.CopyField(bclass.CID, afield.Name, 0, -1, '', int(afield.FieldOwnerClassID))

        abaseclass.ForEachField(cffunc, aclass)
        if abaseclass.IsMethodInClass('OnClassCreateEvent', UID=UID):
            abaseclass.OnClassCreateEvent.Execute('', -1, aoid, UID=UID)
        return aclass

    def MoveClass(self, basecid, acid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassDelete', acid, -1, '', '', '')
        aclass = self.GetClassByID(acid, UID=UID)
        blist = []
        iclass = aclass.Inherited
        while iclass is not None:
            blist.append(iclass.CID)
            iclass = iclass.Inherited
        try:
            bcid = int(aclass.BaseCID)
        except:
            bcid = -1
        self.UnlinkClassFromBaseClass(bcid, acid, UID=UID)
        self.MetaClass.aDerivedClasses[basecid] = self.MetaClass.aDerivedClasses[basecid] + str(acid) + ':' + str(self.MetaClass.CID) + ':'
        self.MetaClass.aBaseCID[acid] = str(basecid)
        abaseclass = self.GetClassByID(basecid, UID=UID)
        self.MetaClass.aBasePath[acid] = abaseclass.ClassPath
        auid = UID    # prevents syntax error: can not delete variable UID referenced in nested scope

        def bfunc(aclass, blist, acid):
            aICORDBEngine.Classes.MetaClass.aBasePath[aclass.CID] = aclass.Inherited.ClassPath

            def ffunc(aclass, afield, blist, acid):
                sfid = str(aclass.CID) + '_' + afield.Name
                foid = aICORDBEngine.Classes.MetaField.aIDClassField.Identifiers(sfid, UID=auid)
                if foid >= 0:
                    try:
                        fowner = int(aICORDBEngine.Classes.MetaField.aFieldOwnerClassID[foid])
                        if fowner in blist:
                            aICORDBEngine.Classes.MetaField.aFieldOwnerClassID[foid] = str(acid)
                    except:
                        pass

            aclass.ForEachField(ffunc, blist, acid)

        bfunc(aclass, blist, acid)
        aclass.ForEachDerivedClass(bfunc, blist, acid)
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassRefreshProperties', basecid, -1, '', '', '')
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassRefreshProperties', acid, -1, '', '', '')
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassAdd', acid, -1, '', '', '')

    def DeleteClass(self, acid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.classes.has_key(acid):
            del self.classes[acid]
        aclass = self.GetClassByID(acid, UID=UID)
        try:
            abasecid = int(aclass.BaseCID)
        except:
            abasecid = -1
        self.UnlinkClassFromBaseClass(abasecid, acid, UID=UID)
        aICORDBEngine.icorapi.RepositoryChange(UID, 'ClassDelete', acid, -1, '', '', '')
        self.MetaClass.DeleteObject(acid, UID=UID)
        return

    def UnlinkClassFromBaseClass(self, abasecid, acid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        abaseclass = self.GetClassByID(abasecid, UID=UID)
        if abaseclass is not None:
            arefs = self.MetaClass.aDerivedClasses.GetRefList(abaseclass.CID, UID=UID)
            arefs.DelRef(acid)
            self.MetaClass.aDerivedClasses[abaseclass.CID] = arefs.AsString()

    def GetClassID(self, aclasspath, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = self._GetClassIDs.get(aclasspath, None)
        if ret is None:
            ret = aICORDBEngine.icorapi.GetClassID(UID, aclasspath)
            self._GetClassIDs[aclasspath] = ret
        return ret

    def ClassExists(self, acid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if isinstance(acid, types.StringTypes):
            return self.GetClassID(acid) > MAX_ICOR_SYSTEM_TYPE
        return aICORDBEngine.icorapi.ClassExists(UID, acid) > 0

    def GetClassByID(self, cid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if cid <= MAX_ICOR_SYSTEM_TYPE:
            return None
        if self.classes.has_key(cid):
            aclass = self.classes[cid]
        else:
            if self.ClassExists(cid, UID=UID):
                aclass = ICORDBClassItem(cid)
                aclass.Classes = self
                self.classes[cid] = aclass
            else:
                return None
        return aclass

    def GetFieldByFID(self, afid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        fclass = self.GetClassByName('CLASSES_System_ICORField')
        aidclass = fclass.FieldsByName('aIDClassField', UID=UID)[afid]
        l = aidclass.split('_')
        bclass = self.GetClassByID(int(l[0]), UID=UID)
        afield = bclass.FieldsByName(l[1], UID=UID)
        return afield

    def GetTypeByTypeID(self, tid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if tid > MAX_ICOR_SYSTEM_TYPE:
            aci = self.GetClassByID(tid, UID=UID)
            if aci is None:
                return ''
            else:
                return aci.ClassPath
        if tid == mt_String:
            return 'String'
        elif tid == mt_Integer:
            return 'Integer'
        elif tid == mt_Boolean:
            return 'Bool'
        elif tid == mt_DateTime:
            return 'DateTime'
        elif tid == mt_Double:
            return 'Double'
        return ''

    def GetTypeIDByType(self, atype, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        atypes = {'String': mt_String, 'Integer': mt_Integer, 'Bool': mt_Boolean, 'Boolean': mt_Boolean, 'Double': mt_Double, 'Date': mt_DateTime, 'Time': mt_DateTime, 'DateTime': mt_DateTime}
        if atypes.has_key(atype):
            return atypes[atype]
        aci = self.GetClassByName(atype, UID=UID)
        if aci is not None:
            return aci.CID
        return -1

    def GetClassByName(self, aname, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        aid = self.GetClassID(aname, UID=UID)
        return self.GetClassByID(aid, UID=UID)

    def FirstClass(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        acid = self.MetaClass.FirstObject(UID=UID)
        return self.GetClassByID(acid, UID=UID)

    def NextClass(self, acid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if acid is None:
            return None
        if type(acid) == types.InstanceType:
            acid = acid.CID
        acid = self.MetaClass.NextObject(acid, UID=UID)
        return self.GetClassByID(acid, UID=UID)

    def ForEachClass(self, afunc, aclass=None, *parms):
        from icorlib.icoriterators import ForEachClassParms
        ForEachClassParms(afunc, aclass, parms)


class ICORDBObject:

    def __init__(self, OID, aci, arefs=None, asortfield=None, adescending=0):
        self.__dict__['OID'] = OID
        self.SetObjectClass(aci)
        if isinstance(arefs, types.StringTypes):
            from icorlib.icoriterators import FieldRefIterator
            brefs = FieldRefIterator(arefs)
            if asortfield is not None:
                brefs.sort(asortfield)
                if adescending:
                    brefs.reverse()
            self.__dict__['Refs'] = brefs
        else:
            self.__dict__['Refs'] = arefs

    def SetObjectClass(self, aclass):
        self.__dict__['Class'] = aICORDBEngine.Classes[aclass]
        if self.__dict__['Class'] is not None:
            self.__dict__['CID'] = self.Class.CID
        else:
            self.__dict__['CID'] = -1

    def __setattr__(self, name, value):
        if not self.SetFieldValue(name, value):
            self.__dict__[name] = value

    def __getitem__(self, name):
        if type(name) == type(()):
            return apply(self.GetFieldValue, name)
        return self.GetFieldValue(name, mt_Any)

    def __setitem__(self, name, value):
        self.SetFieldValue(name, value)

    def __len__(self):
        if self.Refs is None:
            return self.Class.ObjectsCount()
        else:
            return self.Refs.len

    def __nonzero__(self):
        return self.OID >= 0

    def __repr__(self):
        return '[%d,%d]' % (self.OID, self.CID)

    def __str__(self):
        sl = self.AsColumnValues()
        return string.join(sl, ', ')

    def Exists(self, UID=-1):
        if self.OID < 0:
            return 0
        if UID == -1:
            del UID
            UID = GetUID()
        return self.Class.ObjectExists(self.OID, UID=UID)

    def GetObjectValue(self):
        if self.OID < 0:
            return {}
        return self.Class.GetObjectValue(self.OID)

    def GetFieldValue(self, name, atype=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        afield = self.Class.FieldsByName(name, UID=UID)
        if afield is None:
            return None
        if afield.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.OID < 0:
                return None
            else:
                if atype is None or atype in [mt_String, mt_Memo]:
                    return afield[self.OID]
                elif atype in [mt_Integer, mt_Boolean]:
                    return afield.ValuesAsInt(self.OID, UID=UID)
                elif atype in [mt_Double]:
                    return afield.ValuesAsFloat(self.OID, UID=UID)
                elif atype == mt_DateTime:
                    return afield.ValuesAsDateTime(self.OID, UID=UID)
                else:
                    return afield.ValuesAsComp(self.OID, UID=UID)
        else:
            if self.OID < 0:
                aobj = ICORDBObject(-1, afield.ClassOfType)
            else:
                arefs = afield.GetRefList(self.OID, UID=UID)
                aobj = arefs.AsObject()
                aobj.SetObjectClass(afield.ClassOfType)
            return aobj

    __getattr__ = GetFieldValue

    def SetFieldValue(self, name, value, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Class is None:
            return 0
        afield = self.Class.FieldsByName(name, UID=UID)
        if afield is not None:
            afield[self.OID] = value
            return 1
        return 0

    def UpdateParms(self):
        if self.Refs.position < 0:
            self.__dict__['OID'] = -1
            return
        if self.Refs.CID != self.CID:
            self.__dict__['CID'] = self.Refs.CID
            self.__dict__['Class'] = self.Refs.Class
        self.__dict__['OID'] = self.Refs.OID

    def First(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            if afield is None:
                self.__dict__['OID'] = self.Class.FirstObject(UID=UID)
            else:
                if isinstance(afield, types.StringTypes):
                    self.__dict__['OID'] = self.Class.FieldsByName(afield, UID=UID).GetFirstValueID(UID=UID)
                else:
                    self.__dict__['OID'] = afield.GetFirstValueID(UID=UID)
        else:
            self.Refs.First()
            self.UpdateParms()

    def Last(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            if afield is None:
                self.__dict__['OID'] = self.Class.LastObject(UID=UID)
            else:
                if isinstance(afield, types.StringTypes):
                    self.__dict__['OID'] = self.Class.FieldsByName(afield, UID=UID).GetLastValueID(UID=UID)
                else:
                    self.__dict__['OID'] = afield.GetLastValueID(UID=UID)
        else:
            self.Refs.Last()
            self.UpdateParms()

    def Next(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            if afield is None:
                self.__dict__['OID'] = self.Class.NextObject(self.OID, UID=UID)
            else:
                if isinstance(afield, types.StringTypes):
                    self.__dict__['OID'] = self.Class.FieldsByName(afield, UID=UID).GetNextValueID(self.OID, UID=UID)
                else:
                    self.__dict__['OID'] = afield.GetNextValueID(self.OID, UID=UID)
        else:
            self.Refs.Next()
            self.UpdateParms()

    def Prev(self, afield=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            if afield is None:
                self.__dict__['OID'] = self.Class.PrevObject(self.OID, UID=UID)
            else:
                if isinstance(afield, types.StringTypes):
                    self.__dict__['OID'] = self.Class.FieldsByName(afield, UID=UID).GetPrevValueID(self.OID, UID=UID)
                else:
                    self.__dict__['OID'] = afield.GetPrevValueID(self.OID, UID=UID)
        else:
            self.Refs.Prev()
            self.UpdateParms()

    def SetByPosition(self, apos, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            self.__dict__['OID'] = self.Class.GetObjectIDByPosition(apos, UID=UID)
        else:
            self.Refs.SetByPosition(apos)
            self.UpdateParms()

    def SetByOID(self, aoid, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.Refs is None:
            if self.Class.ObjectExists(aoid, UID=UID):
                self.__dict__['OID'] = aoid
            else:
                self.__dict__['OID'] = -1
        else:
            apos, afind = self.Refs.FindRef(aoid, self.CID)
            self.Refs.SetByPosition(apos)
            self.UpdateParms()

    def GetOIDRanges(self, adict=None, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        ret = []
        if adict is None:
            adict = {}
        if adict.has_key((self.CID, self.OID)):
            return ret
        adict[(self.CID, self.OID)] = 1
        aoidrangeobj = self.GetFieldValue('OIDRange', UID=UID)
        while aoidrangeobj:
            ret.append([aoidrangeobj['IDMin'], aoidrangeobj['IDMax']])
            aoidrangeobj.Next()
        if ret:
            del adict[(self.CID, self.OID)]
            return ret
        bfields = self.Class.BackRefFields
        for bfield in bfields:
            bobj = self.GetFieldValue(bfield.Name, UID=UID)
            if bobj:
                ret = bobj.GetOIDRanges(adict=adict, UID=UID)
                if ret:
                    del adict[(self.CID, self.OID)]
                    return ret
        del adict[(self.CID, self.OID)]
        return ret

    def NewObject(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.Class.AddObject(arefobject=self, UID=UID)

    def AddObject(self, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.Class.AddObject(arefobject=self, UID=UID)

    def DeleteObject(self, UID=-1, anorefs=0):
        if UID == -1:
            del UID
            UID = GetUID()
        if (self.Refs is None) or anorefs:
            poid, pcid, = self.OID, self.CID
            aclass = self.Class
            bfield = None
            roid, rcid = -1, -1
            flist = aclass.GetFieldsList(UID=UID)
            for afname in flist:
                afield = aclass.FieldsByName(afname, UID=UID)
                if afield.WWWBackRefField:
                    gclass = afield.ClassOfType
                    glist = gclass.GetFieldsList(UID=UID)
                    for gfname in glist:
                        gfield = gclass.FieldsByName(gfname, UID=UID)
                        rclass = gfield.ClassOfType
                        if rclass is not None and rclass.CID == aclass.CID:
                            prefs = afield.GetRefList(poid, UID=UID)
                            while prefs:
                                gfield.DeleteRefs(prefs.OID, [poid, pcid], UID=UID)
                                if prefs.OID >= 0:
                                    roid, rcid = prefs.OID, prefs.CID
                                prefs.Next()
            aclass.DeleteObject(poid, UID=UID)
            self.__dict__['OID'] = -1
            return roid, rcid
        else:
            return -1, -1

    def AsObject(self):
        if self.Refs is None:
            return ICORDBObject(self.OID, self.Class)
        else:
            return ICORDBObject(self.OID, self.Class, self.Refs.AsString())

    def AsString(self):
        if self.Refs is None:
            return str(self.OID) + ':' + str(self.CID) + ':'
        else:
            return self.Refs.AsString()

    def AsRefs(self):
        return self.Refs.AsRefs()

    def AsRefString(self):
        return str(self.OID) + ':' + str(self.CID) + ':'

    def AssignFrom(self, bobj, asimple=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if asimple:
            afields = self.Class.GetFieldsList(UID=UID)
            for afname in afields:
                bfield = bobj.Class.FieldsByName(afname, UID=UID)
                if bfield is not None:
                    afield = self.Class.FieldsByName(afname, UID=UID)
                    afield[self.OID] = bfield[bobj.OID]
        return

    def CopyFieldValue(self, afield1, aOID, aCID=-1, afield2='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if aOID == self.OID:
            return
        if afield2 == '':
            afield2 = afield1
        if aCID == -1:
            aCID = self.CID
        asrcclass = aICORDBEngine.Classes[aCID]
        self.Class.FieldsByName(afield1, UID=UID)[self.OID] = asrcclass.FieldsByName(afield2, UID=UID)[aOID]

    def Duplicate(self, aOID, aCID, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if self.CID != aCID:
            return
        asrcclass = aICORDBEngine.Classes[aCID]
        afields = asrcclass.GetFieldsList(UID=UID)
        for afield in afields:
            self.DuplicateFieldValue(afield, aOID, aCID, UID=UID)
        return

    def DuplicateFieldValue(self, afield1, aOID, aCID=-1, afield2='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if aOID == self.OID:
            return
        if afield2 == '':
            afield2 = afield1
        if aCID == -1:
            aCID = self.CID
        asrcclass = aICORDBEngine.Classes[aCID]
        asrcfield = asrcclass.FieldsByName(afield2, UID=UID)
        at1 = asrcfield.FieldTID
        if at1 > MAX_ICOR_SYSTEM_TYPE:
            arefs = asrcfield.GetRefList(aOID, UID=UID)
            s = ''
            while arefs.position >= 0:
                atmpclass = aICORDBEngine.Classes[arefs.CID]
                atmpoid = atmpclass.AddObject(UID=UID)
                atmpobject = ICORDBObject(atmpoid, arefs.CID)
                atmpobject.Duplicate(arefs.OID, arefs.CID, UID=UID)
                s = s + str(atmpoid) + ':' + str(arefs.CID) + ':'
                arefs.Next()
            self.Class.FieldsByName(afield1, UID=UID)[self.OID] = s
        else:
            self.Class.FieldsByName(afield1, UID=UID)[self.OID] = asrcfield[aOID]

    def AsColumnValues(self, amaxcol=3, arecurclasses=None, aretvaluesbytype=None, anowwwtreerecur=1, aappendemptyvalues=0, UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        if arecurclasses is None:
            arecurclasses = []
        elif self.CID in arecurclasses:
            return []
        if amaxcol <= 0:
            amaxcol = 3
        arecurclasses.append(self.CID)
        res = []
        for afield in self.Class.FieldsAsColumns:
            if anowwwtreerecur and afield.WWWTreeRecur:
                pass
            elif afield.ClassOfType is None:
                s = afield[self.OID]
                if s or aappendemptyvalues:
                    res.append(s)
                    if aretvaluesbytype is not None:
                        aretvaluesbytype.append(afield.ValuesAsComp(self.OID, UID=UID))
            else:
                bobj = afield.GetRefList(self.OID, UID=UID).AsObject()
                if bobj:
                    blist = bobj.AsColumnValues(amaxcol, arecurclasses, aretvaluesbytype=aretvaluesbytype, UID=UID)
                    if blist:
                        res.extend(blist)
            if len(res) >= amaxcol:
                break
        arecurclasses.pop()
        return res


class ICORDBEngine:

    def __init__(self):
        self.InitConnection()
        self.Refresh()
        self.InitParams()

    def InitConnection(self):
        try:
            import ICORDelphi
            self.icorapi = ICORDelphi
            self.ICOR_EXECUTE_EXTERNAL = 0
        except:
            import icorapi
            self.icorapi = icorapi
            self.ICOR_EXECUTE_EXTERNAL = 1

    def InitParams(self):
        self.StorageManager = icorstorage.MManager()
        self.SysBase = self.StorageManager.GetSysBase()

    def Refresh(self, asystem=0):
        self.Classes = ICORDBClasses()
        self.Classes.ICORDBEngine = self
        self.Variables = ICORVariables(self)
        self.UserVars = ICORUserVars()
        self.SessionVars = {}
        self._SystemID = ''
        self._SystemOwnerUserID = -1
        self._SystemProfileOID = -1
        self._ProfileGroupRefs = None

        self._ACCESS_LEVEL_FOR_USER_RECURSIVE_CACHE = {}
        self._ACCESS_LEVEL_FOR_USER_CACHE = {}
        self._ACCESS_LEVEL_GROUPS_CACHE = {}
        self._ITEMS_GROUP2USERS_CACHE = {}
        self._USER_GROUPS_LEVELS_CACHE = {}
        self._USER_PROFILES_CACHE = {}
        if asystem:
            import icorlib.wwwserver.icorwwwinterface as ICORWWWInterface
            ICORWWWInterface.aICORWWWServerInterface.Refresh('Default')

    def SystemID(self, astr=''):
        if self._SystemID == '':
            self._SystemID = self.icorapi.GetSystemID('')
        if astr == '':
            return self._SystemID
        return self.icorapi.GetSystemID(astr)

    def HashString(self, astr):
        return hashlib.md5(astr).hexdigest().upper()

    def HashFile(self, afilepath):    #returns '' if error
        ret = ''
        amd5 = hashlib.md5()
        try:
            fin = open(afilepath, 'rb')
            try:
                while 1:
                    adata = fin.read(65536)
                    if not adata:
                        break
                    amd5.update(adata)
            finally:
                fin.close()
            ret = amd5.hexdigest().upper()
        except:
            ret = ''
        return ret

    def RepositoryChange(self, akind, aid=-1, aid2=-1, asubitem='', avalue1='', avalue2='', UID=-1):
        if UID == -1:
            del UID
            UID = GetUID()
        return self.icorapi.RepositoryChange(UID, akind, aid, aid2, asubitem, avalue1, avalue2)

    def __getattr__(self, name):
        if name == 'SystemOwnerUserID':
            if self._SystemOwnerUserID == -1:
                try:
                    aclass = self.Classes[STARTUP_CLASS_LOCATION]
                    aoid = aclass.FirstObject()
                    arefs = aclass.SystemOwnerUser.GetRefList(aoid)
                    aoid = arefs.OID
                except:
                    aoid = -2
                self._SystemOwnerUserID = aoid
            return self._SystemOwnerUserID
        if name == 'IsAdministrator':
            return self.SystemOwnerUserID == 0
        if name == 'User':
            return self.Classes[USER_CLASS_LOCATION]
        if name == 'UserProfile':
            return self.Classes[USER_PROFILE_CLASS_LOCATION]
        if name == 'SystemProfileOID':
            if self._SystemProfileOID == -1:
                arefs = self.User.Profile.GetRefList(self.SystemOwnerUserID)
                self._SystemProfileOID = arefs.OID
            return self._SystemProfileOID
        if name == 'SystemBaseClasses':
            aclass = self.Classes[STARTUP_CLASS_LOCATION]
            aoid = aclass.FirstObject()
            afield = aclass.FieldsByName('Classes')
            arefs = afield.GetRefList(aoid)
            l = []
            while arefs.position >= 0:
                l.append(arefs.OID)
                arefs.Next()
            return l
        if name == 'ProfileGroupRefs':
            if self._ProfileGroupRefs is None:
                aclass = self.Classes[STARTUP_CLASS_LOCATION]
                aoid = aclass.FirstObject()
                self._ProfileGroupRefs = aclass.ProfileGroup.GetRefList(aoid)
            self._ProfileGroupRefs.First()
            return self._ProfileGroupRefs
        return getattr(__builtins__, name)


aICORDBEngine = ICORDBEngine()
