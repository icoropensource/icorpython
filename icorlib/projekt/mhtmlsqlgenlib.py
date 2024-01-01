# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.msqlquery as MSQLQuery
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import string
import types


#*********************************************************************************
def GetFormValidateParms():
    return ''


#   return "validate='onchange' invalidColor='gold' mark year4"


#*********************************************************************************
def GetFieldValidationText(afield, aissearch=0):
    return ''
    if aissearch:
        return ''
    ret = []
    if not aissearch:
        if afield.IsObligatory:
            ret.append('REQUIRED=1 ')
#      if afield.Lowercase:
#         ret.append('lowercase ')
#      if afield.NoSpace:
#         ret.append('nospace ')
#      if afield.Uppercase:
#         ret.append('uppercase ')
        if afield.Filter:
            ret.append("FILTER='%s' " % afield.Filter, )
#      if afield.Mask:
#         ret.append("mask='%s' "%afield.Mask,)
        if afield.Regex:
            ret.append("REGEXP='%s' " % afield.Regex, )
        if afield.MinValue:
            ret.append("MIN='%s' " % afield.MinValue)
        if afield.MaxValue:
            ret.append("MAX='%s' " % afield.MaxValue)
    if afield.Type == 'string':
        pass
    elif afield.Type == 'numeric':
        if not afield.Unsigned:
            ret.append('SIGNED=1 ')
        ret.append('FLOAT=1 ')
    elif afield.Type in ['money', 'float']:
        if not afield.Unsigned:
            ret.append('SIGNED=1 ')
        ret.append('FLOAT=1 ')    #AMOUNT
    elif afield.Type == 'date' and not aissearch:
        ret.append("DATE='YYYY/M/D' ")
    elif afield.Type == 'datetime' and not aissearch:
        ret.append("DATE='YYYY/M/D' ")
    elif afield.Type == 'bool':
        pass
    elif afield.Type in ['dict', 'dict int']:
        pass
    elif afield.Type in ['external dict', 'external dict multiple']:
        pass
    elif afield.Type == 'text':
        pass
    elif afield.Type == 'integer':
        if not afield.Unsigned:
            ret.append('SIGNED=1 ')
        ret.append('INTEGER=1 ')
    else:
        pass
    return string.join(ret, '')


#*********************************************************************************
def GetFieldValidationScript(afield, afieldid, aissearch=0):
    ret = []
    if aissearch:
        return ret
    if not aissearch:
        if afield.IsObligatory:
            ret.append('jQuery("#%s").rules("add",{required:true});jQuery("#%s").addClass("required");\n' % (afieldid, afieldid))
#      if afield.Lowercase:
#         ret.append('lowercase ')
#      if afield.NoSpace:
#         ret.append('nospace ')
#      if afield.Uppercase:
#         ret.append('uppercase ')
        if afield.Filter:
            ret.append('''jQuery("#%s").rules("add",{myFilter:'%s'});\n''' % (afieldid, afield.Filter.replace('\\', '\\\\')), )
#      if afield.Mask:
#         ret.append("mask='%s' "%afield.Mask,)
        if afield.Regex:
            ret.append('''jQuery("#%s").rules("add",{myRegexp:'%s'});\n''' % (afieldid, afield.Regex.replace('\\', '\\\\')), )
        if afield.MinValue:
            ret.append('''jQuery("#%s").rules("add",{min:%s});\n''' % (afieldid, afield.MinValue))
        if afield.MaxValue:
            ret.append('''jQuery("#%s").rules("add",{max:%s});\n''' % (afieldid, afield.MaxValue))
    if afield.Type == 'string':
        if afield.TypeDescription == 'EMail':
            ret.append('''jQuery("#%s").rules("add",{emailCheck:true});\n''' % (afieldid, ))
        elif afield.TypeDescription == 'Nr rachunku bankowego':
            ret.append('''jQuery("#%s").rules("add",{iban:true});\n''' % (afieldid, ))
    elif afield.Type in ['numeric', 'float']:
        if afield.Unsigned:
            ret.append('''jQuery("#%s").rules("add",{myNumeric:true});\n''' % (afieldid, ))
        else:
            ret.append('''jQuery("#%s").rules("add",{mySignedNumeric:true});\n''' % (afieldid, ))
    elif afield.Type in ['money', ]:
        if afield.Unsigned:
            ret.append('''jQuery("#%s").rules("add",{myMoney:true});\n''' % (afieldid, ))
        else:
            ret.append('''jQuery("#%s").rules("add",{mySignedMoney:true});\n''' % (afieldid, ))
    elif afield.Type == 'date' and not aissearch:
        ret.append('''jQuery("#%s").rules("add",{myDate:true});\n''' % (afieldid, ))
    elif afield.Type == 'datetime' and not aissearch:
        ret.append('''jQuery("#%s").rules("add",{myDate:true});\n''' % (afieldid, ))
    elif afield.Type == 'bool':
        pass
    elif afield.Type in ['dict', 'dict int']:
        pass
    elif afield.Type in ['external dict', 'external dict multiple']:
        pass
    elif afield.Type == 'text':
        pass
    elif afield.Type == 'integer':
        if afield.Unsigned:
            ret.append('''jQuery("#%s").rules("add",{myInteger:true});\n''' % (afieldid, ))
        else:
            ret.append('''jQuery("#%s").rules("add",{mySignedInteger:true});\n''' % (afieldid, ))
    else:
        pass
    return ret


#*********************************************************************************
def WriteTableFieldsDescription(atable):
    ret = ['%>\n', '<hr>\n']
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.Description:
            s = '<b>%s</b><br>%s<br>' % (afield.PrettyName, afield.Description)
            ret.append(s)
    ret.append('<%\n')
    if len(ret) > 3:
        return string.join(ret, '')
    return ''


#*********************************************************************************
def ShowExternalDictSelection2(afield, aisnew=0):
    ret = ''
    aselect = afield.DictSourceTable.GetSelectClause(atop=1000)
    ret = ret + """
      Set rsdd1 = Server.CreateObject("ADODB.Recordset")
      rsdd1.ActiveConnection = cn
      rsdd1.CursorType = adOpenKeyset
      rsdd1.LockType = adLockOptimistic
      rsdd1.Source="%s"                    
      rsdd1.Open
""" % (aselect.AsString())
    ret = ret + """
if not (rsdd1.EOF or rsdd1.BOF) then
"""
    if not aisnew:
        ret = ret + """
sd=""
if rs.State<>adStateClosed then
   if not (rs.EOF or rs.BOF) then
      sd=rs.Fields("%s").Value
   end if
end if
""" % (afield.Name, )
    else:
        ret = ret + """
   sd=""
"""
    ret = ret + """
   Response.Write "<SELECT class='wide' id='%s' name='%s'>"
   Do While Not rsdd1.EOF
      sdv=rsdd1("_OID")
      if sd=sdv then
         sds="SELECTED "
      else
         sds=""
      end if
      Response.Write "<OPTION " & sds & "value='" & sdv & "'>"
""" % (afield.Name, afield.Name)
    for addfield in afield.DictSourceTable.FieldsByTabID:
        #      if addfield.IsAliased and addfield.IsInteractive:
        if addfield.IsAliased and addfield.DictSourceTable is None:
            ret = ret + """
      Response.Write rsdd1("%s") & ", "
""" % (addfield.Name, )
    ret = ret + """
      Response.Write "</OPTION>" & chr(10)
      rsdd1.MoveNext
   Loop
   Response.Write "</SELECT>"
end if
if rsdd1.State<>adStateClosed then
   rsdd1.Close
end if
set rsdd1=Nothing
"""
    return ret


#*********************************************************************************
def ShowExternalDictSelectionMultiple(dbfield, aisnew=0, aissinglevalue=0, aisdialog=0, aascheckbox=0):
    aascheckbox = 1
    ret = '''
' ShowExternalDictSelectionMultiple - START
'''
    try:
        atop = int(dbfield.Table.Creator.CRM.ProjectVars['aExternalDictMultipleMaxItemsCount'])
    except:
        atop = 242
    aquery = MSQLQuery.QuerySQL(atop=atop)
    aquery.PushTable(dbfield)    #.DictSourceTable
    aoidfield = aquery.ThisTable.Fields['_OID']
    if aissinglevalue:    #i jesli to jest pole referencyjne
        aquery.ThisTable.IsASPSQLConstraint = 1
        aquery.ThisTable.ASPSQLConstraintPrefix = dbfield.Name
        d = {'type': 'like', 'value': 'awhere', 'asasp': '1'}
        aoidfield.AddRule(d)
        ret = ret + """
      if aoidref<>"-1" and areffield="%s" then
         awhere=aoidref
      else
         awhere="%%"
      end if
""" % (dbfield.Name, )
    aquery.AsSQL()
    for atable in aquery.Tables:
        if atable.IsASPSQLConstraint:
            ret = ret + """
      if isempty(extrule_%s_%s) then
         extrule_%s_%s=""
      end if
      if extrule_%s_%s<>"" then
         extrule_%s_%s=" AND (" & extrule_%s_%s & ") "
      end if
""" % (atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, )
    ret = ret + """
      Set rsdd1 = Server.CreateObject("ADODB.Recordset")
      rsdd1.ActiveConnection = cn
      rsdd1.CursorType = adOpenStatic
      rsdd1.LockType = adLockOptimistic
      rsdd1.Source="%s"
      rsdd1.Open
""" % (aquery.SQLString)

    #$$SK
    ret = ret + """
if (rsdd1.EOF or rsdd1.BOF) then
"""
    if not aascheckbox:
        ret = ret + """
   Response.Write "<SELECT id='%s' multiple=multiple name='%s' size=10>"
""" % (dbfield.Name, dbfield.Name, )
#   if not dbfield.IsObligatory:
#      ret=ret+"""
#   if not (aoidref<>"-1" and areffield="%s") then
#      Response.Write "<OPTION value=''></OPTION>"
#   end if
#"""%(dbfield.Name)
    ret = ret + """
else
"""

    if aisdialog:
        ret = ret + """
   if rsdd1.RecordCount<=%d then
""" % (atop, )
    if not aisnew:
        ret = ret + """
   sd=""
   if rs.State<>adStateClosed then
      if not (rs.EOF or rs.BOF) then
         sd=rs.Fields("%s").Value
      end if
   end if
   if rsdd1.RecordCount=%d and aoid<>"-1" and sd<>"" then '[ and sd<>"" ]
      if rsdd1.State<>adStateClosed then
         rsdd1.Close
      end if
      awhere=sd
      rsdd1.Source="%s"
      rsdd1.Open
   end if
""" % (dbfield.Name, atop, aquery.SQLString)
    else:
        ret = ret + """
   sd=""
"""
    if not aascheckbox:
        ret = ret + """
   Response.Write "<SELECT multiple=multiple id='%s' name='%s' size=10>"
""" % (dbfield.Name, dbfield.Name, )
#   if not dbfield.IsObligatory:
#      ret=ret+"""
#   if not (aoidref<>"-1" and areffield="%s") then
#      Response.Write "<OPTION value=''></OPTION>"
#   end if
#"""%(dbfield.Name)
    ret = ret + """
   sdbvalue1=""
   svbvaluecnt=0
   scheckcnt=0
   Do While Not rsdd1.EOF
      sdv=rsdd1(%d)
      if isnull(sdv) then
         sdv=""
      end if
      sdbvalue=""
""" % (aquery.FieldsDict[aoidfield.NameSQL])
    if not aascheckbox:
        ret = ret + """
      if sd=sdv then
         sds="SELECTED "
      else
         sds=""
      end if
      Response.Write "<OPTION " & sds & "value='" & sdv & "'>"
"""
    else:
        ret = ret + """
      if InStr(sd,sdv)>0 then
         sds="CHECKED "
      else
         sds=""
      end if
      Response.Write "<span><input class=checkradio value='" & sdv & "' type=checkbox name='%s' id='%s_" & CStr(scheckcnt) & "'" & sds & ">"
      scheckcnt=scheckcnt+1
""" % (dbfield.Name, dbfield.Name, )
    lfields = aquery.AsColumnFields()
    for afield in lfields:
        if afield.IsAliased and not afield.IsDictViewHidden:
            ret = ret + """
      sdv=rsdd1("%s").Value
      if isnull(sdv) then
         sdv=""
      end if
""" % (afield.PrettyName, )
            if afield.Type == 'bool':
                ret = ret + """               
      if CBool(sdv) then
         sdv="Tak"
      else
         sdv="Nie"
      end if
"""
            ret = ret + """
      if sdv<>"" then
         svbvaluecnt=svbvaluecnt+1
         sdv="<b>%s:</b> " & sdv
         sdbvalue=sdbvalue & CStr(sdv) & ", "
         sdbvalue1=CStr(sdv)
      end if
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), )
    ret = ret + """
      if sdbvalue="" then
         sdbvalue="&nbsp;-&nbsp;"
      else
         sdbvalue=left(trim(sdbvalue),len(sdbvalue)-2)
      end if
      if svbvaluecnt=1 then
         if sdbvalue1="" then
            sdbvalue1="&nbsp;-&nbsp;"
         end if
         Response.Write sdbvalue1
      else
         Response.Write sdbvalue
      end if
"""
    if not aascheckbox:
        ret = ret + """
      Response.Write "</OPTION>" & chr(10)
"""
    else:
        ret = ret + """
      Response.Write "<br></span>" & chr(10)
"""
    ret = ret + """
      rsdd1.MoveNext
   Loop
"""
    if not aascheckbox:
        ret = ret + """
   Response.Write "</SELECT>"
"""

    ret = ret + """           
else
"""
    if aisdialog:
        ret = ret + ShowSingleValueFromExternalDict(dbfield, arsnum='tmpdict', arsbasenum=-1, anoref=1, asvariable='mydictvalue', aisedit=1)
        arequired = ''
        if dbfield.IsObligatory:
            arequired = " REQUIRED='1'"
        ret = ret + '''
      Response.Write "<INPUT type=hidden id='%s' name='%s' value='" & mydictvalueoid & "'%s>"
      Response.Write "<INPUT type=text size=40 readonly=yes style='BACKGROUND-COLOR:#f0f0f0;' id='%sVisible' name='%sVisible' value=""" & server.htmlencode(mydictvalue) & """%s>"
''' % (dbfield.Name, dbfield.Name, arequired, dbfield.Name, dbfield.Name, arequired)
        if dbfield.FieldValuePreviewLink:
            afdictpage = dbfield.FieldValuePreviewLink
        else:
            afdictpage = 'BZR_%d_sv.asp' % (dbfield.DictSourceTable.ID, )
        if dbfield.ModelXMLDataIDEdit:
            afdictpage = 'xmldata_BZR_%d_sv.asp' % (dbfield.ModelXMLDataIDEdit, )
        if afdictpage != '-':
            ret = ret + """
      Response.Write "&nbsp;<IMG alt='wybór ze słownika' src='/icormanager/images/icon_dictsearch.png' style='cursor:pointer;' onclick='javascript:showPopupFPDict(""%s"",""%s"",""my%sFrame"");'>"
""" % (afdictpage, dbfield.Name, dbfield.Name, )
        ret = ret + """
      Response.Write "<br>"
      Response.Write "<iframe id=my%sFrame style='display:none;width:100%%;height:480px;'; ALLOWTRANSPARENCY=YES FRAMEBORDER=0 SCROLLING=YES></iframe>"
      end if
""" % (dbfield.Name, )
    else:
        ret = ret + """
   Response.Write "&nbsp;"
      end if
"""
    ret = ret + """
end if
if rsdd1.State<>adStateClosed then
   rsdd1.Close
end if
set rsdd1=Nothing
' ShowExternalDictSelectionMultiple - END
"""
    return ret


#*********************************************************************************
def ShowExternalDictSelection(dbfield, aisnew=0, aissinglevalue=0, aisdialog=0):
    ret = ''
    try:
        atop = int(dbfield.Table.Creator.CRM.ProjectVars['aExternalDictMaxItemsCount'])
    except:
        atop = 300
    if dbfield.TextRows not in [0, 6]:
        atop = dbfield.TextRows
    try:
        ashowonlyvaluesinexternaldicts = int(dbfield.Table.Creator.CRM.ProjectVars['aShowOnlyValuesInExternalDicts'])
    except:
        ashowonlyvaluesinexternaldicts = 0
    axmlid = dbfield.ModelXMLDataIDEdit
    if axmlid:
        amodelxml = dbfield.Table.Creator.CRM.GetTableXMLDataByID(axmlid, anoparse=1)
        amodelxml.Parse(anoassql=1)
        aquery = amodelxml.Parser.querysql
        aquery.Top = atop
    else:
        aquery = MSQLQuery.QuerySQL(atop=atop)
        aquery.PushTable(dbfield)
    aquery.Clear()
    aquery.IsASPStrings=1
    aoidfield = aquery.ThisTable.Fields['_OID']
    if aissinglevalue:    #i jesli to jest pole referencyjne
        aquery.ThisTable.IsASPSQLConstraint = 1
        aquery.ThisTable.ASPSQLConstraintPrefix = dbfield.Name
        d = {'type': 'like', 'value': 'awhere', 'asasp': '1'}
        aoidfield.AddRule(d)
        ret = ret + """
      ahidepreview=0
      if aoidref<>"-1" and areffield="%s" then
         awhere=aoidref
         ahidepreview=1
      else
         awhere="%%"
      end if
""" % (dbfield.Name, )
    aquery.AsSQL()
    for atable in aquery.Tables:
        if atable.IsASPSQLConstraint:
            ret = ret + """
      if isempty(extrule_%s_%s) then
         extrule_%s_%s=""
      end if
      if extrule_%s_%s<>"" then
         extrule_%s_%s=" AND (" & extrule_%s_%s & ") "
      end if
""" % (atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, atable.ASPSQLConstraintPrefix, atable.NameSQLID, )
    ret = ret + """
      Set rsdd1 = Server.CreateObject("ADODB.Recordset")
      rsdd1.ActiveConnection = cn
      rsdd1.CursorType = adOpenStatic
      rsdd1.LockType = adLockOptimistic
      rsdd1.Source="%s"
      rsdd1.Open
""" % (aquery.SQLString)

    #$$SK
    ret = ret + """
if (rsdd1.EOF or rsdd1.BOF) then
"""
    ret = ret + """
   Response.Write "<SELECT class='wide' id='%s' name='%s'>"
""" % (dbfield.Name, dbfield.Name, )
    if not dbfield.IsObligatory:
        ret = ret + """
   if not (aoidref<>"-1" and areffield="%s") then
      Response.Write "<OPTION value=''></OPTION>"
   end if
""" % (dbfield.Name)
    ret = ret + """
else
"""

    if aisdialog:
        ret = ret + """
   if rsdd1.RecordCount<%d then
""" % (atop, )
    if not aisnew:
        ret = ret + """
   sd=""
   if rs.State<>adStateClosed then
      if not (rs.EOF or rs.BOF) then
         sd=rs.Fields("%s").Value
      end if
   end if
   if rsdd1.RecordCount=%d and aoid<>"-1" and sd<>"" then '[ and sd<>"" ]
      if rsdd1.State<>adStateClosed then
         rsdd1.Close
      end if
      awhere=sd
      rsdd1.Source="%s"
      rsdd1.Open
   end if
""" % (dbfield.Name, atop, aquery.SQLString)
    else:
        ret = ret + """
   sd=""
"""
    ret = ret + """
   Response.Write "<SELECT class='wide' id='%s' name='%s'>"
""" % (dbfield.Name, dbfield.Name, )
    if not dbfield.IsObligatory:
        ret = ret + """
   if not (aoidref<>"-1" and areffield="%s") then
      Response.Write "<OPTION value=''></OPTION>"
   end if
""" % (dbfield.Name)
    ret = ret + """
   sdbvalue1=""
   Do While Not rsdd1.EOF
      svbvaluecnt=0
      sdv=rsdd1(%d)
      if isnull(sdv) then
         sdv=""
      end if
      if sd=sdv then
         sds="SELECTED "
      else
         sds=""
      end if
      Response.Write "<OPTION " & sds & "value='" & sdv & "'>"
      sdbvalue=""
""" % (aquery.FieldsDict[aoidfield.NameSQL])
    lfields = aquery.AsColumnFieldsQuery()
    for afield in lfields:
        if afield.IsAliased and not afield.IsDictViewHidden:
            ret = ret + """
      sdv=rsdd1("%s").Value
      if isnull(sdv) then
         sdv=""
      end if
""" % (afield.PrettyName, )
            if afield.Type == 'bool':
                ret = ret + """                                         
      if CBool(sdv) then
         sdv="Tak"
      else
         sdv="Nie"
      end if
"""
            if ashowonlyvaluesinexternaldicts:
                ret = ret + """
      if sdv<>"" then
         svbvaluecnt=svbvaluecnt+1
         sdbvalue1=CStr(sdv)
         sdbvalue=sdbvalue & CStr(sdv) & ", "
      end if
"""
            else:
                ret = ret + """
      if sdv<>"" then
         svbvaluecnt=svbvaluecnt+1
         sdbvalue1=CStr(sdv)
         sdv="<b>%s:</b> " & sdv
         sdbvalue=sdbvalue & CStr(sdv) & ", "
      end if
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), )
    ret = ret + """
      if sdbvalue="" then
         sdbvalue="&nbsp;-&nbsp;"
      else
         sdbvalue=left(trim(sdbvalue),len(sdbvalue)-2)
      end if
      if svbvaluecnt=1 then
         if sdbvalue1="" then
            sdbvalue1="&nbsp;-&nbsp;"
         end if
         Response.Write sdbvalue1
      else
         Response.Write sdbvalue
      end if
      Response.Write "</OPTION>" & chr(10)
      rsdd1.MoveNext
   Loop
   Response.Write "</SELECT>"
"""
    ret = ret + """
else
"""
    if aisdialog:
        ret = ret + ShowSingleValueFromExternalDict(dbfield, arsnum='tmpdict', arsbasenum=-1, anoref=1, asvariable='mydictvalue', awhere='awhere', aisedit=1)
        arequired = ''
        if dbfield.IsObligatory:
            arequired = " REQUIRED='1'"
        ret = ret + '''
      Response.Write "<INPUT type=hidden id='%s' name='%s' value='" & mydictvalueoid & "'%s>"
      Response.Write "<INPUT type=text size=40 readonly=yes style='BACKGROUND-COLOR:#f0f0f0;' id='%sVisible' name='%sVisible' value=""" & server.htmlencode(mydictvalue) & """%s>"
''' % (dbfield.Name, dbfield.Name, arequired, dbfield.Name, dbfield.Name, arequired)
        if dbfield.FieldValuePreviewLink:
            afdictpage = dbfield.FieldValuePreviewLink
        else:
            afdictpage = 'BZR_%d_sv.asp' % (dbfield.DictSourceTable.ID, )
        if dbfield.ModelXMLDataIDEdit:
            afdictpage = 'xmldata_BZR_%d_sv.asp' % (dbfield.ModelXMLDataIDEdit, )
        if afdictpage != '-':
            ret = ret + """
   if ahidepreview=0 then
      Response.Write "&nbsp;<IMG alt='wybór ze słownika' src='/icormanager/images/icon_dictsearch.png' style='cursor:pointer;' onclick='javascript:showPopupFPDict(""%s"",""%s"",""my%sFrame"");'>"
   end if
""" % (afdictpage, dbfield.Name, dbfield.Name, )
        if not dbfield.IsObligatory:
            ret = ret + '''
   if ahidepreview=0 then
      Response.Write "&nbsp;<IMG alt='wyczyść pole' src='/icorimg/silk/erase.png' style='cursor:pointer;' onclick='javascript:jQuery(""#%s"").val("""");jQuery(""#%sVisible"").val("""");'>"
   end if
''' % (dbfield.Name, dbfield.Name, )
        ret = ret + """
      Response.Write "<br>"
      Response.Write "<iframe id=my%sFrame style='display:none;width:100%%;height:480px;'; ALLOWTRANSPARENCY=YES FRAMEBORDER=0 SCROLLING=YES></iframe>"
      end if
""" % (dbfield.Name, )
    else:
        ret = ret + """
   Response.Write "&nbsp;"
      end if
"""
    ret = ret + """
end if
if rsdd1.State<>adStateClosed then
   rsdd1.Close
end if
set rsdd1=Nothing
"""
    return ret


#*********************************************************************************
def ShowSingleValueFromExternalDictMultiple(dbfield, arsnum=1, arsbasenum=-1, anoref=0, afieldid=None, asvariable='', dbtable=None, aseparator=''):
    irsbasenum = arsbasenum
    if arsbasenum <= 0:
        irsbasenum = 0
        arsbasenum = ''
    else:
        arsbasenum = str(arsbasenum)
    if not isinstance(arsnum, types.StringTypes):
        if arsnum <= 0:
            arsnum = irsbasenum + 1
        arsnum = str(arsnum)
    ret = '''
' ShowSingleValueFromExternalDictMultiple - START
'''
    if asvariable:
        ret = ret + """
   %s=""
   %soid=""
""" % (asvariable, asvariable, )
    ret = ret + """      
if rs%s.State<>adStateClosed then                                                                      
if not (rs%s.EOF or rs%s.BOF) then
""" % (arsbasenum, arsbasenum, arsbasenum, )

    if dbtable is None:
        dbtable = dbfield
        aDictSourceTable = dbfield.DictSourceTable
    else:
        aDictSourceTable = dbtable

    aquery = MSQLQuery.QuerySQL()
    aquery.PushTable(dbtable)
    aoidfield = aquery.ThisTable.Fields['_OID']
    if afieldid is None:
        afieldid = '"%s"' % dbfield.Name
    elif isinstance(afieldid, types.StringTypes):
        afieldid = '"%s"' % afieldid
    else:
        afieldid = str(afieldid)
#   d={'type':'like', 'value':'"%%"+rs%s(%s)+"%%"'%(arsbasenum,afieldid), 'astext':'1'}
    d = {'type': 'like', 'value': """'"+rs%s(%s)+"' LIKE '%%'+%s+'%%'""" % (arsbasenum, afieldid, aoidfield.NameSQL), 'astext': '1'}
    aoidfield.AddRule(d)
    aquery.AsSQL()
    ret = ret + """
Set rs%(rsnum)s = Server.CreateObject("ADODB.Recordset")
rs%(rsnum)s.ActiveConnection = cn
rs%(rsnum)s.CursorType = adOpenStatic
rs%(rsnum)s.LockType = adLockOptimistic
rs%(rsnum)s.Source = "%(asqlstring)s"
rs%(rsnum)s.Open
""" % {'rsnum': arsnum, 'asqlstring': aquery.SQLString}
    ret = ret + """
if not (rs%s.EOF or rs%s.BOF) then
 sdbtoptable=""
 sdbheadertable=""
""" % (arsnum, arsnum, )
    lfields = aquery.AsColumnFields(aincludesqlaliased=1)
    for afield in lfields:
        if (afield.IsAliased or afield.IsSQLAliased) and afield.TypeDescription != 'HTML' and not afield.IsDictViewHidden and not afield.Name[:1] == '_' and aquery.FieldsDict[afield.NameSQL] >= 0:
            ret = ret + """
   sdbheadertable=sdbheadertable & "<th>%s</th>"
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), )
    ret = ret + """
 sdbvaluetable=""
 sdbfootertable=""
 sdbseparator="%s"
 sdbfirstvalue=1
 do while not rs%s.EOF
   sdbvalue=""
   sdbvaluetable=sdbvaluetable & "<tr>"
   sdbfieldcnt=0
   if isempty(link_%s_%s) then
      link_%s_%s=true
   end if
""" % (aseparator, arsnum, dbfield.Name, aDictSourceTable.NameSQLID, dbfield.Name, aDictSourceTable.NameSQLID, )
    if asvariable:
        #bylo: %soid=CStr(rs%s("_OID"))
        ret = ret + """
   %soid=CStr(rs%s(0))
""" % (asvariable, arsnum)
#   ret=ret+"""
#' $$$ FIELDSLIST
#"""
#   for afield in aquery.FieldsList:
#      ret=ret+"""  %s - %s
#"""%(afield.NameSQL,aquery.FieldsDict.get(afield.NameSQL,-2))
    for afield in lfields:
        if (afield.IsAliased or afield.IsSQLAliased) and afield.TypeDescription != 'HTML' and not afield.IsDictViewHidden and not afield.Name[:1] == '_' and aquery.FieldsDict[afield.NameSQL] >= 0:
            ret = ret + """
' %s""" % (afield.NameSQL, )
            ret = ret + """
   dbv=rs%s(%d)
   if isnull(dbv) then
      dbv=""
   end if
""" % (arsnum, aquery.FieldsDict[afield.NameSQL])
            if afield.Type == 'bool':
                ret = ret + """
   if CBool(dbv) then
      dbv="Tak"
   else
      dbv="Nie"
   end if
"""
            ret = ret + """
   if CStr(dbv)<>"" then
      sdbfieldcnt=sdbfieldcnt+1
      sdbvalue=sdbvalue & CStr(dbv) & ", "
      if link_%s_%s then
""" % (dbfield.Name, aDictSourceTable.NameSQLID, )
            ret = ret + """
         sdbvaluetable=sdbvaluetable & "<td><a class=objectitemasanchor href='BZR_%d_so.asp?ioid=" & rs%s(%d) & "'>" & CStr(dbv) & "</a></td>"
""" % (aDictSourceTable.ID, arsnum, aquery.FieldsDict[aoidfield.NameSQL], )
            ret = ret + """
      else
         sdbvaluetable=sdbvaluetable & "<td>%s</td><td>" & CStr(dbv) & "</td>"
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), )
            ret = ret + """
      end if
   end if
"""

    ret = ret + """
   sdbvalue=trim(sdbvalue)
   if sdbvalue="" then
      sdbvalue="&nbsp;-&nbsp;"
   else
      sdbvalue=left(sdbvalue,len(sdbvalue)-1)
   end if
"""
    if anoref:
        if asvariable:
            ret = ret + """
   %s=sdbvalue
""" % (asvariable, )
        else:
            ret = ret + """
   if sdbfirstvalue=0 then
      Response.Write sdbseparator
   end if
   Response.Write sdbvalue
"""
    else:
        ret = ret + """
   if sdbfieldcnt>1 then
      sdbtoptable="<table id=dicttable_%s><thead><tr>" & sdbheadertable & "</tr></thead><tbody>"
      sdbfootertable="</tbody></table><script type='text/javascript'>jQuery(function (){makeTable('#dicttable_%s');});</script>"
   else
      if link_%s_%s then
         Response.Write  "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='BZR_%d_so.asp?ioid=" & rs%s(%d) & "'>" & sdbvalue & "</a>"
      else
         Response.Write sdbvalue
      end if
   end if
""" % (dbfield.Name, dbfield.Name, dbfield.Name, aDictSourceTable.NameSQLID, aDictSourceTable.ID, arsnum, aquery.FieldsDict[aoidfield.NameSQL])
    ret = ret + """
   sdbvaluetable=sdbvaluetable & "</tr>"

   sdbfirstvalue=0
   rs%s.MoveNext
   loop
   if sdbtoptable<>"" then
       Response.Write sdbtoptable
       Response.Write sdbvaluetable
       Response.Write sdbfootertable
   end if
else
   Response.Write "&nbsp;"
end if
if rs%s.State<>adStateClosed then
   rs%s.Close
end if
Set rs%s=Nothing
""" % (arsnum, arsnum, arsnum, arsnum)
    if not asvariable:
        ret = ret + """
else
   Response.Write "&nbsp;"
"""
    ret = ret + """
end if
end if
' ShowSingleValueFromExternalDictMultiple - END
"""
    return ret


#*********************************************************************************
def ShowSingleValueFromExternalDict(dbfield, arsnum=1, arsbasenum=-1, anoref=0, afieldid=None, asvariable='', awhere='', aisedit=0):
    irsbasenum = arsbasenum
    if arsbasenum <= 0:
        irsbasenum = 0
        arsbasenum = ''
    else:
        arsbasenum = str(arsbasenum)
    if not isinstance(arsnum, types.StringTypes):
        if arsnum <= 0:
            arsnum = irsbasenum + 1
        arsnum = str(arsnum)
    if afieldid is None:
        afieldid = '"%s"' % dbfield.Name
    else:
        afieldid = str(afieldid)
    axmlid = dbfield.ModelXMLDataIDView
    if aisedit:
        axmlid = dbfield.ModelXMLDataIDEdit
    if axmlid:
        amodelxml = dbfield.Table.Creator.CRM.GetTableXMLDataByID(axmlid, anoparse=1)
        amodelxml.Parse(anoassql=1)
        aquery = amodelxml.Parser.querysql
    else:
        aquery = MSQLQuery.QuerySQL()
        aquery.PushTable(dbfield)
    aquery.Clear()
    aoidfield = aquery.ThisTable.Fields['_OID']

    ret = ''
    if asvariable:
        ret = ret + """
   %s=""
   %soid=""                          
""" % (asvariable, asvariable, )
    ret = ret + """      
rstmpwhere=""
if rs%s.State<>adStateClosed then
   if not (rs%s.EOF or rs%s.BOF) then
      rstmpwhere=CStr(rs%s(%s))
   end if
end if
""" % (arsbasenum, arsbasenum, arsbasenum, arsbasenum, afieldid, )
    if awhere != '':
        ret = ret + """
if %s<>"%%" and %s<>"" then
   rstmpwhere=%s
end if
""" % (awhere, awhere, awhere)
    ret = ret + """
if rstmpwhere<>"" then
"""

    d = {'type': 'eq', 'value': 'rstmpwhere', 'asasp': '1'}
    aoidfield.AddRule(d)
    aquery.IsASPStrings=1
    aquery.AsSQL()
    ret = ret + """
Set rs%(rsnum)s = Server.CreateObject("ADODB.Recordset")
rs%(rsnum)s.ActiveConnection = cn
rs%(rsnum)s.CursorType = adOpenKeyset
rs%(rsnum)s.LockType = adLockOptimistic
rs%(rsnum)s.Source = "%(asqlstring)s"
rs%(rsnum)s.Open
""" % {'rsnum': arsnum, 'asqlstring': aquery.SQLString}
    ret = ret + """
if not (rs%s.EOF or rs%s.BOF) then
   sdbvalue=""
   sdbvaluetable=""
   sdbfieldcnt=0
   if isempty(link_%s_%s) then
      link_%s_%s=true
   end if
""" % (arsnum, arsnum, dbfield.Name, dbfield.DictSourceTable.NameSQLID, dbfield.Name, dbfield.DictSourceTable.NameSQLID, )
    if asvariable:
        #bylo: %soid=CStr(rs%s("_OID"))
        ret = ret + """
   %soid=CStr(rs%s(%s))
""" % (asvariable, arsnum, aquery.FieldsDict[aoidfield.NameSQL])
    amaxcol = 5
    if dbfield.ModelXMLDataIDView:
        amaxcol = 100
        lfields = aquery.FieldsList
    else:
        lfields = aquery.AsColumnFieldsQuery(amaxcol=amaxcol)
#   ret=ret+"""
#' $$$ FIELDSLIST
#"""
#   for afield in aquery.FieldsList:
#      ret=ret+"""  %s - %s
#"""%(afield.NameSQL,aquery.FieldsDict.get(afield.NameSQL,-2))
    for afield in lfields:
        if (dbfield.ModelXMLDataIDView) and (afield.Type in ['external dict', 'external dict multiple']):
            continue
        if afield.IsAliased and afield.TypeDescription != 'HTML' and not afield.IsDictViewHidden and not afield.Name[:1] == '_' and aquery.FieldsDict[afield.NameSQL] >= 0:
            ret = ret + """
' %s""" % (afield.NameSQL, )
            ret = ret + """
   dbv=rs%s(%d)
   if isnull(dbv) then
      dbv=""
   end if
""" % (arsnum, aquery.FieldsDict[afield.NameSQL])
            if afield.Type == 'bool':
                ret = ret + """
   if CBool(dbv) then
      dbv="Tak"
   else
      dbv="Nie"
   end if
"""
            ret = ret + """
   if CStr(dbv)<>"" then
      sdbfieldcnt=sdbfieldcnt+1
      sdbvalue=sdbvalue & CStr(dbv) & ", "
      if link_%s_%s then
""" % (dbfield.Name, dbfield.DictSourceTable.NameSQLID, )
            ret = ret + """
         sdbvaluetable=sdbvaluetable & "<tr><td class=objectseditdatafieldname>%s</td><td class=objectseditdatafieldvalue><a class='fg-button-single ui-state-default ui-corner-all uihover' href='BZR_%d_so.asp?ioid=" & rs%s(%d) & "'>" & CStr(dbv) & "</a></td></tr>"
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), dbfield.DictSourceTable.ID, arsnum, aquery.FieldsDict[aoidfield.NameSQL], )
            ret = ret + """
      else
         sdbvaluetable=sdbvaluetable & "<tr><td class=objectseditdatafieldname>%s</td><td class=objectseditdatafieldvalue>" & CStr(dbv) & "</td></tr>"
""" % (XMLUtil.GetAsXMLStringNoPL(afield.PrettyName), )
            ret = ret + """
      end if
   end if
"""

    ret = ret + """
   sdbvalue=trim(sdbvalue)
   if sdbvalue="" then
      sdbvalue="&nbsp;-&nbsp;"
   else
      sdbvalue=left(sdbvalue,len(sdbvalue)-1)
   end if
"""
    if anoref:
        if asvariable:
            ret = ret + """
   %s=sdbvalue
""" % (asvariable, )
        else:
            ret = ret + """
   Response.Write sdbvalue
"""
    else:
        ret = ret + """
   if sdbfieldcnt>1 then
      Response.Write "<div style='border:2px dotted #bbccee;'><table>"
      Response.Write sdbvaluetable
      Response.Write "</table></div>"
   else
      if link_%s_%s then
         Response.Write  "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='BZR_%d_so.asp?ioid=" & rs%s(%d) & "'>" & sdbvalue & "</a>"
      else
         Response.Write sdbvalue
      end if
   end if
""" % (dbfield.Name, dbfield.DictSourceTable.NameSQLID, dbfield.DictSourceTable.ID, arsnum, aquery.FieldsDict[aoidfield.NameSQL])
    ret = ret + """
else
   Response.Write "&nbsp;"
end if
if rs%s.State<>adStateClosed then
   rs%s.Close
end if
Set rs%s=Nothing
""" % (arsnum, arsnum, arsnum)
    if not asvariable:
        ret = ret + """
else
   Response.Write "&nbsp;"
"""
    ret = ret + """
end if 'rstmpwhere
"""
    return ret


#*********************************************************************************
def GetSQLSP_GetUpdateRandomIDByLen():
    ret = """

GO

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[GetUpdateRandomIDByLen]'))
drop procedure [dbo].[GetUpdateRandomIDByLen]

GO

CREATE PROCEDURE GetUpdateRandomIDByLen  @atablename varchar(200), @afieldname varchar(200), @apinlen int=8  AS
SET NOCOUNT ON
declare @ssql varchar(4000)
set @atablename='konta'
set @afieldname='pin'
set @ssql='declare @pin varchar(50);'
set @ssql=@ssql+'declare @aoid varchar(44);'
set @ssql=@ssql+'declare @i int, @n int;'
set @ssql=@ssql+'DECLARE acursor CURSOR FOR SELECT _OID FROM '+ @atablename +' WHERE '+ @afieldname +'='''';'
set @ssql=@ssql+'OPEN acursor;'
set @ssql=@ssql+'FETCH NEXT FROM acursor INTO @aoid;'
set @ssql=@ssql+'WHILE @@FETCH_STATUS = 0'
set @ssql=@ssql+'    BEGIN'
set @ssql=@ssql+'       set @n=1'
set @ssql=@ssql+'       set @pin='''''
set @ssql=@ssql+'       while @pin='''''
set @ssql=@ssql+'          begin'  
set @ssql=@ssql+'             if @n=7'
set @ssql=@ssql+'                Break' 
set @ssql=@ssql+'             set @i=1'
set @ssql=@ssql+'             set @pin=@pin+char(49+floor(9*rand()))'
set @ssql=@ssql+'             while @i<'+cast(@apinlen as varchar(20))
set @ssql=@ssql+'                begin'
set @ssql=@ssql+'                   set @pin=@pin+char(48+floor(10*rand()))'
set @ssql=@ssql+'                   set @i=@i+1'
set @ssql=@ssql+'                end'
set @ssql=@ssql+'             if not exists(select _OID from '+ @atablename +' where '+ @afieldname +'=@pin)'
set @ssql=@ssql+'                begin'
set @ssql=@ssql+'                   update '+ @atablename +' set '+ @afieldname +'=@pin where _OID=@aoid'
set @ssql=@ssql+'                   break'
set @ssql=@ssql+'                end'
set @ssql=@ssql+'             else'
set @ssql=@ssql+'                set @pin='''''
set @ssql=@ssql+'             set @n=@n+1'
set @ssql=@ssql+'          end'
set @ssql=@ssql+'       FETCH NEXT FROM acursor INTO @aoid'
set @ssql=@ssql+'    END;'
set @ssql=@ssql+'CLOSE acursor;'
set @ssql=@ssql+'DEALLOCATE acursor'
exec(@ssql)
SET NOCOUNT OFF

GO

"""
    return ret


#*********************************************************************************
def SQLShowTableFromQuery(aquery, acaption=''):
    if isinstance(aquery, types.StringTypes):
        asql = aquery
    ret = """
rs.Open "%s", cn
if not rs.EOF then
   Response.Write("<span class='objectsviewcaption'>%s</span>")
   Response.Write("<TABLE class='objectsviewtable'>")
   Response.Write("<TR>")
   For i = 1 To rs.Fields.Count-1
      Response.Write "<TH class='objectsviewheader'>" & rs.Fields(i).Name & "</TH>"
   Next
   Response.Write("</TR>")
   Do While Not rs.EOF
      Response.Write "<TR class='objectsviewrow'>"
'      aoid=rs.Fields(0).Value
      For i = 1 to rs.Fields.Count-1
         Response.Write "<td class='objectsviewdataeven'>"
'         Response.Write "<a class='objectitemasanchor' href='__procent__s.asp?ioid=" & cstr(aoid) & "'>" & rs.Fields(i).Value & "</a>"
         Response.Write rs.Fields(i).Value
         Response.Write "</TD>"
      Next
      Response.Write "</TR>"
      rs.MoveNext   
   Loop
   Response.Write("</TABLE>")
end if
""" % (asql, acaption)
    return ret


def GetEditorTemplatesAddOns(afield):
    ret = ''
    if 0:
        ddict = {'fieldname': afield.Name, }
        ret = ret + '''
<script language="javascript">
function editorImageClick%(fieldname)s() {
   window.parent.postMessage({
      type: 'editorButtonClick',
      ownerTab: window.ownerTab,
      ownerSheet: window.ownerSheet,
      mode: 'file',
      fieldname: '%(fieldname)s'
   }, '*');
}
</script>
<a class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:editorImageClick%(fieldname)s();">Wstaw plik</a>
''' % ddict
    btable = afield.DictSourceTable
    if afield.DictValues or type(btable) != type(-1):
        ret = ret + """
<script language="javascript">
function insert%s(aparam) {
   var atresc=aparam;
""" % (afield.Name, )
        for akey, avalue in afield.DictValues:
            if akey[:1] == '@':
                akey = akey[1:]
            ret = ret + """       
   if (aparam=="%s") {
      atresc="%s";
   }
""" % (ICORUtil.str2ProperID(akey), avalue)
        ret = ret + """
//   if (document.getElementById("insertmode%s")[0].checked) {
//      oEditor.EditorDocument.body.insertAdjacentHTML("beforeEnd",htmlDecode(atresc));
//   }
   if (jQuery("#insertmode2%s").get(0).checked) {
      CKEDITOR.instances['%s'].insertHtml(htmlDecode(atresc));
   }
   if (jQuery("#insertmode3%s").get(0).checked) {
      CKEDITOR.instances['%s'].setData(htmlDecode(atresc))
   }
}
</script>
<!--<input class=checkradio type=radio name=insertmode%s id=insertmode1%s checked>wstaw na końcu-->
<input class=checkradio type=radio name=insertmode%s id=insertmode2%s>wstaw w miejscu kursora
<input class=checkradio type=radio name=insertmode%s id=insertmode3%s checked>zastąp treść szablonem<br>
""" % (afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name, afield.Name)
        for akey, avalue in afield.DictValues:
            if akey[:1] == '@':
                akey = akey[1:]
            ret = ret + """
<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:insert%s('%s');">%s</button>
""" % (afield.Name, ICORUtil.str2ProperID(akey), akey)
        if type(btable) != type(-1) and btable is not None:
            atrescfield = ''
            ltitle = []
            for bfield in btable.Fields:
                if bfield.Type == 'text' and not atrescfield:
                    atrescfield = bfield.Name
                if len(ltitle) <= 2 and bfield.Type == 'string' and bfield.IsInteractive and bfield.IsAliased and not bfield.Name in ['InformacjaOpisCzynnosci', 'InformacjaDataWytworzenia', 'InformacjaOsobaOdpowiedzialna', 'InformacjaPodmiotUdostepniajacy']:
                    ltitle.append(bfield.Name)
            stitlefields = 'rstmpdict("' + '") & " " & rstmpdict("'.join(ltitle) + '")'
            dd = {'fieldname': afield.Name, 'sql': 'SELECT * FROM %s' % (btable.NameSQL, ), 'titlefields': stitlefields, 'trescfield': atrescfield, }
            ret = ret + '''
<select id=dbtemplates_%(fieldname)s name=dbtemplates_%(fieldname)s>
<option value="">*** dostępne szablony ***</option>
<%%
Set rstmpdict = Server.CreateObject("ADODB.Recordset")
rstmpdict.ActiveConnection = cn
rstmpdict.CursorType = adOpenKeyset
rstmpdict.LockType = adLockOptimistic
rstmpdict.Source = "%(sql)s"
rstmpdict.Open
sdadd=""
Do While Not rstmpdict.EOF
   Response.Write "<option value='" & rstmpdict("_OID") & "'>" & %(titlefields)s & "</option>"
   sdadd=sdadd & "<div style='display:none;' id=dbtemplates_%(fieldname)s_" & rstmpdict("_OID") & ">" & rstmpdict("%(trescfield)s") & "</div>"
   rstmpdict.MoveNext
Loop
if rstmpdict.State<>adStateClosed then
   rstmpdict.Close                                                                                            
end if
Set rstmpdict=Nothing
%%>
</select>
<%%
Response.Write sdadd
%%>
<script language="javascript">
jQuery("#dbtemplates_%(fieldname)s").change(function(){
   var soid=jQuery("#dbtemplates_%(fieldname)s").val();
   if (soid!='') {
      atresc=jQuery("#dbtemplates_%(fieldname)s_"+soid).html();
      insert%(fieldname)s(atresc);
   }
});
</script>
''' % dd
    return ret


def GetShowSingleSelectTable(atable, abasers=-1, aeventsrc=None, aOnLoad1=None, lfields=None, afieldsdict=None):
    if abasers <= 0:
        abasers = 0
        sbasers = ''
    else:
        sbasers = str(abasers)

    ret = ''
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeSheetShowOneTable'):
        ret = ret + "\n' *** ASPSourceOnBeforeSheetShowOneTable -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnBeforeSheetShowOneTable
        ret = ret + "\n' *** ASPSourceOnBeforeSheetShowOneTable -- END ***\n"

    ret = ret + """
   Response.Write("<TABLE>")
"""
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeFieldsSheetShowOneTable'):
        ret = ret + "\n' *** ASPSourceOnBeforeFieldsSheetShowOneTable -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnBeforeFieldsSheetShowOneTable
        ret = ret + "\n' *** ASPSourceOnBeforeFieldsSheetShowOneTable -- END ***\n"

    if aOnLoad1 is None:
        aOnLoad1 = []
    i = 1
    if lfields is None:
        lfields = atable.FieldsByTabID
    alastgroup = ''
    for afield in lfields:
        #         if afield.Name[:1]!='_' and (afield.IsInteractive or afield.IsAliased):
        if afield.Name[:1] != '_' and not afield.IsSingleViewHidden:    #afield.IsInteractive or afield.IsAliased
            if afieldsdict is None:
                afieldnamesql = '"%s"' % afield.Name
            else:
                afieldnamesql = str(afieldsdict[afield.NameSQL])
            if afield.PrettyName in ['Informacja podmiot udostępniający', 'Informacja osoba odpowiedzialna', 'Informacja data wytworzenia', 'Informacja opis czynności']:
                stdfieldnameclass, sfieldvalueclass = 'objectseditsysteminfo', 'objectseditsysteminfovalue'
            else:
                stdfieldnameclass, sfieldvalueclass = 'objectseditdatafieldname', 'objectseditdatafieldvalue'
            wclose = 1
            ret = ret + """
currentFieldName="%s"
currentFieldGroup="%s"
currentFieldNum="%d"
""" % (afield.Name, afield.Group, i)
            if afield.Group != alastgroup:
                ret = ret + """
Response.Write "<TR id=""GROUP_%s"" class=""ui-widget-header""><TD colspan=""2"">%s</TD></TR>"
""" % (afield.Name, afield.Group)
                alastgroup = afield.Group

            aASPSourceOnBeforeFieldSheetShowOne = ''
            aASPSourceOnAfterFieldSheetShowOne = ''
            if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeFieldsSheetShowOneTable'):
                eobj = aeventsrc.GetFieldEventsObj(afield.Name)
                if eobj:
                    while eobj:
                        if eobj.EventKind.EventName == 'ASPSourceOnBeforeFieldSheetShowOne':
                            s = aeventsrc.GetFieldEventText(eobj)
                            aASPSourceOnBeforeFieldSheetShowOne = aASPSourceOnBeforeFieldSheetShowOne + s
                        if eobj.EventKind.EventName == 'ASPSourceOnAfterFieldSheetShowOne':
                            s = aeventsrc.GetFieldEventText(eobj)
                            aASPSourceOnAfterFieldSheetShowOne = aASPSourceOnAfterFieldSheetShowOne + s
                        eobj.Next()

            if aASPSourceOnBeforeFieldSheetShowOne:
                ret = ret + "\n' *** ASPSourceOnBeforeFieldSheetShowOne -- START ***\n"
                ret = ret + aASPSourceOnBeforeFieldSheetShowOne
                ret = ret + "\n' *** ASPSourceOnBeforeFieldSheetShowOne -- END ***\n"

            if not afield.TypeDescription in ['HTML', 'Arkusz']:
                ret = ret + '   Response.Write "<TR id=""FIELD_%s"" VALIGN=top class=objectseditrow><td class=%s>%s:%s</td><td class=%s>"\n' % (afield.Name, stdfieldnameclass, afield.PrettyName, afield.DescriptionName, sfieldvalueclass)
            if afield.Type == 'bool':
                ret = ret + """
at1rsvalue=rs%s.Fields(%s).Value
if not isnull(at1rsvalue) then
   if CBool(at1rsvalue) then
      Response.Write "Tak"
   else
      Response.Write "Nie"
   end if
end if
""" % (sbasers, afieldnamesql, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            elif afield.Type == 'money':
                ret = ret + """
      Response.Write Currency2HTML(rs%s.Fields(%s).Value,0)
""" % (sbasers, afieldnamesql, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            elif afield.Type == 'external dict':
                ret = ret + ShowSingleValueFromExternalDict(afield, arsnum=abasers + 1, arsbasenum=abasers)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            elif afield.Type == 'external dict multiple':
                ret = ret + ShowSingleValueFromExternalDictMultiple(afield, arsnum=abasers + 1, arsbasenum=abasers)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + """
      sd=CStr(rs%s.Fields(%s).Value)
      sds=sd
""" % (sbasers, afieldnamesql, )
                for akey, avalue in afield.DictValues:
                    ret = ret + """
      if sd="%s" then
         sds="%s"
      end if 
""" % (akey, avalue)
                ret = ret + """
      if (sds="") and (sd<>"") then
         sds=sd
      end if
      Response.Write sds
"""
                if afield.OID >= 0:
                    ret = ret + 'Response.Write "&nbsp;<a href=\'dictgraphs/%d_%d_%s.png\' target=\'_new\'><img valign=middle vspace=0 border=0 src=\'/icormanager/images/icons/silk/icons/share.png\' alt=\'Diagram przejść stanów\'></a>"\n' % (afield.CID, afield.OID, afield.Name, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            else:
                if afield.TypeDescription == 'HTML':
                    ret = ret + '   Response.Write "</table><br><table width=\'100%\'>"\n'
                    ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldnameleftalign>%s:</td></tr>"\n' % (afield.PrettyName)
                    ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldvaluehtml>"\n'
                    ret = ret + '   stext=rs%s.Fields(%s).Value\n' % (sbasers, afieldnamesql, )
                    ret = ret + '   stext=replace(stext,"<!--*","")\n'
                    ret = ret + '   stext=replace(stext,"*-->","")\n'
                    ret = ret + '   Response.Write stext\n'
                    ret = ret + '   Response.Write "</td></tr></table><br><table>"\n'
                    wclose = 0
                elif afield.TypeDescription == 'Arkusz':
                    ahref = '%s_gfv.asp?ioid=<%%=Request.QueryString("ioid")%%>&afield=%s' % (atable.NameFile, afield.Name)
                    ret = ret + '   Response.Write "</table><br><table width=\'100%\'>"\n'
                    ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldnameleftalign>%s:</td></tr>"\n' % (afield.PrettyName)
                    ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldvalue>"\n'
                    ret = ret + """

aarkuszid=""
astanprzeliczenia=""
adatetime=""
Set rs1x = Server.CreateObject("ADODB.Recordset")
rs1x.ActiveConnection = cn
rs1x.CursorType = adOpenKeyset
rs1x.LockType = adLockOptimistic
rs1x.Source = "select _OID,NazwaTabeli,NazwaPola,OIDArkusza,NazwaArkusza,StanPrzeliczenia,_datetime from TMP_SHEETINFO_0 WHERE (OIDArkusza='" & Request.QueryString("ioid") & "') AND (NazwaPola='%s')"
rs1x.Open
if not rs1x.EOF then
   aarkuszid=rs1x("NazwaArkusza")
   select case rs1x("StanPrzeliczenia")
     case 1: astanprzeliczenia="czeka na przeliczenie"
     case 2: astanprzeliczenia="jest w trakcie przeliczenia"     
     case 3: astanprzeliczenia="jest przeliczony"
     case else: astanprzeliczenia="nieznany stan - skontaktuj się z administratorem!"
   end select
   adatetime=rs1x("_datetime")
end if
if rs1x.State<>adStateClosed then
   rs1x.Close
end if
set rs1x=Nothing
Response.Write "<div align=left width='100%%' style='background:buttonface;'>&nbsp;&nbsp;ID Arkusza:&nbsp;<b>" & aarkuszid & "</b>, " & astanprzeliczenia & ", <i>" & adatetime & "</i></div>"
%%>""" % (afield.Name, )
                    atext, aonloadtext, aOnBeforeLoadText, aOnAfterLoadText = GetWorksheetText(aid=afield.Name, aheight="480px", ahref=ahref, aviewonly=1)
                    aOnLoad1.append([aonloadtext, aOnBeforeLoadText, aOnAfterLoadText])
                    ret = ret + atext
                    ret = ret + """
<%
"""
                    ret = ret + '   Response.Write "</td></tr></table><br><table>"\n'
                    wclose = 0
                elif afield.TypeDescription == 'EMail':
                    ret = ret + 'if CStr(rs%s.Fields(%s).Value)<>"" then\n' % (sbasers, afieldnamesql, )
                    ret = ret + '   Response.Write "<img src=\'/icormanager/images/wfxtree/items/Add_Command_FileMail_Recipient.png\'>&nbsp;<a href=\'mailto:" & rs%s.Fields(%s).Value & "\'>" & rs%s.Fields(%s).Value & "</a>"\n' % (sbasers, afieldnamesql, sbasers, afieldnamesql, )
                    ret = ret + 'end if\n'
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                elif afield.TypeDescription == 'URL':
                    ret = ret + 'if CStr(rs%s.Fields(%s).Value)<>"" then\n' % (sbasers, afieldnamesql, )
                    ret = ret + '   Response.Write "<img src=\'/icormanager/images/wfxtree/items/Add_Command_WebHyperlink.png\'>&nbsp;<a href=\'" & rs%s.Fields(%s).Value & "\' target=\'_new\'>" & rs%s.Fields(%s).Value & "</a>"\n' % (sbasers, afieldnamesql, sbasers, afieldnamesql, )
                    ret = ret + 'end if\n'
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                elif afield.TypeDescription == 'Kolor':
                    ret = ret + 'if CStr(rs%s.Fields(%s).Value)<>"" then\n' % (sbasers, afieldnamesql, )
                    ret = ret + '   Response.Write rs%s.Fields(%s).Value & "&nbsp;<span style=\'background:" & rs%s.Fields(%s).Value & ";border:1px dotted #000000;\'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>"\n' % (sbasers, afieldnamesql, sbasers, afieldnamesql, )
                    ret = ret + 'end if\n'
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                elif afield.TypeDescription == 'Opis':
                    if afield.TextNoWrap == 'On':
                        ret = ret + """
arsValue=rs%s.Fields(%s).Value
Response.Write "<pre>"
Response.Write arsValue
Response.Write "</pre>"
Response.Write "%s"
""" % (sbasers, afieldnamesql, afield.DescriptionValue)
                    else:
                        ret = ret + """
arsValue=rs%s.Fields(%s).Value
Response.Write arsValue
Response.Write "%s"
""" % (sbasers, afieldnamesql, afield.DescriptionValue)
                else:
                    ret = ret + """
arsValue=rs%s.Fields(%s).Value
arsType=rs%s.Fields(%s).Type
if (arsType=7) or (arsType=133) or (arsType=134) or (arsType=135) then
   arsValue=getDateTimeAsStr(arsValue)
end if
call UpdateLastVisitHistoryValue("%s",arsValue)
""" % (sbasers, afieldnamesql, sbasers, afieldnamesql, afield.PrettyName)
                    if afield.IsU2ULink:
                        ret = ret + '''   Response.Write "<img align=middle align=top vspace=0 src='/icormanager/images/icons/silk/icons/link_go.png'>&nbsp;<a href=u2u.asp?t=1&amp;v1=" & Request.QueryString("ioid") & "&amp;v2=" & aTableID & ">" & Server.HTMLEncode(Replace(Replace(arsValue,"""","`"),"'","`")) & "</a>"\n'''
                    else:
                        ret = ret + '   Response.Write arsValue\n'
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
            if wclose:
                ret = ret + '   Response.Write "</td></tr>"\n'

            if aASPSourceOnAfterFieldSheetShowOne:
                ret = ret + "\n' *** ASPSourceOnAfterFieldSheetShowOne -- START ***\n"
                ret = ret + aASPSourceOnAfterFieldSheetShowOne
                ret = ret + "\n' *** ASPSourceOnAfterFieldSheetShowOne -- END ***\n"

        i = i + 1

    if afieldsdict is None:
        afieldnamesql = '"_UserName"'
    else:
        ifieldnamesql = afieldsdict.get(atable.NameSQL + '._UserName', -1)
        if ifieldnamesql >= 0:
            afieldnamesql = str(afieldsdict[atable.NameSQL + '._UserName'])
        else:
            afieldnamesql = ''
    if afieldnamesql:
        ret = ret + """
      arsValue=rs%s.Fields(%s).Value
      if arsValue<>"" then 
         Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditsysteminfo>Zmodyfikował:</td><td class=objectseditsysteminfovalue>"
         Response.Write arsValue
         Response.Write "</td></tr>"
      end if
""" % (sbasers, afieldnamesql)

    if afieldsdict is None:
        afieldnamesql = '"_DateTime"'
    else:
        ifieldnamesql = afieldsdict.get(atable.NameSQL + '._DateTime', -1)
        if ifieldnamesql >= 0:
            afieldnamesql = str(afieldsdict[atable.NameSQL + '._DateTime'])
        else:
            afieldnamesql = ''
    if afieldnamesql:
        ret = ret + """
      arsValue=getDateTimeAsStr(rs%s.Fields(%s).Value)
      if arsValue<>"" then
         Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditsysteminfo>Data modyfikacji:</td><td class=objectseditsysteminfovalue>"
         Response.Write arsValue
         Response.Write "</td></tr>"
      end if
""" % (sbasers, afieldnamesql)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnAfterFieldsSheetShowOneTable'):
        ret = ret + "\n' *** ASPSourceOnAfterFieldsSheetShowOneTable -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnAfterFieldsSheetShowOneTable
        ret = ret + "\n' *** ASPSourceOnAfterFieldsSheetShowOneTable -- END ***\n"

    ret = ret + """
   Response.Write "</TABLE>"
"""

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnAfterSheetShowOneTable'):
        ret = ret + "\n' *** ASPSourceOnAfterSheetShowOneTable -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnAfterSheetShowOneTable
        ret = ret + "\n' *** ASPSourceOnAfterSheetShowOneTable -- END ***\n"
    return ret


def CheckFieldColumnVisibility(afield, averbose=0):
    w = 0
    if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', 'external dict multiple']:
        w = 1
    if hasattr(afield, 'Table') and afield.Table is not None and not afield.Table.IsSQLView:
        if averbose:
            print '  afield.Table %s' % (afield.Table.NameSQL, )
        if hasattr(afield.Table, 'RevContextField') and afield.Table.RevContextField != '':
            if averbose:
                print '    afield.Table.RevContextField %s' % (afield.Table.RevContextField, )
            if hasattr(afield.Table, 'ParentTable') and afield.Table.ParentTable is not None:
                qfield = afield.Table.ParentTable.FieldsByName(afield.Table.RevContextField)
                if qfield is None and afield.Table.RevContextField == '_Dotyczy':
                    #print '$$ _dotyczy is None:',afield.Table.Name,afield.Name
                    if averbose:
                        print '      afield.Table.RevContextField A0'
                    w = 0
                elif (qfield is not None) and (qfield.Type in ['external dict multiple', ]):
                    if averbose:
                        print '      qfield.Type A1'
                    w = 0
    return w
