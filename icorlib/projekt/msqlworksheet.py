# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_Win32_OLE_ICORExcel import *
from CLASSES_Library_DBBase_GDVR_Main_ICORGDVRMain import aICORGDVR
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_DBBase_Util_Excel_HTMLXLSTable as HTMLXLSTable
import icorlib.wwwserver.icorwwwinterfaceutil as ICORWWWInterfaceUtil
import string
import re
import cStringIO
import cPickle
import types

import icordbmain.adoutil as ADOLibInit
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icordbmain.dbaccess as dbaccess

ExceptionIgnore = 'ExceptionIgnore'


class StatusInfo:

    def __init__(self, atype, adescription, acell='', acellref='', alinkref='', adata=''):
        self.Type = atype    # Error, Warning, Info, Debug
        self.Description = adescription
        if isinstance(acell, types.StringTypes):
            self.Cell = acell
        else:
            acol, arow = acell
            self.Cell = GetCellAddressAsExcelCellAddress(acol, arow)
        if isinstance(acellref, types.StringTypes):
            self.CellRef = acellref
        else:
            acol, arow = acellref
            self.CellRef = GetCellAddressAsExcelCellAddress(acol, arow)
        self.LinkRef = alinkref
        self.Data = adata

    def AsString(self):
        s = '%s: %s; %s' % (self.Cell, self.Type, self.Description)
        if self.LinkRef:
            s = s + ' : [' + str(self.LinkRef) + ']'
        if self.Data:
            s = s + ': <' + str(self.Data) + '>'
        return s


class ICORWorksheetCell:

    def __init__(self, aquery, acolumnid, acellrow, axlscell):
        self.Query = aquery
        self.aWorksheetQueries = aquery.Queries
        self.ColumnID = acolumnid
        self.CellRow = acellrow
        self.Coords = self.ColumnID, self.CellRow
        self.Cell = axlscell
        self.CellID = self.Query.TableID + '!' + GetCellAddressAsExcelCellAddress(self.ColumnID, self.CellRow)
        self.IsCalculated = 0

    def __getattr__(self, name):
        if name == 'Formula':
            s = self.Cell.Value
            if not isinstance(s, types.StringTypes):
                return str(s)
            return s
        if name == 'ValueType':
            if type(self.Cell.Value) == type(0.0):
                return mt_Double
            else:
                return mt_String
        if name == 'Value':
            return self.Cell.Value
        if name == 'ValueAsComp':
            return self.Cell.Value
        if name == 'ValueAsString':
            return self.Cell.ValueAsString

    def cmd_CELLNAME(self, avalue):    # do zrobienia
        return 1

    def GetProperNumLine(self, aline):
        patt = '([\(\,])0(\d)'

        def f(amatch):
            return amatch.group(1) + amatch.group(2)

        return re.sub(patt, f, aline)

    def EvalCommand(self, aline):
        gdict = {'CELLNAME': self.cmd_CELLNAME, }
        try:
            aline = self.GetProperNumLine(aline)
            res = eval(aline, gdict)
            if res is not None:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'nieznana komenda w komórce', acell=(acol, arow), acellref='', alinkref='', adata=aline)
        except:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'błędna zawartość', acell=(acol, arow), acellref='', alinkref='', adata=aline)
            import traceback
            traceback.print_exc()

    def stm_IIF(self, w, t, f):
        if w:
            return t
        return f

    def stm_CELL(self, arange):
        if string.find(arange, '!') >= 0:
            sl = string.split(arange, '!')
            if len(sl) != 2:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'nieprawidłowe odniesienie do innego arkusza', acell=(acol, arow), acellref='', alinkref='', adata=arange)
                return 0.0
            aworksheet = self.aWorksheetQueries[sl[0]]
            if aworksheet is None:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'odniesienie do nieistniejącego arkusza', acell=(acol, arow), acellref='', alinkref='', adata=sl[0])
                return 0.0
            arange = sl[1]
        else:
            aworksheet = self.Query
        if string.find(arange, ':') >= 0:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'nieprawidłowe odniesienie do zakresu', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return 0.0
        acol1, arow1 = GetExcelCellAddressAsCellAddress(arange)
        if acol1 < 0 or arow1 < 0 or acol1 > 256 or arow1 > 65536:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'Odniesienie do komórki poza zakresem', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return 0.0
        sum = 0.0
        if acol1 > aworksheet.MaxCol or arow1 > aworksheet.MaxRow:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'odniesienie do komórki poza zakresem', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return sum
        acell = aworksheet[acol1, arow1]
        if acell is not None:
            if not acell.IsCalculated:
                acell.Calculate()
            elif acell.CellID in self.aWorksheetQueries._CalculateRecurList:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'referencja do tej samej komórki', acell=(acol, arow), acellref='', alinkref='', adata=string.join(self.aWorksheetQueries._CalculateRecurList, ', '))
                return 0.0
            sum = acell.ValueAsComp
            if type(sum) != type(0.0):
                acol1, arow1 = self.Coords
                acol2, arow2 = acell.Coords
                sv = acell.Formula
                s = 'komórka %s [%d,%d] odwołuje się do komórki %s [%d,%d], która nie posiada wartości numerycznej: %s' % (GetCellAddressAsExcelCellAddress(acol1, arow1), acol1, arow1, GetCellAddressAsExcelCellAddress(acol2, arow2), acol2, arow2, sv)
                self.Query.AddStatusInfo('Warning', 'odwołanie do komórki, która nie posiada wartości numerycznej', acell=(acol1, arow1), acellref=(acol2, arow2), alinkref='', adata=sv)
                if isinstance(sum, types.StringTypes):
                    if string.strip(sum) == '':
                        sum = 0.0
#            raise ExceptionIgnore
        return sum

    def stm_SUM(self, arange):
        if string.find(arange, '!') >= 0:
            sl = string.split(arange, '!')
            if len(sl) != 2:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'nieprawidłowe odniesienie do innego arkusza', acell=(acol, arow), acellref='', alinkref='', adata=arange)
                return 0.0
            aworksheet = self.aWorksheetQueries[sl[0]]
            if aworksheet is None:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'odniesienie do nieistniejącego arkusza', acell=(acol, arow), acellref='', alinkref='', adata=sl[0])
                return 0.0
            arange = sl[1]
        else:
            aworksheet = self.Query
        sl = string.split(arange, ':')
        if not len(sl) or len(sl) > 2:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'nieprawidłowy zakres', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return 0.0
        if len(sl) == 1:
            sl.append(sl[0])
        acol1, arow1 = GetExcelCellAddressAsCellAddress(sl[0])
        if acol1 < 0 or arow1 < 0 or acol1 > 256 or arow1 > 65536:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'Odniesienie do komórki poza zakresem', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return 0.0
        acol2, arow2 = GetExcelCellAddressAsCellAddress(sl[1])
        if acol2 < 0 or arow2 < 0 or acol2 > 256 or arow2 > 65536:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'Odniesienie do komórki poza zakresem', acell=(acol, arow), acellref='', alinkref='', adata=arange)
            return 0.0
        sum = 0.0
        w = 0
        while arow1 <= arow2:
            bcol = acol1
            while bcol <= acol2:
                if bcol > aworksheet.MaxCol or arow1 > aworksheet.MaxRow:
                    acol, arow = self.Coords
                    self.Query.AddStatusInfo('Error', 'odniesienie do komórki poza zakresem', acell=(acol, arow), acellref='', alinkref='', adata=arange)
                    w = 1
                    break
                acell = aworksheet[bcol, arow1]
                if acell is not None:
                    if not acell.IsCalculated:
                        acell.Calculate()
                    elif acell.CellID in self.aWorksheetQueries._CalculateRecurList:
                        acol, arow = self.Coords
                        self.Query.AddStatusInfo('Error', 'referencja do tej samej komórki', acell=(acol, arow), acellref='', alinkref='', adata=string.join(self.aWorksheetQueries._CalculateRecurList, ', '))
                        return sum
                    try:
                        avc = acell.ValueAsComp
                        if avc:
                            sum = sum + avc
                    except:
                        acol1, arow1 = self.Coords
                        acol2, arow2 = acell.Coords
                        sv = acell.Formula
                        if sv:
                            self.Query.AddStatusInfo('Error', 'odwołanie do komórki, która posiada błędną wartość', acell=(acol1, arow1), acellref=(acol2, arow2), alinkref='', adata=sv)
                        else:
                            self.Query.AddStatusInfo('Error', 'odwołanie do komórki, która nie posiada wartości', acell=(acol1, arow1), acellref=(acol2, arow2), alinkref='', adata='')
##                  import traceback
##                  traceback.print_exc()
##                  print s
                        raise ExceptionIgnore
                bcol = bcol + 1
            if w:
                break
            arow1 = arow1 + 1
        return sum

    def stm_GETVALUE(self, adict, aitem, ayear, amonth, aday, afield):
        adate = (ayear, amonth, aday)
        agvrdict = aICORGDVR[self.Query.StructName, adict]
        try:
            bitem = agvrdict[aitem]
        except:
            acol, arow = self.Coords
            sv = '#!getvalue("%s","%s",%d,%d,%d,"%s")' % (adict, aitem, ayear, amonth, aday, afield)
            self.Query.AddStatusInfo('Error', 'odwołanie do nieistniejącej pozycji', acell=(acol, arow), acellref='', alinkref='', adata=sv)
            return 0.0
##         raise ExceptionIgnore
        try:
            bfield = bitem.ValueFields[afield]
        except:
            acol, arow = self.Coords
            sv = '#!getvalue("%s","%s",%d,%d,%d,"%s")' % (adict, aitem, ayear, amonth, aday, afield)
            self.Query.AddStatusInfo('Error', 'odwołanie do nieistniejącego pola', acell=(acol, arow), acellref='', alinkref='', adata=sv)
            return 0.0
##         raise ExceptionIgnore
        res = bfield[adate]
        if res == 0.0:
            acol, arow = self.Coords
            sv = '#!getvalue("%s","%s",%d,%d,%d,"%s")' % (adict, aitem, ayear, amonth, aday, afield)
            self.Query.AddStatusInfo('Warning', 'funkcja zwróciła wartość 0.00', acell=(acol, arow), acellref='', alinkref='', adata=sv)
        return res

    def EvalFormula(self, aline):
        gdict = {
            'iif': self.stm_IIF,
            'cell': self.stm_CELL,
            'sum': self.stm_SUM,
        #         'getvalue':self.stm_GETVALUE,
        }
        try:
            aline = self.GetProperNumLine(aline)
            acol, arow = self.Coords
            try:
                res = eval(aline, self.aWorksheetQueries.GlobalDict, gdict)
            except ZeroDivisionError:
                res = 0.0
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Warning', 'dzielenie przez zero', acell=(acol, arow), acellref='', alinkref='', adata=aline)
            if res is None:
                acol, arow = self.Coords
                self.Query.AddStatusInfo('Error', 'nieznana formuła', acell=(acol, arow), acellref='', alinkref='', adata=aline)
            else:
                if not isinstance(res, types.StringTypes):
                    res = str(res)
                self.Cell.SetValue(res)
        except ExceptionIgnore:
            pass
        except SyntaxError:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'błąd składni (sprawdź nawiasy i cudzysłowy)', acell=(acol, arow), acellref='', alinkref='', adata=aline)
        except NameError, e:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'nieznany identyfikator', acell=(acol, arow), acellref='', alinkref='', adata='[' + e.args[0] + '] ' + aline)
        except:
            acol, arow = self.Coords
            self.Query.AddStatusInfo('Error', 'błędna formuła', acell=(acol, arow), acellref='', alinkref='', adata=aline)
            import traceback
            traceback.print_exc()


##         raise

    def Calculate(self):
        self.IsCalculated = 1
        acol, arow = self.Coords
        if self.CellID in self.aWorksheetQueries._CalculateRecurList:
            self.Query.AddStatusInfo('Error', 'odniesienie do tej samej komórki', acell=(acol, arow), acellref='', alinkref='', adata=string.join(self.aWorksheetQueries._CalculateRecurList, ', '))
            return
        self.aWorksheetQueries._CalculateRecurList.append(self.CellID)
        aformula = self.Formula
        if string.find(aformula, '#!') >= 0:
            sl = string.split(aformula, '#!')
            for aline in sl:
                if not aline:
                    continue
                if aline[:1] == '@':
                    self.Cell.SetValue(aline[1:])
                elif aline[:1] == '=':
                    self.EvalFormula(aline[1:])
                else:
                    if aline[-1:] != ')':
                        aline = aline + '()'
                    self.EvalCommand(aline)
        else:
            self.Cell.SetValue(aformula)
        self.aWorksheetQueries._CalculateRecurList.pop()
        return

    def DumpHTML(self, file):
        valueasis = 0
        res = ['    <TD']
        sclass = 'objectsviewdata'
        res.append(' class="%s"' % sclass)
        res.append('>')
        sf = ''
        s = self.ValueAsString
        if not s:
            s = '&nbsp;'
        res.append(s)
        res.append('</TD>\n')
        file.write(string.join(res, ''))


class ICORWorksheetQuery:

    def __init__(self, aqueries, anazwatabeli, anazwapola, aoidarkusza, anazwaarkusza, astanprzeliczenia):
        #      self.ClassItem=aICORDBEngine.Classes['CLASSES_Library_DBBase_Query_WorkSheet_Main']
        #      self.OID=aoid
        #      self.StructName=astructname
        self.Queries = aqueries
        self.SQLNazwaTabeli = anazwatabeli
        self.SQLNazwaPola = anazwapola
        self.SQLOIDArkusza = aoidarkusza
        self.SQLNazwaArkusza = anazwaarkusza
        self.IsCalculated = astanprzeliczenia == 2
        self.InitVariables()
        print '  Init QUERY:', self

    def __repr__(self):
        return 'n: %s, p: %s, o: %s, id: %s, c: %d' % (self.SQLNazwaTabeli, self.SQLNazwaPola, self.SQLOIDArkusza, self.SQLNazwaArkusza, self.IsCalculated)

    __str__ = __repr__

    def InitVariables(self):
        self.TableID = self.SQLNazwaArkusza
        #      self._TableTitle,self._TableID,self._TableDescription,self._TableAuthor=None,None,None,None
        self._MaxCol, self._MaxRow = None, None
        self._XLSTable = None
        self._Cells = {}

    def __getattr__(self, name):
        if name == 'XLSTable':
            if self._XLSTable is None:
                amhtmltableparser = HTMLXLSTable.MHTMLXLSTableParser()
                asrc = self.Queries.GetXLSSource(self)
                amhtmltableparser.Process(asrc)
                self._XLSTable = amhtmltableparser.Table
            return self._XLSTable
        if name == 'MaxCol':
            if self._MaxCol is None:
                self._MaxCol = self.XLSTable.MaxCol
            return self._MaxCol
        if name == 'MaxRow':
            if self._MaxRow is None:
                self._MaxRow = self.XLSTable.MaxRow
            return self._MaxRow

    def __getitem__(self, akey):
        acol, arow = akey
        if self._Cells.has_key(akey):
            acell = self._Cells[akey]
        else:
            acell = ICORWorksheetCell(self, acol, arow, self.XLSTable[acol, arow])
            self._Cells[akey] = acell
        return acell

    def StatusCalculateAsString(self):
        ret = []
        for sdata, asi in self._CalculateInfo:
            ret.append(asi.AsString())
        return string.join(ret, '\n')

    def Calculate(self, asettext=1):
        if self.IsCalculated:
            print '  nic do przeliczenia!'
            return
        print '  CALCULATE:', self
        self.InitVariables()
        self.Queries._CalculateRecurList = []
        self._CalculateInfo = []
        for arow in range(self.MaxRow):
            for acol in range(self.MaxCol):
                acell = self[acol + 1, arow + 1]
                if acell is not None:
                    acell.IsCalculated = 0
        max = self.MaxRow * self.MaxCol
        for arow in range(self.MaxRow):
            for acol in range(self.MaxCol):
                acell = self[acol + 1, arow + 1]
                if acell is not None:
                    if not acell.IsCalculated:
                        acell.Calculate()


#      self.ClassItem.LastCalculation.SetValuesAsDateTime(self.OID,ICORUtil.tdatetime())
        if asettext:
            self.SetTextAsHTML()
        self.IsCalculated = 1

    def SetTextAsHTML(self):
        f = cStringIO.StringIO()
        self.XLSTable.DumpAsHTML(f, aasvisible=1)
        astatus = self.StatusCalculateAsString()
        self.Queries.StoreQueryHTML(self, f.getvalue(), astatus)

    def AddStatusInfo(self, atype='', adescription='', acell='', acellref='', alinkref='', adata=''):
        asi = StatusInfo(atype, adescription, acell=acell, acellref=acellref, alinkref=alinkref, adata=adata)
        print asi.AsString()
        self._CalculateInfo.append([(atype, adescription), asi])

    def DumpHTML(self, afile, aspage=0, ashowerrors=0):
        if isinstance(afile, types.StringTypes):
            file = ICORUtil.OpenText(afile, 'w')
            fclosed = 1
        else:
            file = afile
            fclosed = 0
        try:
            if aspage:
                file.write('<HTML>\n')
                file.write('<HEAD><meta http-equiv="X-UA-Compatible" content="IE=8">\n')
                file.write(ICORWWWInterfaceUtil.GetScriptCSS())
                file.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=windows-1250">\n')
                file.write('<TITLE>Tabela</TITLE>\n')
                file.write('</HEAD><BODY>\n\n')
            file.write('<TABLE class="objectsviewtable">\n')
            if self.TableTitle:
                file.write('  <CAPTION class="objectsviewcaption">%s</CAPTION>\n' % (self.TableTitle, ))
            for arow in range(self.MaxRow):
                file.write('  <TR>\n')
                for acol in range(self.MaxCol):
                    acell = self[acol + 1, arow + 1]
                    if acell is not None:
                        acell.DumpHTML(file)
                    else:
                        file.write('    <TD class="objectsviewdata">&nbsp;</TD>\n')
                file.write('  </TR>\n')
            file.write('</TABLE>')
            if ashowerrors:
                file.write('<PRE>%s</PRE>' % self.StatusCalculateAsString())
            if aspage:
                file.write('</BODY></HTML>\n')
        finally:
            if fclosed:
                file.close()


class DBName2SQLName:

    def __init__(self, pobj):
        self.ProjectsClass = pobj.Class
        self.DefaultOID = pobj.OID
        self.Projects = {}

    def __getitem__(self, key):
        if type(key) == type(()):
            aproject, aname = key
        else:
            aproject, aname = '', key
        if self.Projects.has_key(aproject):
            d = self.Projects.get(aproject, {})
        else:
            if not aproject:
                aoid = self.DefaultOID
            else:
                aoid = self.ProjectsClass.Nazwa.Identifiers(aproject)
            if aoid < 0:
                return ''
            d = {}
            pobj = self.ProjectsClass[aoid]
            amodifier = pobj.BaseNameModifier
            bobj = pobj.BazyZrodlowe
            while bobj:
                d[bobj.Nazwa] = amodifier + 'BZR_' + str(bobj.OID)
                bobj.Next()
            self.Projects[aproject] = d
        return d.get(aname, '')


class ICORWorksheetQueries:

    def __init__(self, pobj):
        self.ProjectObj = pobj
        self.ConnectionString = dbaccess.GetConnectionString(pobj.DBAccess)
        self.WorksheetTable = pobj.BaseNameModifier + 'SHEETINFO_0'
        self.GlobalDict = {}
        self._Connection = None
        self._ExternalConnections = {}
        self.DBName2SQL = DBName2SQLName(pobj)
        #      self.ClassItem=aICORDBEngine.Classes['CLASSES_Library_DBBase_Query_WorkSheet_QueryStruct']
        #      self.QueryClass=self.ClassItem.Query.ClassOfType
        self.adolib, self.adoconst, amajor, aminor = ADOLibInit.ADOInitialize()
        self.Refresh()

    def __getattr__(self, name):
        if name == 'Connection':
            return self.GetConnection()

    def GetConnection(self, aprojectname=''):
        if aprojectname:
            if not self._ExternalConnections.has_key(aprojectname):
                poid = self.ProjectObj.Class.Nazwa.Identifiers(aprojectname)
                if poid < 0:
                    print 'proba dostepu do nieznanego projektu:', aprojectname
                    return None
                pobj = self.ProjectObj.Class[poid]
                aConnection = self.adolib.Connection()
                aConnection.Open(dbaccess.GetConnectionString(pobj.DBAccess))
                aConnection.CursorLocation = self.adoconst.adUseClient
                aConnection.CommandTimeout = 0
                self._ExternalConnections[aprojectname] = aConnection
            return self._ExternalConnections.get(aprojectname, None)
        if self._Connection is None:
            self._Connection = self.adolib.Connection()
            self._Connection.Open(self.ConnectionString)
            self._Connection.CursorLocation = self.adoconst.adUseClient
            self._Connection.CommandTimeout = 0
        return self._Connection

    def CloseConnection(self, aprojectname=''):
        if aprojectname:
            if self._ExternalConnections.has_key(aprojectname):
                aconnection = self._ExternalConnections[aprojectname]
                aconnection.Close()
                del self._ExternalConnections[aprojectname]
            return
        for akey, aconnection in self._ExternalConnections.items():
            aconnection.Close()
        self._ExternalConnections = {}
        if self._Connection is None:
            return
        self._Connection.Close()
        self._Connection = None

    def GetRecordSet(self, asql, aprojectname=''):
        aconnection = self.GetConnection(aprojectname)
        rs = self.adolib.Recordset()
        rs.Open(asql, aconnection, self.adoconst.adOpenKeyset, self.adoconst.adLockOptimistic)
        return rs

    def CloseRecordset(self, rs):
        if rs is None:
            return
        if rs.State != self.adoconst.adStateClosed:
            rs.Close()

    def GetRecordSetValue(self, rs, i, adefault=None):
        ret = adefault
        if rs.EOF:
            return ret
        v = rs.Fields.Item(i).Value
        s = rs.Fields.Item(i).Name
        atype = rs.Fields.Item(i).Type
        s = s.encode('cp1250')
        #      print 'GetRecordSetValue:',s,i,atype
        if s == '_OID':
            ret = v.encode('cp1250')
        elif atype in [self.adoconst.adDate, self.adoconst.adDBDate, self.adoconst.adDBTime, self.adoconst.adDBTimeStamp]:
            ret = ICORUtil.tdatetime(int(v))
        elif atype in [self.adoconst.adBoolean, ]:
            try:
                v = v.encode('cp1250')
            except:
                #            print '*** unknown conversion type for *** :',rs.Fields.Item(i).Type
                v = str(v).encode('cp1250')
            ret = int(string.strip(v))
        elif atype in [self.adoconst.adTinyInt, self.adoconst.adSmallInt, self.adoconst.adInteger, self.adoconst.adBigInt, self.adoconst.adUnsignedTinyInt, self.adoconst.adUnsignedSmallInt, self.adoconst.adUnsignedInt, self.adoconst.adUnsignedBigInt]:
            try:
                v = v.encode('cp1250')
            except:
                print '*** unknown conversion type for *** :', rs.Fields.Item(i).Type
                v = str(v).encode('cp1250')
            ret = float(string.strip(v))
        elif atype in [self.adoconst.adSingle, self.adoconst.adDouble, self.adoconst.adCurrency, self.adoconst.adDecimal, self.adoconst.adNumeric]:
            try:
                v = v.encode('cp1250')
            except:
                print '*** unknown conversion type for *** :', rs.Fields.Item(i).Type
                v = str(v).encode('cp1250')
            ret = float(string.strip(v))
        elif atype in [self.adoconst.adBSTR, self.adoconst.adChar, self.adoconst.adVarChar, self.adoconst.adLongVarChar, self.adoconst.adWChar, self.adoconst.adVarWChar, self.adoconst.adLongVarWChar]:
            v = v.encode('cp1250')    #XMLUtil.GetAsXMLStringNoPL
            ret = string.strip(v)
        elif atype in [self.adoconst.adGUID]:
            v = v.encode('cp1250')
            ret = string.strip(v)
        elif atype in [self.adoconst.adEmpty, self.adoconst.adError, self.adoconst.adUserDefined, self.adoconst.adVariant, self.adoconst.adIDispatch, self.adoconst.adIUnknown, self.adoconst.adBinary, self.adoconst.adVarBinary, self.adoconst.adLongVarBinary, self.adoconst.adChapter, self.adoconst.adFileTime, self.adoconst.adPropVariant, self.adoconst.adVarNumeric, self.adoconst.adArray]:
            v = v.encode('cp1250')
            ret = string.strip(v)


#      print '  ret:',ret
        return ret

    def InitWorksheet(self, rs):
        anazwatabeli = rs.Fields.Item('NazwaTabeli').Value.encode('cp1250')
        anazwapola = rs.Fields.Item('NazwaPola').Value.encode('cp1250')
        aoidarkusza = rs.Fields.Item('OIDArkusza').Value.encode('cp1250')
        anazwaarkusza = rs.Fields.Item('NazwaArkusza').Value.encode('cp1250')
        astanprzeliczenia = int(rs.Fields.Item('StanPrzeliczenia').Value)
        aitem = ICORWorksheetQuery(self, anazwatabeli, anazwapola, aoidarkusza, anazwaarkusza, astanprzeliczenia)
        self.Dicts[anazwaarkusza] = aitem
        print '  AFTER INIT WORKSHEET:', aitem
        return aitem

    def Refresh(self):
        self.Dicts = {}
        self._CalculateRecurList = []
        try:
            asql = 'SELECT * FROM ' + self.WorksheetTable + ' WHERE StanPrzeliczenia=1'
            rs, status = self.Connection.Execute(asql)
            if rs.State != self.adoconst.adStateClosed:
                while not rs.EOF and not rs.BOF:
                    self.InitWorksheet(rs)
                    rs.MoveNext()
        except:
            print 'Error in SQL command:', asql
            raise
        self.GlobalDict['aICORDBEngine'] = aICORDBEngine
        self.GlobalDict['aICORWorksheetQueries'] = self
        self.GlobalDict['adoconst'] = self.adoconst
        self.GlobalDict['re'] = re
        self.GlobalDict['string'] = string
        self.GlobalDict['ICORUtil'] = ICORUtil
        mobj = self.ProjectObj.SheetMethods
        while mobj:
            atext = string.replace(mobj.SheetMethodText + '\n', chr(13), '')
            try:
                exec atext in self.GlobalDict
            except:
                print 'Error in worksheet method "%s"' % mobj.Nazwa
            mobj.Next()

    def Calculate(self):
        for aquery in self.Dicts.values():
            print '  START CALCULATE:', aquery
            aquery.Calculate()

    def GetXLSSource(self, aquery):
        print '  GetXLSSource:', aquery
        res = ''
        try:
            asql = "SELECT %s_Src FROM %s WHERE _OID='%s'" % (aquery.SQLNazwaPola, aquery.SQLNazwaTabeli, aquery.SQLOIDArkusza)
            rs, status = self.Connection.Execute(asql)
            if rs.State != self.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    res = rs.Fields.Item(0).Value.encode('cp1250')
        except:
            print 'Error in SQL command:', asql
            raise
        return res

    def StoreQueryHTML(self, aquery, ahtml, astatus=''):
        print '  StoreQueryHTML:', aquery
        try:
            asql = "SELECT StanPrzeliczenia,Status FROM %s WHERE NazwaPola='%s' AND OIDArkusza='%s'" % (self.WorksheetTable, aquery.SQLNazwaPola, aquery.SQLOIDArkusza)
            rs = self.adolib.Recordset()
            rs.Open(asql, self.Connection, self.adoconst.adOpenKeyset, self.adoconst.adLockOptimistic)
            #            rs,status=aconnection.Execute(asql)
            if rs.State != self.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    rs.Fields.Item(0).Value = 3
                    rs.Fields.Item(1).Value = astatus
                    rs.Update()
                rs.Close()
            asql = "SELECT %s FROM %s WHERE _OID='%s'" % (aquery.SQLNazwaPola, aquery.SQLNazwaTabeli, aquery.SQLOIDArkusza)
            rs.Open(asql, self.Connection, self.adoconst.adOpenKeyset, self.adoconst.adLockOptimistic)
            if rs.State != self.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    rs.Fields.Item(0).Value = ahtml
                    rs.Update()
                rs.Close()
            rs = None
        except:
            print 'Error in SQL command:', asql
            raise

    def __getitem__(self, key):
        if self.Dicts.has_key(key):
            return self.Dicts.get(key, None)
        aitem = None
        try:
            asql = "SELECT * FROM %s WHERE NazwaArkusza='%s'" % (self.WorksheetTable, key)
            rs, status = self.Connection.Execute(asql)
            if rs.State != self.adoconst.adStateClosed:
                if not rs.EOF and not rs.BOF:
                    aitem = self.InitWorksheet(rs)
        except:
            print 'Error in SQL command:', asql
            raise
        if aitem is None:
            print 'Uknown QUERY:', key
        return aitem
