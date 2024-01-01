# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
from icorlib.wwwserver.icorwwwinterface import *
import icorlib.projekt.msqllib as MSQLLib
import string

DEBUG = 0

RULES_DICT = {'like': 'LIKE', 'ge': '>', 'le': '<', 'eq': '=', 'leq': '<=', 'geq': '>=', 'neq': '<>', 'in': 'IN', 'nin': 'NOT IN', }

SP_KEYWORD, SP_NUMBER, SP_IDENTIFIER, SP_COMMENT = 1, 2, 3, 4

SQL_REPL_TOP1 = 999999
SQL_REPL_TOP2 = 999998
SQL_REPL_WHERE = 999997


class QuerySQLException(Exception):

    def __init__(self, errmsg=''):
        Exception.__init__(self, errmsg)


class QuerySQLRule:

    def __init__(self, afield, attrs, aisleftjoin=0, atablename=''):
        self.Field = afield
        self.Type = attrs['type']
        self.TypeOp = RULES_DICT.get(self.Type, self.Type)
        self.Value = attrs['value']
        self.AsRef = int(attrs.get('asref', '0'))
        self.AsASP = int(attrs.get('asasp', '0'))
        self.AsText = int(attrs.get('astext', '0'))
        self.AsStoredProcedure = int(attrs.get('asstoredprocedure', '0'))
        self.IsLeftJoin = aisleftjoin
        if int(attrs.get('asleftjoin', '0')):
            self.IsLeftJoin = 1
        self.AsSearchField = int(attrs.get('assearchfield', '0'))
        self.ValueTableName = atablename

    def AsSQL(self):
        aop = RULES_DICT.get(self.Type, None)
        if not aop:
            print 'Nieznany operator:', self.Type
            return None
        if (self.Field.Type in ['string', 'text', 'date', 'datetime', 'text'] or aop == 'LIKE') and not (self.AsRef or self.AsASP or aop == 'IN' or aop == 'NOT IN') and not self.AsText:
            avalue = "'%s'" % self.Value
        else:
            avalue = self.Value
        if self.AsASP:
            ret = '%s %s \'" & %s & "\' ' % (self.Field.NameSQL, aop, avalue)
        elif self.AsStoredProcedure:
            ret = '(%s %s %s)' % (self.Field.NameSQL, aop, avalue)
        elif self.AsText:
            ret = avalue
        else:
            ret = '%s %s %s' % (self.Field.NameSQL, aop, avalue)
        return ret


class QuerySQLMarkerRule:

    def __init__(self, amarker, attrs):
        self.Marker = amarker
        self.Type = attrs.get('type', 'eq')
        self.Value = attrs.get('value', '')
        self.AsASP = int(attrs.get('asasp', '0'))

    def AsVB(self, awhat):
        atype = self.Marker.Field.Type
        aVBOperator = RULES_DICT.get(self.Type, None)
        if atype in ['string', 'text', 'external dict', 'external dict multiple', 'dict', 'dict int']:    # czy dla multiple rownież tak?
            if self.AsASP:
                if self.Type == 'like':
                    return 'InStr(LCase(%s),%s))>0' % (awhat, self.Value)
                else:
                    return '%s %s "%s"' % (awhat, aVBOperator, self.Value)
            else:
                if self.Type == 'like':
                    return 'InStr(LCase(%s),LCase("%s"))>0' % (awhat, self.Value)
                else:
                    return '%s %s "%s"' % (awhat, aVBOperator, self.Value)
        elif atype in ['integer']:
            if self.AsASP:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),%s))>0' % (awhat, self.Value)
                else:
                    return 'CLng(%s) %s %s' % (awhat, aVBOperator, self.Value)
            else:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),LCase("%s"))>0' % (awhat, self.Value)
                else:
                    return 'CLng(%s) %s %s' % (awhat, aVBOperator, self.Value)
        elif atype in ['numeric', 'money', 'float']:
            if self.AsASP:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),%s))>0' % (awhat, self.Value)
                else:
                    return 'CDbl(%s) %s %s' % (awhat, aVBOperator, self.Value)
            else:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),LCase("%s"))>0' % (awhat, self.Value)
                else:
                    return 'CDbl(%s) %s %s' % (awhat, aVBOperator, self.Value)
        elif atype in ['date', 'datetime']:
            if self.AsASP:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),%s))>0' % (awhat, self.Value)
                else:
                    return 'CDate(%s) %s %s' % (awhat, aVBOperator, self.Value)
            else:
                if self.Type == 'like':
                    return 'InStr(LCase(CStr(%s)),LCase("%s"))>0' % (awhat, self.Value)
                else:
                    return 'CDate(%s) %s getStrAsDateTime("%s","","",False)' % (awhat, aVBOperator, self.Value)
        elif atype == 'bool':
            if self.AsASP:
                ret = 'CBool(%s) %s %s' % (awhat, aVBOperator, self.Value)
                return ret
            else:
                if ICORUtil.str2bool(self.Value):
                    return 'CBool(%s) %s True' % (awhat, aVBOperator)
                else:
                    return 'CBool(%s) %s False' % (awhat, aVBOperator)
        else:
            print 'unknown XML MARKERRULE Field Type: [%s]' % atype
        return ''


class QuerySQLMarker:

    def __init__(self, afield, attrs):
        self.Field = afield
        self.Rules = []
        self.Group = attrs.get('group', '')
        if not self.Group:
            self.Group = self.Field.UniqueName
        self.Color = attrs.get('color', 'red')
        self.Description = attrs.get('description', '')
        self.Character = attrs.get('character', '&#9632;')
        self.FontFace = attrs.get('fontface', 'arial')
        self.FontSize = attrs.get('fontsize', '-1')
        self.MarkerID = 'aMARKER' + ICORUtil.str2ProperID(self.Group)

    def AddMarkerRule(self, attrs):
        arule = QuerySQLMarkerRule(self, attrs)
        self.Rules.append(arule)


class FormElement:

    def __init__(self, attrs, atext=''):
        self.Type = attrs.get('type', 'info')    #info,fieldset,text,rowbutton,toolbarbutton,attachment,xmllink
        self.Placement = attrs.get('placement', 'before')    #before,insidebefore,beforesubmit,insideafter,after,
        self.Class = attrs.get('class', '')
        self.Action = attrs.get('action', '')
        self.Max = attrs.get('max', '')
        self.Accept = attrs.get('accept', '')
        self.Name = attrs.get('name', '')
        self.Info = attrs.get('info', '')
        self.Text = attrs.get('text', '') + atext


class QuerySQLField:

    def __init__(self, atable, attrs):
        self.XMLAttrs = attrs
        self.Table = atable
        self.OID = -1
        self.CID = -1
        self.Rules = []
        self.FormElements = []
        self.IsPivotRow, self.IsPivotColumn, self.IsPivotData = 0, 0, 0
        self.PivotDataAxisTotalFunction = ''
        self.PivotDataAxisNumberFormat = None
        self.IsPivotExcludeColumnAxisField1 = None
        self.IsPivotExcludeColumnAxisField2 = None
        self.IsPivotExcludeColumnAxisField3 = None
        self.IsPivotExcludeColumnAxisField4 = None
        self.IsPivotExcludeRowAxisField1 = None
        self.IsPivotExcludeRowAxisField2 = None
        self.IsPivotExcludeRowAxisField3 = None
        self.IsPivotExcludeRowAxisField4 = None
        self.PivotExcludeColumnMetric = None
        self.PivotExcludeRowMetric = None
        self.IsPivotFilterAxisField = None
        self.ModelXMLDataIDView = 0
        self.ModelXMLDataIDEdit = 0
        self.NoPastDate = 0    #$$
        self.TextCols = 32
        self.TextRows = 6
        self.TextNoWrap = 'Off'
        self.IsClickable = 0
        if type(attrs) == type({}):
            self.SQLField = None
            self.Name = attrs['name']
            self.Type = attrs['type']
            self.TypeDescription = attrs.get('typedescription', '')
            self.PrettyName = string.replace(attrs.get('prettyname', ''), "'", '"')    #"
            self.IsSQLAliased = int(attrs.get('issqlaliased', '0'))

            self.SortStyle = 0
            self.IsSorted = int(attrs.get('issorted', '0'))
            if self.IsSorted:
                self.SortStyle = 1
#            print 'issorted==1, XML Field:',self.Name,self.Table.NameSQL
            if int(attrs.get('sortstyle', '0')):
                self.SortStyle = int(attrs.get('sortstyle', '0'))
                self.IsSorted = 1
            self.SortTabID = int(attrs.get('sorttabid', '-1'))
            if self.SortTabID < 0:
                self.SortTabID = self.Table.Query.MaxFieldSortTabID
                self.Table.Query.MaxFieldSortTabID = self.Table.Query.MaxFieldSortTabID + 10
            self.IsClickable = int(attrs.get('isclickable', '0'))
            self.IsPivotRow = int(attrs.get('ispivotrow', '0'))
            self.IsPivotColumn = int(attrs.get('ispivotcolumn', '0'))
            self.IsPivotData = int(attrs.get('ispivotdata', '0'))
            if self.IsPivotData:
                self.PivotDataAxisTotalFunction = attrs.get('pivotdataaxistotalfunction', 'sum')
                self.PivotDataAxisNumberFormat = attrs.get('pivotdataaxisnumberformat', '[BLACK] #,##0;[RED]-#,##0')
            else:
                self.PivotDataAxisTotalFunction = attrs.get('pivotdataaxistotalfunction', '')
                self.PivotDataAxisNumberFormat = attrs.get('pivotdataaxisnumberformat', '')
            self.IsPivotExcludeColumnAxisField1 = int(attrs.get('pivotexcludecolumnaxisfield1', '0'))
            self.IsPivotExcludeColumnAxisField2 = int(attrs.get('pivotexcludecolumnaxisfield2', '0'))
            self.IsPivotExcludeColumnAxisField3 = int(attrs.get('pivotexcludecolumnaxisfield3', '0'))
            self.IsPivotExcludeColumnAxisField4 = int(attrs.get('pivotexcludecolumnaxisfield4', '0'))
            self.IsPivotExcludeRowAxisField1 = int(attrs.get('pivotexcluderowaxisfield1', '0'))
            self.IsPivotExcludeRowAxisField2 = int(attrs.get('pivotexcluderowaxisfield2', '0'))
            self.IsPivotExcludeRowAxisField3 = int(attrs.get('pivotexcluderowaxisfield3', '0'))
            self.IsPivotExcludeRowAxisField4 = int(attrs.get('pivotexcluderowaxisfield4', '0'))
            self.PivotExcludeColumnMetric = attrs.get('pivotexcludecolumnmetric', '')
            self.PivotExcludeRowMetric = attrs.get('pivotexcluderowmetric', '')
            self.IsPivotFilterAxisField = int(attrs.get('ispivotfilteraxisfield', '0'))
            self.Size = attrs.get('size', '200')
            try:
                self.SizeAsNumber = int(self.Size)
            except:
                self.SizeAsNumber = 0
            self.IsSearch = int(attrs.get('issearch', '0'))
            self.IsIndexed = int(attrs.get('isindexed', '0'))
            self.IsAliased = int(attrs.get('isaliased', '0'))
            self.IsInteractive = int(attrs.get('isinteractive', '1'))
            self.IsObligatory = int(attrs.get('isobligatory', '1'))
            self.ExtDictConstraint = attrs.get('extdictconstraint', '')
            self.SearchTabID = int(attrs.get('searchtabid', '99999'))
            self.IsSingleViewHidden = int(attrs.get('issingleviewhidden', '0'))
            self.IsDictViewHidden = int(attrs.get('isdictviewhidden', '0'))
            self.IsSearchByValue = int(attrs.get('issearchbyvalue', '0'))
            self.ColumnWidth = int(attrs.get('columnwidth', '0'))
            self.FieldInfo = attrs.get('fieldinfo', '')
            self.FormShowAsRadio = int(attrs.get('formshowasradio', '0'))
            self.FieldItemClass = attrs.get('fielditemclass', '')
            self.FieldNameClass = attrs.get('fieldnameclass', '')
            self.FieldLinkClass = attrs.get('fieldlinkclass', '')
            self.FieldHTMLClass = attrs.get('fieldhtmlclass', '')
            self.FieldValueClass = attrs.get('fieldvalueclass', '')
            self.Filter = attrs.get('filter', '')
            self.Regex = attrs.get('regex', '')
            self.MinValue = attrs.get('minvalue', '')
            self.MaxValue = attrs.get('maxvalue', '')
            self.Unsigned = int(attrs.get('unsigned', '0'))
            self.TypeCaption = attrs.get('typecaption', '')
            self.FieldValuePreviewLink = attrs.get('fieldvaluepreviewlink', '')
            self.DefaultEntry = attrs.get('defaultentry', '')
            self.IsUnique = int(attrs.get('isunique', '0'))
            self.DisableDictShowAllValues = int(attrs.get('disabledictshowallvalues', '0'))
            self.FieldInputTemplate = attrs.get('fieldinputtemplate', '')
            self.NoEmptyValues = int(attrs.get('noemptyvalues', '0'))
            self.FieldDivClear = int(attrs.get('fielddivclear', '1'))
            self.Group = attrs.get('group', '')
            self.ColorSelectedValue = attrs.get('colorselectedvalue', '')
            self.ColorBackground = attrs.get('colorbackground', '')
            self.IsU2ULink = int(attrs.get('isu2ulink', '0'))
            self.TextNoWrap = attrs.get('textnowrap', 'On')
            self.IsClientStored = int(attrs.get('isclientstored', '0'))
        else:
            self.SQLField = attrs
            self.Name = self.SQLField.Name
            self.Type = self.SQLField.Type
            self.TypeDescription = self.SQLField.TypeDescription
            self.Size = self.SQLField.Size
            self.SizeAsNumber = self.SQLField.SizeAsNumber
            self.PrettyName = self.SQLField.PrettyName
            self.IsSQLAliased = 0
            self.IsSorted = self.SQLField.IsSorted
            self.SortTabID = self.Table.Query.MaxFieldSortTabID
            self.Table.Query.MaxFieldSortTabID = self.Table.Query.MaxFieldSortTabID + 10
            self.SortStyle = self.SQLField.SortStyle
            self.IsSearch = self.SQLField.IsSearch
            self.IsIndexed = self.SQLField.IsIndexed
            self.IsAliased = self.SQLField.IsAliased
            self.IsInteractive = self.SQLField.IsInteractive
            self.IsObligatory = self.SQLField.IsObligatory
            self.ExtDictConstraint = self.SQLField.ExtDictConstraint
            self.SearchTabID = self.SQLField.SearchTabID
            self.IsSingleViewHidden = self.SQLField.IsSingleViewHidden
            self.IsDictViewHidden = self.SQLField.IsDictViewHidden
            self.IsSearchByValue = 0
            self.ColumnWidth = 0
            self.FieldInfo = ''
            self.FormShowAsRadio = 0
            self.FieldItemClass = ''
            self.FieldNameClass = ''
            self.FieldLinkClass = ''
            self.FieldHTMLClass = ''
            self.FieldValueClass = ''
            self.Filter = self.SQLField.Filter
            self.Regex = self.SQLField.Regex
            self.MinValue = self.SQLField.MinValue
            self.MaxValue = self.SQLField.MaxValue
            self.Unsigned = self.SQLField.Unsigned
            self.TypeCaption = self.SQLField.TypeCaption
            self.FieldValuePreviewLink = self.SQLField.FieldValuePreviewLink
            self.DefaultEntry = self.SQLField.DefaultEntry
            self.IsUnique = self.SQLField.IsUnique
            self.DisableDictShowAllValues = self.SQLField.DisableDictShowAllValues
            self.FieldInputTemplate = self.SQLField.FieldInputTemplate
            self.NoEmptyValues = 0
            self.FieldDivClear = 1
            self.Group = self.SQLField.Group
            self.ColorSelectedValue = self.SQLField.ColorSelectedValue
            self.ColorBackground = self.SQLField.ColorBackground
            self.IsU2ULink = self.SQLField.IsU2ULink
            self.TextNoWrap = self.SQLField.TextNoWrap
            self.IsClientStored = 0
        if not self.PrettyName:
            self.PrettyName = self.Name
        self.DictValues = []
        self.DictValuesParents = {}
        self.Description = ''
        self.DescriptionName = ''
        self.DescriptionValue = ''
        self.DescriptionValue2 = ''
        self.FieldCnt = 0
        self.PrettyNameDisplayed = ICORUtil.GetProperCaption(self.PrettyName, amaxcaptionlen=48)
        #      if self.IsPivotRow or self.IsPivotColumn or self.IsPivotData:
        #         self.SimplifyPrettyName()
        if self.Type in ['external dict', 'external dict multiple']:
            self.IsSorted = 0
            self.SortStyle = 0


#      if self.Name[:1]=='_' and self.PrettyName==self.Name:
#         self.PrettyName='%s_%s'%(self.Table.NameSQL,self.Name)
        self.ThisMarker = None
        self.QueryDictTable = None
        self.ExternalDictTable = None
        self.NameSQL = self.Table.NameSQL + '.' + self.Name
        self.NameAlias = self.Table.NameAlias + '.' + self.Name
        self.UniqueName = self.Table.Query.GetUniqueFieldName(self)
        if not self.Table.FieldsAliased:
            self.IsAliased = 0

    def __getattr__(self, name):
        if name == 'TypeID':
            if self.Type == 'string':
                return mt_String
            elif self.Type in ['numeric', 'float']:
                return mt_Double
            elif self.Type == 'date':
                return mt_DateTime
            elif self.Type == 'datetime':
                return mt_DateTime
            elif self.Type == 'bool':
                return mt_Boolean
            elif self.Type == 'dict':
                return mt_String
            elif self.Type == 'dict int':
                return mt_Integer
            elif self.Type in ['external dict', 'external dict multiple']:
                return mt_String
            elif self.Type == 'text':
                return mt_String
            elif self.Type == 'integer':
                return mt_Integer
            elif self.Type == 'money':
                return mt_Double
        elif name == 'IsContainer':
            return self.Type in ['text', ]
        elif name == 'DictSourceTable':
            return self.QueryDictTable
        print 'UNKNOWN F:', name
        raise AttributeError

    def __repr__(self):
        return self.NameSQL

    def __str__(self):
        return self.NameSQL

    def AddMarker(self, attrs):
        self.ThisMarker = QuerySQLMarker(self, attrs)
        amarkergroup = self.Table.Query.MarkerGroups.get(self.ThisMarker.Group, [])
        amarkergroup.append(self.ThisMarker)
        self.Table.Query.MarkerGroups[self.ThisMarker.Group] = amarkergroup

    def AddDictValue(self, attrs):
        self.DictValues.append([attrs['key'], attrs['value']])
        sp = attrs.get('parents', '')
        spl = string.split(sp, '|')
        if spl:
            self.DictValuesParents[attrs['key']] = spl

    def AddFormElement(self, attrs, atext=''):
        aelement = FormElement(attrs, atext=atext)
        self.FormElements.append(aelement)

    def SimplifyPrettyName(self):
        self.PrettyName = string.replace(self.PrettyName[:22], '-', '_')

    def AddRule(self, attrs, aisleftjoin=0, atablename=''):
        self.Table.RulesExists = 1
        arule = QuerySQLRule(self, attrs, aisleftjoin=aisleftjoin, atablename=atablename)
        self.Rules.append(arule)

    def GenerateSQL(self, lfields, lconditions, dleftjoins, lleftjoins, lsearchfields, lstoredproceduresrules):
        afid = "%s.%s" % (self.Table.NameSQL, self.Name, )
        if self.Type == 'text':
            afid = 'CAST(%s AS varchar(220))' % (afid)
        elif self.Type in ['date', 'datetime']:
            afid = self.Table.GetSQLDateTimeColumnAsString(afid)
        if self.IsSQLAliased or self.PrettyName != self.Name:
            if self.Table.Query.AsJSONTable:
                afid = "%s AS [%s]" % (afid, self.UniqueName, )
            else:
                afid = "%s AS [%s]" % (afid, self.PrettyName, )
        lfields.append(afid)
        self.Table.Query.RegisterFieldSelect(self)
        for arule in self.Rules:
            if arule.IsLeftJoin:
                self.Table.AddLeftJoin(lleftjoins, dleftjoins, arule.AsSQL(), arule.ValueTableName)
            elif arule.AsSearchField:
                lsearchfields.append(arule)
            elif arule.AsStoredProcedure:
                lstoredproceduresrules.append(arule.AsSQL())
            else:
                lconditions.append(arule.AsSQL())


class QuerySQLTable:

    def __init__(self, aquery, aparent, attrs, aistableview=0, afieldsaliased=1, anamealias=''):
        self.XMLAttrs = attrs
        self.Query = aquery
        self.ParentTable = aparent
        self.FieldsList = []
        self.FormElements = []
        self.Fields = {}
        self.ThisField = None
        self.SubTables = []
        self.RulesExists = 0
        self.ParentExtConstraint = ''
        self.ContextField, self.RevContextField = '', ''
        self.LinkFields = None
        self.SortedFields = []
        self.SortedFieldsID = []
        self.SortedFieldsIDXML = []
        self.IsASPSQLConstraint = 0
        self.IsTableView = aistableview
        self.FieldsAliased = afieldsaliased
        self._FieldsByTabID = None
        self.NameAlias = anamealias
        if type(attrs) == type({}):
            self.SQLTable = None
            self.NameSQLID = attrs['namesql']
            self.TablePrefix = attrs.get('tableprefix', '')
            self.NameSQL = self.TablePrefix + self.NameSQLID
            self.Caption = attrs.get('caption', self.NameSQL)
            self.Name = self.Caption
            try:
                self.OID = int(attrs.get('OID', '-1'))
            except:
                self.OID = attrs.get('OID', '-1')
            self.NameFile = attrs.get('file', '')
            self.HasVersions = int(attrs.get('hasversions', '0'))
            self.HasVersions = 0
            self.VersionTable = None
            self.IsSQLView = int(attrs.get('issqlview', '0'))
        else:
            if isinstance(attrs, MSQLLib.SQLField):
                self.SQLTable = attrs.DictSourceTable
                self.ParentExtConstraint = attrs.ExtDictConstraint
            elif isinstance(attrs, QuerySQLField):
                self.SQLTable = attrs.QueryDictTable
                self.ParentExtConstraint = attrs.ExtDictConstraint
            else:
                self.SQLTable = attrs
            self.NameSQLID = self.SQLTable.NameSQLID    # UWAGA! Ten fragment musi byc na koncu kontruktora!
            self.TablePrefix = self.SQLTable.TablePrefix
            self.NameSQL = self.TablePrefix + self.NameSQLID
            self.Caption = self.SQLTable.Name
            self.Name = self.Caption
            self.OID = self.SQLTable.OID
            self.NameFile = self.SQLTable.NameFile
            self.HasVersions = self.SQLTable.HasVersions
            self.VersionTable = self.SQLTable.VersionTable
            self.IsSQLView = self.SQLTable.IsSQLView
            d = {'prettyname': "%s__OID" % self.NameSQLID, 'name': "_OID", 'type': "string", 'asref': "1"}
            afield = self.AddField(d)
            self.Query.RegisterFieldSelect(afield)
            d = {'prettyname': "%s__datetime" % self.NameSQLID, 'name': "_datetime", 'type': "datetime", 'asref': "1"}
            afield = self.AddField(d)
            self.Query.RegisterFieldSelect(afield)
            d = {'prettyname': "%s__UID" % self.NameSQLID, 'name': "_UID", 'type': "string", 'asref': "1"}
            afield = self.AddField(d)
            self.Query.RegisterFieldSelect(afield)
            d = {'prettyname': "%s__UserName" % self.NameSQLID, 'name': "_UserName", 'type': "string", 'asref': "1"}
            afield = self.AddField(d)
            self.Query.RegisterFieldSelect(afield)
        self.NameFileSubmit = self.NameFile
        self.NameSQLXSL = self.Query.GetUniqueTableName(self.NameSQLID)
        self.ID = self.OID

    def __getattr__(self, name):
        if name == 'FieldsByTabID':
            if self.SQLTable is None:
                if self._FieldsByTabID is None:
                    l = []
                    for afield in self.FieldsList:
                        l.append([afield.SortTabID, afield.Name, afield])
                    l.sort()
                    self._FieldsByTabID = []
                    for atabid, aname, afield in l:
                        self._FieldsByTabID.append(afield)
                return self._FieldsByTabID
            else:
                return self.SQLTable.FieldsByTabID
        print 'UNKNOWN T:', name
        raise AttributeError

    def __repr__(self):
        return self.NameSQL

    def __str__(self):
        return self.NameSQL

    def FieldsByName(self, aname):
        return self.Fields.get(aname, None)

    def AddField(self, attrs):
        self.ThisField = QuerySQLField(self, attrs)
        self.Fields[self.ThisField.Name] = self.ThisField
        self.FieldsList.append(self.ThisField)
        self.Query.RegisterField(self.ThisField)
        if self.ThisField.SortStyle == 1:
            self.SortedFields.append(self.ThisField.NameSQL + ' ASC')
            self.SortedFieldsID.append([self.ThisField.SortTabID, self.ThisField.NameSQL + ' ASC'])
            self.SortedFieldsIDXML.append([self.ThisField.SortTabID, self.ThisField.NameAlias + ' ASC'])
        elif self.ThisField.SortStyle == 2:
            self.SortedFields.append(self.ThisField.NameSQL + ' DESC')
            self.SortedFieldsID.append([self.ThisField.SortTabID, self.ThisField.NameSQL + ' DESC'])
            self.SortedFieldsIDXML.append([self.ThisField.SortTabID, self.ThisField.NameAlias + ' DESC'])
        return self.ThisField

    def AddFormElement(self, attrs, atext=''):
        aelement = FormElement(attrs, atext=atext)
        self.FormElements.append(aelement)

    def AddSubTable(self, atable):
        self.SubTables.append(atable)

    def GetSQLDateTimeColumnAsString(self, scolumn, aalias=None):
        if aalias is not None:
            aalias = ' as %s' % aalias
        else:
            aalias = ''
        ret = "replace(replace(convert(varchar(max),%s,120),'T00:00:00',''),' 00:00:00','')%s" % (scolumn, aalias)
        return ret

    def GetSQLUserName(self, tprefix='', aBaseNameModifier=''):
        if tprefix:
            if tprefix[-1:] != '.':
                tprefix = tprefix + '.'
        ret = "coalesce((select top 1 ItemValue from %sPROJECTVARS_0 tpv where %s_username=tpv._Username and tpv.ItemCategory='users' and tpv.ItemKind='alias'),%s_username) as _username" % (aBaseNameModifier, tprefix, tprefix)
        return ret

    def ProcessFieldsByID(self):
        if self.SQLTable is None:
            return
        cnt = 0
        fls = []
        flo = []
        if self.Query.NoUnderscore:
            d = {'name': '_OID', 'type': 'string', 'asref': '1'}
            self.AddField(d)
            d = {'name': '_datetime', 'type': 'datetime', 'asref': '1'}
            self.AddField(d)
            d = {'name': '_UID', 'type': 'string', 'asref': '1'}
            self.AddField(d)
            d = {'name': '_UserName', 'type': 'string', 'asref': '1'}
            self.AddField(d)
            if self.SQLTable.FieldsByName('_OIDDictRef') is not None:
                d = {'name': '_OIDDictRef', 'type': 'string', 'asref': '1'}
                self.AddField(d)
        for afield in self.SQLTable.FieldsByTabID:
            w = 0
            if (self.Query.IsAliased and afield.IsAliased) or not self.Query.IsAliased:
                w = 1
            if (self.Query.IsInteractive and afield.IsInteractive) or not self.Query.IsInteractive:
                w = 1
            if self.Query.NoUnderscore and afield.Name[:1] == '_':
                w = 0
            if self.Query.DisableHiddenDictFields and afield.IsDictViewHidden and self.ParentTable is not None:
                w = 0
            if w:
                asqlfield = self.AddField(afield)
                #            if afield.Type in ['external dict','external dict multiple'] and afield.IsObligatory: #and afield.IsAliased:
                if ((afield.Type == 'external dict') and afield.IsObligatory) or (afield.Type == 'external dict multiple'):    #and afield.IsAliased:
                    tlinks = self.Query.LinkFields
                    self.Query.LinkFields = None
                    afieldsaliased = afield.IsAliased
                    if not self.FieldsAliased:
                        afieldsaliased = 0
                    qtable = self.Query.PushTable(afield, afieldsaliased=afieldsaliased)
                    if qtable is not None:
                        qtable.RevContextField = asqlfield.Name
                        asqlfield.QueryDictTable = qtable
                        self.Query.PopTable()
                    self.Query.LinkFields = tlinks

    def AddLeftJoin(self, lleftjoins, dleftjoins, asql, avaluetablename=''):
        if not self.NameSQL in lleftjoins:
            lleftjoins.append(self.NameSQL)
        if avaluetablename and avaluetablename in lleftjoins:
            lpos = lleftjoins.index(self.NameSQL)
            tpos = lleftjoins.index(avaluetablename)
            if tpos > lpos:
                del lleftjoins[tpos]
                lleftjoins.insert(lpos, avaluetablename)
        ljoins = dleftjoins.get(self.NameSQL, [])
        ljoins.append(asql)
        dleftjoins[self.NameSQL] = ljoins

    def GenerateSQL(self, lfields, ltables, lconditions, lsorted, dleftjoins, lleftjoins, lsearchfields, lstoredproceduresrules):
        ltables.append(self.NameSQL)
        #      print ' '*len(ltables),self.NameSQL
        #      print ' '*len(ltables),'  linkfields:',self.LinkFields
        #      print ' '*len(ltables),'  contextfield:',self.ContextField
        #      print ' '*len(ltables),'  RevContextField:',self.RevContextField
        if self.LinkFields is not None and self.ParentTable is not None:
            srcfield, dstfield, aconstraint = self.LinkFields
            sls = string.split(srcfield, ',')
            sld = string.split(dstfield, ',')
            # check if all destionation field exists (could be disabled dict view field)
            w = 1
            for i in range(len(sls)):
                if not self.Fields.has_key(sld[i]):
                    w = 0
                    break
            if w:
                for i in range(len(sls)):
                    afield = self.Fields[sld[i]]
                    drule = {'type': 'eq', 'value': self.ParentTable.NameSQL + '.' + sls[i], 'asref': '1'}
                    afield.AddRule(drule, aisleftjoin=1, atablename=self.ParentTable.NameSQL)
                if aconstraint:
                    self.AddLeftJoin(lleftjoins, dleftjoins, aconstraint)
        elif self.ContextField:
            afield = self.Fields[self.ContextField]
            drule = {'type': 'eq', 'value': self.ParentTable.NameSQL + '._OID', 'asref': '1'}
            afield.AddRule(drule, atablename=self.ParentTable.NameSQL)
        elif self.RevContextField and self.ParentTable is not None:
            afield = self.Fields['_OID']
            if self.ParentTable.FieldsByName(self.RevContextField).Type == 'external dict multiple':
                if self.Query.IsASPStrings:
                    drule = {'type': 'like', 'value': self.ParentTable.NameSQL + '.' + self.RevContextField + " like '%'+" + afield.NameSQL + "+'%'", 'astext': 1}
                else:
                    drule = {'type': 'like', 'value': self.ParentTable.NameSQL + '.' + self.RevContextField + " like ''%''+" + afield.NameSQL + "+''%''", 'astext': 1}
            else:
                drule = {'type': 'eq', 'value': self.ParentTable.NameSQL + '.' + self.RevContextField, 'asref': '1'}
            afield.AddRule(drule, aisleftjoin=1, atablename=self.ParentTable.NameSQL)
        for afield in self.Fields.values():
            afield.GenerateSQL(lfields, lconditions, dleftjoins, lleftjoins, lsearchfields, lstoredproceduresrules)
        lsorted.extend(self.SortedFieldsID)
        if self.ParentExtConstraint:
            lconditions.append(self.ParentExtConstraint)
        for atable in self.SubTables:
            atable.GenerateSQL(lfields, ltables, lconditions, lsorted, dleftjoins, lleftjoins, lsearchfields, lstoredproceduresrules)

    def GetTableColumns(self, ltablecaptions, ltablecolumns, apath='.', arecur=None, avirtualroot='', type_EMail_xsl_BeforeFieldValue='', type_Telefon_xsl_BeforeFieldValue='', type_URL_xsl_BeforeFieldValue='', adisablerefs=0):
        if arecur is None:
            arecur = []
        arecur.append(self.NameSQLXSL)
        for afield in self.SQLTable.FieldsByTabID:
            w = 0
            if (self.Query.IsAliased and afield.IsAliased) or not self.Query.IsAliased:
                w = 1
            if (self.Query.IsInteractive and afield.IsInteractive) or not self.Query.IsInteractive:
                w = 1
            if self.Query.NoUnderscore and afield.Name[:1] == '_':
                w = 0
#         if afield.IsDictViewHidden:
#            print 'isdictviewhidden %s %s'%(afield.Name,`self.ParentTable is not None`)
            if self.Query.DisableHiddenDictFields and afield.IsDictViewHidden and self.ParentTable is not None:
                w = 0
            if afield.TypeDescription == 'Obrazek' or afield.Type == 'text':
                w = 0
            if afield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                w = 0
            if w:
                asqlfield = self.Fields[afield.Name]
                if asqlfield.QueryDictTable is not None:
                    if not afield.IsSingleViewHidden:
                        if afield.Type in ['external dict', 'external dict multiple']:    #$$ czy dla multiple tez?
                            if not asqlfield.QueryDictTable.NameSQLXSL in arecur:
                                asqlfield.QueryDictTable.GetTableColumns(ltablecaptions, ltablecolumns, apath + '/' + asqlfield.QueryDictTable.NameSQLXSL, arecur, avirtualroot=avirtualroot, type_EMail_xsl_BeforeFieldValue=type_EMail_xsl_BeforeFieldValue, type_Telefon_xsl_BeforeFieldValue=type_Telefon_xsl_BeforeFieldValue, type_URL_xsl_BeforeFieldValue=type_URL_xsl_BeforeFieldValue, adisablerefs=adisablerefs)
                else:
                    bpath = '%s/%s' % (apath, asqlfield.Name)
                    if asqlfield.TypeDescription == 'EMail':
                        if not self.IsTableView and not adisablerefs:
                            sxsl = """  <xsl:if test="(%s!='')">%s<a><xsl:attribute name="href">mailto:<xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a>&#160;</xsl:if>""" % (bpath, type_EMail_xsl_BeforeFieldValue, bpath, bpath)
                        else:
                            sxsl = """  <xsl:if test="(%s!='')">%s<xsl:value-of select="%s" disable-output-escaping="yes" />&#160;</xsl:if>""" % (bpath, type_EMail_xsl_BeforeFieldValue, bpath)
                    elif asqlfield.TypeDescription == 'URL':
                        if not self.IsTableView and not adisablerefs:
                            sxsl = """  <xsl:if test="(%s!='')">%s<a><xsl:attribute name="target">_new</xsl:attribute><xsl:attribute name="href">mailto:<xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a>&#160;</xsl:if>""" % (bpath, type_URL_xsl_BeforeFieldValue, bpath, bpath)
                        else:
                            sxsl = """  <xsl:if test="(%s!='')">%s<xsl:value-of select="%s" disable-output-escaping="yes" />&#160;</xsl:if>""" % (bpath, type_URL_xsl_BeforeFieldValue, bpath)
                    elif asqlfield.TypeDescription == 'Telefon':
                        sxsl = """  <xsl:if test="(%s!='')">%s<xsl:value-of select="%s" disable-output-escaping="yes" />&#160;</xsl:if>""" % (bpath, type_Telefon_xsl_BeforeFieldValue, bpath)
                    elif asqlfield.Type == 'bool':
                        sxsl = """  <xsl:if test="(%s='1')">Tak</xsl:if><xsl:if test="(%s='0')">Nie</xsl:if>""" % (bpath, bpath)
                    else:
                        sxsl = """  <xsl:if test="(%s!='')"><xsl:value-of select="%s" disable-output-escaping="yes" />&#160;</xsl:if>""" % (bpath, bpath)
                    if not afield.IsSingleViewHidden:
                        ltablecaptions.append(asqlfield.PrettyName)
                        ltablecolumns.append([bpath, sxsl])
        arecur.pop()

    def ProcessHTMLTree(self, arootnode):
        tnode = arootnode.AddNode(acaption='<b>Tabela: </b>' + self.Caption, aexpanded=1, asorted=0)
        if self.FieldsList:
            #         fnode=tnode.AddNode(acaption='Pola',aexpanded=1,asorted=1)
            for afield in self.FieldsList:
                if afield.IsAliased:
                    tnode.AddNode(acaption='<b>Pole: </b>' + afield.PrettyName, aexpanded=1, asorted=0)
        if self.SubTables:
            #         snode=tnode.AddNode(acaption='Podtabele',aexpanded=1,asorted=0)
            for atable in self.SubTables:
                atable.ProcessHTMLTree(tnode)

    def GenerateShapeSQL(self, llines, lxsllines, lxmllines, alevel=0, alastsubtable=0, acontext=None):
        if self.SQLTable is None:
            return
        avirtualroot, achapteroid, acgipath = '', -1, ''
        if acontext is not None:
            avirtualroot = acontext.VirtualRoot
            achapteroid = acontext.ThisChapter.OID
            acgipath = acontext.CGIPath
            type_EMail_xsl_BeforeFieldValue = acontext.TemplateXML.get('type_EMail_xsl_BeforeFieldValue', '')
            type_Telefon_xsl_BeforeFieldValue = acontext.TemplateXML.get('type_Telefon_xsl_BeforeFieldValue', '')
            type_URL_xsl_BeforeFieldValue = acontext.TemplateXML.get('type_URL_xsl_BeforeFieldValue', '')
            aisgallery, agallerycolumns = acontext.IsGallery, acontext.GalleryColumns
        else:
            type_EMail_xsl_BeforeFieldValue, type_Telefon_xsl_BeforeFieldValue, type_URL_xsl_BeforeFieldValue = '', '', ''
            aisgallery, agallerycolumns = 0, 4
        atableclass, arowclass, acellclass = 'WygladTabela', 'TabelaNazwaPola', 'TabelaWartoscPola'
        if self.IsTableView and self.Query.XSLShowAsTable and not alevel:
            atableclass, arowclass, acellclass = 'WygladTabelaMain', 'TabelaNazwaPolaMain', 'TabelaWartoscPolaMain{$apos}'
        aindent = '  ' * alevel
        llines.append(aindent + ' SHAPE { SELECT ')
        lxmllines.append(aindent + 'SELECT ')
        ll = [aindent + '%s._OIDDictRef' % self.NameSQL, aindent + '%s._OID' % self.NameSQL]
        llxml = [aindent + '%s._OID' % self.NameAlias, aindent + '%s._OIDDictRef' % self.NameAlias]
        if acontext:
            ll.append(aindent + '%s._ChapterID' % self.NameSQL)
            llxml.append(aindent + '%s._ChapterID' % self.NameAlias)
        if alevel == 0:
            ll.extend([aindent + '%s._datetime' % self.NameSQL, aindent + '%s._username' % self.NameSQL])
            llxml.extend([aindent + '%s._datetime' % self.NameAlias, aindent + '%s._username' % self.NameAlias])
            if acontext is not None:
                ll.extend([aindent + '%s.InformacjaPodmiotUdostepniajacy' % self.NameSQL, aindent + '%s.InformacjaDataWytworzenia' % self.NameSQL, aindent + '%s.InformacjaOsobaOdpowiedzialna' % self.NameSQL, aindent + '%s.InformacjaOpisCzynnosci' % self.NameSQL])
                llxml.extend([aindent + '%s.InformacjaPodmiotUdostepniajacy' % self.NameAlias, aindent + '%s.InformacjaDataWytworzenia' % self.NameAlias, aindent + '%s.InformacjaOsobaOdpowiedzialna' % self.NameAlias, aindent + '%s.InformacjaOpisCzynnosci' % self.NameAlias])
            lxsllines.append("""<?xml version="1.0" encoding="%s" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:custom="//icor.pl/custom" version="1.0">
<xsl:output method="html" omit-xml-declaration="yes"/>
<xsl:param name="printpreview">0</xsl:param>
<xsl:param name="firstchapterid">-1</xsl:param>
<xsl:param name="isgallery">%d</xsl:param>
<xsl:param name="gallerycolumns">%d</xsl:param>

<msxsl:script language="JScript" implements-prefix="custom"><![CDATA[
function uriencode(string) {
 return encodeURIComponent(string);
}
//<xsl:value-of select="custom:uriencode(string(Tytul))" />
]]></msxsl:script>

<xsl:template match="CHAPTERDATA">
  <table border="0" class="%s" cellspacing="2" cellpadding="2"  width="100%%"><tr><td class="TrescTytul"><xsl:value-of select="@title" disable-output-escaping="yes" /></td></tr></table>
  <table border="0" class="%s" cellspacing="2" cellpadding="2"  width="100%%"><xsl:apply-templates select="%s"/></table>
</xsl:template>""" % (self.Query.DefaultEncoding, aisgallery, agallerycolumns, atableclass, atableclass, self.NameSQLXSL,
                      ))
        ltablecaptions, ltablecolumns = [], []
        if (self.IsTableView and (alevel > 0)) or (self.Query.XSLShowAsTable and not alevel):
            lxsllines.append("""\n<xsl:template match="%s">""" % (self.NameSQLXSL, ))
            adisablerefs = not alevel and not self.Query.XSLShowAsTable
            self.GetTableColumns(ltablecaptions, ltablecolumns, avirtualroot=avirtualroot, type_EMail_xsl_BeforeFieldValue=type_EMail_xsl_BeforeFieldValue, type_Telefon_xsl_BeforeFieldValue=type_Telefon_xsl_BeforeFieldValue, type_URL_xsl_BeforeFieldValue=type_URL_xsl_BeforeFieldValue, adisablerefs=adisablerefs)
            lxsllines.append("""  <xsl:if test="position()=1"><tr>""")
            for afcaption in ltablecaptions:
                lxsllines.append("""    <td class="%s">%s</td>""" % (arowclass, afcaption, ))
            lxsllines.append("""  </tr></xsl:if>""")
            if self.Query.XSLShowAsTable and not alevel:
                lxsllines.append("""  <xsl:variable name="apos" select="position() mod 2" /><tr style="cursor:pointer;">""")
                apar1 = '&amp;'
                if string.find(acgipath, '?') == -1:
                    apar1 = '?'
                amodcgipath = string.replace(acgipath, '#', '<xsl:value-of select="$firstchapterid" disable-output-escaping="yes" />')
                lxsllines.append("""    <xsl:attribute name="onclick">window.location=&quot;%s%ssoid=<xsl:value-of select="@OID" disable-output-escaping="yes" /><xsl:if test="$firstchapterid!=./_ChapterID">&amp;chapterdest=<xsl:value-of select="_ChapterID" disable-output-escaping="yes" /></xsl:if>&quot;</xsl:attribute>""" % (amodcgipath, apar1))
            else:
                lxsllines.append("""  <tr>""")
            for afpath, asxsl in ltablecolumns:
                lxsllines.append("""    <td class="%s">%s&#160;</td>""" % (acellclass, asxsl, ))
            lxsllines.append("""  </tr>""")
        elif not alevel:
            lxsllines.append("""\n<xsl:template match="%s">\n  <xsl:if test="position()&gt;1"><tr><td colspan="2"><hr/></td></tr></xsl:if>""" % (self.NameSQLXSL, ))
        elif self.RevContextField:
            lxsllines.append("""\n<xsl:template match="%s">""" % (self.NameSQLXSL, ))
        else:
            lxsllines.append("""\n<xsl:template match="%s">\n  <tr><td colspan="2"><hr/></td></tr>""" % (self.NameSQLXSL, ))

        for afield in self.SQLTable.FieldsByTabID:
            w = 0
            if (self.Query.IsAliased and afield.IsAliased) or not self.Query.IsAliased:
                w = 1
            if (self.Query.IsInteractive and afield.IsInteractive) or not self.Query.IsInteractive:
                w = 1
            if self.Query.NoUnderscore and afield.Name[:1] == '_':
                w = 0
            if self.Query.DisableHiddenDictFields and afield.IsDictViewHidden and self.ParentTable is not None:
                w = 0
            if afield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                w = 0
            if w:
                asqlfield = self.Fields[afield.Name]
                if asqlfield.Type in ['external dict', 'external dict multiple']:    #$$ czy dla multiple tez?
                    ll.insert(0, " %s.%s " % (asqlfield.Table.NameSQL, asqlfield.Name, ))
                    llxml.insert(1, " %s.%s " % (asqlfield.Table.NameAlias, asqlfield.Name, ))
                elif alevel and asqlfield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                    pass
                else:
                    ll.append(" %s.%s " % (asqlfield.Table.NameSQL, asqlfield.Name, ))
                    llxml.append(" %s.%s " % (asqlfield.Table.NameAlias, asqlfield.Name, ))
#            if afield.IsSingleViewHidden: #uwaga! koniec petli
#               continue
                if self.IsTableView and self.Query.XSLShowAsTable and not alevel:
                    continue    #uwaga! koniec petli
                if not self.IsTableView or (self.IsTableView and not self.Query.XSLShowAsTable and not alevel):
                    s1, s2 = '', ''
                    if asqlfield.TypeDescription == 'Telefon':
                        s1 = type_Telefon_xsl_BeforeFieldValue    #'<img border="0" src="%simg/telefon.gif"/>&#160;'%avirtualroot

    #              elif asqlfield.TypeDescription!='HTML':
    #                  s2=' disable-output-escaping="yes" '
                    elif asqlfield.TypeDescription == 'URL':
                        s1 = type_URL_xsl_BeforeFieldValue    #'<img border="0" src="%simg/telefon.gif"/>&#160;'%avirtualroot
                    if asqlfield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                        pass
                    elif self.RevContextField:
                        if asqlfield.TypeDescription == 'Obrazek':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><img alt="*"><xsl:attribute name="src">%simages/<xsl:value-of select="%s" /></xsl:attribute></img>&#160;</xsl:if>""" % (asqlfield.Name, avirtualroot, asqlfield.Name, ))
                        elif asqlfield.Type in ['external dict', 'external dict multiple']:
                            pass
                        elif asqlfield.TypeDescription == 'EMail':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s">%s<a><xsl:attribute name="href">mailto:<xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a>&#160;</xsl:if>""" % (asqlfield.Name, type_EMail_xsl_BeforeFieldValue, asqlfield.Name, asqlfield.Name))
                        elif asqlfield.TypeDescription == 'URL':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s">%s<a><xsl:attribute name="target">new</xsl:attribute><xsl:attribute name="href"><xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a>&#160;</xsl:if>""" % (asqlfield.Name, type_URL_xsl_BeforeFieldValue, asqlfield.Name, asqlfield.Name))
                        else:
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s">%s<xsl:value-of select="%s" disable-output-escaping="yes" />&#160;</xsl:if>""" % (asqlfield.Name, s1, asqlfield.Name))
                    else:
                        if asqlfield.TypeDescription == 'Obrazek':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td colspan="2" class="WartoscPola" width="100%%"><img alt="*"><xsl:attribute name="src">%simages/<xsl:value-of select="%s" /></xsl:attribute></img></td></tr></xsl:if>""" % (asqlfield.Name, avirtualroot, asqlfield.Name, ))
                        elif asqlfield.Type in ['external dict', 'external dict multiple']:
                            pass
                        elif asqlfield.TypeDescription == 'EMail':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td class="WartoscPola" width="100%%">%s<a><xsl:attribute name="href">mailto:<xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a></td></tr></xsl:if>""" % (asqlfield.Name, asqlfield.PrettyName, type_EMail_xsl_BeforeFieldValue, asqlfield.Name, asqlfield.Name))
                        elif asqlfield.TypeDescription == 'URL':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td class="WartoscPola" width="100%%">%s<a><xsl:attribute name="target">new</xsl:attribute><xsl:attribute name="href"><xsl:value-of select="%s" disable-output-escaping="yes" /></xsl:attribute><xsl:value-of select="%s" disable-output-escaping="yes" /></a></td></tr></xsl:if>""" %
                                                 (asqlfield.Name, asqlfield.PrettyName, type_URL_xsl_BeforeFieldValue, asqlfield.Name, asqlfield.Name))
                        elif asqlfield.TypeDescription == 'Arkusz':
                            if not afield.IsSingleViewHidden:
                                d = {'FieldName': asqlfield.Name, 'UniqueName': asqlfield.Name + '_' + str(asqlfield.FieldCnt), 'ChapterOID': self.Query.XSLChapterOID}
                                lxsllines.append("""
  <xsl:if test="(%(FieldName)s!='')"><tr><td class="WartoscPola" width="100%%" colspan="2"><br/>     
     <OBJECT classid="clsid:0002E559-0000-0000-C000-000000000046" name="%(UniqueName)sVisible" id="%(UniqueName)sVisible" style="width=100%%;height=480px;"></OBJECT>
     <SCRIPT language="vbscript">
<![CDATA[
document.getElementById("%(UniqueName)sVisible").DisplayTitleBar = False
document.getElementById("%(UniqueName)sVisible").Cells.Clear
document.getElementById("%(UniqueName)sVisible").DataType = "HTMLURL"
document.getElementById("%(UniqueName)sVisible").HTMLURL = "getxmlsheetvalue.asp?chapter=%(ChapterOID)d&field=%(FieldName)s&oid=]]><xsl:value-of select="@OID"/><![CDATA["
document.getElementById("%(UniqueName)sVisible").Range("A1").Select
document.getElementById("%(UniqueName)sVisible").DisplayColHeaders = False
document.getElementById("%(UniqueName)sVisible").DisplayRowHeaders = False
'document.getElementById("%(UniqueName)sVisible").DisplayToolbar = False
document.getElementById("%(UniqueName)sVisible").AllowPropertyToolbox = False
document.getElementById("%(UniqueName)sVisible").Cells.Locked = True
document.getElementById("%(UniqueName)sVisible").ActiveSheet.Protection.Enabled = True
]]>
     </SCRIPT><br/></td></tr>
  </xsl:if>
""" % d)
                        elif asqlfield.Type == 'text':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td class="WartoscPola" width="100%%" colspan="2"><br/><xsl:value-of select="%s" disable-output-escaping="yes" /><br/></td></tr></xsl:if>""" % (asqlfield.Name, asqlfield.Name, ))
                        elif asqlfield.Type == 'bool':
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td class="WartoscPola" width="100%%"><xsl:if test="%s='1'">Tak</xsl:if><xsl:if test="%s='0'">Nie</xsl:if></td></tr></xsl:if>""" % (asqlfield.Name, asqlfield.PrettyName, asqlfield.Name, asqlfield.Name, ))
                        else:
                            if not afield.IsSingleViewHidden:
                                lxsllines.append("""  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td class="WartoscPola" width="100%%">%s<xsl:value-of select="%s" disable-output-escaping="yes" /></td></tr></xsl:if>""" % (asqlfield.Name, asqlfield.PrettyName, s1, asqlfield.Name))

        llines.append(aindent + string.join(ll, ', '))
        lxmllines.append(aindent + string.join(llxml, ', '))
        so, ss = '', ''
        soxml, ssxml = '', ''
        if alevel == 0:
            if not self.Query.XSLIsTableView:
                if achapteroid >= 0:
                    if not acontext.ThisChapter['SGShowAllRecords']:
                        ss = aindent + ' WHERE (%s._ChapterID=%d)' % (self.NameSQL, achapteroid)
                        ssxml = aindent + ' WHERE (%s._ChapterID=%d)' % (self.NameAlias, achapteroid)
            elif achapteroid >= 0:
                if not acontext.ThisChapter['SGShowAllRecords']:
                    ss = aindent + " WHERE %s._ChapterID=%d" % (self.NameSQL, achapteroid)
                    ssxml = aindent + " WHERE %s._ChapterID=%d" % (self.NameAlias, achapteroid)
        if self.SortedFieldsID:
            lsorted = self.SortedFieldsID[:]
            lsorted.sort()
            lsorted = map(lambda x: x[1], lsorted)
            lsortedxml = self.SortedFieldsIDXML[:]
            lsortedxml.sort()
            lsortedxml = map(lambda x: x[1], lsortedxml)
            so = ' ORDER BY ' + string.join(self.Query.UniqueList(lsorted), ', ')
            soxml = ' ORDER BY ' + string.join(self.Query.UniqueList(lsortedxml), ', ')
        llines.append(aindent + ' FROM %s %s%s } AS %s ' % (self.NameSQL, ss, so, self.NameSQLXSL))
        lxmllines.append(aindent + ' FROM %s AS %s %s%s ' % (self.NameSQL, self.NameAlias, ssxml, soxml, ))
        lxsllines2 = []
        if self.SubTables:
            llines.append(aindent + ' APPEND ')
            for i in range(len(self.SubTables)):
                if i > 0:
                    llines.append(aindent + ' , ')
                llines.append(aindent + '( ( ')
                asubtable = self.SubTables[i]
                if not self.IsTableView or (self.IsTableView and not self.Query.XSLShowAsTable and not alevel):
                    if asubtable.RevContextField:
                        #                  arfname=asubtable.SQLTable.TableCaption
                        arfname = self.Fields[asubtable.RevContextField].PrettyName
                        apar1 = '&amp;'
                        if string.find(acgipath, '?') == -1:
                            apar1 = '?'
                        amodcgipath = string.replace(acgipath, '#', '<xsl:value-of select="$firstchapterid" disable-output-escaping="yes" />')
                        amodcgipath = amodcgipath + apar1 + 'aoid=<xsl:value-of select="%s/@OID" disable-output-escaping="yes" />&amp;chapterdest=<xsl:value-of select="%s/_ChapterID" disable-output-escaping="yes" />' % (asubtable.NameSQLXSL, asubtable.NameSQLXSL)
                        lxsllines.append("""
  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td class="WartoscPola" width="100%%">
   <xsl:if test="%s/_ChapterID">
       <a>
         <xsl:attribute name="href">%s</xsl:attribute>
         <xsl:apply-templates select="%s"/>
       </a>
   </xsl:if>
   <xsl:if test="not(%s/_ChapterID)">
      <xsl:apply-templates select="%s"/>
   </xsl:if>
  </td></tr></xsl:if>
""" % (asubtable.NameSQLXSL, arfname, asubtable.NameSQLXSL, amodcgipath, asubtable.NameSQLXSL, asubtable.NameSQLXSL, asubtable.NameSQLXSL))
                    elif asubtable.IsTableView:
                        lxsllines.append("""  <xsl:if test="%s"><tr><td colspan="2"><hr/></td></tr><tr><td colspan="2"><table class="%s" border="0" width="100%%" cellspacing="2" cellpadding="2"><caption class="TabelaCaption" >%s:</caption><xsl:apply-templates select="%s"/></table></td></tr></xsl:if>""" % (asubtable.NameSQLXSL, atableclass, asubtable.SQLTable.TableCaption, asubtable.NameSQLXSL, ))
                    else:
                        lxsllines.append("""  <xsl:if test="%s"><tr><td class="NazwaPola" nowrap="nowrap">%s:</td><td><table class="%s" border="0" width="100%%" cellspacing="2" cellpadding="2"  ><xsl:apply-templates select="%s"/></table></td></tr></xsl:if>""" % (asubtable.NameSQLXSL, asubtable.SQLTable.TableCaption, atableclass, asubtable.NameSQLXSL, ))
                alast = i == len(self.SubTables) - 1
                asubtable.GenerateShapeSQL(llines, lxsllines2, lxmllines, alevel + 1, alast, acontext=acontext)
                if asubtable.RevContextField:
                    llines.append(aindent + ' ) RELATE %s TO _OID )' % asubtable.RevContextField)
                else:
                    llines.append(aindent + ' ) RELATE _OID TO _OIDDictRef )')
#      if acontext is not None and (not self.IsTableView or (self.IsTableView and not self.Query.XSLShowAsTable and not alevel)):
        if acontext is not None and ((not self.IsTableView and not alevel) or (self.IsTableView and not self.Query.XSLShowAsTable and not alevel)):    #$$ Slawek
            lxsllines.append(acontext.XSLMainObjectAtEnd)
        lxsllines.append("""</xsl:template>""")
        lxsllines.extend(lxsllines2)
        if not alevel:
            if acontext is not None and (not self.IsTableView or (self.IsTableView and not self.Query.XSLShowAsTable and not alevel)):
                lxsllines.append(acontext.XSLAtEnd)
            lxsllines.append("""\n</xsl:stylesheet>""")

    def GenerateShapeSQLXML(self, lxmllines, alevel=0, swhere0='', alastsubtable=0, acontext=None):
        if self.SQLTable is None:
            return
        avirtualroot, achapteroid, acgipath = '', -1, ''
        if acontext is not None:
            avirtualroot = acontext.VirtualRoot
            achapteroid = acontext.ThisChapter.OID
            aBaseNameModifier = acontext.CRM.BaseNameModifier
        else:
            aBaseNameModifier = self.NameSQLID.split('_')[0] + '_'
        aindent = '  ' * alevel
        asql = ''
        ssxml = swhere0
        if alevel == 0:
            if acontext:
                if not self.Query.XSLIsTableView:
                    if achapteroid >= 0:
                        if not acontext.ThisChapter['SGShowAllRecords']:
                            if ssxml:
                                ssxml = ssxml + ' AND '
                            ssxml = aindent + ' (%s._ChapterID=%d)' % (self.NameAlias, achapteroid)
                elif achapteroid >= 0:
                    if not acontext.ThisChapter['SGShowAllRecords']:
                        if ssxml:
                            ssxml = ssxml + ' AND '
                        ssxml = aindent + " (%s._ChapterID=%d)" % (self.NameAlias, achapteroid)

                ichapter = acontext.OID
                if hasattr(acontext, 'InfoTablesSufix'):
                    ichapter = acontext.InfoTablesSufix
                if not self.Query.XSLIsTableView:
                    if achapteroid >= 0:
                        if not acontext.ThisChapter['SGShowAllRecords']:
                            asql = aindent + "select (select top 1 chaptername from %sCHAPTERS_%d where ChapterID=%d order by _datetime) as '@title',( " % (acontext.CRM.BaseNameModifier, ichapter, achapteroid)
                elif achapteroid >= 0:
                    if not acontext.ThisChapter['SGShowAllRecords']:
                        asql = aindent + "select (select top 1 chaptername from %sCHAPTERS_%d where ChapterID=%d order by _datetime) as '@title',( " % (acontext.CRM.BaseNameModifier, ichapter, achapteroid)
            if not asql:
                asql = aindent + "select '' as '@title',( "
            sw = ''
            if ssxml:
                sw = ' WHERE ' + ssxml
            asql = asql + aindent + "         select count(*) FROM %s AS T1 %s) as '@rows',( select top %d * from (" % (self.NameSQL, sw, SQL_REPL_TOP2)
            lxmllines.append(asql)
        soxml = ''
        if self.SortedFieldsID:
            lsortedxml = self.SortedFieldsIDXML[:]
            lsortedxml.sort()
            lsortedxml = map(lambda x: x[1], lsortedxml)
            soxml = ' ORDER BY ' + string.join(self.Query.UniqueList(lsortedxml), ', ')
        else:
            soxml = ' ORDER BY %s._OID ' % (self.NameAlias)
        if alevel == 0:
            if self.Query.Top:
                lxmllines.append(aindent + 'SELECT TOP %d ' % (self.Query.Top, ))
            else:
                lxmllines.append(aindent + 'SELECT TOP %d ' % SQL_REPL_TOP1)
        else:
            lxmllines.append(aindent + 'SELECT ')
        llxml = [aindent + "%s._OID as '@OID'" % self.NameAlias, aindent + '%s._OID' % self.NameAlias, aindent + '%s._OIDDictRef' % self.NameAlias]
        if alevel == 0:
            llxml.insert(1, "ROW_NUMBER() OVER(%s) as '@row'" % (soxml, ))
        if acontext:
            llxml.append(aindent + '%s._ChapterID' % self.NameAlias)
        if alevel == 0:
            llxml.extend([aindent + self.GetSQLDateTimeColumnAsString('%s._datetime' % self.NameAlias, '_datetime'), aindent + self.GetSQLUserName(self.NameAlias, aBaseNameModifier)])
            if acontext is not None:
                llxml.extend([aindent + '%s.InformacjaPodmiotUdostepniajacy' % self.NameAlias, self.GetSQLDateTimeColumnAsString(aindent + '%s.InformacjaDataWytworzenia' % self.NameAlias, 'InformacjaDataWytworzenia'), aindent + '%s.InformacjaOsobaOdpowiedzialna' % self.NameAlias, aindent + '%s.InformacjaOpisCzynnosci' % self.NameAlias])

        for afield in self.SQLTable.FieldsByTabID:
            w = 0
            if (self.Query.IsAliased and afield.IsAliased) or not self.Query.IsAliased:
                w = 1
            if (self.Query.IsInteractive and afield.IsInteractive) or not self.Query.IsInteractive:
                w = 1
            if self.Query.NoUnderscore and afield.Name[:1] == '_':
                w = 0
            if self.Query.DisableHiddenDictFields and afield.IsDictViewHidden and self.ParentTable is not None:
                w = 0
            if afield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                w = 0
            if w:
                asqlfield = self.Fields[afield.Name]
                if asqlfield.Type in ['external dict', 'external dict multiple']:    #$$ czy dla multiple tez?
                    llxml.insert(3, " %s.%s " % (asqlfield.Table.NameAlias, asqlfield.Name, ))
                elif alevel and asqlfield.Name.lower() in ['informacjapodmiotudostepniajacy', 'informacjadatawytworzenia', 'informacjaosobaodpowiedzialna', 'informacjaopisczynnosci']:
                    pass
                elif asqlfield.Type in ['date', 'datetime']:
                    llxml.append(' %s ' % self.GetSQLDateTimeColumnAsString('%s.%s' % (asqlfield.Table.NameAlias, asqlfield.Name, ), asqlfield.Name))
                else:
                    llxml.append(' %s.%s ' % (asqlfield.Table.NameAlias, asqlfield.Name, ))


#            if afield.IsSingleViewHidden: #uwaga! koniec petli
#               continue
                if self.IsTableView and self.Query.XSLShowAsTable and not alevel:
                    continue    #uwaga! koniec petli

        if self.SubTables:
            #llines.append(aindent+' APPEND ')
            for i in range(len(self.SubTables)):
                #if i>0:
                #llines.append(aindent+' , ')
                #llines.append(aindent+'( ( ')
                asubtable = self.SubTables[i]
                alast = i == len(self.SubTables) - 1
                lslines = ['(']
                swhere = ''
                if asubtable.LinkFields:
                    srcfield, dstfield, aconstraint = asubtable.LinkFields
                    sls = string.split(srcfield, ',')
                    sld = string.split(dstfield, ',')
                    swhere = aindent + "('0'='0') AND "
                    for i in range(len(sls)):
                        if i > 0:
                            swhere = swhere + 'AND '
                        swhere = swhere + '(%s.%s=%s.%s) ' % (self.NameAlias, sls[i], asubtable.NameAlias, sld[i])
                elif asubtable.RevContextField:
                    swhere = aindent + "('1'='1') AND " + '(%s.%s=%s._OID) ' % (self.NameAlias, asubtable.RevContextField, asubtable.NameAlias)
                else:
                    swhere = aindent + "('2'='2') AND " + '(%s._OID=%s._OIDDictRef) ' % (self.NameAlias, asubtable.NameAlias)
                asubtable.GenerateShapeSQLXML(lslines, alevel + 1, swhere0=swhere, alastsubtable=alast, acontext=acontext)
                lslines.append("for xml path('%s'),type ) as 'sub_%s' " % (asubtable.NameSQLID, asubtable.NameSQLID))
                llxml.append('\n'.join(lslines))

        lxmllines.append(aindent + string.join(llxml, ', '))

        if (alevel == 0) and (acontext is not None):
            afilesorder = acontext.StructVars.get('aFileUploadsOrderInChapters', 'Description,Name')
            lxmllines.append(''',(
    select TOP 50 _OID as '@OID',_OID, InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, %s, InformacjaOpisCzynnosci, _OIDDictRef,_ChapterID,%s,%s,_OIDRef,
    case _action 
        when 'INSERT' then 'nowa pozycja'
        when 'UPDATE' then 'modyfikacja wartości'
        when 'DELETE' then 'usunięcie pozycji'
        else _action
    end as _action
    from %sBZR_V_%d WHERE _OIDRef=T1._OID ORDER BY _datetime DESC
for xml path('VERSION'),type 
) as VERSIONS
,(
    select _OID as '@OID', ROW_NUMBER()  OVER(ORDER BY ItemPosition,%s) as '@fpos',
    case lower(parsename(Name,1)) 
        when 'jpg' then 1
        when 'jpeg' then 1
        when 'gif' then 1
        when 'png' then 1
        else 0
    end as '@isimage',
    coalesce((
      select ipos from (
        select _oid, ROW_NUMBER() OVER (ORDER BY ItemPosition,%s) AS ipos FROM %sFILEUPLOADS_0 WHERE StatusKonwersji='Z' and Status in ('','N','A','G') and RefOID=T1._OID AND ((lower(parsename(Name, 1))='jpg') or (lower(parsename(Name, 1))='jpeg') or (lower(parsename(Name, 1))='gif') or (lower(parsename(Name, 1))='png'))
      ) f2 where _oid=f1._oid
    ),0) as '@ipos',
    _OID, Name, Path, FileSize, %s, Description, InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, %s, RefTable, RefOID, %s, _UID, %s,
    InformacjaOpisCzynnosci, Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, ItemStatus, ItemPosition,
    case
        when FileSize/1048576>0 then cast(convert(decimal (18,2),FileSize/1048576.0) as varchar(20))+' MB'
        else cast(convert(decimal (18,2),FileSize/1024.0) as varchar(20))+' KB'
    end as PrettyFileSize
    from %sFILEUPLOADS_0 f1
    WHERE StatusKonwersji='Z' and Status in ('','N','A','G') and RefOID=T1._OID
    ORDER BY ItemPosition,%s
for xml path('FILE'),type 
) as FILES
''' % (self.GetSQLDateTimeColumnAsString('InformacjaDataWytworzenia', 'InformacjaDataWytworzenia'), self.GetSQLDateTimeColumnAsString('_datetime', '_datetime'), self.GetSQLUserName('%sBZR_V_%d' % (acontext.CRM.BaseNameModifier, self.OID), aBaseNameModifier), acontext.CRM.BaseNameModifier, self.OID, afilesorder, afilesorder, acontext.CRM.BaseNameModifier, self.GetSQLDateTimeColumnAsString(
                'LastModification', 'LastModification'), self.GetSQLDateTimeColumnAsString('InformacjaDataWytworzenia', 'InformacjaDataWytworzenia'), self.GetSQLDateTimeColumnAsString('_datetime', '_datetime'), self.GetSQLUserName('f1', aBaseNameModifier), acontext.CRM.BaseNameModifier, afilesorder))

        if ssxml:
            ssxml = 'WHERE ' + ssxml
        lxmllines.append(aindent + 'FROM %s AS %s %s%s ' % (self.NameSQL, self.NameAlias, ssxml, soxml, ))
        if alevel == 0:
            lxmllines.append(aindent + ") T0 where [@row]>=0 for xml path('%s'), type) for xml path('CHAPTERDATA') " % (self.NameSQLID, ))


class DependencyID:

    def __init__(self, attrs):
        self.XMLAttrs = attrs
        self.FromID = attrs['fromid']
        self.ToID = attrs['toid']


class QueryDependency:

    def __init__(self, aquery, attrs):
        self.XMLAttrs = attrs
        self.Query = aquery
        self.OID = int(attrs['id'])
        self.IDList = []

    def AddDependencyID(self, attrs):
        adependencyid = DependencyID(attrs)
        self.IDList.append(adependencyid)


class AlertLink:

    def __init__(self, aquery, attrs):
        self.XMLAttrs = attrs
        self.Query = aquery
        self.URL = attrs.get('url', '')
        self.OIDAppend = int(attrs.get('oidappend', '0'))
        self.Icon = attrs.get('icon', '')
        self.Text = attrs.get('text', 'kliknij tutaj!')
        self.ID = attrs.get('id', '')


class AlertParam:

    def __init__(self, aquery, attrs):
        self.XMLAttrs = attrs
        self.Query = aquery
        #disablepreview
        #disableedit
        self.Name = attrs.get('name', '')
        self.Value = attrs.get('value', '')

    def AsBool(self):
        return ICORUtil.str2bool(self.Value)

    def AsInt(self):
        if not self.Value:
            return 0
        return int(self.Value)


class QuerySQL:

    def __init__(self, acrm=None, atop=0, aisaliased=1, aisinteractive=1, anounderscore=1, adistinct=0, aencoding='utf-8', isaspstrings=0, asjsontable=0, sqlnoorder=0):
        #      self.CRM=acrm
        self.Top = atop
        self.Distinct = adistinct
        self.IsAliased = aisaliased
        self.IsInteractive = aisinteractive
        self.NoUnderscore = anounderscore
        self.DefaultEncoding = aencoding
        self.Tables = []
        self.ThisTable = None
        self.tablecnt = 0
        self.sql = []
        self.sqllex = []
        self.Status = []
        self.LinkFields = None
        self.FieldsDict = {}
        self.FieldsList = []
        self.TablesList = []
        self.FormElements = []
        self.QueryDependencies = {}
        self.OutputType = ''
        self.PivotRowFields, self.PivotColumnFields, self.PivotDataFields, self.FilterAxisFields = [], [], [], []
        self.LegendCaption, self.SubmitCaption = '', ''
        self.ShowChart, self.PivotShowDetails = '0', '0'
        self.IsPivot = 0
        self.SQLString = ''
        self.URLParams = ''
        self.MarkerGroups = {}
        self.RecurTables = []
        self.DisableHiddenDictFields = 0
        self.MaxFieldSortTabID = 90000
        self.IsCMSPublic = 0
        self.EventPivotDetails = ''
        self.AlertLinks = []
        self.AlertParams = {}
        self.AllowDelete = 0
        self.XMLAttrs = {}
        self.XSLShowAsTable = 1
        self.XSLIsTableView = 1
        self.SQLShapeString = ''
        self.XSLTransformString = ''
        self.SQLXMLString = ''
        self.SQLString = ''
        self.QuasarString = ''
        self.IsASPStrings = isaspstrings
        self.AsJSONTable = asjsontable
        self.SQLNoOrder = sqlnoorder

    def SetTemplateParms(self, attrs):
        self.XMLAttrs = attrs
        self.OutputType = attrs.get('outputtype', '')
        self.PivotCaption = attrs.get('pivotcaption', '')
        self.URLParams = attrs.get('urlparams', '')
        self.ShowChart = attrs.get('showchart', '0')
        self.PivotShowDetails = attrs.get('pivotshowdetails', '0')
        self.ChartCaption = attrs.get('chartcaption', self.PivotCaption)
        self.ChartID = attrs.get('chartid', '3')
        self.PivotSubtotals = attrs.get('pivotsubtotals', '1')
        self.LegendCaption = attrs.get('legendcaption', '')
        self.SubmitCaption = attrs.get('submitcaption', 'Zapamiętaj')
        self.Distinct = int(attrs.get('distinct', '0'))
        self.TableWidth = attrs.get('tablewidth', '')
        self.DetailViewWidth = attrs.get('detailviewwidth', '')
        self.NoDetailView = int(attrs.get('nodetailview', '0'))
        self.IsEditor = int(attrs.get('iseditor', '0'))
        if attrs.has_key('top'):
            self.Top = int(attrs.get('top', '20000'))
        self.ButtonSearchCaption = attrs.get('buttonsearchcaption', 'Szukaj')
        self.ButtonPivotCaption = attrs.get('buttonpivotcaption', 'Pokaż tabelę przestawną')
        self.ButtonSearchDisable = int(attrs.get('buttonsearchdisable', '0'))
        self.ButtonPivotDisable = int(attrs.get('buttonpivotdisable', '0'))
        self.IsCMSPublic = int(attrs.get('iscmspublic', '0'))
        self.CMSAuthorization = int(attrs.get('cmsauthorization', '0'))

    def SetEventPivotDetails(self, adata):
        self.EventPivotDetails = adata

    def AddFormElement(self, attrs, atext=''):
        aelement = FormElement(attrs, atext=atext)
        self.FormElements.append(aelement)
        if aelement.Action == 'RowDelete':
            self.AllowDelete = 1

    def GetFormElement(self, aaction='', asingle=1):
        ret = []
        for aelement in self.FormElements:
            if aelement.Action == aaction:
                if asingle:
                    return aelement
                ret.append(aelement)
        return ret

    def GetFormElements(self):
        ret = []
        for aelement in self.FormElements:
            ret.append(aelement)
        for atable in self.TablesList:
            for aelement in atable.FormElements:
                ret.append(aelement)
            for afield in atable.FieldsList:
                for aelement in afield.FormElements:
                    ret.append(aelement)
        return ret

    def AddQueryDependency(self, attrs):
        adependency = QueryDependency(self, attrs)
        self.QueryDependencies[adependency.OID] = adependency
        self.ThisQueryDependency = adependency

    def AddAlertLink(self, attrs):
        aalertlink = AlertLink(self, attrs)
        self.AlertLinks.append(aalertlink)

    def AddAlertParam(self, attrs):
        aalertparam = AlertParam(self, attrs)
        self.AlertParams[aalertparam.Name] = aalertparam

    def AddDependencyID(self, attrs):
        self.ThisQueryDependency.AddDependencyID(attrs)

    def _CheckIsRecur(self, atable, btablename):
        if atable is None:
            return 0
        if atable.NameSQL == btablename:
            return 1
        return self.CheckIsRecur(atable.ParentTable, btablename)

    def CheckIsRecur(self, atable, btablename):
        for rtable in self.RecurTables:
            if rtable.NameSQL == btablename:
                return 1
        return self._CheckIsRecur(atable, btablename)

    def PushTable(self, attrs, aistableview=0, afieldsaliased=1):
        if type(attrs) == type({}):
            aNameSQL = attrs['namesql']
        else:
            if isinstance(attrs, MSQLLib.SQLField):
                if attrs.DictSourceTable is None or type(attrs.DictSourceTable) == type(1):
                    raise QuerySQLException('$$$ pole słownikowe bez przypisanej tabeli: ' + attrs.NameSQL)
                else:
                    aNameSQL = attrs.DictSourceTable.NameSQL
            elif isinstance(attrs, QuerySQLField):
                if attrs.DictSourceTable is None or type(attrs.DictSourceTable) == type(1):
                    raise QuerySQLException('$$$ pole słownikowe bez przypisanej tabeli: ' + attrs.NameSQL)
                else:
                    aNameSQL = attrs.DictSourceTable.NameSQL
            else:
                aNameSQL = attrs.NameSQL
        if self.CheckIsRecur(self.ThisTable, aNameSQL):
            return None
        self.tablecnt = 1 + self.tablecnt
        atable = QuerySQLTable(self, self.ThisTable, attrs, aistableview, afieldsaliased=afieldsaliased, anamealias='T' + str(self.tablecnt))
        atable.LinkFields = self.LinkFields
        if DEBUG:
            print 'PushTable: %s (%s)' % (atable.NameSQL, str(atable.LinkFields))
        if self.ThisTable is None:
            self.Tables.append(atable)
        else:
            self.ThisTable.AddSubTable(atable)
        self.ThisTable = atable
        self.TablesList.append(atable)
        self.ThisTable.ProcessFieldsByID()
        return self.ThisTable

    def PopTable(self):
        if self.ThisTable is not None:
            self.ThisTable = self.ThisTable.ParentTable
            if DEBUG:
                if self.ThisTable is None:
                    print 'PopTable : None'
                else:
                    print 'PopTable :', self.ThisTable.NameSQL

    def GetUniqueTableName(self, aname):
        w, i = 1, 1
        bname = aname
        while w:
            w = 0
            for atable in self.TablesList:
                if atable.NameSQLID == bname:
                    bname = aname + str(i)
                    w = 1
                    i = i + 1
                    break
        return bname

    def GetUniqueFieldName(self, asqlfield):
        w, i = 1, 0
        bname = asqlfield.Table.NameSQLID + '_' + asqlfield.Name
        while w:
            w = 0
            for afield in self.FieldsList:
                if afield.UniqueName == bname:
                    i = i + 1
                    bname = asqlfield.Table.NameSQLID + '_' + asqlfield.Name + str(i)
                    w = 1
                    break
        return bname

    def RegisterField(self, asqlfield):
        if asqlfield.IsPivotRow:
            self.PivotRowFields.append(asqlfield)
        if asqlfield.IsPivotColumn:
            self.PivotColumnFields.append(asqlfield)
        if asqlfield.IsPivotData:
            self.PivotDataFields.append(asqlfield)
        if asqlfield.IsPivotFilterAxisField:
            self.FilterAxisFields.append(asqlfield)
        self.IsPivot = self.IsPivot or asqlfield.IsPivotRow or asqlfield.IsPivotColumn or asqlfield.IsPivotData
        self.FieldsList.append(asqlfield)
        asqlfield.FieldCnt = len(self.FieldsList)

    def RegisterFieldSelect(self, asqlfield):
        if self.FieldsDict.has_key(asqlfield.NameSQL):
            #         print 'HAS KEY!!!',asqlfield.NameSQL
            return 0
        ti = -1
        for i in range(len(self.FieldsList)):
            if self.FieldsList[i].NameSQL == asqlfield.NameSQL:
                ti = i
                break
        self.FieldsDict[asqlfield.NameSQL] = ti
        return 1

    def UniqueList(self, alist, ashowmessage=1):
        ret = []
        for aitem in alist:
            if aitem in ret:
                if ashowmessage:
                    self.Status.append('Pozycja %s została powtórzona, sprawdź definicję zestawienia' % aitem)
            else:
                ret.append(aitem)
        return ret

    def AsColumnFields(self, amaxcol=5, lcolumns=None, atable=None, arecur=None, aincludesqlaliased=0):
        if arecur is None:
            arecur = []
        if lcolumns is None:
            lcolumns = []
        if atable is None:
            atable = self.ThisTable
        if atable.NameSQL in arecur:
            return lcolumns
        arecur.append(atable.NameSQL)
        for afield in atable.FieldsList:
            if len(lcolumns) >= amaxcol:
                return lcolumns
            w = 0
            if aincludesqlaliased:
                if afield.SQLField is not None:
                    w = afield.SQLField.IsSQLAliased
                else:
                    w = afield.IsSQLAliased
            if afield.SQLField is not None and ((afield.SQLField.IsAliased or w) and afield.SQLField.TypeDescription != 'HTML' and afield.SQLField.TypeDescription != 'Arkusz' and not afield.SQLField.IsDictViewHidden and not afield.SQLField.IsSingleViewHidden):
                if afield.QueryDictTable is None:
                    if afield.Type not in ['external dict', 'external dict multiple']:
                        lcolumns.append(afield)
                else:
                    self.AsColumnFields(amaxcol, lcolumns, afield.QueryDictTable, arecur)
        arecur.pop()
        return lcolumns

    def AsColumnFieldsQuery(self, amaxcol=5, lcolumns=None, atable=None, arecur=None, aincludesqlaliased=0):
        if arecur is None:
            arecur = []
        if lcolumns is None:
            lcolumns = []
        if atable is None:
            atable = self.ThisTable
        if atable.NameSQL in arecur:
            return lcolumns
        arecur.append(atable.NameSQL)
        for afield in atable.FieldsList:
            if len(lcolumns) >= amaxcol:
                return lcolumns
            w = 0
            if aincludesqlaliased:
                w = afield.IsSQLAliased
            if ((afield.IsAliased or w) and afield.TypeDescription != 'HTML' and afield.TypeDescription != 'Arkusz' and not afield.IsDictViewHidden and not afield.IsSingleViewHidden):
                if afield.QueryDictTable is None:
                    if afield.Type not in ['external dict', 'external dict multiple']:
                        lcolumns.append(afield)
                else:
                    self.AsColumnFieldsQuery(amaxcol, lcolumns, afield.QueryDictTable, arecur)
        arecur.pop()
        return lcolumns

    def SQLAppend(self, awhat, atype):
        self.sql.append(awhat)
        self.sqllex.append(atype)

    def Clear(self):
        self.sql = []
        self.sqllex = []
        self.SQLString = ''
        if self.ThisTable is None:
            if self.TablesList:
                self.ThisTable = self.TablesList[0]

    def AsSQL(self, asstoredprocedure=0, aasshape=0, acontext=None, atop=0, adistinct=0, asxmlshape=0, swhere0='', ascountonly=0):
        self.Clear()
        if self.ThisTable is None:
            if self.TablesList:
                self.ThisTable = self.TablesList[0]
        l = []
        amax, aonlychars = 128, 0
        if self.IsPivot:
            amax, aonlychars = 22, 1
        if not aasshape:
            for afield in self.FieldsList:
                if (afield.PivotExcludeColumnMetric or afield.PivotExcludeRowMetric) and afield.Type in ['date', 'datetime']:
                    afield.PrettyName = ICORUtil.GetUniqueStringInContainer(afield.PrettyName + ' ' * 17, l, 17, 1, aonlychars=aonlychars, alower=1)
                elif self.IsPivot:
                    afield.PrettyName = ICORUtil.GetUniqueStringInContainer(afield.PrettyName, l, amax, 1, aonlychars=aonlychars, alower=1)
        lfields, ltables, lconditions, lsorted, lleftjoins, self.LSearchFields, lstoredproceduresrules = [], [], [], [], [], [], []
        if self.AsJSONTable:
            lconditions.append('%d=%d' % (SQL_REPL_WHERE, SQL_REPL_WHERE))
        dleftjoins = {}
        for atable in self.Tables:
            atable.GenerateSQL(lfields, ltables, lconditions, lsorted, dleftjoins, lleftjoins, self.LSearchFields, lstoredproceduresrules)
        if atop:
            if adistinct or self.Distinct:
                self.SQLAppend('SELECT DISTINCT TOP', SP_KEYWORD)
            else:
                self.SQLAppend('SELECT TOP', SP_KEYWORD)
            self.SQLAppend(str(atop), SP_NUMBER)
        elif self.Top:
            if adistinct or self.Distinct:
                self.SQLAppend('SELECT DISTINCT TOP', SP_KEYWORD)
            else:
                self.SQLAppend('SELECT TOP', SP_KEYWORD)
            self.SQLAppend(str(self.Top), SP_NUMBER)
        else:
            if adistinct or self.Distinct:
                self.SQLAppend('SELECT DISTINCT', SP_KEYWORD)
            else:
                self.SQLAppend('SELECT', SP_KEYWORD)
        sqlpart1count_index1 = len(self.sql)
        lfields2 = []
        lfields3 = []
        dfields3 = {}
        i = 0
        for afield in self.FieldsList:
            if not dfields3.has_key(afield.NameSQL):
                dfields3[afield.NameSQL] = 1
                self.FieldsDict[afield.NameSQL] = i
                lfields3.append(afield)
                i = i + 1
                afid = "%s.%s" % (afield.Table.NameSQL, afield.Name)
                if afield.Type in ['date', 'datetime']:
                    afid = afield.Table.GetSQLDateTimeColumnAsString(afid)
                if self.AsJSONTable:
                    lfields2.append("%s AS [%s]" % (afid, afield.UniqueName))
                else:
                    lfields2.append("%s AS [%s]" % (afid, afield.PrettyName))
        self.FieldsList = lfields3
        if ascountonly:
            self.SQLAppend(' count(*) as cnt ', SP_IDENTIFIER)
        else:
            self.SQLAppend(string.join(self.UniqueList(lfields2), ', '), SP_IDENTIFIER)
        sqlpart1count_index2 = len(self.sql)
        self.SQLAppend('FROM', SP_KEYWORD)
        sqlpart1from_index1 = len(self.sql)
        ltables = self.UniqueList(ltables, ashowmessage=0)
        for stable in lleftjoins:
            if stable in ltables:
                ltables.remove(stable)
        self.SQLAppend(string.join(self.UniqueList(ltables), ', '), SP_IDENTIFIER)
        for stable in lleftjoins:
            self.SQLAppend('LEFT JOIN', SP_KEYWORD)
            self.SQLAppend(stable, SP_IDENTIFIER)
            self.SQLAppend('ON', SP_KEYWORD)
            l = self.UniqueList(dleftjoins[stable])
            for i in range(len(l)):
                self.SQLAppend(l[i], SP_IDENTIFIER)
                if i < (len(l) - 1):
                    self.SQLAppend('AND', SP_KEYWORD)


#               self.SQLAppend('OR',SP_KEYWORD)
        sqlpart1 = self.sql[:]
        sqlpart1count = self.sql[:sqlpart1count_index1] + ['Count(*)', ] + self.sql[sqlpart1count_index2:]
        sqlpart1index = len(self.sql)
        wwhere = 0
        abeforewhere = len(self.sql)
        sqlpart1from = self.sql[sqlpart1from_index1:abeforewhere]
        if lconditions:
            self.SQLAppend('WHERE', SP_KEYWORD)
            wwhere = 1
            l = self.UniqueList(lconditions)
            for i in range(len(l)):
                self.SQLAppend(l[i], SP_IDENTIFIER)
                if i < (len(l) - 1):
                    self.SQLAppend('AND', SP_KEYWORD)
        elif self.LSearchFields:
            pass
        lstoredproceduresrules = self.UniqueList(lstoredproceduresrules)
        for atable in self.Tables:
            if atable.IsASPSQLConstraint:
                if not wwhere:
                    self.SQLAppend('WHERE', SP_KEYWORD)
                    wwhere = 1
                self.SQLAppend(' " & extrule_%s_%s & " ' % (atable.ASPSQLConstraintPrefix, atable.NameSQLID), SP_IDENTIFIER)
        abeforeorder = len(self.sql)
        worder = 0
        if lsorted and not ascountonly and not self.SQLNoOrder:
            lsorted.sort()
            lsorted = map(lambda x: x[1], lsorted)
            self.SQLAppend('ORDER BY', SP_KEYWORD)
            self.SQLAppend('/*ORDERSTART*/', SP_IDENTIFIER)
            self.SQLAppend(string.join(self.UniqueList(lsorted), ', '), SP_IDENTIFIER)
            self.SQLAppend('/*ORDEREND*/', SP_IDENTIFIER)
            worder = 1
        astatus = ''
        if 0:
            if self.Status:
                for aline in self.Status:
                    astatus = astatus + '\n-- ' + aline
                    self.SQLAppend('-- ' + aline, SP_COMMENT)
        sqlpart2 = self.sql[sqlpart1index:]
        self.SQLString = string.replace(string.join(self.sql, ' '), '\n', ' ')
        self.SQLStringPart1 = string.replace(string.join(sqlpart1, ' '), '\n', ' ')
        self.SQLStringPart1Count = string.replace(string.join(sqlpart1count, ' '), '\n', ' ')
        self.SQLStringPart2 = string.replace(string.join(sqlpart2, ' '), '\n', ' ')
        self.SQLStringFrom = string.replace(string.join(sqlpart1from, ' '), '\n', ' ')

        self.SQLString_SelectJoin = string.replace(string.join(self.sql[:abeforewhere], ' '), '\n', ' ')
        self.SQLString_Where, self.SQLString_Order = '', ''
        if wwhere:
            self.SQLString_Where = string.replace(string.join(self.sql[abeforewhere + 1:abeforeorder], ' '), '\n', ' ')
        self.SQLString_StoredProcedureWhere = string.join(lstoredproceduresrules, ' AND ')
        if worder and not ascountonly:
            self.SQLString_Order = string.replace(string.join(self.sql[abeforeorder + 1:], ' '), '\n', ' ')

        self.SQLShapeString = ''
        if asxmlshape:
            llines = []
            self.ThisTable.GenerateShapeSQLXML(llines, swhere0=swhere0, acontext=acontext)
            self.SQLXMLString = string.join(llines, '\n')
        elif aasshape:
            llines, lxsllines, lxmllines = [], [], []
            self.ThisTable.GenerateShapeSQL(llines, lxsllines, lxmllines, acontext=acontext)
            self.SQLShapeString = string.join(llines, '\n')
            self.XSLTransformString = string.join(lxsllines, '\n')
            lxmllines = []
            self.ThisTable.GenerateShapeSQLXML(lxmllines, swhere0=swhere0, acontext=acontext)
            self.SQLXMLString = string.join(lxmllines, '\n')
        return self.SQLString + astatus

    def AsHTML(self, file=None):
        ret = ['<pre>']
        for i in range(len(self.sqllex)):
            ali = self.sqllex[i]
            if ali == SP_KEYWORD:
                ret.append('<font color="NAVY"><b>')
                ret.append(self.sql[i])
                ret.append('</b></font>\n')
            elif ali == SP_NUMBER:
                ret.append('<font color="RED">')
                ret.append(self.sql[i])
                ret.append('</font>\n')
            elif ali == SP_IDENTIFIER:
                ret.append('<font color="BLACK">')
                ret.append(self.sql[i])
                ret.append('</font>\n')
            elif ali == SP_COMMENT:
                ret.append('<font color="NAVY" style="background=YELLOW;"><i>')
                ret.append(self.sql[i])
                ret.append('</i></font>\n')
        ret.append('</pre>')
        s = string.join(ret, '')
        if file:
            file.write(s)
        return s

    def AsASP(self, file=None):
        ret = ['response.write "<pre>"\n']
        for i in range(len(self.sqllex)):
            ali = self.sqllex[i]
            if ali == SP_KEYWORD:
                ret.append('response.write "<font color=""NAVY""><b>"\n')
                ret.append('response.write "' + string.replace(self.sql[i], '"', '""') + '"\n')    #"
                ret.append('response.write "</b></font>" & vbcrlf\n')
            elif ali == SP_NUMBER:
                ret.append('response.write "<font color=""RED"">"\n')
                ret.append('response.write "' + string.replace(self.sql[i], '"', '""') + '"\n')    #"
                ret.append('response.write "</font>" & vbcrlf\n')
            elif ali == SP_IDENTIFIER:
                ret.append('response.write "<font color=""BLACK"">"\n')
                ret.append('response.write "' + string.replace(self.sql[i], '"', '""') + '"\n')    #"
                ret.append('response.write "</font>" & vbcrlf\n')
            elif ali == SP_COMMENT:
                ret.append('response.write "<font color=""NAVY"" style=""background=YELLOW;""><i>"\n')
                ret.append('response.write "' + string.replace(self.sql[i], '"', '""') + '"\n')    #"
                ret.append('response.write "</i></font>" & vbcrlf\n')
        ret.append('response.write "</pre>"\n')
        s = string.join(ret, '')
        if file:
            file.write(s)
        return s

    def ProcessHTMLTree(self, arootnode):
        if self.TablesList:
            self.TablesList[0].ProcessHTMLTree(arootnode)

    def Dump(self, file=None):
        for asql in self.sql:
            if file:
                file.write(asql + '\n')
            else:
                print asql

    def DumpShapeSQL(self):
        l = self.SQLShapeString.split('\n')
        for s in l:
            print s
        print
        l = self.SQLXMLString.split('\n')
        for s in l:
            print s


def GetCRMByDocument(aclass, aproject):
    poid = aclass.Nazwa.Identifiers(aproject)
    if poid < 0:
        return
    pobj = aclass[poid]
    import icorlib.projekt.mcrmbase as mcrmbase
    acrm = mcrmbase.MCRM(pobj.Nazwa, acreatetables=0, abasenamemodifier=pobj.BaseNameModifier)
    adir = FilePathAsSystemPath(aICORWWWServerInterface.AppPath) + pobj.AppPath
    acrm.PreProcess(pobj, adir)
    return acrm


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    acrm = GetCRMByDocument(aclass, 'PEBR')
    if 0:
        querysql = QuerySQL(atop=1000)

        atable = acrm.sourcetables[200008]
        aq1table = querysql.PushTable(atable.SQLTable)
        asql = querysql.AsSQL(aasshape=1)
        #print '*** SQL Dump ***'
        #querysql.Dump()
        querysql.DumpShapeSQL()
        #print querysql.SQLShapeString
    if 0:
        import icorlib.projekt.mcrmwwwmenulib as MCRMWWWMenuLib

        class C1(object):
            pass

        c = C1()
        c.NameSQL = '_name_sql'
        rclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
        sclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
        #robj=rclass[201199]
        robj = rclass[201220]
        sobj = sclass[201000]
        aWWWMenuStruct = MCRMWWWMenuLib.WWWMenuStruct(acrm)
        aWWWMenuStruct.Process(sobj)
        aWWWMenuStruct.TemplateXML = {}
        aWWWMenuStruct.ThisChapter = robj
        #aWWWMenuStruct.Table_MenuChapters=c
        aquery = aWWWMenuStruct.GetChapterQuery(robj)
        print query.SQLShapeString
    return
