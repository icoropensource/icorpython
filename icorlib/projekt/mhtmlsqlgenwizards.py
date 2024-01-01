# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.projekt.mhtmlsqlgenlib as MHTMLSQLGenLib
from icorlib.wwwhtml.main import *
import icorlib.wwwhtml.fckmain as FCKMain
from icorlib.wwwhtml.worksheetmain import *
import string


#*********************************************************************************
def GetWizardMainPage(awizard, akreatortable):
    ret = """
Response.Write "<br>"
if CheckUserAccess("%s")=1 then
   abr=1
   Response.Write "<a class=reflistoutnavy href='%s.asp'>Nowy wpis</a><br>"
   Response.Write "<hr>"
end if
""" % (awizard.AccessLevelView, awizard.NewPage, )
    if awizard.steps:
        ret = ret + """
if CheckUserAccess("%s")=1 then 'Wizard - AccessLevelView
   Set rs1=Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenStatic
   rs1.LockType = adLockOptimistic
   rs1.Source = "select top 100 _OID,DokumentID,DokumentOID,KreatorEtapID,KreatorEtapOID,KreatorID,KreatorInfo,KreatorOID,StanEtapu,_datetime,_UserName from %s WHERE DokumentOID='-1' AND KreatorID=%d AND KreatorEtapID=%d ORDER BY _datetime DESC"
   rs1.Open
   if not rs1.EOF then
      Response.Write("<span class='objectsviewcaption'>%s</span>")
      Response.Write("<TABLE class='objectsviewtable'>")
      Response.Write("<TR>")
      Response.Write "<TH class='objectsviewheader'>Ostatnio zmodyfikowany</TH>"
      Response.Write "<TH class='objectsviewheader'>Przez</TH>"
      Response.Write "<TH class='objectsviewheader'>Stan zaawansowania</TH>"
      Response.Write "<TH class='objectsviewheader' colspan=2>Opis</TH>"
      Response.Write("</TR>")                 
      Do While Not rs1.EOF
            Response.Write "<TR class='objectsviewrow'>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "'>" & rs1.Fields("_datetime").Value & "</a>"
            Response.Write "</TD>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "'>" & rs1.Fields("_UserName").Value & "</a>"
            Response.Write "</TD>"
            if rs1.Fields("StanEtapu").Value>0 then
               Response.Write "<td class='objectsviewdataeven'>"
               sz="zakończony"
            else
               Response.Write "<td class='objectsviewdataeven' align=center>"
               sz="&nbsp;-&nbsp;"
            end if
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "'>" & sz & "</a>"
            Response.Write "</TD>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<img style='cursor:pointer;' src='/icormanager/images/tree/menu_link_txt.png' alt='Edycja opisu pozycji' onclick='javascript:window.location=""DOKKREATOR_0_au.asp?ioid=" & rs1("_OID") & "&wlocation=" & Server.HTMLEncode("%s.asp") & "&x=1"";'>&nbsp;"
            Response.Write "</TD>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "'>" & rs1.Fields("KreatorInfo") & "&nbsp;</a>"
            Response.Write "</TD>"
         Response.Write "</TR>"
         rs1.MoveNext
      Loop
      Response.Write("</TABLE><BR>")
   end if
   if rs1.State<>adStateClosed then
      rs1.Close
   end if
   set rs1=Nothing
end if
""" % (awizard.AccessLevelView, awizard.CRM.Table_DokKreator.NameSQL, awizard.OID, awizard.steps[0].OID, awizard.Title, awizard.steps[0].OID, awizard.steps[0].OID, awizard.steps[0].OID, awizard.NameFile, awizard.steps[0].OID)
    return ret


#*********************************************************************************
# pmode: 0-show, 1-submit
def GetWizardStepPage(awizard, astep, prevstep, nextstep, adoketapytable, akreatortable):
    #   Response.Write "<input type=hidden id='_OID' name='_OID' size=20 value='" & CStr(aoid) & "'>"
    #   Response.Write "<input type=hidden id='_BOID' name='_BOID' size=20 value='" & CStr(boid) & "'>"

    wlast = astep.OID == nextstep.OID
    wfirst = astep.OID == prevstep.OID

    ret = """
WizardStepRepeat=0
WizardStepRepeatMessage=""
WizardStepRepeatStatus=0

if Request.QueryString("stepmode")="1" then
   stepmode="submit"
else
   stepmode="show"
end if

if Request.QueryString("ioid")<>"" then
   aoid=Request.QueryString("ioid")
else
   aoid="-1"
end if

akreatoroid=""

if Request.QueryString("doktypeid")="" then
   adoktypeid="-1"
else
   adoktypeid=Request.QueryString("doktypeid")
end if

if Request.QueryString("dokid")="" then
   adokid="-1"
else
   adokid=Request.QueryString("dokid")
end if

if Request.QueryString("wizardmsg")<>"" then
   Response.Write "<h1><font color=red>" & Request.QueryString("wizardmsg") & "</font></h1>"
end if

if stepmode="show" then
   Response.Write "<br>"
   if adoktypeid<>"-1" then
      Response.Write "<a class=reflistoutnavy href='DOK_" & adoktypeid & "_so.asp?ioid=" & adokid & "'>Powrót do dokumentu</a><br>"
   else
      Response.Write "<a class=reflistoutnavy href='%s.asp'>Powrót do listy</a><br>"
   end if
""" % (awizard.NameFile, )
    if wfirst:
        ret = ret + """
      Set rs1 = Server.CreateObject("ADODB.Recordset")
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      if aoid="-1" then
         rs1.Source = "select _OID,DokumentID,DokumentOID,KreatorID,KreatorInfo,_UID,_UserName,_DateTime from %s where _OID='-1'"
         rs1.Open
         rs1.AddNew
         rs1("DokumentID")=adoktypeid
         rs1("DokumentOID")=adokid
         rs1("KreatorID")="%d"
         rs1("KreatorInfo")=""
         rs1("_UID")=Dession("uid")
         rs1("_UserName")=Dession("username")
         rs1("_DateTime")=Now
         rs1.Update
         Call SetItemHistory(rs1,"%s","Nowy kreator")
         akreatoroid=rs1("_OID")
      else
         rs1.Source = "select _OID,_KreatorOID from %s where _OID='" & aoid & "'"
         rs1.Open
         if not (rs1.EOF or rs1.BOF) then
            akreatoroid=rs1("_KreatorOID")
         end if
      end if
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      Set rs1=Nothing
      if akreatoroid="" then
         Response.Write "<h1>Nieznany typ kreatora dla pierwszego dokumentu</h1>"
         if rs.State<>adStateClosed then
            rs.Close
         end if
         Set rs=Nothing
         Response.End
      end if
""" % (akreatortable.NameSQL, awizard.OID, akreatortable.NameSQL, astep.SQLTable.NameSQL)
    else:
        ret = ret + """
      if aoid="-1" then
         akreatoroid=Request.QueryString("koid")
      else
         Set rs1 = Server.CreateObject("ADODB.Recordset")
         rs1.ActiveConnection = cn
         rs1.CursorType = adOpenKeyset
         rs1.LockType = adLockOptimistic
         rs1.Source = "select _OID,_KreatorOID from %s where _OID='" & aoid & "'"
         rs1.Open
         if not (rs1.EOF or rs1.BOF) then
            akreatoroid=rs1("_KreatorOID")
         end if                                                                    
         if rs1.State<>adStateClosed then
            rs1.Close
         end if
         Set rs1=Nothing
      end if
      if akreatoroid="" then
         Response.Write "<h1>Nieznany typ kreatora</h1>"
         if rs.State<>adStateClosed then
            rs.Close
         end if
         Set rs=Nothing
         Response.End
      end if
""" % (astep.SQLTable.NameSQL, )
#
    ret = ret + """
PrevEtapOID=""
"""
    if not wfirst:
        d = {'table': adoketapytable.NameSQL, 'woid': awizard.OID, 'poid': prevstep.OID, 'psoid': prevstep.OID}
        ret = ret + '''
   Set rs1 = Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select DokumentID,DokumentOID,KreatorID,KreatorOID,KreatorEtapID,KreatorEtapOID from  %(table)s WHERE DokumentID='" & adoktypeid & "' AND DokumentOID='" & adokid & "' AND KreatorID=%(woid)d AND KreatorOID='" & akreatoroid & "' AND KreatorEtapID=%(psoid)d"
   rs1.Open
   if not (rs1.EOF or rs1.BOF) then
      PrevEtapOID=rs1("KreatorEtapOID")
   end if
   if rs1.State<>adStateClosed then
      rs1.Close
   end if
   Set rs1=Nothing
''' % d
#
    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceShowBefore, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)

    ret = ret + """
   Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='%s.asp?stepmode=1&doktypeid=" & adoktypeid & "&dokid=" & adokid & "&ioid=" & aoid & "&koid=" & akreatoroid & "'>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), astep.NameFile)
    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceShowFieldsBefore, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)

    ret = ret + """
'   For Each key In Request.Form
'      Response.Write "<input type=hidden id='" & key & "' name='" & key & "' value='" & Request.Form(key) & "'>"
'   Next
   Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%%' border=1>"
   if aoid<>"-1" then
"""

    fls = ['_OID', ]
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_':
            fls.append(afield.Name)
    sf = string.join(fls, ',')
    ret = ret + """
rs.Open "select %s from %s WHERE _OID='" & aoid & "'", cn
""" % (sf, astep.SQLTable.NameSQL)
    i = 1
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
            ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s>"\n' % (snclass, afield.PrettyName, svclass, )
            if afield.Type == 'string':
                ds = 2 + int(afield.Size)
                if ds > 40:
                    ds = 40
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type in ['numeric', 'float']:
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'money':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'date':
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type == 'datetime':
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),15\n' % (afield.Name, afield.Name, i, i)
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),1\n' % (afield.Name, afield.Name, i, i)
            elif afield.Type == 'bool':
                ret = ret + """
   at1rsvalue=rs.Fields(%d).Value
   sd=""
   if not isnull(at1rsvalue) then
      if CBool(at1rsvalue) then
         sd=" Checked"
      end if
   end if
""" % (i, )
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\' " & sd & ">"\n' % (afield.Name, afield.Name)
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + """
sd=rs.Fields(%d).Value
wsd=0
Response.Write "<SELECT id='%s' name='%s'>"
""" % (i, afield.Name, afield.Name, )
                for akey, avalue in afield.DictValues:
                    ret = ret + """
   if sd="%s" then
      sds="SELECTED "
      wsd=1
   else
      sds=""
   end if
   Response.Write "<OPTION " & sds & "value='%s'>%s</OPTION>"
""" % (akey, akey, avalue)
                ret = ret + """
if (wsd=0) and (sd<>"") then
   Response.Write "<OPTION SELECTED value='" & sd & "'>" & sd & "</OPTION>"
end if
Response.Write "</SELECT>"
"""
            elif afield.Type == 'external dict':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelection(afield)
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=6 %s>" & rs.Fields(%d).Value & "</textarea>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield), i)
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield))
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            ret = ret + 'Response.Write "</td></tr>"\n'
            i = i + 1
    ret = ret + """
else
"""
    i = 1
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'

            ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s>"\n' % (snclass, afield.PrettyName, svclass, )
            if afield.Type == 'string':
                ds = 2 + int(afield.Size)
                if ds > 40:
                    ds = 40
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'\' %s>"\n' % (afield.Name, afield.Name, ds, afield.Size, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type in ['numeric', 'float']:
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type == 'money':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'date':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type == 'datetime':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),15\n' % (afield.Name, afield.Name, )
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),1\n' % (afield.Name, afield.Name, )
            elif afield.Type == 'bool':
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\'>"\n' % (afield.Name, afield.Name)
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + """
Response.Write "<SELECT id='%s' name='%s'>"
""" % (i, afield.Name, afield.Name, )
                for akey, avalue in afield.DictValues:
                    ret = ret + """
   sd="%s"
   sdv="%s"
   Response.Write "<OPTION value='" & sd & "'>" & sdv & "</OPTION>"
""" % (akey, avalue, )
                ret = ret + """
Response.Write "</SELECT>"
"""
            elif afield.Type == 'external dict':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelection(afield, aisnew=1)
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=6 %s></textarea>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            ret = ret + 'Response.Write "</td></tr>"\n'
            i = i + 1
    ret = ret + """
end if
"""
    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceShowFields, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)

    ret = ret + """
   Response.Write "</TABLE>"
   Response.Write "<br>"
"""
    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceShowFieldsAfter, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)
    #
    if not wfirst:
        d = {'table': adoketapytable.NameSQL, 'woid': awizard.OID, 'poid': prevstep.OID, 'psoid': prevstep.OID}
        ret = ret + '''
   if PrevEtapOID<>"" then
      spref="wizard_%(woid)d_%(poid)d.asp?ioid=" & PrevEtapOID & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
      Response.Write "<input class='pushbutton' type='button' onclick='javascript:window.location.href=""" & spref & """' value='  Poprzedni etap  ' tabIndex=1>&nbsp;&nbsp;"
   end if                                
''' % d
#
    if wlast:
        ret = ret + """
   Response.Write "<input class='pushbutton' TYPE='submit' VALUE='  Zapamiętaj  ' tabIndex=2></form>"
"""
    else:
        ret = ret + """
   Response.Write "<input class='pushbutton' TYPE='submit' VALUE='  Następny etap  ' tabIndex=2></form>"
"""

    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceShowAfter, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)
    # *** submit ***
    ret = ret + """
elseif stepmode="submit" then
   akreatoroid=Request.QueryString("koid")
   if Request.QueryString("ioid")<>"" then
      aoid=Request.QueryString("ioid")
   else
      aoid="-1"
   end if
"""
    fls = ['_OID', ]
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_':
            fls.append(afield.Name)
    sf = string.join(fls, ',')
    ret = ret + """
   rs.ActiveConnection = cn
   rs.CursorType = adOpenKeyset
   rs.LockType = adLockOptimistic
   rs.Source = "select %s,_KreatorID,_KreatorOID,_Dotyczy,_UID,_UserName,_DateTime from %s WHERE _OID='" & aoid & "'"
   rs.Open
   if aoid="-1" then
      rs.AddNew
   end if
""" % (sf, astep.SQLTable.NameSQL)
    i = 1
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if afield.Type == 'string':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type in ['numeric', 'money', 'float']:
                ret = ret + '         if IsNumeric(Request.Form("%s")) then rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name, afield.Name)
            elif afield.Type == 'date':
                ret = ret + '         rs("%s") = getStrAsDateTime(Request.Form("%s"),"","",%d)\n' % (afield.Name, afield.Name, afield.NoPastDate)
            elif afield.Type == 'datetime':
                ret = ret + '         rs("%s") = getStrAsDateTime(Request.Form("%s"),Request.Form("%s_h"),Request.Form("%s_mi"),%d)\n' % (afield.Name, afield.Name, afield.Name, afield.Name, afield.NoPastDate)
            elif afield.Type == 'bool':
                ret = ret + """
if Request.Form("%s")<>"" then 
   rs("%s") = "True"                                         
else
   rs("%s") = "False"
end if
""" % (afield.Name, afield.Name, afield.Name, )
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict':
                #$$
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'text':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'integer':
                ret = ret + '         if IsNumeric(Request.Form("%s")) then rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name, afield.Name)
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
        i = i + 1
    ret = ret + """
   if akreatoroid<>"" then
      rs("_KreatorID")="%d"
      rs("_KreatorOID")=akreatoroid
      rs("_Dotyczy")=adokid
   end if
   rs("_UID")=Dession("uid")
   rs("_UserName")=Dession("username")
   rs("_DateTime")=Now
   rs.Update
   if aoid="-1" then
      Call SetItemHistory(rs,"%s","Nowe dane dla etapu kreatora")
   else
      Call SetItemHistory(rs,"%s","Modyfikacja danych etapu kreatora")
   end if
""" % (awizard.OID, astep.SQLTable.NameSQL, astep.SQLTable.NameSQL)
    ret = ret + """
   if aoid="-1" then
      rsoid=rs("_OID")
      if rs.State<>adStateClosed then
         rs.Close
      end if
      rs.Source = "select %s,_KreatorID,_KreatorOID,_Dotyczy,_UID,_UserName from %s WHERE _OID='" & rsoid & "'"
      rs.Open
   end if
   """ % (sf, astep.SQLTable.NameSQL)
    ret = ret + """
      Set rs1 = Server.CreateObject("ADODB.Recordset")
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      rs1.Source = "select _OID,DokumentID,DokumentOID,KreatorID,KreatorOID,KreatorInfo,KreatorEtapID,KreatorEtapOID,StanEtapu,_UID,_UserName,_DateTime from %s where KreatorEtapOID='" & aoid & "'"
      rs1.Open
      if aoid="-1" then
         rs1.AddNew
         rs1("DokumentID")=adoktypeid
         rs1("DokumentOID")=adokid
         rs1("KreatorID")="%d"
         rs1("KreatorOID")=akreatoroid
         rs1("KreatorInfo")=""
         rs1("KreatorEtapID")="%d"
         rs1("KreatorEtapOID")=rs("_OID")
      else
         akreatoroid=rs1("KreatorOID")
      end if
      rs1("_UID")=Dession("uid")
      rs1("_UserName")=Dession("username")
      rs1("_DateTime")=Now
      rs1.Update
      if aoid="-1" then
         Call SetItemHistory(rs1,"%s","Rejestracja nowego etapu kreatora")
      else
         Call SetItemHistory(rs1,"%s","Rejestracja modyfikacji etapu kreatora")
      end if
      etapoid=rs1("_OID")
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      Set rs1=Nothing
""" % (adoketapytable.NameSQL, awizard.OID, astep.OID, adoketapytable.NameSQL, adoketapytable.NameSQL,
       )

    arepldict = {'aCRM': awizard.CRM, 'this': astep, 'aWizard': awizard, 'aPrevStep': prevstep, 'aNextStep': nextstep, 'isFirstStep': wfirst, 'isLastStep': wlast, }
    ret = ret + ICORUtil.GetTextAsHTMLText(astep.ASPSourceSubmit, repldict=arepldict, aengine=aICORDBEngine, aashtmlstring=0)

    ret = ret + """
if WizardStepRepeat=0 then
   cn.Execute "UPDATE %s SET StanEtapu=%d WHERE DokumentID='" & adoktypeid & "' AND DokumentOID='" & adokid & "' AND KreatorID=%d AND KreatorOID='" & akreatoroid & "'"
else
   cn.Execute "UPDATE %s SET StanEtapu=0 WHERE DokumentID='" & adoktypeid & "' AND DokumentOID='" & adokid & "' AND KreatorID=%d AND KreatorOID='" & akreatoroid & "'"
end if
""" % (adoketapytable.NameSQL, wlast, awizard.OID, adoketapytable.NameSQL, awizard.OID)

    if wlast:
        ret = ret + """
   Response.Write "<script language='javascript'>" & chr(10)
if WizardStepRepeat=1 then
   sst=""
   if WizardStepRepeatMessage<>"" then
      sst=sst & "&wizardmsg=" & Server.HTMLEncode(WizardStepRepeatMessage)
   end if
   if WizardStepRepeatStatus<>0 then
      sst=sst & "&wizardstatus=" & CStr(WizardStepRepeatStatus)
   end if
   Response.Write "window.location='%s.asp?ioid=" & rs("_OID") & "&stepmode=0&doktypeid=" & adoktypeid & "&dokid=" & adokid & "&koid=" & akreatoroid & sst & "';" & chr(10)
else
   if adoktypeid<>"-1" then
      Response.Write "window.location='DOK_" & adoktypeid & "_so.asp?ioid=" & adokid & "';" & chr(10)
   else
      Response.Write "window.location='%s.asp';" & chr(10)
   end if
end if
   Response.Write "</script>"
""" % (astep.NameFile, awizard.NameFile)
    else:
        ret = ret + """
   boid="-1"
   if aoid<>"-1" then
      Set rs1 = Server.CreateObject("ADODB.Recordset")
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      rs1.Source = "select _OID,KreatorEtapID,KreatorEtapOID,DokumentOID from %s where KreatorOID='" & akreatoroid & "' and KreatorEtapID='%d'"
      rs1.Open
      if not (rs1.EOF or rs1.BOF) then
         boid=rs1("KreatorEtapOID")
      end if
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      Set rs1=Nothing
   end if

   Response.Write "<script language='javascript'>" & chr(10)
if WizardStepRepeat=1 then
   sst=""
   if WizardStepRepeatMessage<>"" then
      sst=sst & "&wizardmsg=" & Server.HTMLEncode(WizardStepRepeatMessage)
   end if
   if WizardStepRepeatStatus<>0 then
      sst=sst & "&wizardstatus=" & CStr(WizardStepRepeatStatus)
   end if
   Response.Write "window.location='%s.asp?ioid=" & rs("_OID") & "&stepmode=0&doktypeid=" & adoktypeid & "&dokid=" & adokid & "&koid=" & akreatoroid & sst & "';" & chr(10)
else
   Response.Write "window.location='%s.asp?ioid=" & boid & "&stepmode=0&doktypeid=" & adoktypeid & "&dokid=" & adokid & "&koid=" & akreatoroid & "';" & chr(10)
end if
   Response.Write "</script>"
""" % (adoketapytable.NameSQL, nextstep.OID, astep.NameFile, nextstep.NameFile,
        )

    ret = ret + """
end if
"""
    return ret


#*********************************************************************************
def GetWizardStepShowOnePage(awizard, astep, prevstep, nextstep, adoketapytable):
    wlast = astep.OID == nextstep.OID
    wfirst = astep.OID == prevstep.OID

    ret = """

if Request.QueryString("doktypeid")="" then
   adoktypeid="-1"
else
   adoktypeid=Request.QueryString("doktypeid")
end if

if Request.QueryString("dokid")="" then
   adokid="-1"
else
   adokid=Request.QueryString("dokid")
end if

if (Request.QueryString("dnum")<>"") and (Request.QueryString("dnum")=Dession("doknumber")) then
   cn.Execute "DELETE %s WHERE KreatorOID='" & Request.QueryString("koid") & "'"
   cn.Execute "DELETE %s WHERE _OID='" & Request.QueryString("koid") & "'"
""" % (awizard.CRM.Table_DokKreator.NameSQL, awizard.CRM.Table_Kreator.NameSQL)
    for bstep in awizard.steps:
        ret = ret + """
   cn.Execute "DELETE %s WHERE _KreatorOID='" & Request.QueryString("koid") & "'"
""" % (bstep.SQLTable.NameSQL, )
    ret = ret + """
   SetItemHistoryByOID Request.QueryString("koid"),"%s","Usuniecie kreatora"
""" % (bstep.SQLTable.NameSQL, )
    ret = ret + """
%s
""" % awizard.ASPSourceOnDelete
    ret = ret + """
   Response.Write "<script language='javascript'>" & chr(10)
   if adoktypeid<>"-1" then
      Response.Write "window.location='DOK_" & adoktypeid & "_so.asp?ioid=" & adokid & "';"  & chr(10)
   else
      Response.Write "window.location='%s.asp';"  & chr(10)
   end if
   Response.Write "</script>"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   Set rs=Nothing
   Response.End
end if
""" % (awizard.NameFile)

    fls = ['_OID', ]
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_':
            fls.append(afield.Name)
    fls.extend(['_KreatorOID', '_Dotyczy'])
    sf = string.join(fls, ',')
    ret = ret + """
if (Request.QueryString("ioid")="") or (Request.QueryString("ioid")="-1") then
  Response.Write "<!-- pusty rekord -->"
         if rs.State<>adStateClosed then
            rs.Close
         end if
         Set rs=Nothing
         Response.End
end if

rs.ActiveConnection = cn
rs.CursorType = adOpenKeyset
rs.LockType = adLockOptimistic
rs.Source = "SELECT %s FROM %s WHERE _OID='" & Request.QueryString("ioid") & "'"
rs.Open

if adoktypeid="-1" then
   Response.Write "<br><a class=reflistoutnavy href='%s.asp'>Powrót do listy</a><br>"
end if
Response.Write("<BR><TABLE>")
""" % (sf, astep.SQLTable.NameSQL, awizard.NameFile)
    i = 2
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class=objectseditdatafieldvalue>"\n' % (afield.PrettyName)
            if afield.Type == 'bool':
                ret = ret + """
at1rsvalue=rs.Fields("%s")
if not isnull(at1rsvalue) then
   if CBool(at1rsvalue) then
      Response.Write "Tak"
   else
      Response.Write "Nie"
   end if
end if
""" % (afield.Name, )
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield)
            elif afield.Type == 'money':
                ret = ret + '   Response.Write Currency2HTML(rs.Fields("%s").Value,0)\n' % (afield.Name, )
            else:
                ret = ret + '   Response.Write rs.Fields("%s").Value\n' % (afield.Name, )
            ret = ret + 'Response.Write ("</td>")\n'
            i = i + 1
    ret = ret + """
if adoktypeid<>"-1" then
   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>Dotyczy:</td><td class=objectseditdatafieldvalue>"
   Response.Write "<a class=reflistoutnavy href='DOK_" & adoktypeid & "_so.asp?ioid=" & rs.Fields("_Dotyczy") & "'>"
   Response.Write "Dokument</a></td></tr>"
end if
"""
    psoid, nsoid = -1, -1
    if not wfirst:
        psoid = prevstep.OID
    if not wlast:
        nsoid = nextstep.OID
    d = {'table': adoketapytable.NameSQL, 'woid': awizard.OID, 'poid': prevstep.OID, 'noid': nextstep.OID, 'psoid': psoid, 'nsoid': nsoid}
    ret = ret + """
   Set rs1 = Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select DokumentID,DokumentOID,KreatorID,KreatorOID,KreatorEtapID,KreatorEtapOID from  %(table)s WHERE DokumentID='" & adoktypeid & "' AND DokumentOID='" & adokid & "' AND KreatorID=%(woid)d AND KreatorOID='" & rs("_KreatorOID") & "' AND (KreatorEtapID=%(psoid)d or KreatorEtapID=%(nsoid)d)"
   rs1.Open

   if not (rs1.EOF or rs1.BOF) then
      eoid=rs1("KreatorEtapOID")
      spref=""
      snref=""
      if rs1("KreatorEtapID")=%(poid)d then
         spref="WSTP_%(poid)d_so.asp?ioid=" & eoid & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
      end if
      if rs1("KreatorEtapID")=%(noid)d then
         snref="WSTP_%(noid)d_so.asp?ioid=" & eoid & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
      end if
      rs1.MoveLast
      eoid=rs1("KreatorEtapOID")
      if not (rs1.EOF or rs1.BOF) then
         if rs1("KreatorEtapID")=%(poid)d then
            spref="WSTP_%(poid)d_so.asp?ioid=" & eoid & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
         end if
         if rs1("KreatorEtapID")=%(noid)d then
            snref="WSTP_%(noid)d_so.asp?ioid=" & eoid & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
         end if
      end if
      Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>Etap:</td><td class=objectseditdatafieldvalue>"
      if spref<>"" then
         Response.Write "<a class=reflistoutnavy href='" & spref & "'>"
         Response.Write "Poprzedni</a>"
         if snref<>"" then
            Response.Write ","
         end if
      end if
      if snref<>"" then
         Response.Write "<a class=reflistoutnavy href='" & snref & "'>"
         Response.Write "Nastepny</a>"
      end if
      Response.Write "</td></tr>"
   end if                                
   if rs1.State<>adStateClosed then
      rs1.Close
   end if
   Set rs1=Nothing
""" % d
    ret = ret + """
Response.Write "</TABLE>"
"""
    ret = ret + """
Response.Write "<hr><a class=reflistoutnavy href='wizard_%d_%d.asp?doktypeid=" & adoktypeid & "&ioid=" & Request.QueryString("ioid") & "&dokid=" & rs.Fields("_Dotyczy") & "'>Edycja danych</a><br>"
""" % (awizard.OID, astep.OID, )

    ret = ret + """
allowdelete=1
if allowdelete>0 then
   dnum=CStr(CLng(1e8*rnd(0)+Timer))
   Dession("doknumber")=dnum
   dhref="WSTP_%d_so.asp?koid=" & rs("_KreatorOID") & "&dnum=" & dnum & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
   Response.Write "<a class=reflistoutnavy onclick=""javascript:if (confirm('Czy na pewno chcesz wybrać tę pozycję?')) {this.href='" & dhref & "';} else {this.href='javascript:var umm=1;';} ;"" HREF=""javascript:var umm=1;"" >Usuń ten wpis</a><br>"
end if
""" % (astep.OID, )

    return ret
