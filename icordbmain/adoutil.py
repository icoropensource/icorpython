import sys
import time
import re
import decimal
import traceback

import pywintypes

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.icorsecurity as ICORSecurity

import icorexceptions
import dbaccess

VERBOSE = 0

#   adolib,adoconst,amajor,aminor=ADOInitialize()
#   db = adolib.Connection()
#   rs = adolib.Recordset()

adoconst = None


def ADOInitialize(amode=''):
    global adoconst
    import win32com.client.gencache
    import win32con
    ado_list=[
       ['ADO2.8','{2A75196C-D9EB-4129-B803-931327F72D5C}',2,8],# ADO 2.8 - came with MDAC
       #['ADO2.7','{EF53050B-882E-4776-B643-EDA472E8E3F2}',2,7],# ADO 2.7 - came with Windows XP
       #['ADO2.6','{00000206-0000-0010-8000-00AA006D2EA4}',2,6],# ADO 2.6 - came with SQL Server 2000
       #['ADO2.5','{00000205-0000-0010-8000-00AA006D2EA4}',2,5],# ADO 2.5 - came with Windows 2000
       #['ADO2.1','{00000201-0000-0010-8000-00AA006D2EA4}',2,1],# ADO 2.1 - earliest version still around
       #['ADO2.0','{00000200-0000-0010-8000-00AA006D2EA4}',2,0],# ADO 2.0 - no longer available
    ] # yapf: disable
    adolib, adoconst, amajor, aminor = None, None, -1, -1
    for aname, auuid, amajor, aminor in ado_list:
        try:
            #         print aname,auuid,amajor,aminor
            adolib = win32com.client.gencache.EnsureModule(auuid, win32con.LANG_NEUTRAL, amajor, aminor, None)    # UUID, LCID, Major version, Minor version, Silent progress or win32com.client.genpy.GeneratorProgress()
            #         print adolib
            adoconst = adolib.constants
            break
        except AttributeError:
            pass
        except:
            import traceback
            traceback.print_exc()
            pass
#         raise
    return adolib, adoconst, amajor, aminor


#adolib,adoconst,amajor,aminor=ADORInitialize()
def ADORInitialize():
    global adoconst
    import win32com.client.gencache
    import win32con
    adolib, adoconst, amajor, aminor = ADOInitialize()
    auuid = '{00000300-0000-0010-8000-00AA006D2EA4}'    # ADOR - all - subset od ADO + constants
    adolib = win32com.client.gencache.EnsureModule(auuid, win32con.LANG_NEUTRAL, amajor, aminor, None)    # UUID, LCID, Major version, Minor version, Silent progress or win32com.client.genpy.GeneratorProgress()
    adoconst = adolib.constants
    return adolib, adoconst, amajor, aminor


#adolib,adoconst,amajor,aminor=ADOXInitialize()
def ADOXInitialize():
    global adoconst
    import win32com.client.gencache
    import win32con
    adolib, adoconst, amajor, aminor = ADOInitialize()
    auuid = '{00000600-0000-0010-8000-00AA006D2EA4}'    # ADOX - all - ADO Extensions
    adolib = win32com.client.gencache.EnsureModule(auuid, win32con.LANG_NEUTRAL, amajor, aminor, None)    # UUID, LCID, Major version, Minor version, Silent progress or win32com.client.genpy.GeneratorProgress()
    adoconst = adolib.constants
    return adolib, adoconst, amajor, aminor


class ADOColTypes:
    adBSTR = 0x8    # from enum DataTypeEnum
    adBigInt = 0x14    # from enum DataTypeEnum
    adBinary = 0x80    # from enum DataTypeEnum
    adBoolean = 0xb    # from enum DataTypeEnum
    adChapter = 0x88    # from enum DataTypeEnum
    adChar = 0x81    # from enum DataTypeEnum
    adCurrency = 0x6    # from enum DataTypeEnum
    adDBDate = 0x85    # from enum DataTypeEnum
    adDBTime = 0x86    # from enum DataTypeEnum
    adDBTimeStamp = 0x87    # from enum DataTypeEnum
    adDate = 0x7    # from enum DataTypeEnum
    adDecimal = 0xe    # from enum DataTypeEnum
    adDouble = 0x5    # from enum DataTypeEnum
    adEmpty = 0x0    # from enum DataTypeEnum
    adError = 0xa    # from enum DataTypeEnum
    adFileTime = 0x40    # from enum DataTypeEnum
    adGUID = 0x48    # from enum DataTypeEnum
    adIDispatch = 0x9    # from enum DataTypeEnum
    adIUnknown = 0xd    # from enum DataTypeEnum
    adInteger = 0x3    # from enum DataTypeEnum
    adLongVarBinary = 0xcd    # from enum DataTypeEnum
    adLongVarChar = 0xc9    # from enum DataTypeEnum
    adLongVarWChar = 0xcb    # from enum DataTypeEnum
    adNumeric = 0x83    # from enum DataTypeEnum
    adPropVariant = 0x8a    # from enum DataTypeEnum
    adSingle = 0x4    # from enum DataTypeEnum
    adSmallInt = 0x2    # from enum DataTypeEnum
    adTinyInt = 0x10    # from enum DataTypeEnum
    adUnsignedBigInt = 0x15    # from enum DataTypeEnum
    adUnsignedInt = 0x13    # from enum DataTypeEnum
    adUnsignedSmallInt = 0x12    # from enum DataTypeEnum
    adUnsignedTinyInt = 0x11    # from enum DataTypeEnum
    adUserDefined = 0x84    # from enum DataTypeEnum
    adVarBinary = 0xcc    # from enum DataTypeEnum
    adVarChar = 0xc8    # from enum DataTypeEnum
    adVarNumeric = 0x8b    # from enum DataTypeEnum
    adVarWChar = 0xca    # from enum DataTypeEnum
    adVariant = 0xc    # from enum DataTypeEnum
    adWChar = 0x82    # from enum DataTypeEnum


def handle_com_error(error_info, aprint=1):
    return []
    exception_string = ''
    try:
        hresult_code, hresult_name, additional_info, parameter_in_error = error_info
        exception_string = ["%s - %s" % (hex(hresult_code), hresult_name)]
        if additional_info:
            wcode, source_of_error, error_description, whlp_file, whlp_context, scode = additional_info
            exception_string.append("  Error in: %s" % source_of_error)
            exception_string.append("  %s - %s" % (hex(scode), error_description.strip()))
        if aprint:
            for s in exception_string:
                print s
    except:
        import traceback
        traceback.print_exc()
    #raise x_wmi, "\n".join (exception_string)
    return exception_string


def GetRSNameAsStr(ars, afield):
    v = ars.Fields.Item(afield).Name
    if type(v) != type(''):
        try:
            v = v.encode('cp1250')
        except:
            v = str(v).encode('cp1250')
    ret = v.strip()
    return ret


def GetRSValueAsStr(ars, afield, adatedelimiter='-', astype=0, acontext=None, asutf=0, asdecimal=0):
    global adoconst
    t = ars.Fields.Item(afield).Type
    v = ars.Fields.Item(afield).Value
    if v is None:
        return ''
    if acontext:
        badoconst = acontext.adoconst
    else:
        badoconst = adoconst
    ret = ''
    if 0:
        print 'name  :', ars.Fields.Item(afield).Name
        print 'type  :', ars.Fields.Item(afield).Type
        print 'dsize :', ars.Fields.Item(afield).DefinedSize
        print 'asize :', ars.Fields.Item(afield).ActualSize
        print 'prec  :', ars.Fields.Item(afield).Precision
        print 'nscale:', ars.Fields.Item(afield).NumericScale
        print 'attrs :', ars.Fields.Item(afield).Attributes
    if t in [badoconst.adDate, badoconst.adDBDate, badoconst.adDBTime, badoconst.adDBTimeStamp]:    #adDate,adDBDate,adDBTime,adDBTimeStamp
        try:
            ret = ICORUtil.tdatetime(int(v))
            if astype:
                return ret
            ret = ICORUtil.tdatetime2fmtstr(ret, adelimiter=adatedelimiter, longfmt=1)
        except:
            #traceback.print_exc()
            ret = ''
    elif t in [badoconst.adTinyInt, badoconst.adSmallInt, badoconst.adInteger, badoconst.adUnsignedTinyInt, badoconst.adUnsignedSmallInt, badoconst.adUnsignedInt]:
        try:
            ret = int(v)
            if astype:
                return ret
            ret = str(ret)
        except:
            ret = ''
    elif t in [badoconst.adBigInt, badoconst.adUnsignedBigInt]:
        try:
            ret = long(v)
            if astype:
                return ret
            ret = str(ret)
        except:
            ret = ''
    elif t in [badoconst.adSingle, badoconst.adDouble, badoconst.adDecimal, badoconst.adNumeric]:
        try:
            if asdecimal:
                ret = decimal.Decimal(v)
                if astype:
                    return ret
                ret = str(ret)
            else:
                ret = float(v)
                if astype:
                    return ret
                ret = '%0.2f' % (ret, )
        except:
            ret = ''
    elif t in [badoconst.adBoolean, ]:
        try:
            ret = int(v)
            if astype:
                return ret
            if v:
                ret = '1'
            else:
                ret = '0'
        except:
            ret = ''
    elif t in [badoconst.adCurrency]:
        try:
            hi, lo = v
            TWO32 = 2L**32
            if lo < 0:
                lo += TWO32
            if hi == -1 or hi == 0:
                adecimal = 2
                ret = round((float((long(hi) << 32) + lo)) / 10000.0, adecimal)
                if astype:
                    return ret
                return '%0.2f' % (ret, )    #'%d'%(ret,)
            else:
                ret = ((long(hi) << 32) + lo) / 10000
                if astype:
                    return ret
                ret = '%0.2f' % (ret, )
        except:
            raise
            ret = ''
    elif t == badoconst.adLongVarChar:
        asize = ars.Fields.Item(afield).ActualSize
        ret = ''
        if asize > 0:
            v = ars.Fields.Item(afield).GetChunk(asize)
            if type(v) != type(''):
                try:
                    v = v.encode('cp1250')    #XMLUtil.GetAsXMLStringNoPL
                except:
                    v = str(v).encode('cp1250')
            ret = v.strip()
            if asutf:
                ret = storageutil.CP1250_To_UTF8(ret)
    elif t == badoconst.adBinary or t == badoconst.adVarBinary or t == badoconst.adLongVarBinary:
        asize = ars.Fields.Item(afield).ActualSize
        ret = ''
        if asize > 0:
            if ars.Fields.Item(afield).Attributes & adoconst.adFldLong > 0:
                ret = ars.Fields.Item(afield).GetChunk(asize)
            elif 0:
                if type(v) != type(''):
                    try:
                        v = v.encode('cp1250')
                    except:
                        v = str(v).encode('cp1250')
                ret = v.strip()
            else:
                ret = ''
            if asutf:
                ret = storageutil.CP1250_To_UTF8(ret)
    elif t not in [badoconst.adChapter, ]:
        if type(v) != type(''):
            try:
                v = v.encode('cp1250')
            except:
                v = str(v).encode('cp1250')
        ret = v.strip()
        if asutf:
            ret = storageutil.CP1250_To_UTF8(ret)
    else:
        print 'field', afield, 'has other type:', t
    return ret


class ADOUtil(object):

    def __init__(self, aconnectionstring='', aservercursor=1, acnt=1, acominitialize=0, dbaccessobj=None, aconnectiontimeout=5, acommandtimeout=180):
        self.COMInitialize = acominitialize
        self.isclosed = 1
        # context variables
        self.SetContextVars(uid=-1, poid=-1, cmsid=-1, toid=-1, coid=-1, ioid=-1, basenamemodifier='', infotablessufix=0)
        if dbaccessobj is None:
            self.ConnectionString = aconnectionstring
            self.DBAccessObj = None
        else:
            self.DBAccessObj = dbaccessobj.AsObject()
            self.ConnectionString = dbaccess.GetConnectionString(self.DBAccessObj)
        self.ADOTypes = {}
        if not self.ConnectionString:
            if dbaccessobj:
                dbaccess.RegisterConnectionError(dbaccessobj)
            raise icorexceptions.ICORExceptionDatabase('ADOUtil empty connection string')
        if self.COMInitialize:
            sys.coinit_flags = 0
            import pythoncom
            pythoncom.CoInitialize()
        ainc = 1
        while acnt:
            asleep = 0.05
            try:
                self.adolib, self.adoconst, amajor, aminor = ADOInitialize()
                self.adolibx, self.adoconstx = None, None
                self.connection = self.adolib.Connection()
                if aservercursor:
                    alocation = self.adoconst.adUseServer
                else:
                    alocation = self.adoconst.adUseClient
                try:
                    self.connection.CursorLocation = alocation
                    self.connection.ConnectionTimeout = aconnectiontimeout
                    self.connection.CommandTimeout = acommandtimeout
                    self.connection.Open(self.ConnectionString)
                    self.connection.CursorLocation = alocation
                    self.isclosed = 0
                    break
                except pywintypes.com_error, e:
                    if e.args[0] == -2147352567 and 'The login failed' in e.args[2][2]:    #(-2147352567, 'Exception occurred.', (0, 'Microsoft OLE DB Provider for ODBC Drivers', '[Microsoft][ODBC SQL Server Driver][SQL Server]Cannot open database "ICORPEBR" requested by the login. The login failed.', None, 0, -2147467259), None)
                        self.ConnectionString, w = self.SwapConnectionFailover(self.ConnectionString)
                        if w:
                            asleep = 0.001
                            if acnt == 1:
                                acnt = acnt + ainc
                                ainc = 0
                    raise
            except:
                acnt = acnt - 1
                if not acnt:
                    if dbaccessobj:
                        dbaccess.RegisterConnectionError(dbaccessobj)
                    if self.COMInitialize:
                        pythoncom.CoUninitialize()
                    raise
                else:
                    time.sleep(asleep)

    def __del__(self):
        self.Close()

    def __nonzero__(self):
        return self.isclosed == 0

    def SetContextVars(self, uid=None, poid=None, cmsid=None, toid=None, coid=None, ioid=None, basenamemodifier=None, infotablessufix=None):
        if uid is not None:
            self.uid = int(uid)
        if poid is not None:
            self.poid = int(poid)
        if cmsid is not None:
            self.cmsid = int(cmsid)
        if toid is not None:
            self.toid = int(toid)
        if coid is not None:
            self.coid = int(coid)
        if ioid is not None:
            self.ioid = ioid
        if basenamemodifier is not None:
            self.basenamemodifier = basenamemodifier
        if infotablessufix is not None:
            self.infotablessufix = infotablessufix

    def CheckContextAccess(self, mode, aacclevelname, adefault=0):
        if self.uid < 0:
            return 0
        if mode == 'project':
            if self.poid < 0:
                return adefault
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
            aobj = aclass[self.poid]
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, aacclevelname, self.uid)
        elif mode == 'cms':
            if self.cmsid < 0:
                return adefault
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
            aobj = aclass[self.cmsid]
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, aacclevelname, self.uid)
        elif mode == 'table':
            if self.toid < 0:
                return adefault
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
            aobj = aclass[self.toid]
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, aacclevelname, self.uid)
        elif mode == 'chapter':
            if self.coid < 0:
                return adefault
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
            aobj = aclass[self.coid]
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, aacclevelname, self.uid)
        elif mode == 'record':
            if self.toid < 0 or self.ioid == '':
                return adefault
            aclass = ICORInterface.aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Dotyczy']
            aobj = aclass[self.toid]
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, aacclevelname, self.uid)
        return ret

    def SwapConnectionFailover(self, aconnectionstring):
        w = 0
        apatt = re.compile('\; *server *\= *(.*?)\;.*?failover partner *\= *(.*?)\;', re.I)
        m = apatt.search(aconnectionstring)
        if m:
            w = 1
            aconnectionstring = aconnectionstring.replace(m.group(2), '$$$V1$$$')
            aconnectionstring = aconnectionstring.replace(m.group(1), m.group(2))
            aconnectionstring = aconnectionstring.replace('$$$V1$$$', m.group(1))
        return aconnectionstring, w

    def OpenADOX(self):
        self.adolibx, self.adoconstx, amajorx, aminorx = ADOXInitialize()
        self.catalog = self.adolibx.Catalog()
        self.catalog.ActiveConnection = self.connection
        for akey, avalue in ADOColTypes.__dict__.items():
            if type(avalue) == type(1):
                self.ADOTypes[avalue] = akey[2:]

    def CloseADOX(self):
        pass

    def Close(self):
        if self.isclosed:
            return
        self.isclosed = 1
        self.CloseADOX()
        if self.connection is not None:
            self.connection.Close()
            self.connection = None
        if self.COMInitialize:
            import pythoncom
            pythoncom.CoUninitialize()

    def GetRS(self, asql, aclient=0):
        if self.isclosed:
            return
        if VERBOSE:
            startutil.GetLogTempFileName('sqlexec', aprefix='sql', asufix='adoutil_getrs', avalue=asql, atrace=1)
        rs = self.adolib.Recordset()
        if aclient:
            rs.CursorLocation = self.adoconst.adUseClient
            rs.Open(asql, self.connection, self.adoconst.adOpenStatic, self.adoconst.adLockOptimistic)    #
        else:
            rs.CursorLocation = self.adoconst.adUseServer
            rs.Open(asql, self.connection, self.adoconst.adOpenKeyset, self.adoconst.adLockOptimistic)    #
        return rs

    def CloseRS(self, rs):    #rs=adoutil.CloseRS(rs)
        if rs is None:
            return None
        if rs.State != self.adoconst.adStateClosed:
            rs.Close()
        rs = None
        return None

    def RSCorrectTextFields(self, rs, adefault=0):
        mf = rs.Fields.Count
        for i in range(mf):
            if rs.Fields.Item(i).Type == adoconst.adLongVarChar:
                if adefault:
                    atext = ''
                else:
                    atext = GetRSValueAsStr(rs, i)
                rs.Fields.Item(i).Value = atext

    def StoreField(self, rs, afield, avalue):
        t = rs.Fields.Item(afield).Type
        if t in [adoconst.adDate, adoconst.adDBDate, adoconst.adDBTime, adoconst.adDBTimeStamp]:    #adDate,adDBDate,adDBTime,adDBTimeStamp
            avalue = ICORUtil.ISODateTime2SQLDateTime(avalue)
            if not avalue:
                return
        rs.Fields.Item(afield).Value = avalue

    def UpdateRS(self, rs, acnt=7):
        self.RSCorrectTextFields(rs)
        while acnt:
            try:
                rs.Update()
                break
            except:
                acnt = acnt - 1
                if not acnt:
                    raise
                time.sleep(7)

    def AddNew(self, rs):
        self.RSCorrectTextFields(rs, 1)
        rs.AddNew()

    def Execute(self, asql):
        if self.isclosed:
            return
        if VERBOSE:
            startutil.GetLogTempFileName('sqlexec', aprefix='sql', asufix='adoutil_execute', avalue=asql, atrace=1)
        rs1, status = self.connection.Execute(asql)
        if rs1.State != self.adoconst.adStateClosed:
            rs1.Close()
        rs1 = None
        return status

    def SQL2RS(self, asql, aexecute=1):
        if self.isclosed:
            return
        if VERBOSE:
            startutil.GetLogTempFileName('sqlexec', aprefix='sql', asufix='adoutil_sql2rs', avalue=asql, atrace=1)
        if aexecute:
            rs, status = self.connection.Execute(asql)
        else:
            rs = self.GetRS(asql)
        return rs

    def GetSchemaObjects(self):
        ltables, lviews, lstoredprocedures, lfunctions = [], [], [], []
        atables = self.catalog.Tables
        for atable in atables:
            if atable.Type == 'TABLE':
                ltables.append(atable.Name)
            elif atable.Type == 'VIEW':
                lviews.append(atable.Name)
        return ltables, lviews, lstoredprocedures, lfunctions

    def GetTableInfo(self, atablename):
        atable = self.catalog.Tables(atablename)
        print atable.Name, atable.Type
        for acolumn in atable.Columns:
            aname, atype, asize = acolumn.Name, self.ADOTypes[acolumn.Type], acolumn.DefinedSize
            if asize > 20000:
                asize = 0
            if asize:
                print aname, atype, asize
            else:
                print aname, atype

    def RSIterator(self, asql, afunc, aexecute=0):
        if VERBOSE:
            startutil.GetLogTempFileName('sqlexec', aprefix='sql', asufix='adoutil_rsiterator', avalue=asql, atrace=1)
        if aexecute:
            rs, status = self.connection.Execute(asql)
        else:
            rs = self.GetRS(asql)
        if rs.State != self.adoconst.adStateClosed:
            while not rs.EOF and not rs.BOF:
                apply(afunc, (rs, ))
                rs.MoveNext()
        rs = self.CloseRS(rs)

    def GetRSAsTable(self, rs, file, acaption='', amaxvaluelen=0, aentityencode=1, acounter=0):
        icnt = 1000
        while rs is not None and icnt:
            icnt = icnt - 1
            if rs.State != self.adoconst.adStateClosed:
                if acaption:
                    file.write('<h2>%s</h2>' % (acaption, ))
                file.write("<TABLE id='sortedTable0'>")
                file.write('<thead><tr>')
                if acounter:
                    file.write('<th>l.p.</th>')
                mf = rs.Fields.Count
                for i in range(mf):
                    file.write('<th>' + GetRSNameAsStr(rs, i) + '</th>')
                file.write('</tr></thead><tbody>')
                ir = 0
                acnt = 1
                while not rs.EOF and not rs.BOF:
                    if not ir:
                        file.write("<tr class='sort-row-odd'>")
                    else:
                        file.write("<tr class='sort-row-even'>")
                    if acounter:
                        file.write('<td>%d</td>' % (acnt, ))
                    ir = 1 - ir
                    for i in range(mf):
                        avalue = GetRSValueAsStr(rs, i)
                        if not avalue:
                            avalue = '-'
                        if amaxvaluelen:
                            avalue = avalue[:amaxvaluelen]
                        if aentityencode:
                            avalue = XMLUtil.GetAsXMLStringNoPL(avalue)
                        file.write('<td>' + avalue + '</td>')
                    file.write('</tr>')
                    acnt = acnt + 1
                    rs.MoveNext()
                file.write('</tbody></table>')
            try:
                rs, status = rs.NextRecordset()
            except Exception, v:
                file.write('<font color=red><pre>')
                hresult_code, hresult_name, additional_info, parameter_in_error = v
                exception_string = ["%s - %s" % (hex(hresult_code), hresult_name)]
                if additional_info:
                    wcode, source_of_error, error_description, whlp_file, whlp_context, scode = additional_info
                    exception_string.append("  Error in: %s" % source_of_error)
                    exception_string.append("  %s - %s" % (hex(scode), error_description.strip()))
                for s in exception_string:
                    file.write(s + '\n')
                file.write('</pre></font>')

    def GetRSValueAsStr(self, ars, afield, adatedelimiter='-', astype=0, acontext=None, asutf=0, asdecimal=0):
        return GetRSValueAsStr(ars, afield, adatedelimiter=adatedelimiter, astype=astype, acontext=self, asutf=asutf, asdecimal=asdecimal)
