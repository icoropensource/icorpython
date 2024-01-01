# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_DBBase_Util_CSVImport
import icorlib.projekt.sqlrun as SQLRun
import cStringIO
import string
import re
import types


def GetCSVDictValues(adictvalues):
    aMaxDictValueLen = 0
    aDictValues = []
    aDictValuesParents = {}
    afile = cStringIO.StringIO()
    try:
        afile.write(adictvalues)
        afile.seek(0)
        acsv = CLASSES_Library_DBBase_Util_CSVImport.CSVImport(ahasheader=0, adelimiter=',', atextQualifier='"', astripdata=1)
        acsv.Open(afile)
        try:
            while not acsv.EOF:
                if len(acsv.Record) in [2, 3]:
                    sk = XMLUtil.GetAsXMLStringNoPL(string.strip(acsv.Record[0]))
                    sv = XMLUtil.GetAsXMLStringNoPL(string.strip(acsv.Record[1]))
                    aMaxDictValueLen = max(len(sv), aMaxDictValueLen)
                    aDictValues.append([sk, sv])
                if len(acsv.Record) == 3:
                    sp = XMLUtil.GetAsXMLStringNoPL(string.strip(acsv.Record[2]))
                    spl = string.split(sp, '|')
                    aDictValuesParents[sk] = spl
                acsv.Next()
        finally:
            acsv.Close()
    finally:
        afile.close()
    return aMaxDictValueLen, aDictValues, aDictValuesParents


def ReplaceSQLQuotes(s):
    l = re.findall("\'+", s)
    for s1 in l:
        if len(s1) & 1:
            return s.replace("'", "''")
    return s


class SQLField:

    def __init__(self, atable, aname, atype='', asize='', aqualifiers='', aprettyname='', aisaliased=0, aissearch=0, adictvalues='', atabposition=-1, aisobligatory=0, afilter='', alowercase=0, amask='', anospace=0, aregex='', aunsigned=0, auppercase=0, adescription='', anopastdate=0, aisindexed=0, aisinteractive=1, adictsourcetable=-1, aminvalue='', amaxvalue='', aissorted=0, aisunique=0, atypecaption='', atypedescription='', atextcols=0, atextrows=0, atextnowrap=0,
                 aextdictconstraint='', asortstyle=0, asearchtabid=-1, aissingleviewhidden=0, aisdictviewhidden=0, aisversioncontrol=0, afieldvalues='', afieldnamedescription='', afieldvaluedescription='', afieldvaluedescription2='', afieldvaluepreviewlink='', aisu2ulink=0, adefaultvalue='', adefaultentry='', adisabledictshowallvalues=0, agroup='', acolorselectedvalue='', acolorbackground='', amodelxmldataidview=0, amodelxmldataidedit=0):
        self.CID = -1
        self.OID = -1
        self.Table = atable
        self.Name = aname
        self.NameSQL = self.Table.NameSQL + '.' + self.Name
        self.Type = atype
        self.Size = asize
        try:
            self.SizeAsNumber = int(asize)
        except:
            self.SizeAsNumber = 0
        self.Qualifiers = aqualifiers
        self.IsInteractive = aisinteractive
        self.IsAliased = aisaliased
        self.IsSearch = aissearch
        self.IsObligatory = aisobligatory
        self.IsSingleViewHidden = aissingleviewhidden
        self.IsDictViewHidden = aisdictviewhidden
        self.IsIndexed = aisindexed
        self.SortStyle = 0
        self.IsSorted = aissorted
        self.IsVersionControl = aisversioncontrol
        #      if self.IsSorted:
        #         print 'issorted==1, Field:',self.NameSQL
        if aissorted:
            self.SortStyle = 1
        if asortstyle:
            self.SortStyle = asortstyle
            self.IsSorted = 1
        if self.Type in ['external dict', 'external dict multiple']:
            self.IsSorted = 0
            self.SortStyle = 0
        self.IsUnique = aisunique
        self.Filter = afilter
        self.Lowercase = alowercase
        self.Mask = amask
        self.NoSpace = anospace
        self.Regex = aregex
        self.Unsigned = aunsigned
        self.Uppercase = auppercase
        self.Description = adescription
        self.DescriptionName = string.replace(afieldnamedescription, '"', '""')
        self.DescriptionValue = string.replace(afieldvaluedescription, '"', '""')
        self.DescriptionValue2 = string.replace(afieldvaluedescription2, '"', '""')
        self.NoPastDate = anopastdate
        self.MinValue = aminvalue
        self.MaxValue = amaxvalue
        if atextcols <= 0:
            self.TextCols = 32
        else:
            self.TextCols = atextcols
        if atextrows <= 0:
            self.TextRows = 6
        else:
            self.TextRows = atextrows
        if atextnowrap:
            self.TextNoWrap = 'On'
        else:
            self.TextNoWrap = 'Off'
        if atabposition < 0:
            self.TabPosition = 99999
        else:
            self.TabPosition = atabposition
        if asearchtabid < 0:
            self.SearchTabID = 99999
        else:
            self.SearchTabID = asearchtabid
        if not aprettyname:
            aprettyname = aname
        self.ExtDictConstraint = aextdictconstraint
        self.PrettyName = aprettyname
        self.PrettyNameDisplayed = ICORUtil.GetProperCaption(aprettyname, amaxcaptionlen=48)
        self.UniqueName = self.Name    #self.Table.NameSQL+'_'+
        self.TypeCaption = atypecaption
        self.TypeDescription = atypedescription
        self.MaxDictValueLen = 0
        self.IsU2ULink = aisu2ulink
        self.DictValues = []
        self.DictValuesParents = {}
        self._DictSourceTable = adictsourcetable
        if adictvalues:
            self.MaxDictValueLen, self.DictValues, self.DictValuesParents = GetCSVDictValues(adictvalues)


#         def mycompare(l1,l2):
#            return ICORUtil.ICORCompareText(l1[0],l2[0])
#         self.DictValues.sort(mycompare)
        self.FieldValues = []
        if type(afieldvalues) == type([]):
            self.FieldValues = afieldvalues
        elif afieldvalues:
            self.FieldValues = string.split(afieldvalues, '\n')
        if self.FieldValues:
            i = 0
            for avalue in self.FieldValues:
                self.Table.RegisterFieldValue(i, self.Name, avalue)
                i = i + 1
        self.FieldValuePreviewLink = afieldvaluepreviewlink
        self.DefaultValue = adefaultvalue
        self.DefaultEntry = adefaultentry
        self.DisableDictShowAllValues = adisabledictshowallvalues
        self.FieldInputTemplate = ''
        self.Group = agroup
        self.ColorSelectedValue = acolorselectedvalue
        self.ColorBackground = acolorbackground
        self.ModelXMLDataIDView = amodelxmldataidview
        self.ModelXMLDataIDEdit = amodelxmldataidedit

    def __repr__(self):
        return self.Name

    def __str__(self):
        return self.Name

    def __getattr__(self, name):
        if name == 'DictSourceTable':
            if type(self._DictSourceTable) == type(1) and self._DictSourceTable >= 0:
                self._DictSourceTable = self.Table.Creator.GetExternalTable(self._DictSourceTable)
            return self._DictSourceTable
        elif name == 'TypeID':
            return self.GetTypeIDByTypeName(self.Type)
        elif name == 'IsContainer':
            return self.Type in ['text', ]

    def GetTypeIDByTypeName(self, atypename):
        if atypename == 'string':
            return mt_String
        elif atypename == 'numeric':
            return mt_Double
        elif atypename == 'date':
            return mt_DateTime
        elif atypename == 'datetime':
            return mt_DateTime
        elif atypename == 'bool':
            return mt_Boolean
        elif atypename == 'dict':
            return mt_String
        elif atypename == 'dict int':
            return mt_Integer
        elif atypename in ['external dict', 'external dict multiple']:
            return mt_String
        elif atypename == 'text':
            return mt_String
        elif atypename == 'integer':
            return mt_Integer
        elif atypename in ['money', 'float']:
            return mt_Double

    def GetSQLCreateIfNotExists(self):
        aftype, afdefault = GetFieldCreateParms(self.Type, self.TypeDescription, self.Size, self.DefaultValue, self.Table.IsVersionControl, adblquote=1)
        ret = """
BEGIN TRANSACTION
DECLARE @SQL nvarchar(2000)
DECLARE @TableName nVarchar(200)
DECLARE @ColName nVarchar(200)
DECLARE @ColNameNew nVarChar(200)
DECLARE @ColTypeNew nVarChar(200)
DECLARE @ColDefaultNew nVarChar(200)

SELECT @TableName='%s'
SELECT @ColName='%s'
SELECT @ColNameNew=@ColName
SELECT @ColTypeNew='%s'
SELECT @ColDefaultNew='%s'

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @TableName AND COLUMN_NAME = @ColName)
BEGIN
   -- utworzenie kolumny
   IF @ColNameNew<>'' BEGIN
      IF @ColDefaultNew<>'' BEGIN
        SELECT @SQL = 'Alter table ' + @TableName + ' ADD ' + @ColNameNew + ' '+ @ColTypeNew + + ' NOT NULL DEFAULT ' + @ColDefaultNew
      END ELSE BEGIN
        SELECT @SQL = 'Alter table ' + @TableName + ' ADD ' + @ColNameNew + ' '+ @ColTypeNew + + ' NOT NULL'
      END
      EXEC(@SQL)
   END

   -- utworzenie nowego indeku dla kolumny
   IF EXISTS (SELECT name FROM sysindexes WHERE name = 'id_'+@TableName+'_'+@ColNameNew) BEGIN
      SELECT @SQL = 'DROP INDEX ' + @TableName + '.id_'+@TableName+'_'+@ColNameNew
      EXEC(@SQL)
   END
   SELECT @SQL = 'CREATE INDEX id_'+@TableName+'_'+@ColNameNew+' ON '+@TableName+' ('+@ColNameNew+')'
   EXEC(@SQL)

END

COMMIT
""" % (self.Table.NameSQL, self.Name, aftype, afdefault)
        return ret

    def DumpAsXML(self, file, arecur, aindent=0, aaddobligatoryfields=0):
        if arecur.has_key(self.Table.NameSQL + '_' + self.Name):
            return
        arecur[self.Table.NameSQL + '_' + self.Name] = 1
        s = '%s<SQLFIELD prettyname="%s" ' % (' ' * aindent, self.PrettyName)
        s = s + 'name="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.Name)
        s = s + 'type="%s" ' % self.Type
        s = s + 'typedescription="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.TypeDescription)
        s = s + 'size="%s" ' % self.Size
        s = s + 'issqlaliased="0" '
        s = s + 'isinteractive="%d" ' % self.IsInteractive
        s = s + 'isaliased="%d" ' % self.IsAliased
        s = s + 'issearch="%d" ' % self.IsSearch
        s = s + 'isobligatory="%d" ' % self.IsObligatory
        s = s + 'isindexed="%d" ' % self.IsIndexed
        s = s + 'sortstyle="%d" ' % self.SortStyle
        s = s + 'filter="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.Filter)
        s = s + 'regex="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.Regex)
        s = s + 'searchtabid="%d" ' % self.SearchTabID
        s = s + 'extdictconstraint="%s" ' % XMLUtil.GetAsXMLStringNoPL(string.strip(self.ExtDictConstraint))
        s = s + 'minvalue="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.MinValue)
        s = s + 'maxvalue="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.MaxValue)
        s = s + 'unsigned="%d" ' % self.Unsigned
        s = s + 'issingleviewhidden="%d" ' % self.IsSingleViewHidden
        s = s + 'isdictviewhidden="%d" ' % self.IsDictViewHidden
        s = s + 'typecaption="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.TypeCaption)
        s = s + 'fieldvaluepreviewlink="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.FieldValuePreviewLink)
        s = s + 'defaultentry="%s" ' % XMLUtil.GetAsXMLStringNoPL(self.DefaultEntry)
        s = s + 'isunique="%d" ' % self.IsUnique
        s = s + 'disabledictshowallvalues="%d" ' % self.DisableDictShowAllValues
        s = s + 'group="%s" ' % self.Group
        s = s + 'colorselectedvalue="%s" ' % self.ColorSelectedValue
        s = s + 'colorbackground="%s" ' % self.ColorBackground
        s = s + 'textnowrap="%s" ' % self.TextNoWrap
        s = s + 'isu2ulink="%d" ' % self.IsU2ULink
        s = s + 'isclientstored="0" '
        s = s + 'modelxmldataidview="%d" ' % self.ModelXMLDataIDView
        s = s + 'modelxmldataidedit="%d" ' % self.ModelXMLDataIDEdit
        s = s + ' >\n'
        file.write(s)
        if self.DictValues:
            for sk, sv in self.DictValues:
                lp = self.DictValuesParents.get(sk, None)
                sp = ''
                if lp is not None:
                    sp = ' parents="' + XMLUtil.GetAsXMLStringNoPL(string.join(lp, '|')) + '" '
                file.write('%s<DICTVALUE key="%s" value="%s"%s/>\n' % ('   ' + ' ' * aindent, XMLUtil.GetAsXMLStringNoPL(sk), XMLUtil.GetAsXMLStringNoPL(sv), sp))
        if self.Type in ['external dict', 'external dict multiple'] and (self.IsObligatory or aaddobligatoryfields):
            self.DictSourceTable.DumpAsXML(file, arecur, aindent=aindent + 3)
        file.write('%s</SQLFIELD>\n' % (' ' * aindent, ))
        del arecur[self.Table.NameSQL + '_' + self.Name]


class SQLStoredProcedure:

    def __init__(self, atable, aname, atext=''):
        self.Table = atable
        self.Name = aname
        self.Text = atext
        self.TextDrop = """
if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[%s]'))
drop procedure [dbo].[%s]
""" % (self.Name, self.Name)


def GetFieldCreateParms(afieldType, afieldTypeDescription, afieldSize, afieldDefault, aIsVersionControl, adblquote=0, asqlversion=2008):
    if not adblquote and afieldType in ['string', 'dict', 'external dict', 'external dict multiple', 'text']:
        afieldDefault = string.replace(afieldDefault, "'", "''")
    retType, retDefault = None, None
    if afieldType == 'string':
        if aIsVersionControl:
            retType = 'varchar(%s)' % afieldSize
            retDefault = '(\'%s\')' % afieldDefault
        else:
            if afieldTypeDescription == 'Auto PIN':
                retType = 'varchar(%s)' % afieldSize
                retDefault = '''(left(cast(FLOOR(RAND()*10+1) as varchar(2)),1)+RIGHT('000'+CAST(FLOOR(RAND()*1e3) as varchar(3)),3))'''
            elif afieldTypeDescription == 'GUID':
                retType = 'varchar(%s)' % afieldSize
                retDefault = 'REPLACE(CONVERT(varchar(44),newid()),\'-\',\'\')'
            else:
                retType = 'varchar(%s)' % afieldSize
                retDefault = '(\'%s\')' % afieldDefault
    elif afieldType == 'numeric':
        if not afieldDefault:
            afieldDefault = "0.0"
        retType = 'numeric(%s)' % afieldSize
        retDefault = '%s' % afieldDefault
    elif afieldType == 'date':
        if not afieldDefault:
            afieldDefault = "getdate()"
        retType = 'datetime'
        retDefault = '%s' % afieldDefault
    elif afieldType == 'datetime':
        if not afieldDefault:
            afieldDefault = "getdate()"
        retType = 'datetime'
        retDefault = '%s' % afieldDefault
    elif afieldType == 'bool':
        if not afieldDefault:
            afieldDefault = "0"
        retType = 'bit'
        retDefault = '%s' % afieldDefault
    elif afieldType == 'dict':
        retType = 'varchar(%s)' % afieldSize
        retDefault = '(\'%s\')' % afieldDefault
    elif afieldType == 'dict int':
        if not afieldDefault:
            afieldDefault = "0"
        retType = 'int'
        retDefault = '%s' % afieldDefault
    elif afieldType in ['external dict', 'external dict multiple']:
        retType = 'varchar(%s)' % afieldSize
        retDefault = '(\'%s\')' % afieldDefault
    elif afieldType == 'text':
        if asqlversion < 2008:
            retType = 'text'
        else:
            retType = 'varchar(max)'
        retDefault = '(\'%s\')' % afieldDefault
    elif afieldType == 'integer':
        if not afieldDefault:
            afieldDefault = "0"
        if aIsVersionControl:
            retType = 'int'
            retDefault = '%s' % afieldDefault
        else:
            if afieldTypeDescription == 'Auto increment':
                retType = 'int IDENTITY (1000, 1)'
                retDefault = ''
            else:
                retType = 'int'
                retDefault = '%s' % afieldDefault
    elif afieldType == 'money':
        if not afieldDefault:
            afieldDefault = "0"
        retType = 'money'
        retDefault = '%s' % afieldDefault
    elif afieldType == 'float':
        if not afieldDefault:
            afieldDefault = "0.0"
        retType = 'float'
        retDefault = '%s' % afieldDefault
    else:
        pass
    if adblquote:
        retDefault = string.replace(retDefault, "'", "''")
    return retType, retDefault


class SQLTable:

    def __init__(self, acreator, aname, aid, atablecaption='', aisexternal=0, asingleobjectname='', atop=0, ahasversions=0, aisversioncontrol=0, aissecurityenabled=0, atablegroup='', adbname='', adbowner='', agenerateenable=0, anoprefix=1):
        self.Creator = acreator
        self.Name = aname
        self.ID = aid
        self.OID = aid
        self.DataBaseName = adbname
        self.DataBaseOwner = adbowner
        self.GenerateEnable = agenerateenable
        self.TablePrefix = ''
        if self.DataBaseName and not anoprefix:
            self.TablePrefix = self.DataBaseName + '.' + self.DataBaseOwner + '.'
        self.Fields = []
        self.StoredProcedures = {}
        self._FieldsByTabID, self._DefaultSQLQuery = None, None
        self.NameSQLID = self.Name + '_' + str(self.ID)
        self.NameSQL = self.TablePrefix + self.NameSQLID
        self.TableCaption = atablecaption
        if asingleobjectname:
            self.SingleObjectName = asingleobjectname
        else:
            self.SingleObjectName = 'Dotyczy'
        self.NameFile = string.replace(self.NameSQLID, self.Creator.BaseNameModifier, '')
        self.NameFileSubmit = self.NameFile
        self.IsExternal = aisexternal
        self.HasVersions = ahasversions
        self.IsVersionControl = aisversioncontrol
        self.IsSecurityEnabled = aissecurityenabled
        self.Values = []
        self.RegisteredFieldValues = {}
        self.Top = atop
        self.VersionTable = None
        self.TableGroup = atablegroup
        self.RevContextField = None
        self.IsSQLView = 0

    def __repr__(self):
        return self.NameSQL

    def __str__(self):
        return self.NameSQL

    def __getattr__(self, name):
        if name == 'FieldsByTabID':
            if self._FieldsByTabID is None:
                l = []
                #            print 'tabela:',self.NameSQL
                for afield in self.Fields:
                    #               print afield.TabPosition,afield.Name
                    l.append([afield.TabPosition, afield.Name, afield])
                l.sort()
                self._FieldsByTabID = []
                for atabid, aname, afield in l:
                    self._FieldsByTabID.append(afield)
            return self._FieldsByTabID
        elif name == 'DefaultSQLQuery':
            if self._DefaultSQLQuery is None:
                import icorlib.projekt.msqlquery as MSQLQuery
                self._DefaultSQLQuery = MSQLQuery.QuerySQL(atop=self.Top)
                self._DefaultSQLQuery.PushTable(self)
            return self._DefaultSQLQuery

    def FieldsByName(self, aname):
        for afield in self.Fields:
            if afield.Name == aname:
                return afield
        return None

    def AddField(self, aname, atype, asize='', aqualifiers='', aprettyname='', aisaliased=0, aissearch=0, adictvalues='', atabposition=-1, aisobligatory=0, afilter='', alowercase=0, amask='', anospace=0, aregex='', aunsigned=0, auppercase=0, adescription='', anopastdate=0, aisindexed=0, aisinteractive=1, adictsourcetable=-1, aminvalue='', amaxvalue='', aissorted=0, aisunique=0, atypecaption='', atypedescription='', atextcols=0, atextrows=0, atextnowrap=0,
                 aextdictconstraint='', asortstyle=0, asearchtabid=-1, aissingleviewhidden=0, aisdictviewhidden=0, aisversioncontrol=0, afieldvalues='', afieldnamedescription='', afieldvaluedescription='', afieldvaluedescription2='', afieldvaluepreviewlink='', aisu2ulink=0, adefaultvalue='', adefaultentry='', adisabledictshowallvalues=0, agroup='', acolorselectedvalue='', acolorbackground='', amodelxmldataidview=0, amodelxmldataidedit=0):
        self._FieldsByTabID = None
        afield = SQLField(self, aname, atype, asize, aqualifiers, aprettyname, aisaliased, aissearch, adictvalues, atabposition, aisobligatory=aisobligatory, afilter=afilter, alowercase=alowercase, amask=amask, anospace=anospace, aregex=aregex, aunsigned=aunsigned, auppercase=auppercase, adescription=adescription, anopastdate=anopastdate, aisindexed=aisindexed, aisinteractive=aisinteractive, adictsourcetable=adictsourcetable, aminvalue=aminvalue, amaxvalue=amaxvalue,
                          aissorted=aissorted, aisunique=aisunique, atypecaption=atypecaption, atypedescription=atypedescription, atextcols=atextcols, atextrows=atextrows, atextnowrap=atextnowrap, aextdictconstraint=aextdictconstraint, asortstyle=asortstyle, asearchtabid=asearchtabid, aissingleviewhidden=aissingleviewhidden, aisdictviewhidden=aisdictviewhidden, aisversioncontrol=aisversioncontrol, afieldvalues=afieldvalues, afieldnamedescription=afieldnamedescription,
                          afieldvaluedescription=afieldvaluedescription, afieldvaluedescription2=afieldvaluedescription2, afieldvaluepreviewlink=afieldvaluepreviewlink, aisu2ulink=aisu2ulink, adefaultvalue=adefaultvalue, adefaultentry=adefaultentry, adisabledictshowallvalues=adisabledictshowallvalues, agroup=agroup, acolorselectedvalue=acolorselectedvalue, acolorbackground=acolorbackground, amodelxmldataidview=amodelxmldataidview, amodelxmldataidedit=amodelxmldataidedit)
        self.Fields.append(afield)
        if atypedescription == 'Arkusz':
            bfield = SQLField(self, aname + '_Src', atype, asize, aqualifiers, aprettyname='', aisaliased=0, aissearch=0, adictvalues='', atabposition=99999, aisobligatory=0, afilter='', alowercase=0, amask='', anospace=0, aregex='', aunsigned=0, auppercase=0, adescription='', anopastdate=0, aisindexed=0, aisinteractive=0, adictsourcetable=-1, aminvalue='', amaxvalue='', aissorted=0, aisunique=0, atypecaption='', atypedescription='Opis', atextcols=0, atextrows=0,
                              atextnowrap=0, aextdictconstraint='', asortstyle=0, asearchtabid=-1, aissingleviewhidden=1, aisdictviewhidden=1, aisversioncontrol=0, afieldvalues=afieldvalues, afieldnamedescription=afieldnamedescription, afieldvaluedescription=afieldvaluedescription, afieldvaluedescription2=afieldvaluedescription2, afieldvaluepreviewlink=afieldvaluepreviewlink, aisu2ulink=0, adefaultvalue='', adefaultentry='', adisabledictshowallvalues=0)
            self.Fields.append(bfield)
        return afield

    def AddStoredProcedure(self, aname, atext='', aquery=None):
        if 1:
            if aquery is None:
                aNameSQLID = self.NameSQLID
                aNameSQL = self.NameSQL
            else:
                aNameSQLID = aquery.Tables[0].NameSQLID
                aNameSQL = aquery.Tables[0].NameSQL
        if 0:
            aNameSQLID = self.NameSQLID
            aNameSQL = self.NameSQL
        aname = 'sp_' + aNameSQLID + '_' + aname
        asp = SQLStoredProcedure(self, aname, atext)
        self.StoredProcedures[aname] = asp
        return asp

    def GetStoredProcedure(self, aname, aquery=None):
        if aquery is None:
            aNameSQLID = self.NameSQLID
            aNameSQL = self.NameSQL
        else:
            aNameSQLID = aquery.Tables[0].NameSQLID
            aNameSQL = aquery.Tables[0].NameSQL
        if self.StoredProcedures.has_key(aname):
            return self.StoredProcedures[aname]
        bname = 'sp_' + aNameSQLID + '_' + aname
        if self.StoredProcedures.has_key(bname):
            return self.StoredProcedures[bname]
        return self.AddStoredProcedure(aname, aquery=aquery)

    def AddValues(self, avalues):
        self.Values.append(avalues)

    def RegisterFieldValue(self, aid, afieldname, avalue):
        d = self.RegisteredFieldValues.get(aid, {})
        d[afieldname] = avalue
        self.RegisteredFieldValues[aid] = d

    def GetDropSQL(self):
        return "IF EXISTS (SELECT * FROM sysobjects WHERE id = OBJECT_ID('%s'))\n  DROP TABLE %s;\n\n" % (self.NameSQL, self.NameSQL)

    def GetTruncateSQL(self):
        return "IF EXISTS (SELECT * FROM sysobjects WHERE id = OBJECT_ID('%s'))\n  TRUNCATE TABLE %s;\n\n" % (self.NameSQL, self.NameSQL)

    def GetCreateTableSQLIfNotExists(self, ainsertvaluesonly=0):
        ret = "IF NOT EXISTS (SELECT * FROM sysobjects WHERE id = OBJECT_ID('%s')) BEGIN\n\n" % (self.NameSQL, )
        ret = ret + self.GetCreateTableSQL(ainsertvaluesonly)
        ret = ret + '\n\nEND\n\n'
        return ret

    def GetCreateTableSQL(self, ainsertvaluesonly=0, acreateifnotexists=0):
        ssql = ''
        if acreateifnotexists:
            ssql = ssql + "IF NOT EXISTS (SELECT * FROM sysobjects WHERE id = OBJECT_ID('%s')) BEGIN\n\n" % (self.NameSQL, )
        ssql = ssql + """CREATE TABLE %s ( \n""" % (self.NameSQL)
        ssql = ssql + '  _OID varchar(44) NOT NULL PRIMARY KEY CLUSTERED DEFAULT REPLACE(CONVERT(varchar(44),newid()),\'-\',\'\'),\n'
        lsf = []
        for afield in self.Fields:
            aftype, afdefault = GetFieldCreateParms(afield.Type, afield.TypeDescription, afield.Size, afield.DefaultValue, self.IsVersionControl, asqlversion=self.Creator.SQLVersion)
            if aftype is None:
                print '  *** %s_%d:%s posiada nieznany typ: %s! ***' % (self.Name, self.ID, afield.Name, afield.Type)
            elif afdefault:
                ssql = ssql + '  %s %s NOT NULL DEFAULT %s,\n' % (afield.Name, aftype, afdefault)
            else:
                ssql = ssql + '  %s %s NOT NULL,\n' % (afield.Name, aftype, )
            lsf.append(afield.Name)
        ssql = ssql + '  _datetime datetime NOT NULL DEFAULT getdate(),\n'
        ssql = ssql + '  _UID varchar(44) NOT NULL DEFAULT (\'\'),\n'
        ssql = ssql + '  _UserName varchar(200) NOT NULL DEFAULT (\'\'),\n'
        if self.IsVersionControl:
            ssql = ssql + '  _OIDRef varchar(44) NOT NULL DEFAULT (\'\'),\n'
            ssql = ssql + '  _action varchar(200) NOT NULL DEFAULT (\'\'),\n'
            ssql = ssql + '  _actiontime datetime NOT NULL DEFAULT getdate(),\n'
        if self.IsSecurityEnabled:
            ssql = ssql + '  _ACLRead varbinary (4000) NOT NULL DEFAULT 0,\n'
            ssql = ssql + '  _ACLWrite varbinary (4000) NOT NULL DEFAULT 0,\n'
            ssql = ssql + '  _ACLDelete varbinary (4000) NOT NULL DEFAULT 0,\n'
        ssql = ssql + '  _timestamp timestamp,\n'
        ssql = ssql + '  );\n\n'
        lsindexfields = ['_datetime', '_UID', '_UserName']
        if self.IsVersionControl:
            lsindexfields.extend(['_OIDRef', '_action', '_actiontime'])
        for afname in lsindexfields:
            siname = 'id_%s_%d_%s' % (self.Name, self.ID, afname)
            ssql = ssql + 'IF EXISTS (SELECT name FROM sysindexes WHERE name = \'%s\') DROP INDEX %s_%d.%s\n' % (siname, self.Name, self.ID, siname)
            ssql = ssql + 'CREATE INDEX %s ON %s_%d (%s)\n' % (siname, self.Name, self.ID, afname)
        for afield in self.Fields:
            if (afield.IsIndexed or afield.IsUnique or afield.TypeDescription == 'GUID' or afield.TypeDescription == 'Auto increment') and afield.Type != 'text':
                siname = 'id_%s_%d_%s' % (self.Name, self.ID, afield.Name)
                if not self.IsVersionControl and (afield.TypeDescription == 'GUID' or afield.TypeDescription == 'Auto increment'):
                    sua = 'UNIQUE '
                else:
                    sua = ''
                ssql = ssql + 'IF EXISTS (SELECT name FROM sysindexes WHERE name = \'%s\') DROP INDEX %s_%d.%s\n' % (siname, self.Name, self.ID, siname)
                ssql = ssql + 'CREATE %sINDEX %s ON %s_%d (%s)\n\n' % (sua, siname, self.Name, self.ID, afield.Name)
        if acreateifnotexists:
            ssql = ssql + '\n\nEND\n\n'
        lk = self.RegisteredFieldValues.keys()
        lk.sort()
        for aid in lk:
            self.Values.append(self.RegisteredFieldValues[aid])
        if self.Values:
            #         ssql=ssql+"\n\nGO\n\n"
            vsql = ''
            if self.IsVersionControl:
                sf1 = string.join(lsf, ',')
                vsql = vsql + "INSERT INTO %s (%s,_OIDRef,_action) select %s,_OID,'INSERT' from %s\n" % (self.NameSQL, sf1, sf1, self.SQLBaseTable.NameSQL)
            else:
                for d in self.Values:
                    lk = d.keys()
                    sf = string.join(lk, ',')
                    lv = []
                    for akey in lk:
                        s = d[akey]
                        if not isinstance(s, types.StringTypes):
                            s = str(s)
                        lv.append("'" + string.replace(s, "'", '"') + "'")    #"
                    sv = string.join(lv, ',')
                    vsql = vsql + 'INSERT INTO %s (%s) VALUES (%s)\n' % (self.NameSQL, sf, sv)
            if ainsertvaluesonly:
                return vsql
            ssql = ssql + vsql
        ssql = ssql + '\n\n'
        return ssql

    def GetDefaultSearchSQL(self, aname='DefaultSearch', aquery=None, asqlversion=2008):
        if isinstance(asqlversion, types.StringTypes):
            asqlversion = int(asqlversion)
        if asqlversion < 2005:
            return self.GetDefaultSearchSQL_2000(aname, aquery)

        if aquery is None:
            lfields = self.FieldsByTabID
            aNameSQLID = self.NameSQLID    #self.Name+'_'+str(self.ID)
            aNameSQL = self.NameSQL    #self.TablePrefix+self.NameSQLID
        else:
            lfields = aquery.FieldsList
            aNameSQLID = aquery.Tables[0].NameSQLID    #self.Name+'_'+str(self.ID)
            aNameSQL = aquery.Tables[0].NameSQL    #self.TablePrefix+self.NameSQLID
        w = 0
        for afield in lfields:
            if (aquery is not None) or ((afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', 'external dict', 'external dict multiple']):
                w = 1
                break
        if not w:
            return None
        asp = self.AddStoredProcedure(aname, aquery=aquery)
        ssql = """
CREATE PROCEDURE %s
@Page INT,
@Size INT,
@MoreRecords INT = 0 OUTPUT,
@sWhere VARCHAR(4000),    -- max dlug. klauzuli WHERE
@sOrder VARCHAR(2000),    -- max dlug. klauzuli ORDER
@UserName VARCHAR(200),         -- uzytkownik sesji
@IsPivot INT=0,
@UserRights varchar(4000)='00'

AS
DECLARE @Start INT, @End INT
DECLARE @cmd VARCHAR(8000) --maksymalna dlugosc calego zapytania
DECLARE @ret INT
DECLARE @secCheck VARCHAR(4000)

DECLARE @TableCount Table(CountMax int)
SET NOCOUNT ON

SET @Start = (((@Page - 1) * @Size) + 1)
IF @@ERROR <> 0
   GOTO ErrorHandler

SET @End = (@Start + @Size - 1)
IF @@ERROR <> 0
   GOTO ErrorHandler                              

""" % (asp.Name, )
        sfl, sfl2, sfl3 = [], [], []
        for afield in lfields:
            if (aquery is not None) or ((afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', 'external dict', 'external dict multiple']):
                if aquery is None:
                    afname = afield.Name
                else:
                    afname = afield.NameSQL
                sfl.append(afname)
                if afield.Name[:1] != '_' or afield.IsAliased:
                    sfl2.append('%s AS [%s]' % (afname, afield.PrettyName))
                if afield.Name[:1] != '_' or afield.IsAliased:
                    sfl3.append('%s AS [%s]' % (afname, afield.UniqueName))
        sf1 = '\n' + string.join(sfl, ', \n') + '\n'
        sf2 = '\n' + string.join(sfl2, ', \n') + '\n'
        sf3 = '\n' + string.join(sfl3, ', \n') + '\n'

        if self.IsSecurityEnabled:
            ssql = ssql + """
SET @secCheck=' master.dbo.CheckFieldSecurity(%s._ACLRead,0x'+@UserRights+')=1 '
""" % (aNameSQL, )
        else:
            ssql = ssql + """
SET @secCheck=''
"""
        if aquery is None:
            squery = "SET @cmd='SELECT Count(*) FROM %s '+@sWhere" % (aNameSQL, )
            soid = '_OID,'
            ssql = ssql + """
IF @sWhere<>''
   SET @sWhere=' WHERE '+@sWhere
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery
        else:
            if aquery.SQLString_Where:
                #            squery="SET @cmd=' %s '+@sWhere"%(string.replace(aquery.SQLStringPart1Count,"'","''"),)
                #**Conversion of ''
                squery = "SET @cmd=' %s '+@sWhere" % (ReplaceSQLQuotes(aquery.SQLStringPart1Count), )
                soid = ''
                ssql = ssql + """
IF @sWhere <>''
   SET @sWhere=' ( '+@sWhere + ') AND ( %s )'
ELSE
   SET @sWhere=' %s '
""" % (ReplaceSQLQuotes(aquery.SQLString_Where), ReplaceSQLQuotes(aquery.SQLString_Where))    #(aquery.SQLString_Where,squery)
                if aquery.SQLString_StoredProcedureWhere:
                    ssql = ssql + """
IF @sWhere <>''
   SET @sWhere=' ( '+@sWhere + ') AND ( %s )'
ELSE
   SET @sWhere=' %s '
""" % (aquery.SQLString_StoredProcedureWhere, aquery.SQLString_StoredProcedureWhere, )
                sorder = ReplaceSQLQuotes(aquery.SQLString_Order)
                if sorder:
                    ssql = ssql + '''
IF @sOrder=''
   SET @sOrder='%s'

''' % (sorder, )
                ssql = ssql + """
IF @sWhere<>''
   SET @sWhere=' WHERE '+ @sWhere
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery
            else:
                squery = "SET @cmd=' %s '+@sWhere" % (ReplaceSQLQuotes(aquery.SQLStringPart1Count), )
                #            squery="SET @cmd='%s '+@sWhereOrder+' %s'"%(aquery.SQLStringPart1All,aquery.SQLString_Order)
                soid = ''
                if aquery.SQLString_StoredProcedureWhere:
                    ssql = ssql + """
IF @sWhere=''
   SET @sWhere=' %s '
ELSE
   SET @sWhere=' ( ' + @sWhere + ') AND ( %s ) '

""" % (aquery.SQLString_StoredProcedureWhere, aquery.SQLString_StoredProcedureWhere, )
                sorder = ReplaceSQLQuotes(aquery.SQLString_Order)
                if sorder:
                    ssql = ssql + '''
IF @sOrder=''
   SET @sOrder='%s'
''' % (sorder, )
                ssql = ssql + """
IF @sWhere<>''
   SET @sWhere=' WHERE '+ @sWhere
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery

        if aquery is None:
            sfrom = ' %s ' % aNameSQL
        else:
            sfrom = ' %s ' % aquery.SQLStringFrom
        ssql = ssql + """
INSERT INTO @TableCount
EXEC (@cmd)

IF @@ERROR <> 0
   GOTO ErrorHandler

Select @MoreRecords=CountMax from @TableCount

IF @IsPivot=0 BEGIN
   IF @sOrder=''
      set @sOrder='ORDER BY %s._OID'
   set @cmd='with aSubQuery as (SELECT %s._OID %s__OID,Row_Number() over('+@sOrder+') as _Row, %s FROM %s '+@sWhere+') Select * from aSubQuery where _Row Between '+str(@Start)+' and '+str(@End)
END ELSE BEGIN
   set @cmd='Select %s from %s '+@sWhere+@sOrder
END

exec(@cmd)

IF @@ERROR <> 0
   GOTO ErrorHandler

""" % (aNameSQL, aNameSQL, aNameSQLID, sf3, sfrom, sf2, sfrom,
        )
        ssql = ssql + """
SET NOCOUNT OFF
RETURN 0

ErrorHandler:
SET NOCOUNT OFF
RETURN @@ERROR
"""
        asp.Text = ssql
        return asp

    def GetDefaultVersionSQL(self, asrctable, acrm):
        lfields = self.FieldsByTabID
        sf1 = []
        for afield in lfields:
            sf1.append(afield.Name)
        sf1 = string.join(sf1, ', ')
        asp = self.AddStoredProcedure('SetVersion')
        ssecsql = ''
        if self.IsSecurityEnabled:
            ssecsql = '_ACLRead,_ACLWrite,_ACLDelete,'
        ssql = """
CREATE PROCEDURE [%s]
   @OID varchar(44),
   @action varchar(200)
AS
   SET @action=UPPER(@action)

   INSERT INTO %s (_OIDREF, %s, %s_action, _datetime, _UID, _UserName)
      SELECT _OID, %s, %s@action, _datetime, _UID, _UserName FROM %s WHERE _OID=@OID

   IF  @action='DELETE' BEGIN
      DELETE FROM %s WHERE _OID=@OID
   END
""" % (asp.Name, self.NameSQL, sf1, ssecsql, sf1, ssecsql, asrctable.NameSQL, asrctable.NameSQL)
        #       DELETE FROM %s WHERE OIDArkusza=@OID
        # ,acrm.Table_SheetInfo.NameSQL
        asp.Text = ssql
        return asp

    def GetStoredProcedures(self, lstoredprocedures):
        if lstoredprocedures is None:
            lstoredprocedures = []
        for aspname, asp in self.StoredProcedures.items():
            lstoredprocedures.append(asp.TextDrop)
            lstoredprocedures.append(asp.Text)

    def WriteImportScript(self, asqldir):
        l = ['_OID', ]
        for afield in self.Fields:
            if afield.Name != '_timestamp':
                l.append(afield.Name)
        l.extend(['_datetime', '_UID', '_UserName'])
        res = """# coding=utf-8
import sys
import icorpipe
import icorlib.projekt.sqlimportlib as SQLImportLib
sql1='''
%s
%s
'''
atablename='%s'
aproject='%s'
lfields=%s
lstoredprocedures=[
""" % (self.GetDropSQL(), self.GetCreateTableSQL(), self.NameSQL, self.Creator.Project, str(l))
        for aspname, asp in self.StoredProcedures.items():
            res = res + '''
"""
-- %s
%s
""",
"""
%s
""",
''' % (asp.Name, asp.TextDrop, asp.Text)
        fout = ICORUtil.OpenText(asqldir + 'UTIL_' + self.NameSQL + '.py', 'w')
        try:
            fout.write(res)
            fout.write('''
]
if __name__=='__main__':
   SQLImportLib.Main(sql1,atablename,aproject,lfields,astoredprocs=lstoredprocedures)
''')
        finally:
            fout.close()

    def GetDefaultSearchSQL_2000(self, aname='DefaultSearch', aquery=None):
        if aquery is None:
            lfields = self.FieldsByTabID
        else:
            lfields = aquery.FieldsList
        w = 0
        for afield in lfields:
            if (aquery is not None) or ((afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', ]):
                w = 1
                break
        if not w:
            return None
        asp = self.AddStoredProcedure(aname)
        ssql = """
CREATE PROCEDURE %s
@Page INT,
@Size INT,
@MoreRecords INT = 0 OUTPUT,
@sWhere VARCHAR(4000),    -- max dlug. klauzuli WHERE
@sOrder VARCHAR(2000),    -- max dlug. klauzuli ORDER
@UserName VARCHAR(200),         -- uzytkownik sesji
@IsPivot INT=0,
@UserRights varchar(4000)='00'

AS
DECLARE @Start INT, @End INT
DECLARE @cmd VARCHAR(8000) --maksymalna dlugosc calego zapytania
DECLARE @ret INT
DECLARE @secCheck VARCHAR(4000)

BEGIN TRANSACTION GetDataSet

SET @Start = (((@Page - 1) * @Size) + 1)
IF @@ERROR <> 0
   GOTO ErrorHandler

SET @End = (@Start + @Size - 1)
IF @@ERROR <> 0
   GOTO ErrorHandler                              

CREATE TABLE #TemporaryTable_%s
(
   _Row INT IDENTITY(1,1) PRIMARY KEY,
""" % (asp.Name, asp.Name)
        if aquery is None:
            ssql = ssql + """
   _OID VARCHAR (44),
"""
        sfl, sfl2 = [], []
        for afield in lfields:
            if (aquery is not None) or ((afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']):
                if aquery is None:
                    afname = afield.Name
                else:
                    afname = afield.UniqueName
                sfl.append(afname)
                if afield.Name[:1] != '_' or afield.IsAliased:
                    sfl2.append('%s AS [%s]' % (afname, afield.PrettyName))
                if afield.Type == 'string':
                    ssql = ssql + '  %s varchar(%s),\n' % (afname, afield.Size)
                elif afield.Type == 'numeric':
                    ssql = ssql + '  %s numeric(%s),\n' % (afname, afield.Size)
                elif afield.Type == 'date':
                    ssql = ssql + '  %s datetime,\n' % (afname, )
                elif afield.Type == 'datetime':
                    ssql = ssql + '  %s datetime,\n' % (afname, )
                elif afield.Type == 'bool':
                    ssql = ssql + '  %s bit,\n' % (afname, )
                elif afield.Type == 'text':
                    ssql = ssql + '  %s text,\n' % (afname, )
                elif afield.Type == 'integer':
                    ssql = ssql + '  %s int,\n' % (afname, )
                elif afield.Type == 'float':
                    ssql = ssql + '  %s float,\n' % (afname, )
                elif afield.Type == 'money':
                    ssql = ssql + '  %s money,\n' % (afname, )
                elif afield.Type == 'dict':
                    ssql = ssql + '  %s varchar(%s),\n' % (afname, afield.Size)
                elif afield.Type == 'dict int':
                    ssql = ssql + '  %s int,\n' % (afname, )
                elif afield.Type in ['external dict', 'external dict multiple']:
                    ssql = ssql + '  %s varchar(%s),\n' % (afname, afield.Size)
                else:
                    print '  *** %s_%d:%s posiada nieznany typ: %s! ***' % (afname, self.ID, afield.Name, afield.Type)
        sf1 = string.join(sfl, ', ')
        sf2 = string.join(sfl2, ', ')
        ssql = ssql + """
)
IF @@ERROR <> 0
   GOTO ErrorHandler
"""
        if self.IsSecurityEnabled:
            ssql = ssql + """
SET @secCheck=' master.dbo.CheckFieldSecurity([%s]._ACLRead,0x'+@UserRights+')=1 '
""" % (self.NameSQL, )
        else:
            ssql = ssql + """
SET @secCheck=''
"""
        if aquery is None:
            squery = "SET @cmd='SELECT top 50000 _OID,%s FROM %s '+@sWhere+@sOrder" % (sf1, self.NameSQL)
            soid = '_OID,'
            ssql = ssql + """
IF @sWhere<>''
   SET @sWhere=' WHERE '+@sWhere
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery
        else:
            if aquery.SQLString_Where:
                squery = "SET @cmd=' %s '+@sWhere+@sOrder" % (ReplaceSQLQuotes(aquery.SQLStringPart1), )
                #            squery="SET @cmd='%s '+@sWhereOrder+' %s'"%(aquery.SQLStringPart1,aquery.SQLString_Order)
                soid = ''
                ssql = ssql + """
IF @sWhere <>''
   SET @sWhere=' ( '+@sWhere + ') AND ( %s )'
ELSE
   SET @sWhere=' %s '
""" % (ReplaceSQLQuotes(aquery.SQLString_Where), ReplaceSQLQuotes(aquery.SQLString_Where))    #(aquery.SQLString_Where,squery)
                if aquery.SQLString_StoredProcedureWhere:
                    ssql = ssql + """
IF @sWhere <>''
   SET @sWhere=' ( '+@sWhere + ') AND ( %s )'
ELSE
   SET @sWhere=' %s '
""" % (aquery.SQLString_StoredProcedureWhere, )
                sorder = ReplaceSQLQuotes(aquery.SQLString_Order)
                if sorder:
                    ssql = ssql + '''
IF @sOrder=''
   SET @sOrder='%s'

''' % (sorder, )
                ssql = ssql + """
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder
IF @sWhere<>''
   SET @sWhere=' WHERE '+ @sWhere

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery
            else:
                squery = "SET @cmd=' %s '+@sWhere+@sOrder" % (ReplaceSQLQuotes(aquery.SQLStringPart1), )
                #            squery="SET @cmd='%s '+@sWhereOrder+' %s'"%(aquery.SQLStringPart1,aquery.SQLString_Order)
                soid = ''
                if aquery.SQLString_StoredProcedureWhere:
                    ssql = ssql + """
IF @sWhere=''
   SET @sWhere=' %s '
ELSE
   SET @sWhere=' ( ' + @sWhere + ') AND ( %s ) '

""" % (aquery.SQLString_StoredProcedureWhere, aquery.SQLString_StoredProcedureWhere, )
                sorder = ReplaceSQLQuotes(aquery.SQLString_Order)
                if sorder:
                    ssql = ssql + '''
IF @sOrder=''
   SET @sOrder='%s'
''' % (sorder, )
                ssql = ssql + """
IF @sOrder<>''
   SET @sOrder=' ORDER BY '+@sOrder
IF @sWhere<>''
   SET @sWhere=' WHERE '+ @sWhere

IF @secCheck<>''
   IF @sWhere<>''
      SET @sWhere=@sWhere+' AND '+@secCheck
   ELSE
      SET @sWhere=' WHERE '+@secCheck
%s
""" % squery

        ssql = ssql + """
INSERT INTO #TemporaryTable_%s
(%s%s)
EXEC (@cmd)

IF @@ERROR <> 0
   GOTO ErrorHandler

SELECT @MoreRecords=COUNT(*) FROM #TemporaryTable_%s

IF @IsPivot=0
   SELECT  %s_Row,%s
   FROM #TemporaryTable_%s
   WHERE (_Row >= @Start) AND (_Row <= @End)
ELSE
   SELECT  %s
   FROM #TemporaryTable_%s
--   WHERE (_Row >= @Start) AND (_Row <= @End)

IF @@ERROR <> 0
   GOTO ErrorHandler

""" % (asp.Name, soid, sf1, asp.Name, soid, sf1, asp.Name, sf2, asp.Name,
        )
        ssql = ssql + """
DROP TABLE #TemporaryTable_%s

COMMIT TRANSACTION GetDataSet
RETURN 0

ErrorHandler:
ROLLBACK TRANSACTION GetDataSet
RETURN @@ERROR
""" % (asp.Name, )
        asp.Text = ssql
        return asp

    def DumpAsXML(self, file, arecur, aindent=0, aaddobligatoryfields=0):
        if arecur.has_key(self.NameSQL):
            return
        arecur[self.NameSQL] = 1
        file.write('%s<SQLTABLE OID="%d" name="%s" namesql="%s" tableprefix="%s" caption="%s" file="%s" isexternal="%d" hasversions="%d">\n' % (' ' * aindent, self.ID, self.Name, self.NameSQLID, self.TablePrefix, self.TableCaption, self.NameFile, self.IsExternal, self.HasVersions))
        for afield in self.Fields:
            afield.DumpAsXML(file, arecur, aindent + 3, aaddobligatoryfields=aaddobligatoryfields)
        file.write('%s<SQLFIELD prettyname="%s__OID" name="_OID" type="string" asref="1"></SQLFIELD>\n' % (' ' * (aindent + 3), self.NameSQLID))
        file.write('%s<SQLFIELD prettyname="%s__datetime" name="_datetime" type="datetime" asref="1"></SQLFIELD>\n' % (' ' * (aindent + 3), self.NameSQLID))
        file.write('%s<SQLFIELD prettyname="%s__UID" name="_UID" type="string" asref="1"></SQLFIELD>\n' % (' ' * (aindent + 3), self.NameSQLID))
        file.write('%s<SQLFIELD prettyname="%s__UserName" name="_UserName" type="string" asref="1"></SQLFIELD>\n' % (' ' * (aindent + 3), self.NameSQLID))
        file.write('%s</SQLTABLE>\n' % (' ' * aindent, ))
        del arecur[self.NameSQL]

    def GetSelectClause(self, atop=0, aisaliased=1, aisinteractive=1, anounderscore=1, aaddsourcetable=0, aextfields=None):
        aselect = SQLSelect(atop, aisaliased, aisinteractive, anounderscore, aaddsourcetable, aextfields)
        aselect.Process(self)
        return aselect


class SQLSelect:

    def __init__(self, atop=0, aisaliased=1, aisinteractive=1, anounderscore=1, aaddsourcetable=0, aextfields=None):
        self.Fields = ''
        self.From = ''
        self._joins = []
        self.Joins = ''
        self.Where = ''
        self.OrderBy = ''
        self.FieldsDict = {}
        self.Top = atop
        self.IsAliased = aisaliased
        self.IsInteractive = aisinteractive
        self.NoUnderscore = anounderscore
        self.AddSourceTable = aaddsourcetable
        if aextfields is None:
            aextfields = []
        self.recurtables = []

    def AsString(self):
        if self._joins:
            self.Joins = string.join(self._Joins)
        l = ['SELECT', self.Fields, 'FROM', self.From, self.Joins]
        if self.Where:
            l.append('WHERE')
            l.append(self.Where)
        if self.OrderBy:
            l.append(self.OrderBy)
        return string.join(l, ' ')

    def AddCriteria(self, afield, acriteria, avalue, avariable=0):
        if type(afield) == type(()):
            btable, afield = afield
        else:
            btable = None
        if not isinstance(afield, types.StringTypes):
            if isinstance(afield, SQLField):
                afield = afield.NameSQL
            elif isinstance(afield, SQLTable):
                afield = afield.NameSQL + '._OID'
        if btable and string.find(afield, '.') < 0:
            afield = btable.NameSQL + '.' + afield
        if self.Where:
            self.Where = self.Where + ' AND'
        self.Where = self.Where + afield + acriteria
        if avariable:
            self.Where = self.Where + '\'" & ' + avalue + ' & "\''
        else:
            self.Where = self.Where + avalue

    def Process(self, atable):
        cnt = 0
        fls = []
        flo = []
        if self.NoUnderscore:
            sf = atable.NameSQL + '._OID'
            fls.append(sf)
            self.FieldsDict[sf] = cnt
            cnt = cnt + 1
        for afield in atable.FieldsByTabID:
            w = 0
            if self.NoUnderscore and afield.Name[:1] == '_':
                w = 0
            if (self.IsAliased and afield.IsAliased) or not self.IsAliased:
                w = 1
            if (self.IsInteractive and afield.IsInteractive) or not self.IsInteractive:
                w = 1
            if w:
                fls.append(afield.NameSQL)
                self.FieldsDict[afield.NameSQL] = cnt
                cnt = cnt + 1
            if afield.SortStyle == 1:
                flo.append(afield.NameSQL + ' ASC')
            elif afield.SortStyle == 2:
                flo.append(afield.NameSQL + ' DESC')
        self.From = atable.NameSQL
        self.Fields = string.join(fls, ', ')
        if self.Top:
            self.Fields = ' TOP %d %s' % (self.Top, self.Fields)
        if not flo:
            flo.append(atable.FieldsByTabID[0].NameSQL)
        self.OrderBy = ' ORDER BY ' + string.join(flo, ', ')


class SQLCreator:

    def __init__(self, aproject, aconnectionstring, abasenamemodifier='', acrm=None, asqlversion=2008):
        self.CRM = acrm
        self.Project = aproject
        self.tables = []
        self.tables_groups = {}
        self.ConnectionString = aconnectionstring
        self.BaseNameModifier = abasenamemodifier
        self.SQLVersion = asqlversion

    def AddTable(self, aname, aid, atablecaption='', aisexternal=0, asingleobjectname='', ahasversions=0, aisversioncontrol=0, aissecurityenabled=0, atablegroup='', adbname='', adbowner='', atop=0, agenerateenable=0):
        atable = SQLTable(self, self.BaseNameModifier + aname, aid, atablecaption, aisexternal, asingleobjectname, ahasversions=ahasversions, aisversioncontrol=aisversioncontrol, aissecurityenabled=aissecurityenabled, atablegroup=atablegroup, adbname=adbname, adbowner=adbowner, atop=atop, agenerateenable=agenerateenable)
        self.tables_groups[atablegroup] = 1
        self.tables.append(atable)
        return atable

    def GetExternalTable(self, atableoid):
        #      print 'GetExternalTable',atableoid
        atable = self.CRM.sourcetables[atableoid]
        #      print 'atable:',atable
        #      print 'atable sql:',atable.SQLTable
        return atable.SQLTable

    def WriteTableDefinitions(self, asqldir, ausertsql=None, lstoredprocedures=None, laddedsql=None, aservercreate=0, aprojectname='', aDisableGenerateDependentTables=0):
        if not asqldir[-1:] in ['/', '\\']:
            asqldir = asqldir + '/'
        if lstoredprocedures is None:
            lstoredprocedures = []
        if laddedsql is None:
            laddedsql = []
        awrite = 1
        if aDisableGenerateDependentTables:
            awrite = 0
        if self.CRM is not None:
            if self.CRM.ProjectVars.get('aSQLScriptsCreate', '1') == '0':
                awrite = 0
        if awrite:
            try:
                ftablesdrop = ICORUtil.OpenText(asqldir + 'sys_tables_drop.sql', 'w')
            except:
                print 'ERROR: WriteTableDefinitions', asqldir + 'sys_tables_drop.sql'
                raise
        dtablescreategroups = {}
        dtablesdropgroups = {}
        if awrite:
            for agroup in self.tables_groups.keys():
                fout = ICORUtil.OpenText(asqldir + 'sys_tables_create_' + agroup + '.sql', 'w')
                dtablescreategroups[agroup] = fout
                fout = ICORUtil.OpenText(asqldir + 'sys_tables_drop_' + agroup + '.sql', 'w')
                dtablesdropgroups[agroup] = fout
            faddedsql = ICORUtil.OpenText(asqldir + 'sys_added_sql.sql', 'w')
            fusersql = ICORUtil.OpenText(asqldir + 'sys_user_sql.sql', 'w')
        try:
            for atable in self.tables:
                if not atable.IsExternal:
                    asql = atable.GetDropSQL()
                    if awrite:
                        ftablesdrop.write(asql)
                    if aservercreate:
                        SQLRun.ExecuteGoSplitSQLCommand(self.ConnectionString, asql, aprint=0)
                else:
                    if aDisableGenerateDependentTables and not atable.GenerateEnable:
                        continue
                    atable.GetStoredProcedures(lstoredprocedures)
                    if awrite:
                        atable.WriteImportScript(asqldir, lstoredprocedures=lstoredprocedures)
            for atable in self.tables:
                if not atable.IsExternal:
                    if aDisableGenerateDependentTables and not atable.GenerateEnable:
                        continue
                    asql = atable.GetCreateTableSQL()
                    if awrite:
                        dtablescreategroups[atable.TableGroup].write(asql)
                    asql = atable.GetDropSQL()
                    if awrite:
                        dtablesdropgroups[atable.TableGroup].write(asql)
                    if aservercreate:
                        SQLRun.ExecuteGoSplitSQLCommand(self.ConnectionString, asql, aprint=0)
            for aaddedsql in laddedsql:
                if awrite:
                    faddedsql.write(aaddedsql)
                if aservercreate:
                    SQLRun.ExecuteGoSplitSQLCommand(self.ConnectionString, aaddedsql, aprint=0)
            if ausertsql:
                for autsql in ausertsql:
                    if awrite:
                        if not autsql.ExecuteNow:
                            autsql.Write(fusersql)
                    if aservercreate:
                        SQLRun.ExecuteGoSplitSQLCommand(self.ConnectionString, autsql, aprint=0)
        finally:
            if awrite:
                ftablesdrop.close()
                for agroup in self.tables_groups.keys():
                    dtablescreategroups[agroup].close()
                faddedsql.close()
                fusersql.close()
        if awrite:
            if aprojectname:
                fout = ICORUtil.OpenText(asqldir + 'sqlrun_%s.py' % aprojectname, 'w')
                fout.write("""import icorpipe
from icorlib.projekt.sqlrun import *

if __name__=='__main__':
   if len(sys.argv)<2:
      print 'usage:\\nsqlrun_%s.py <file.sql>'
   else:
      MainI('%s',sys.argv[1])
""" % (aprojectname, aprojectname))
                fout.close()
                fout = ICORUtil.OpenText(asqldir + 'docreate_%s.py' % aprojectname, 'w')
                fout.write("""import icorpipe
import CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt_Main

if __name__=='__main__':
   CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt_Main.ICORMain(Value='%s')
""" % (aprojectname, ))
                fout.close()

    def ExecuteServerSQLCommand(self, fname, isafile=1):
        if isafile:
            f = ICORUtil.OpenText(fname, 'r')
            try:
                asql = f.read()
            finally:
                f.close()
        else:
            asql = fname
        SQLRun.ExecuteGoSplitSQLCommand(self.ConnectionString, asql, aprint=0)
