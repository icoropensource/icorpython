# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import appplatform.startutil as startutil
import icorlib.projekt.mhtmlsqlgenlib as MHTMLSQLGenLib
from icorlib.wwwhtml.main import *
import icorlib.wwwhtml.fckmain as FCKMain
from icorlib.wwwhtml.worksheetmain import *
import icorlib.wwwserver.icorwwwinterfaceutil as ICORWWWInterfaceUtil
import string


#*********************************************************************************
def GetASPPageBegin(acrm, arefresh='', apage='', anocss=0):
    ret = """<%%@ CodePage=%s LANGUAGE="VBSCRIPT" %%><!-- #include file="../inc/_page_begin.asp" -->
<html>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=8">
""" % (acrm.DefaultCodePage, )
    if not anocss:
        ret = ret + ICORWWWInterfaceUtil.GetScriptCSS()
    ret = ret + """
<meta HTTP-EQUIV="Content-Type" content="text/html; charset=%s">
<meta http-equiv="Content-Language" content="pl">
<meta name="description" content="Opis strony">
<meta name="pragma" content="no-cache">
<meta name="keywords" content="ICOR object oriented database WWW information management repository">
<meta name="author" content="%s">
<META NAME="generator" CONTENT="ICOR"> 
<META HTTP-EQUIV="expires" CONTENT="Mon, 1 Jan 2001 01:01:01 GMT">
""" % (acrm.DefaultEncoding,startutil.appconfig.IParams['meta_author'], )
    if arefresh and apage:
        ret = ret + """
<META HTTP-EQUIV="refresh" CONTENT="%s; URL=%s"> 
""" % (arefresh, apage)
    ret = ret + """
<title>Main page</title>
<!--<base target="TEXT">-->
"""
    ret = ret + ICORWWWInterfaceUtil.GetScriptHeader()
    ret = ret + """
<link rel="stylesheet" href="/icormanager/inc/js_color_picker_v2/js_color_picker_v2.css" media="screen">
<script type="text/javascript" src="/icormanager/inc/js_color_picker_v2/color_functions.js"></script>
<script type="text/javascript" src="/icormanager/inc/js_color_picker_v2/js_color_picker_v2.js"></script>
</head>
<body>
<SCRIPT LANGUAGE=javascript>
var dselectedelement=0;
var reverseDateFormatForDateTimePopup=1;

function printpr() {
   if (isIE()) {
      document.body.insertAdjacentHTML('beforeEnd', '<OBJECT ID="WebBrowser1" WIDTH=0 HEIGHT=0 CLASSID="CLSID:8856F961-340A-11D0-A96B-00C04FD705A2"></OBJECT>');
      WebBrowser1.ExecWB(7,1);
      WebBrowser1.outerHTML = "";
   }
}
function checkSpelling(aelement,alang){
   if ((aelement!=null) && ((aelement.type=='text') || (aelement.type=='textarea') || (aelement.nodeName=='BODY'))){
      var aparams=lasttab = new Object();
      aparams.element=aelement;
      aparams.lang=alang;
      ret=showModalDialog('../../../inc/spellpage.asp',aparams,'dialogWidth:700px;dialogHeight:550px;help:No;Status:No;resizable:Yes;scroll:No')}
   else{
      alert('Wybierz pole tekstowe!');}
}
</SCRIPT>%s
<%%
""" % ('')
    return ret


#*********************************************************************************
def GetASPPageEnd(acreator):
    ret = """
%>
"""
    ret = ret + ICORWWWInterfaceUtil.GetScriptInit()
    ret = ret + """
<!-- #include file="../inc/_page_end.asp" -->
</body>
</html>
"""
    return ret


def GetASPPageEnd_OLD(acreator):
    ret = """
%>
<SCRIPT LANGUAGE=javascript>
try {
//   $("div.rounded").corner();
//   $("div.roundedContent").corner();
} catch(e) {}
</SCRIPT>
<!-- #include file="../inc/_page_end.asp" -->
</body>
</html>
"""
    return ret


#*********************************************************************************
def GetPageTitle_old(atitle, acrm):
    ret = """
if Request.QueryString("sheet")<>"-1" then
   aPageTitle="%s"
   if Request.QueryString("chapterid")<>"" and Request.QueryString("chapterid")<>"-1" then
      Set rs1 = Server.CreateObject("ADODB.Recordset")
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      rs1.Source = "select ChapterID,ChapterName from %s WHERE ChapterID='" & Request.QueryString("chapterid") & "'"
      rs1.Open
      if not rs1.EOF then
         aPageTitle=rs1("ChapterName")
      end if
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      set rs1=Nothing
   end if
%%>

<table border=0 cellpadding=0 cellspacing=0 width="100%%">
<tr>
<td width="100%%">
<table border=0 cellpadding=0 cellspacing=0 width="100%%"><tr>
<td>
<font size="+1"><b>&nbsp;<%%=aPageTitle%%></b></font>
</td>
<td align=right>
<img alt="Powrót" id=pageTitleButtonBack name=pageTitleButtonBack align=middle align=top vspace=0 src="/icormanager/images/icon_back.png" style="cursor:pointer;" onclick="javascript:history.back();">
<img alt="Drukuj" align=middle align=top vspace=0 src="/icormanager/images/icon_print.png" style="cursor:pointer;" onclick="javascript:window.print();">
<!--[if IE]>
<img alt="Podgląd wydruku" align=middle align=top vspace=0 src="/icormanager/images/icon_preview.png" style="cursor:pointer;" onclick="javascript:printpr();">
<![endif]-->
</td></tr>
</table>
</td>
</tr>
</table>
<script type="text/javascript">
function setButtonBackAction(atext) {
   jQuery("#pageTitleButtonBack").click(function(){
      window.location=atext;
   });
}
</script>
<%%
end if
""" % (atitle, acrm.Table_ChaptersID.NameSQL)
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
def DepartmentGetMainASP(adepartment, aetapytable):
    ret = """
Response.Write "<table border=0 cellpadding=0 cellspacing=4 width='100%'>"
"""
    lvirtuals = ['-1', ]
    if adepartment.CreatedDocuments:
        ret = ret + """
Response.Write "<tr><td colspan=2>"
Response.Write "<span class='normal'>Aby utworzyć nowy dokument, wybierz jego nazwę z poniższej listy:</span><br><br>"
"""
        for asymbol, adocument in adepartment.CreatedDocuments:
            if adocument.IsVirtualDocument:
                lvirtuals.append(str(adocument.OID))
            ret = ret + """
Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='newdoc_%d.asp?doid=%d'>%s - %s</a><!-- &nbsp;"
Response.Write "-&nbsp;<a  class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_sa.asp'>wszystkie dokumenty</a> --><br>"
""" % (adocument.OID, adepartment.OID, adocument.Symbol, adocument.Nazwa, adocument.SQLTable.NameFile)
        ret = ret + """
Response.Write "</td></tr>"
Response.Write "</table>"
"""
    svirtuals = string.join(lvirtuals, ',')
    fl = ['-1', ]
    for bdocument in adepartment.CRM.documents.values():
        for aczynnosc in bdocument.czynnosci:
            if aczynnosc.IsFlashing:
                fl.append('"%d"' % aczynnosc.OID)
    sfl = string.join(fl, ',')
    ret = ret + '''
rs.ActiveConnection = cn
rs.CursorType = adOpenKeyset
rs.LockType = adLockOptimistic
rs.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,CzynnoscID,CzynnoscSymbol,CzynnoscName,CzynnoscDescription,CzynnoscState,CzynnoscDateTime,JednostkaID,JednostkaInfo,ObowiazujeOdDateTime,BZRID,BZROID,BZRInfo,Uwagi,_UID,_UserName,CreatorUID,CreatorName from %s where (CzynnoscState='1') and (JednostkaID='%d') and (ObowiazujeOdDateTime<=GetDate()) order by CzynnoscDateTime"
rs.Open
wrecs=0
if rs.RecordCount>0 then
   wrecs=1
   Response.Write "<hr>"
   Response.Write "<table  class='objectsviewtable'><TR>"
   Response.Write "<TH class='objectsviewheader'>Nazwa</TH>"
   Response.Write "<TH class='objectsviewheader'>Dotyczy</TH>"
   Response.Write "<TH class='objectsviewheader'>Z dnia</TH>"
   Response.Write "<TH class='objectsviewheader'>Zadanie</TH>"
   Response.Write "<TH class='objectsviewheader'>Potwierdzenie</TH>"
   Response.Write "</TR>"
end if
atipcnt=1
Do While Not rs.EOF
   Response.Write "<tr>"
'   Response.Write "<td class='objectsviewdatawrap'><img style='cursor:pointer;' align=middle align=top vspace=0 src='/icormanager/images/tree/menu_link_default.png' alt='" & rs("DokumentSymbol") & " - " & rs("DokumentTitle") & "' onclick='javascript:window.location=""DOK_" & rs("DokumentID") & "_so.asp?ioid=" & rs("DokumentOID") & """;'>&nbsp;"
'   Response.Write "<img style='cursor:pointer;' align=middle align=top vspace=0 src='/icormanager/images/tree/home.png' alt='" & rs("BZRInfo") & "' onclick='javascript:window.location=""BZR_" & rs("BZRID") & "_so.asp?ioid=" & rs("BZROID") & """;'>&nbsp;"
'   Response.Write rs("CzynnoscDateTime") & "</td>"

   Response.Write "<td class='objectsviewdatanowrap'><a id='oTipped" &CStr(atipcnt) & "' class='fg-button-single ui-state-default ui-corner-all uihover' href='DOK_" & rs("DokumentID") & "_so.asp?ioid=" & rs("DokumentOID") & "'>" & rs("DokumentSymbol") & "</a><tool:tip element='oTipped" & CStr(atipcnt) & "' avoidmouse='false'>" & rs("DokumentSymbol") & " - " & rs("DokumentTitle") & "</tool:tip>&nbsp;</td>"
   atipcnt=atipcnt+1
   Response.Write "<td class='objectsviewdatanowrap'><a id='oTipped" & CStr(atipcnt) & "' class='fg-button-single ui-state-default ui-corner-all uihover' href='BZR_" & rs("BZRID") & "_so.asp?ioid=" & rs("BZROID") & "'>" & GetTextAsCaption(rs("BZRInfo"),20) & "</a><tool:tip element='oTipped" & CStr(atipcnt) & "' avoidmouse='false'>" & rs("BZRInfo") & "</tool:tip>&nbsp;</td>"
   atipcnt=atipcnt+1
   Response.Write "<td class='objectsviewdatanowrap'>" & rs("CzynnoscDateTime") & "</td>"

   eoid=rs("_OID")
   select case rs("CzynnoscID")
      case %s
         Response.Write "<td class='objectsviewdatawrap'><span class='normal'><font id='cfont" & rs("_OID") & "' style='font-size:10pt;' color='red'>" & rs("CzynnoscName") & "&nbsp;" & rs("CzynnoscDescription") & "&nbsp;</font><t:ANIMATECOLOR targetElement='cfont" & rs("_OID") & "' attributeName='COLOR' to='IVORY' start='0' dur='0.22' fill='hold' autoReverse='true' repeatCount='indefinite'></span></td>"
      case else
         Response.Write "<td class='objectsviewdatawrap'><span style='font-size:10pt;color:green;'>" & rs("CzynnoscName") & "&nbsp;" & rs("CzynnoscDescription") & "&nbsp;</span></td>"
   end select
   select case rs("DokumentID")
      case %s
         isdocumentvirtual=1
      case else
         isdocumentvirtual=0
   end select
   if isdocumentvirtual=1 then
      Response.Write "<td class='objectsviewdatawrap'>&nbsp;</td>"
   else
      Response.Write "<td class='objectsviewdatawrap'><span class='normal'><button class='fg-button-single ui-state-default ui-corner-all uihover' name=etbutton" & eoid & " id=etbutton" & eoid & " disabled onclick=""javascript:window.location='dep_%d_cs.asp?coid=" & rs("_OID") & "';"">Załatwione!</button>&nbsp;&nbsp;<input class='checkradio' type=checkbox onclick=""javascript:if(this.checked){document.getElementById('etbutton" & eoid & "').disabled=0;document.getElementById('etcheck" & eoid & "').style.visibility='';}else{document.getElementById('etbutton" & eoid & "').disabled=1;document.getElementById('etcheck" & eoid & "').style.visibility='hidden';};"">Podpis <span name=etecheck" & eoid & " id=etcheck" & eoid & " style=""visibility:hidden;FONT-FAMILY: times, arial, verdana;COLOR: red;FONT-SIZE: 12pt;FONT-STYLE: italic;FONT-WEIGHT: bold;""> " & Dession("username") & "</span></span></td>"
   end if
   Response.Write "</tr>"
   rs.MoveNext   
Loop
if wrecs=1 then
   Response.Write "</table>"
end if
''' % (aetapytable.NameSQL, adepartment.OID, sfl, svirtuals, adepartment.OID)
    return ret


#*********************************************************************************
def DepartmentGetStoreCzynnoscASP(adepartment, aetapytable):
    ret = """
rs.ActiveConnection = cn
rs.CursorType = adOpenKeyset
rs.LockType = adLockOptimistic
rs.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,CzynnoscID,CzynnoscSymbol,CzynnoscName,CzynnoscDescription,CzynnoscState,CzynnoscDateTime,JednostkaID,JednostkaInfo,BZRID,BZROID,BZRInfo,Uwagi,_UID,_UserName,_DateTime,CreatorUID,CreatorName from %s where _OID='" & Request.QueryString("coid") & "'"
rs.Open 
TaskRepeat=0
""" % (aetapytable.NameSQL, )
    for adocument in adepartment.Documents.values():
        for aczynnosc in adocument.czynnosci:
            if aczynnosc.ASPSourceSubmit:
                ret = ret + """

if rs("CzynnoscID")=%d then
%s
end if
""" % (aczynnosc.OID, aczynnosc.ASPSourceSubmit)

    ret = ret + """
if TaskRepeat=0 then
   rs("CzynnoscState")="2"
   rs("CzynnoscDateTime")=Now
   rs("_UID")=Dession("uid")
   rs("_UserName")=Dession("username")
   rs("_DateTime")=Now
   ssym=rs("CzynnoscSymbol")
   rs.Update
   Call SetItemHistory(rs,"%s","Zatwierdzona czynnosc dla dokumentu")
   
   if ssym="T" then
      sstg="T"
      sexc=""
      slev=""
   else
      if mid(ssym,len(ssym),1)="!" then
         sexc="!"
         slev=mid(ssym,2,len(ssym)-2)
      else
         sexc=""
         slev=mid(ssym,2,len(ssym)-1)
      end if
      sstg=mid(ssym,1,1)
   end if
   
   Set rs1 = Server.CreateObject("ADODB.Recordset") 
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,CzynnoscID,CzynnoscSymbol,CzynnoscName,CzynnoscDescription,CzynnoscState,CzynnoscDateTime,JednostkaID,JednostkaInfo,BZRID,BZROID,BZRInfo,Uwagi,_UID,_UserName,_DateTime,CreatorUID,CreatorName from %s where (DokumentID='" & rs("DokumentID") & "') AND (DokumentOID='" & rs("DokumentOID") & "')"
   rs1.Open
   
   ccount=0
   ecount=0
   fcountn=0
   fcounte=0
   Do While Not rs1.EOF
      ssym1=rs1("CzynnoscSymbol")
      if ssym1="T" then
         sstg1="T"
         sexc1=""
         slev1=""
      else
         if mid(ssym1,len(ssym1),1)="!" then
            sexc1="!"
            slev1=mid(ssym1,2,len(ssym1)-2)
         else
            sexc1=""
            slev1=mid(ssym1,2,len(ssym1)-1)
         end if
         sstg1=mid(ssym1,1,1)
      end if
      if (sstg=sstg1) and (slev=slev1) then
         ccount=ccount+1
         if sexc1="!" then
            ecount=ecount+1
         end if
         if rs1("CzynnoscState")="2" then
            if sexc1="!" then
               fcounte=fcounte+1
            else
               fcountn=fcountn+1
            end if
         end if   
      end if
      rs1.MoveNext   
   Loop
   
   nstate=0
   if ecount>0 then
      if fcounte=ecount then nstate=1
   else
      if fcountn=ccount then nstate=1
   end if
   
   if nstate=1 then
      if sstg="T" then
         sstg="A"
         sexc=""
         slev="1"
      else
         slev=CStr(1+CLng(slev))
      end if
   
      rs1.MoveFirst
      Do While Not rs1.EOF
         ssym1=rs1("CzynnoscSymbol")
         if ssym1="T" then
            sstg1="T"
            sexc1=""
            slev1=""
         else
            if mid(ssym1,len(ssym1),1)="!" then
               sexc1="!"
               slev1=mid(ssym1,2,len(ssym1)-2)
            else
               sexc1=""
               slev1=mid(ssym1,2,len(ssym1)-1)
            end if
            sstg1=mid(ssym1,1,1)
         end if
         if (sstg=sstg1) and (slev=slev1) then
            if rs1("CzynnoscState")="0" then
               rs1("CzynnoscState")="1"
               rs1("CreatorUID")=Dession("uid")
               rs1("CreatorName")=Dession("username")
               rs1("_UID")=Dession("uid")
               rs1("_UserName")=Dession("username")
               rs1("_DateTime")=Now
               rs1.Update
               Call SetItemHistory(rs1,"%s","Nowa czynnosc do wykonania dla dokumentu")
            end if
         end if
         rs1.MoveNext
      Loop
   end if

   if rs1.State<>adStateClosed then
      rs1.Close
   end if
   Set rs1=Nothing
end if

Response.Write "<script language='javascript'>" & chr(10)
Response.Write "window.location='dep_%d.asp';"  & chr(10)
Response.Write "</script>"
""" % (aetapytable.NameSQL, aetapytable.NameSQL, aetapytable.NameSQL, adepartment.OID,
       )
    return ret


#*********************************************************************************
def SQLTableGetSelectAllASP(atable):
    fls = ['%s._OID' % atable.NameSQL, ]
    for afield in atable.FieldsByTabID:
        if afield.IsAliased and afield.IsInteractive:
            fls.append(afield.NameSQL)
    sf = string.join(fls, ',')
    if not len(atable.Fields):
        print 'tabela:', atable.NameSQL
    ret = """   rs.Open "select top 10000 %s from %s ORDER BY %s", cn
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (sf, atable.NameSQL, atable.Fields[0].NameSQL, atable.TableCaption, )
    for afield in atable.FieldsByTabID:
        if afield.IsAliased and afield.IsInteractive:
            ret = ret + """
Response.Write "<TH class='objectsviewheader'>%s</TH>"
""" % (afield.PrettyName, )
#For i = 1 To rs.Fields.Count-1
#   Response.Write "<TH class='objectsviewheader'>" & rs.Fields(i).Name & "</TH>"
#Next
    ret = ret + """
Response.Write("</TR>")
Do While Not rs.EOF
   Response.Write "<TR class='objectsviewrow'>"
   aoid=rs.Fields(0).Value
   For i = 1 to rs.Fields.Count-1
      Response.Write "<td class='objectsviewdataeven'>"
      Response.Write "<a class='objectitemasanchor' href='%s.asp?ioid=" & cstr(aoid) & "'>" & rs.Fields(i).Value & "</a>"
      Response.Write "</TD>"
   Next
   Response.Write "</TR>"
   rs.MoveNext   
Loop
Response.Write("</TABLE>")
""" % (atable.NameFile + '_so', )
    return ret


#*********************************************************************************
def SQLTableGetSelectSingleASPDotyczy(atable, btable, atabs=None, aeventsrc=None):
    fls = ['%s._OID' % atable.NameSQL, '%s._Dotyczy' % atable.NameSQL]
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_':
            fls.append(afield.NameSQL)
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            fls.append(afield.NameSQL)
    sf = string.join(fls, ',')
    ret = """
if (Request.QueryString("ioid")="") or (Request.QueryString("ioid")="-1") then
   Response.Write "<!-- pusty rekord -->"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   Set rs=Nothing
   Response.End
end if
rs.Open "SELECT %s FROM %s JOIN %s ON (%s._Dotyczy = %s._OID) WHERE %s._OID='" & Request.QueryString("ioid") & "'", cn
""" % (sf, atable.NameSQL, btable.NameSQL, atable.NameSQL, btable.NameSQL, atable.NameSQL)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeShowOneTable'):
        ret = ret + "\n' *** ASPSourceOnBeforeShowOneTable -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnBeforeShowOneTable
        ret = ret + "\n' *** ASPSourceOnBeforeShowOneTable -- END ***\n"

    if atabs:
        ret = ret + """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 1</font></h1>")
   else
""" % (atabs[0][0], atabs[0][2])

    ret = ret + """
if not rs.EOF then
"""

    ret = ret + """
Response.Write("<br><br><div class=""rounded background_pasteldark_blue""><div class=""roundedContent background_default"">")
"""
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

    i = 2
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_':
            ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class=objectseditdatafieldvalue>"\n' % (afield.PrettyName)
            if afield.Type == 'bool':
                ret = ret + """
if CBool(rs.Fields(%d).Value) then     
   Response.Write "Tak"
else
   Response.Write "Nie"
end if
""" % (i, )
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield)
            elif afield.Type == 'external dict multiple':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDictMultiple(afield)
            elif afield.Type == 'money':
                ret = ret + '   Response.Write Currency2HTML(rs.Fields(%d).Value,0)\n' % (i, )
            else:
                ret = ret + '   Response.Write rs.Fields(%d).Value\n' % (i, )
            ret = ret + 'Response.Write ("</td>")\n'
            i = i + 1
    ret = ret + """
Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>%s:</td><td class=objectseditdatafieldvalue>"
Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_so.asp?ioid=" & rs.Fields(1).Value & "'>"
""" % (btable.SingleObjectName, btable.NameFile, )
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            ret = ret + """
Response.Write rs.Fields(%d).Value & "&nbsp;&nbsp;"
""" % (i, )
            i = i + 1
    ret = ret + """
Response.Write "</a></td></tr>"
"""

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

    ret = ret + """
Response.Write "</div></div>"
"""

    ret = ret + """
end if
"""
    if atabs:
        ret = ret + """
   end if
end if
"""
    return ret


#*********************************************************************************
def WriteSheetsHeader(atabs, afname):
    ret = """
%%>
<SCRIPT language="javascript">
function do_set_frame(atoframe,atabid) {
   var s="";
   var i=0;
   var aframe;
   while (i<%d) {
      if (i>0)
         s=s+',';
      if (i==atoframe) {
         s=s+'100%%';
         aframe=window.parent.document.getElementById("OBJECTEDITPANE"+atoframe.toString());
         if (aframe.src=="") {
            aframe.src="%s?ioid=<%%=Request.QueryString("ioid")%%>&sheet="+atabid.toString();
            }
      } else {
         s=s+'0';
      }
      i=i+1;
   }
   window.parent.document.getElementById("FRAMEPANES").rows=s;
}
function set_frame(atoframe,atabid) {
//   try {
      do_set_frame(atoframe,atabid);
//   } catch (ex) {
//      window.setTimeout("set_frame("+atoframe.toString()+","+atabid.toString()+")", 500);
//   }
}
""" % (len(atabs), afname,
       )
    ret = ret + """
var last_tab=0;
var max_tab=%d;
document.body.topMargin=0;
function do_change_display(atoframe,atabid) {
   if (atoframe==last_tab)
      return;
   if (last_tab==0) {
      s1img="/icormanager/images/tabs/tab_ng.png";
   } else {
      s1img="/icormanager/images/tabs/tab_gg.png";
   }
   if (last_tab==max_tab) {
      s2img="/icormanager/images/tabs/tab_gn.png";
   } else {
      s2img="/icormanager/images/tabs/tab_gg.png";
   }
   jQuery('#imgtab'+last_tab.toString()).attr('src',s1img);
   jQuery('#imgtab'+(last_tab+1).toString()).attr('src',s2img);
   jQuery('#infotab'+last_tab.toString()).removeClass("tabselected").addClass("tabunselected");
   if (atoframe==0) {
      s1img="/icormanager/images/tabs/tab_ns.png";
   } else {
      s1img="/icormanager/images/tabs/tab_gs.png";
   }
   if (atoframe==max_tab) {
      s2img="/icormanager/images/tabs/tab_sn.png";
   } else {
      s2img="/icormanager/images/tabs/tab_sg.png";
   }
   jQuery('#imgtab'+atoframe.toString()).attr('src',s1img);
   jQuery('#imgtab'+(atoframe+1).toString()).attr('src',s2img);
   jQuery('#infotab'+atoframe.toString()).removeClass("tabunselected").addClass("tabselected");
   last_tab=atoframe;
   set_frame(atoframe,atabid);
   getParentFrame('NAVBAR').SetSheetForCid('%s',atoframe,atabid);
}
function change_display(atoframe,atabid) {
//   try {
      do_change_display(atoframe,atabid);
//   } catch (ex) {
//      window.setTimeout("change_display("+atoframe.toString()+","+atabid.toString()+")", 500);
//   }
}
</SCRIPT>
""" % (len(atabs) - 1, afname,
       )

    if len(atabs) > 1:
        ret = ret + """
<div style="position:absolute;left:30px;top:0px;">
<TABLE cellSpacing=0 cellPadding=0 border=0>
<TBODY>
<TR>
"""
        i = 0
        for aid, atitle, aaccesslevelview in atabs:
            if i == 0:
                ret = ret + """
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="/icormanager/images/tabs/tab_ns.png" border=0></TD>
          <TD align=middle></TD>
""" % (i, )
            elif i == 1:
                ret = ret + """
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="/icormanager/images/tabs/tab_sg.png" border=0></TD>
          <TD align=middle></TD>
""" % (i, )
            else:
                ret = ret + """
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="/icormanager/images/tabs/tab_gg.png" border=0></TD>
          <TD align=middle></TD>
""" % (i, )
            i = i + 1
        ret = ret + """
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="/icormanager/images/tabs/tab_gn.png" border=0></TD>
        </TR>
        <TR>
""" % (i, )
        i = 0
        for aid, atitle, aaccesslevelview in atabs:
            if i == 0:
                s = 'tabselected'
            else:
                s = 'tabunselected'
            ret = ret + """
          <TD id=infotab%d align=middle class="%s">
            <span class=tabtext onclick="javascript:change_display(%d,%d);">%s</span></TD>
""" % (i, s, i, aid, string.replace(atitle, ' ', '&nbsp;'))
            i = i + 1
        ret = ret + """
        </TR>
        <TR>
          <TD style="height:1px" align=middle bgColor=ivory colspan=%d></TD>
        </TR>
</TBODY></TABLE>
</div>
""" % (len(atabs) * 2, )
        ret = ret + """
<div id="buttoncontroldiv" style="position:absolute;left:0;top:-8;z-index:6;white-space:nowrap;">
   <span class="ui-icon ui-icon-circle-triangle-w" style="position:relative;left:0px;top:0px;cursor:pointer;"
      onmouseover="javascript:this.parentElement.style.pixelLeft=document.body.scrollLeft;"
      onclick="javascript:document.body.doScroll('scrollbarPageLeft');this.parentElement.style.pixelLeft=document.body.scrollLeft;"
   ></span>
   <span class="ui-icon ui-icon-circle-triangle-e" style="position:relative;left:14px;top:-16px;cursor:pointer;"
      onmouseover="javascript:this.parentElement.style.pixelLeft=document.body.scrollLeft;"
      onclick="javascript:document.body.doScroll('scrollbarPageRight');this.parentElement.style.pixelLeft=document.body.scrollLeft;"
   ></span>
</div>

<SCRIPT LANGUAGE="JScript"><!--
   window.parent.document.getElementById("FRAMEOBJECTS").rows='16,*';
//--></SCRIPT>
"""
    else:
        ret = ret + """
<SCRIPT LANGUAGE="JScript"><!--
   window.parent.document.getElementById("FRAMEOBJECTS").rows='0,*';
//--></SCRIPT>
"""
    ret = ret + """
<%
"""
    return ret


#*********************************************************************************
def GetDocumentPostUpdateText(adocument):
    ret = """
Set rs1 = Server.CreateObject("ADODB.Recordset") 
rs1.ActiveConnection = cn
rs1.CursorType = adOpenKeyset
rs1.LockType = adLockOptimistic
rs1.Source = "UPDATE %s SET ObowiazujeOdDateTime = '" & getDateAsSQLDate(rs("DataObowiazywania")) & "' WHERE DokumentID = '%d' AND DokumentOID = '" & rs("_OID") & "'"
rs1.Open
if rs1.State<>adStateClosed then
   rs1.Close
end if
Set rs1=Nothing
""" % (adocument.CRM.Table_Etapy.NameSQL, adocument.OID)
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASP2(atable):
    fls = ['_OID', ]
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.IsInteractive and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict']:
            fls.append(afield.Name)
    sf = string.join(fls, ',')
    ret = """
sub DisplaySearchForm()
      Response.Write "<p>Wpisz szukany ciąg znaków do odpowiednich pól:</p>"
      Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='%s_sd.asp'>"
      Response.Write "<input type=hidden id='search' name='search' size=1 value='1'>"
      Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%%' border=1>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), atable.NameFile, )
    i = 1
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.IsInteractive and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict']:
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
            ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s><input type=text id=\'%s\' name=\'%s\' size=20 value=\'\' %s></td></tr>"\n' % (snclass, afield.PrettyName, svclass, afield.Name, afield.Name, GetFieldValidationText(afield, aissearch=1))
            i = i + 1
    ret = ret + """
      Response.Write("</TABLE>")
      Response.Write "<br><input class='pushbutton' TYPE='submit' VALUE='  Szukaj  ' tabIndex=1></form>"
end sub
   if Request.Form("search")="" then
      DisplaySearchForm
   else
      sp=""
"""
    i = 1
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.IsInteractive and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict']:
            if not afield.Type in ['string', 'text', 'dict', 'date', 'datetime']:
                scast = 'CAST(%s AS VarChar(200))' % afield.Name
            elif afield.Type in ['date', 'datetime']:
                scast = 'CONVERT(VarChar(50),%s,121)' % afield.Name
            else:
                scast = afield.NameSQL
            ret = ret + """
      if Request.Form("%s")<>"" then
         if sp<>"" then sp=sp & " AND "
         sp=sp & "%s LIKE '%%" & Replace(Request.Form("%s"), "'", "''") & "%%' "
      end if
""" % (afield.Name, scast, afield.Name, )
            i = i + 1
    ret = ret + """
      if sp="" then 
         DisplaySearchForm
      else
      ssql="select top 1000 %s from %s WHERE " & sp & " ORDER BY %s"
      rs.Open ssql, cn
""" % (sf, atable.NameSQL, atable.FieldsByTabID[0].Name)
    ret = ret + """
Response.Write "<br>"
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (atable.TableCaption, )
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.IsInteractive and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict']:
            ret = ret + 'Response.Write "<TH class=\'objectsviewheader\'>%s</TH>"\n' % (afield.PrettyName, )
    ret = ret + """
Response.Write("</TR>")
Do While Not rs.EOF
   Response.Write "<TR class='objectsviewrow'>"
   aoid=rs.Fields(0).Value
   For i = 1 to rs.Fields.Count-1
      Response.Write "<td class='objectsviewdataeven'>"
      sdv1=rs.Fields(i).Value
      if (rs.Fields(i).Type=7) or (rs.Fields(i).Type=133) or (rs.Fields(i).Type=134) or (rs.Fields(i).Type=135) then
         sdv1=getDateTimeAsStr(sdv1)
      end if
      Response.Write "<a class='objectitemasanchor' href='%s.asp?ioid=" & cstr(aoid) & "'>" & sdv1 & "</a>"
      Response.Write "</TD>"
   Next
   Response.Write "</TR>"
   rs.MoveNext   
Loop
Response.Write("</TABLE>")
   end if
end if
""" % (atable.NameFile + '_so', )
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASP(atable):
    df = {}
    fls = [atable.NameSQL + '._OID', ]
    df[atable.NameSQL + '._OID'] = 0
    dfcnt = 1
    for afield in atable.FieldsByTabID:
        #      if afield.IsSearch and afield.IsInteractive and afield.Type in ['string','numeric','date','datetime','text','integer','money','dict','external dict','bool']:
        if (afield.IsInteractive or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'external dict', 'external dict multiple', 'bool']:
            fls.append(afield.NameSQL)
            df[afield.NameSQL] = dfcnt
            dfcnt = dfcnt + 1
    sf = string.join(fls, ',')
    ret = """
sub DisplaySearchForm()
      Response.Write "<p>Wpisz szukany ciąg znaków do odpowiednich pól:</p>"
      Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='%s_sd.asp'>"
      Response.Write "<input type=hidden id='search' name='search' size=1 value='1'>"
      Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%%' border=1>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), atable.NameFile, )
    i = 1
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
            ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s><input type=text id=\'%s\' name=\'%s\' size=20 value=\'\' %s></td></tr>"\n' % (snclass, afield.PrettyName, svclass, afield.Name, afield.Name, GetFieldValidationText(afield, aissearch=1))
            i = i + 1
    ret = ret + """
      Response.Write("</TABLE>")
      Response.Write "<br><input class='pushbutton' TYPE='submit' VALUE='  Szukaj  ' tabIndex=1></form>"
end sub
   if Request.Form("search")="" then
      DisplaySearchForm
   else
      sp=""
"""
    i = 1
    ltables, lfields, lrules = [], [], []

    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            if not afield.Type in ['string', 'text', 'dict', 'date', 'datetime']:
                scast = 'CAST(%s AS VarChar(200))' % afield.NameSQL
            elif afield.Type in ['date', 'datetime']:
                scast = 'CONVERT(VarChar(50),%s,121)' % afield.NameSQL
            else:
                scast = afield.NameSQL
            if afield.TypeDescription == 'GUID':
                ret = ret + """
      if Request.Form("%s")<>"" then
         if sp<>"" then sp=sp & " AND "
         sp=sp & "%s = '" & Replace(Request.Form("%s"), "'", "''") & "' "
      end if
""" % (afield.Name, afield.NameSQL, afield.Name, )
            else:
                ret = ret + """
      if Request.Form("%s")<>"" then
         if sp<>"" then sp=sp & " AND "
         sp=sp & "%s LIKE '%%" & Replace(Request.Form("%s"), "'", "''") & "%%' "
      end if
""" % (afield.Name, scast, afield.Name, )
        elif (afield.IsInteractive or afield.IsAliased) and afield.Type in ['external dict', ] and not afield.DictSourceTable.NameSQL in ltables:
            ltables.append(afield.DictSourceTable.NameSQL)
            lrules.append(afield.NameSQL + '=' + afield.DictSourceTable.NameSQL + '._OID')
            lfields.append(afield.DictSourceTable.NameSQL + '._OID')
            df[afield.DictSourceTable.NameSQL + '._OID'] = dfcnt
            dfcnt = dfcnt + 1
            bcnt = 3
            for bfield in afield.DictSourceTable.FieldsByTabID:
                if bfield.IsInteractive or bfield.IsAliased:
                    lfields.append(bfield.NameSQL)
                    df[bfield.NameSQL] = dfcnt
                    dfcnt = dfcnt + 1
                    bcnt = bcnt - 1
                    if not bcnt:
                        break
        elif (afield.IsInteractive or afield.IsAliased) and afield.Type in ['external dict multiple', ] and not afield.DictSourceTable.NameSQL in ltables:
            ltables.append(afield.DictSourceTable.NameSQL)
            lrules.append(afield.NameSQL + " like '%'+" + afield.DictSourceTable.NameSQL + "._OID+'%'")
            lfields.append(afield.DictSourceTable.NameSQL + '._OID')
            df[afield.DictSourceTable.NameSQL + '._OID'] = dfcnt
            dfcnt = dfcnt + 1
            bcnt = 3
            for bfield in afield.DictSourceTable.FieldsByTabID:
                if bfield.IsInteractive or bfield.IsAliased:
                    lfields.append(bfield.NameSQL)
                    df[bfield.NameSQL] = dfcnt
                    dfcnt = dfcnt + 1
                    bcnt = bcnt - 1
                    if not bcnt:
                        break
            i = i + 1
    sfields, stables, srules = '', '', ''
    if ltables:
        ltables.insert(0, '')
        stables = string.join(ltables, ', ')
    if lfields:
        lfields.insert(0, '')
        sfields = string.join(lfields, ', ')
    if lrules:
        lrules.insert(0, '')
        srules = string.join(lrules, ' AND ')
    aselect = atable.GetSelectClause(atop=1000)
    ret = ret + """
      if sp="" then 
         DisplaySearchForm
      else
      ssql="select top 1000 %s%s from %s%s WHERE " & sp & "%s %s"
      rs.Open ssql, cn
""" % (sf, sfields, atable.NameSQL, stables, srules, aselect.OrderBy, )
    ret = ret + """
Response.Write "<br>"
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (atable.TableCaption, )
    for afield in atable.FieldsByTabID:
        #      if afield.IsSearch and afield.IsAliased and afield.IsInteractive and afield.Type in ['string','numeric','date','datetime','text','integer','money','dict','external dict','bool']:
        if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'external dict', 'external dict multiple', 'bool']:
            ret = ret + 'Response.Write "<TH class=\'objectsviewheader\'>%s</TH>"\n' % (afield.PrettyName, )
    ret = ret + """
Response.Write("</TR>")
Do While Not rs.EOF
   Response.Write "<TR class='objectsviewrow'>"
   aoid=rs.Fields(0).Value
"""
    for afield in atable.FieldsByTabID:
        #      if afield.IsSearch and afield.IsAliased and afield.IsInteractive:
        if afield.IsAliased:
            ret = ret + """
      Response.Write "<td class='objectsviewdataeven'>"
      Response.Write "<a class='objectitemasanchor' href='%s.asp?ioid=" & cstr(aoid) & "'>"
""" % (atable.NameFile + '_so', )
            if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict']:
                ret = ret + """
      sdv1=rs.Fields(%d).Value
      if (rs.Fields(%d).Type=7) or (rs.Fields(%d).Type=133) or (rs.Fields(%d).Type=134) or (rs.Fields(%d).Type=135) then
         sdv1=getDateTimeAsStr(sdv1)
      end if
Response.Write server.htmlencode(sdv1)
""" % (df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], )
            elif afield.Type in ['bool', ]:
                ret = ret + """
if CBool(rs.Fields(%d).Value) then
   Response.Write "Tak"
else
   Response.Write "Nie"
end if
""" % (df[afield.NameSQL], )
            elif afield.Type in ['external dict', 'external dict multiple']:
                bcnt = 3
                ret = ret + 'Response.Write ""'
                for bfield in afield.DictSourceTable.FieldsByTabID:
                    if bfield.IsInteractive or bfield.IsAliased:
                        bname = bfield.NameSQL
                        if bcnt < 3:
                            ret = ret + ' & ", "'
                        ret = ret + ' & rs.Fields(%d).Value' % (df[bname], )
                        bcnt = bcnt - 1
                        if not bcnt:
                            break
            ret = ret + """

      Response.Write "</a></TD>"
"""
    ret = ret + """
   Response.Write "</TR>"
   rs.MoveNext   
Loop
Response.Write("</TABLE>")
   end if
end if
"""
    return ret


#*********************************************************************************
def DocumentNewASP(adocument, adocumentcustomertable, aetapytable):
    atable = adocument.SourceTable.SQLTable
    btable = adocument.SQLTable
    ret = '''
%>
<script language="javascript">
function doSubmit(apage) {
   jQuery("#iPageNo").val(apage);
   document.getElementById("form1").submit();
}
function doLinkChange(oElement,aRow){
   if (aRow==5)
      return;
   aRow+=1;
   if (oElement.value!='')
      document.getElementById("aRowDiv"+aRow.toString()).style.display='';
   else
      document.getElementById("aRowDiv"+aRow.toString()).style.display='none';
}
function doSubmitRepeat() {
   jQuery("#search").val("2");
   document.getElementById("form1").submit();
}
</script>
<%

if Request.QueryString("doid")="" then
         if rs.State<>adStateClosed then
            rs.Close
         end if
         Set rs=Nothing
         Response.End
end if
if Request.QueryString("boid")="" then

function getDateAsSQLDate(sdatetime)
   dim i,sarr,sdarr,sdate,stime
   sdatetime=Replace(Replace(Replace(trim(sdatetime),".","/"),"-","/"),"\","/")
   if Not IsDate(sdatetime) then
      getDateAsSQLDate=""
   else
      sarr=Split(sdatetime," ")
      for i=0 to ubound(sarr)
         if instr(sarr(i),":")>0 then
            stime=" " & sarr(i)
         elseif sarr(i)<>"" then
            sdarr=Split(sarr(i),"/")
            if CLng(sdarr(0))>31 then
               sdate=sdarr(0) & Right("0" & sdarr(1),2) & Right("0" & sdarr(2),2)
            else
               sdate=sdarr(2) & Right("0" & sdarr(1),2) & Right("0" & sdarr(0),2)
            end if
         end if
      next
      getDateAsSQLDate=trim(sdate & stime)
   end if
end function

sub DisplaySearchForm(ahidden)
   dim i,ss,optArray,svalue,ssearch,sselected,schecked
   ssearch=Request.Form("search")
   sselected="SELECTED"
   schecked="CHECKED"
   if ahidden=0 then
      Response.Write "<h1>Etap I</h1>"
      Response.Write "<p>Każdy dokument czegoś dotyczy np. kontrahenta, obiektu ochrony. Wpisz w poniższych polach informacje pozwalające znaleźć tę informację źródłową.</p>"     
   End if
'''
    ret = ret + '''
   Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='newdoc_%d.asp?doid=" & Request.QueryString("doid") & "'>"
''' % (MHTMLSQLGenLib.GetFormValidateParms(), adocument.OID, )
    ret = ret + '''
   Response.Write "<input type=hidden id='search' name='search' size=1 value='1'>"
   Response.Write "<input type=hidden id='iPageNo' name='iPageNo' value='1'>"
   if ahidden=0 then
      Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%' border=1>" 
      Response.Write "<TR VALIGN=top class=objectseditrow>"
      Response.Write "<td class=objectseditdatafieldvalueeven><br>"
      for i=1 to 3
         ss=CStr(i)
         Response.Write "&nbsp;&nbsp;<input type=radio class=checkradio id='fLinks" & ss & "' name='fLinks" & ss & "' value='AND' "
         if ssearch<>"2" or Request.Form("fLinks" & ss)="AND" then
            Response.Write schecked
         end if   
         Response.Write ">&nbsp;i"
         Response.Write "&nbsp;&nbsp;<input type=radio class=checkradio id='fLinks" & ss & "' name='fLinks" & ss & "' value='OR' "
         if Request.Form("fLinks" & ss)="OR" then
            Response.Write schecked
         end if           
         Response.Write ">&nbsp;lub"
         Response.Write "&nbsp;&nbsp;<input type=radio class=checkradio id='fLinks" & ss & "' name='fLinks" & ss & "' value='AND NOT' "
         if Request.Form("fLinks" & ss)="AND NOT" then
            Response.Write schecked
         end if                    
         Response.Write ">&nbsp;i&nbsp;nie"         
         Response.Write "<div id='aRowDiv" & ss & "' name='aRowDiv" & ss & "'>"
         Response.Write "&nbsp;" & ss & ".&nbsp;"
         Response.Write "<select id='fFieldName" & ss & "' name='fFieldName" & ss & "'>"
         Response.Write "<option value=''></option>"
'''
    i = 0
    for afield in atable.FieldsByTabID:
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            if not i:
                ret = ret + '''
         Response.Write "<option value='%s' "
         if i=1 and ssearch<>"2" or Request.Form("fFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.Name, afield.Name, afield.PrettyName, )
            else:
                ret = ret + '''
         Response.Write "<option value='%s' "
         If Request.Form("fFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.Name, afield.Name, afield.PrettyName, )
            i = i + 1

    ret = ret + '''
         Response.Write "</select>&nbsp;&nbsp;"
         Response.Write "<select id='fOperator" & ss & "' name='fOperator" & ss & "'>"
         Response.Write "<option value='Like2' "
         if Request.Form("fOperator" & ss)="Like2" then
            Response.Write sselected
         end if   
         Response.Write ">zawiera</option>"
         Response.Write "<option value='Like1' "
         if Request.Form("fOperator" & ss)="Like1" then
            Response.Write sselected
         end if
         Response.Write ">rozpoczyna się</option>"
         Response.Write "<option value='<>' "
         if Request.Form("fOperator" & ss)="<>" then
            Response.Write sselected
         end if   
         Response.Write ">różne od</option>"
         Response.Write "<option value='=' "
         if Request.Form("fOperator" & ss)="=" then
            Response.Write sselected
         end if   
         Response.Write ">=</option>"
         Response.Write "<option value='<' "
         if Request.Form("fOperator" & ss)="<" then
            Response.Write sselected
         end if   
         Response.Write "><</option>"
         Response.Write "<option value='<=' "
         if Request.Form("fOperator" & ss)="<=" then
            Response.Write sselected
         end if   
         Response.Write "><=</option>"
         Response.Write "<option value='>' "
         if Request.Form("fOperator" & ss)=">" then
            Response.Write sselected
         end if   
         Response.Write ">></option>"
         Response.Write "<option value='>=' "
         if Request.Form("fOperator" & ss)=">=" then
            Response.Write sselected
         end if   
         Response.Write ">>=</option>"        
         Response.Write "</select>&nbsp;&nbsp;"

         Response.Write "<input type=text id='fValue" & ss & "' name='fValue" & ss & "' size=20 value='" & Request.Form("fValue" & ss) & "'><br>"
         Response.Write "</div>"
      next
      Response.Write "<br></td></tr>"
      Response.Write "<TR VALIGN=top class=objectseditrow>"
      Response.Write "<td class=objectseditdatafieldvalueodd><br>"
      optArray=Array("5","10","15","20","25","50","100","250","500","1000","50000")
      Response.Write "Ilość pozycji na stronie: <select id='iRecsPerPage' name='iRecsPerPage'>"
      for i=0 to ubound(optArray)
         if Dession("DefaultSQLRecordsPerPage")=optArray(i) or (Dession("DefaultSQLRecordsPerPage")="" and i=1) then
            ss=" SELECTED"
         else
            ss=""
         end if
         if i=ubound(optArray) then
            sValue="wszystkie"
         else
            sValue=optArray(i)
         end if
         Response.Write "<option value='" & optArray(i) & "'" & ss &">" & sValue & "</option>"
      next
      Response.Write "</select>"
      Response.Write "<br><br></td></tr>"
      Response.Write "</TABLE>"    
      Response.Write "<br><Input class='pushbutton' TYPE='submit' VALUE='  Szukaj  '>"
   else
      Response.Write "<input type=hidden id='iRecsPerPage' name='iRecsPerPage' value='" & Request.Form("iRecsPerPage") & "' >"
      for i=1 to 3
         Response.Write "<input type=hidden id='fLinks" & CStr(i) & "' name='fLinks" & CStr(i) & "' value='" & Request.Form("fLinks" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fFieldName" & CStr(i) & "' name='fFieldName" & CStr(i) & "' value='" & Request.Form("fFieldName" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fOperator" & CStr(i) & "' name='fOperator" & CStr(i) & "' value='" & Request.Form("fOperator" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fValue" & CStr(i) & "' name='fValue" & CStr(i) & "' value='" & Request.Form("fValue" & CStr(i)) & "' >"
      next
   end if
   Response.Write "</form>"
end sub

Sub doShowControls(aPasek)
   dim i,istart,iend,ipages,scnt,imax,ssep,acarr
   if intNumberOfPages<=1 then
      Exit Sub
   End if
   ipages=5   
   'ssep="|"
   ssep="&nbsp;"
   response.write "<table border=0><tr><td align=center>"
   if intNumberOfPages>0 and aPageNumber>1 then
      Response.Write "<span onmouseover='javascript:window.status=""Pierwsza strona"";this.className=""tablepagecountbuttonpositionhover"";' onmouseout='javascript:window.status="""";this.className=""tablepagecountbuttonposition"";' class=tablepagecountbuttonposition onclick=""javascript:doSubmit(1);"">" & Chr(57) & "</span>" & ssep
   else
      Response.Write "<span class=tablepagecountbuttonpositiondisabled>" & Chr(57) & "</span>" & ssep
   end if
   if aPageNumber>1 and aPageNumber>1 then
      Response.Write "<span onmouseover='javascript:window.status=""Poprzednia strona"";this.className=""tablepagecountbuttonpositionhover"";' onmouseout='javascript:window.status="""";this.className=""tablepagecountbuttonposition"";' class=tablepagecountbuttonposition onclick=""javascript:doSubmit(" &  aPageNumber-1 & ");"">" & Chr(51) & "</span>" & ssep
   else  
      Response.Write "<span class=tablepagecountbuttonpositiondisabled>" & Chr(51) & "</span>" & ssep
   end if
   istart=aPageNumber-ipages
   iend=aPageNumber+ipages
   if istart<1 then
      istart=1
   end if
   if iend>intNumberOfPages then
      iend=intNumberOfPages
   end if
   if iend<=ipages*2 then
     iend=ipages*2+1
   end if
   if istart>=intNumberOfPages-ipages*2 then
      istart=intNumberOfPages-ipages*2
   end if
   if istart<1 then
      istart=1
   end if
   if iend>intNumberOfPages then
      iend=intNumberOfPages
   end if
   imax=len(CStr(iend))
   for i=istart to iend
      scnt=Replace(Right(" " & CStr(i),imax)," ","&nbsp;")
      if i=aPageNumber then
         Response.Write "<span onmouseover='javascript:window.status=""Strona nr " & CStr(i) & "/" & CStr(intNumberOfPages) & """;' onmouseout='javascript:window.status="""";' class=tablepagecountbuttonnumbersel>" &  scnt & "</span>" & ssep 'onclick=""javascript:doSubmit(" & CStr(i) & ");""
      else
         Response.Write "<span onmouseover='javascript:window.status=""Strona nr " & CStr(i) & "/" & CStr(intNumberOfPages) & """;this.className=""tablepagecountbuttonnumberhover"";' onmouseout='javascript:window.status="""";this.className=""tablepagecountbuttonnumber"";' class=tablepagecountbuttonnumber onclick=""javascript:doSubmit(" & CStr(i) & ");"">" &  scnt & "</span>" & ssep
      end if      
   next
   if aPageNumber<intNumberOfPages and aPageNumber<intNumberOfPages then
      Response.Write "<span onmouseover='javascript:window.status=""Następna strona"";this.className=""tablepagecountbuttonpositionhover"";' onmouseout='javascript:window.status="""";this.className=""tablepagecountbuttonposition"";' class=tablepagecountbuttonposition onclick=""javascript:doSubmit(" & aPageNumber+1 & ");"">" & Chr(52) & "</span>" & ssep
   else
     Response.Write "<span class=tablepagecountbuttonpositiondisabled>" & Chr(52) & "</span>" & ssep
   end if
   if intNumberOfPages>1 and aPageNumber<intNumberOfPages then
      Response.Write "<span onmouseover='javascript:window.status=""Ostatnia strona"";this.className=""tablepagecountbuttonpositionhover"";' onmouseout='javascript:window.status="""";this.className=""tablepagecountbuttonposition"";' class=tablepagecountbuttonposition onclick=""javascript:doSubmit(" & intNumberOfPages & ");"">" & Chr(58) & "</span>" & ssep
   else
      Response.Write "<span class=tablepagecountbuttonpositiondisabled>" & Chr(58) & "</span>" & ssep
   end if
   Response.Write "</td></tr>"
   if aPasek=1 and intNumberOfPages>20 then
      Response.Write "<tr><td align=center colspan=""500"">"
      acarr=Array("FF","F4","E8","E1","DA","D1","C8","BD","B2","AB","A4","9D","96","8F","88","7C","70","65","5A","2D")
      Response.Write "<font face='arial' size='+2'>"
      istart=CLng(apagenumber/intnumberOfPages*20)
      for i=1 to 20
         iend=CLng(i*intnumberOfPages/20)
         Response.Write "<span style='cursor:pointer;' onmouseover='javascript:window.status=""" & CStr(i*5) & "/100%" & """;' onmouseout='javascript:window.status="""";' onclick=""javascript:doSubmit(" & CStr(iend) & ");"">"
         if i=istart or (i=1 and istart<i) then
            Response.Write "<font color=red>" 
         else
            Response.Write "<font color='#0000" & acarr(i-1) & "'>"
         end if
         Response.Write "&#9632;</font></span>"
      next
      Response.Write "</font>"
      Response.Write "</td></tr>"
   end if
   Response.Write "</table>"
End Sub

   if Request.Form("search")="" or Request.Form("search")="2" then
      DisplaySearchForm 0
   elseif Request.Form("search")="1" then
Function GetFieldType(afieldname)
   dim afields,atypes,i
   GetFieldType=-1
'''
    sfl, sft = [], []
    for afield in atable.FieldsByTabID:
        if (afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            sfl.append('"' + afield.Name + '"')
            sft.append(str(afield.TypeID))
    ret = ret + '''
   afields = Array(%s)
   atypes  = Array(%s)
''' % (string.join(sfl, ','), string.join(sft, ','))
    ret = ret + '''
   for i=0 to UBound(afields)
      if afields(i)=afieldname then
         GetFieldType=atypes(i)
         Exit For
      end if
   next
End Function

Function CreateSingleSQLQueryConstraint(snumber,sp,sp1,iandcnt,iorcnt)
   dim afieldname,avalue,atype,aoperator,alink
   afieldname=Request.Form("fFieldName" & snumber)
   avalue=Replace(Request.Form("fValue" & snumber), "'", "''")
   atype=GetFieldType(Request.Form("fFieldName" & snumber))
   alink=" " & Request.Form("fLinks" & snumber) & " "
   aOperator=Request.Form("fOperator" & snumber)
   CreateSingleSQLQueryConstraint=True
   if aOperator="Like1" then
      aOperator="Like"
      avalue=avalue & "%"
   elseif aOperator="Like2" then
      aOperator="Like"
      avalue= "%" & avalue & "%"
   end if  
   if (atype=144) or (atype=145) then 'string
      avalue="'" & avalue & "'"
   elseif aOperator="Like" then
      if atype=32 then 'int
         afieldname=" CAST(" & afieldname & " as varchar(40)) "
         avalue="'" & avalue & "'"
      elseif atype=64 then 'double
         afieldname=" CAST(" & afieldname & " as varchar(40)) "
         avalue="'" & avalue & "'"
      elseif atype=112 then 'bit
         afieldname=" CAST(" & afieldname & " as varchar(40)) "
         avalue="'" & avalue & "'"
      elseif atype=96 then 'datetime
         afieldname=" Replace(CONVERT(varchar(40)," & afieldname & ",120),'-','/') "
         avalue="'" & avalue & "'"
      end if
   elseif (atype=32 or atype=64 or atype=112) then 'int
      if Not IsNumeric(avalue) then
         CreateSingleSQLQueryConstraint=False
      end if
   elseif (atype=96) then 'datetime
      avalue=getDateAsSQLDate(avalue)
      if avalue="" then
         CreateSingleSQLQueryConstraint=False
      else
         avalue="'" & avalue & "'"
      end if
   end if
   if alink=" OR " then
      if sp1<>"" then
         sp1=sp1 & alink '" AND "," OR "," AND NOT "
      end if
      sp1=sp1 & " " & afieldname & " " & aoperator & " " & avalue & " "
      iorcnt=iorcnt+1
   else
      if sp<>"" then
         sp=sp & alink '" AND "," OR "," AND NOT "
      elseif alink=" AND NOT " then
         sp=" NOT "
      end if
      sp=sp & " " & afieldname & " " & aoperator & " " & avalue & " "
      iandcnt=iandcnt+1
   end if
End Function

   wquery=True
   sp=""
   sp1=""
   iandcnt=0
   iorcnt=0
   for i=1 to 5     
      if Request.Form("fFieldName" & CStr(i))<>"" then
         wquery=wquery and CreateSingleSQLQueryConstraint(CStr(i),sp,sp1,iandcnt,iorcnt)
      end if
   next
   if sp1<>"" then
      if sp<>"" then
         if (iandcnt=iorcnt) and (iandcnt=1) then
            sp=sp & " OR " & sp1
         else
            sp=sp & " AND ( " & sp1 & " )"
         end if
      else
         sp=sp1
      end if
   end if 
   'Response.Write "<h2>SP:" & sp & "</h2>" 
   if wquery=0 then
      response.write "<h1>Popraw dane!</h1>"
      if rs.State<>adStateClosed then
         rs.Close
      end if
      Cn.Close
      set cn=Nothing
      set rs=Nothing
      response.end
   end if
'   if sp<>"" then
'      sp="WHERE " & sp
'   end if
   DisplaySearchForm 1
   Dession("DefaultSQLRecordsPerPage")=Request.Form("iRecsPerPage")
   aRecsPerPage=Clng(Request.Form("iRecsPerPage"))
   aPageNumber=Clng(Request.Form("iPageNo"))
   if Request.Form("iForPrinting")<>"" then
      aForPrinting=1
   else
      aForPrinting=0
   end if
'''
    asp = atable.GetStoredProcedure('DefaultSearch')
    ret = ret + '''
   Set cmd1 = Server.CreateObject("ADODB.Command")
   cmd1.CommandTimeout=600
   cmd1.ActiveConnection = cn
   cmd1.ActiveConnection.CursorLocation = adUseClient
   cmd1.CommandType = adCmdStoredProc
   cmd1.CommandText = "%s"
   cmd1.Parameters.Refresh
   Cmd1.Parameters("@Page").Value=aPageNumber
   Cmd1.Parameters("@Size").Value=aRecsPerPage
   sob="%s"
   if sob<>"" then
      Cmd1.Parameters("@sWhereOrder").Value=sp & " ORDER BY " & sob
   else
      Cmd1.Parameters("@sWhereOrder").Value=sp
   end if
   set rs=cmd1.Execute
   ReturnValue=CLng(cmd1.Parameters.Item(0).Value)
   MoreRecords=CLng(cmd1.Parameters("@MoreRecords").Value)
   if MoreRecords>0 then
      intNumberOfPages=int(MoreRecords / aRecsPerPage)
      if (MoreRecords mod aRecsPerPage)>0 then
         intNumberOfPages=intNumberOfPages+1
      end if
      Response.Write "<h1>Etap II</h1>"
      Response.Write "<p>Z wyświetlonej listy wybierz właściwą pozycję, do której zostanie dopisany nowy dokument. Klikając <a class=reflistoutnavy href='javascript:history.back();'>tutaj</a> wrócisz do parametrów wyszukiwania.</p>"     
      doShowControls 0
      Response.Write("<span class='objectsviewcaption'>Tabela wynikowa</span>")
      Response.Write("<TABLE class='objectsviewtable'><TR>")
      Response.Write "<TH class='objectsviewheader'>l.p.</TH>"
''' % (asp.Name, string.join(atable.DefaultSQLQuery.ThisTable.SortedFields, ','))
    for afield in atable.FieldsByTabID:
        if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            ret = ret + '''
      Response.Write "<TH class='objectsviewheader'>%s</TH>"
''' % (afield.PrettyName, )
    ret = ret + '''
      Response.Write("</TR>")
      aLpFirst=rs.Fields(1).Value
      Do While Not rs.EOF
         aLpLast=rs.Fields(1).Value
         if CLng(aLpLast) mod 500 = 0 then
            Response.flush()
         end if
         Response.Write "<TR class='objectsviewrow'>"
         aoid=Trim(rs.Fields(0).Value)
         Response.Write "<td class='objectsviewdataeven'>" 'l.p.
         Response.Write "<a class='objectitemasanchor' href='newdoc_%d.asp?doid=" & Request.QueryString("doid") & "&boid=" & cstr(aoid) & "'>"
         arsValue=rs.Fields(1).Value
         if arsValue<>"" then
            Response.Write server.htmlencode(arsValue)
         else
            Response.Write "&nbsp;"
         end if   
         Response.Write "</a></td>"
''' % (adocument.OID, )
    i = 2
    for afield in atable.FieldsByTabID:
        if (afield.IsAliased or afield.IsSearch) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
            if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'bool']:
                ret = ret + '''
         Response.Write "<td class='objectsviewdataeven'>" '%s
         Response.Write "<a class='objectitemasanchor' href='newdoc_%d.asp?doid=" & Request.QueryString("doid") & "&boid=" & cstr(aoid) & "'>"

         sdv1=rs.Fields(%d).Value
         if (rs.Fields(%d).Type=7) or (rs.Fields(%d).Type=133) or (rs.Fields(%d).Type=134) or (rs.Fields(%d).Type=135) then
            sdv1=getDateTimeAsStr(sdv1)
         end if

         arsValue=Trim(sdv1)
         if arsValue<>"" then
            Response.Write server.htmlencode(arsValue)
         else
            Response.Write "&nbsp;"
         end if   
         Response.Write "</a></td>"
''' % (afield.PrettyName, adocument.OID, i, i, i, i, i)
            i = i + 1
    ret = ret + '''
         Response.Write "</TR>"
         rs.MoveNext
      Loop
      Response.Write("</TABLE>")
      if intNumberOfPages>1 then
         Response.Write "Wiersze " & CStr(aLpfirst) & " - " & CStr(aLpLast) & " z " & CStr(MoreRecords)
      end if
      doShowControls 1
      Response.Write "<hr><button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doSubmitRepeat()'> Poprzedni etap </button>"
   Else
      Response.Write "<h1>Brak danych spełniających zadane warunki</h1><br>"
      Response.Write "<button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doSubmitRepeat()'>Powrót</button>"
   End if
 End if
else
'''
    ret = ret + """
if Request.Form("_OID")="" then
   Response.Write "<h1>Etap III</h1><p>To już ostatni etap wprowadzania nowego dokumentu. Po wpisaniu niezbędnych danych do poniższych pól, rozpocznie się przepływ dokumentu pomiędzy działami. Ten dokument dotyczy <b><i>"
"""
    aselect = atable.GetSelectClause()
    aselect.AddCriteria(atable, '=', 'Request.QueryString("boid")', avariable=1)
    ret = ret + """
   rs.Open "%s", cn
   sdotyczy=""
   if not rs.EOF then             
""" % (aselect.AsString(), )
    for afield in atable.FieldsByTabID:
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money']:
            if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
                ret = ret + """
         sdv1=rs.Fields(%d).Value
         if (rs.Fields(%d).Type=7) or (rs.Fields(%d).Type=133) or (rs.Fields(%d).Type=134) or (rs.Fields(%d).Type=135) then
            sdv1=getDateTimeAsStr(sdv1)
         end if
      if sdv1<>"" then
        sdotyczy=sdotyczy & sdv1 & " "
        Response.Write sdv1 & "&nbsp;"
      end if
""" % (aselect.FieldsDict[afield.NameSQL], aselect.FieldsDict[afield.NameSQL], aselect.FieldsDict[afield.NameSQL], aselect.FieldsDict[afield.NameSQL], aselect.FieldsDict[afield.NameSQL],
                )
    ret = ret + """
      sdotyczy=Trim(sdotyczy)
      sdotyczy=Replace(sdotyczy, "'", "")
   end if
   Response.Write "</i></b></p>"
"""
    ret = ret + """   
   Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='newdoc_%d.asp?doid=" & Request.QueryString("doid") & "&boid=" & Request.QueryString("boid") & "'>"
   Response.Write "<input type=hidden id='_OID' name='_OID' value='%d'>"
   Response.Write "<input type=hidden id='_SDotyczy' name='_SDotyczy' value='" & sdotyczy & "'>"
   Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%%' border=1>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), adocument.OID, adocument.OID)
    fls = ['_OID', ]
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            fls.append(afield.Name)
    sf = string.join(fls, ',')
    i = 1
    for afield in btable.FieldsByTabID:
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
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'numeric':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'money':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'date':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'datetime':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),15\n' % (afield.Name, afield.Name, )
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),1\n' % (afield.Name, afield.Name, )
            elif afield.Type == 'bool':
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\'>"\n' % (afield.Name, afield.Name)
            elif afield.Type == 'dict':
                ret = ret + """
Response.Write "<SELECT id='%s' name='%s'>"
""" % (afield.Name, afield.Name, )
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
            elif afield.Type == 'external dict multiple':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelectionMultiple(afield, aisnew=1)
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=15 %s></textarea>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            ret = ret + 'Response.Write "</td></tr>"\n'
            i = i + 1
    ret = ret + """
   Response.Write("</TABLE>")
   Response.Write "<br><input class='pushbutton' TYPE='submit' VALUE='  Zapamiętaj  ' tabIndex=1>&nbsp;&nbsp;"
   Response.Write "<input class='pushbutton' type='button' onclick='javascript:history.back();' value=' Poprzedni etap ' tabIndex=2>"
   Response.Write "</form>"
"""
    ret = ret + WriteTableFieldsDescription(btable)
    ret = ret + """
else
      rs.ActiveConnection = cn
      rs.CursorType = adOpenKeyset
      rs.LockType = adLockOptimistic
      rs.Source = "select %s,_Dotyczy,_UID,_UserName,_DateTime from %s WHERE _OID='-1'"
      rs.Open
""" % (sf, btable.NameSQL)
    ret = ret + """
call RSAddNew(rs)
"""
    i = 1
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if afield.Type == 'string':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'numeric' or afield.Type == 'money':
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
            elif afield.Type == 'dict':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict':
                #$$
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict multiple':
                #$$ - na pewno BABOL
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'text':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'integer':
                ret = ret + '         if IsNumeric(Request.Form("%s")) then rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name, afield.Name)
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
        i = i + 1
    ret = ret + """
   rs("_Dotyczy")=Request.QueryString("boid")
   rs("_UID")=Dession("uid")
   rs("_UserName")=Dession("username")
   rs("_DateTime")=Now
   rs.Update
   Call SetItemHistory(rs,"%s","Nowy dokument")
   
   Set rs1 = Server.CreateObject("ADODB.Recordset") 
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      rs1.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,BZRID,BZROID,BZRInfo,_UID,_UserName,_DateTime from %s WHERE _OID='-1'"
      rs1.Open
      rs1.AddNew
      rs1("DokumentID")="%d"
      rs1("DokumentOID")=rs("_OID")
      rs1("DokumentSymbol")="%s"
      rs1("DokumentTitle")="%s"
      'rs1("DokumentInfo")=""
      'rs1("DokumentDateTime")=""
      rs1("BZRID")="%d"
      rs1("BZROID")=Request.QueryString("boid")
      rs1("BZRInfo")=Request.Form("_SDotyczy")
      rs1("_UID")=Dession("uid")
      rs1("_UserName")=Dession("username")
      rs1("_DateTime")=Now
      rs1.Update
      Call SetItemHistory(rs1,"%s","Rejestracja pierwszych czynnosci dla dokumentu")
      if rs1.State<>adStateClosed then
         rs1.Close
      end if

      rs1.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,CzynnoscSymbol,CzynnoscID,CzynnoscName,CzynnoscDescription,CzynnoscState,CzynnoscDateTime,JednostkaID,JednostkaInfo,BZRID,BZROID,BZRInfo,Uwagi,_UID,_UserName,_DateTime,CreatorUID,CreatorName from %s WHERE _OID='-1'"
      rs1.Open
""" % (btable.NameSQL, adocumentcustomertable.NameSQL, adocument.OID, adocument.Symbol, adocument.Nazwa, adocument.SourceTable.OID, adocumentcustomertable.NameSQL, aetapytable.NameSQL)
    for aczynnosc in adocument.czynnosci:
        if aczynnosc.Symbol == 'T':
            astate = 1
        else:
            astate = 0
        ret = ret + """
      rs1.AddNew
      rs1("DokumentID")="%d"
      rs1("DokumentOID")=rs("_OID")
      rs1("DokumentSymbol")="%s"
      rs1("DokumentTitle")="%s"
      rs1("DokumentInfo")=""
      rs1("CzynnoscSymbol")="%s"
      rs1("CzynnoscID")="%d"
      rs1("CzynnoscName")="%s"
      rs1("CzynnoscDescription")=""
      rs1("CzynnoscState")="%d"
      rs1("JednostkaID")="%d"
      rs1("JednostkaInfo")="%s"
      rs1("BZRID")="%d"
      rs1("BZROID")=Request.QueryString("boid")
      rs1("BZRInfo")=Request.Form("_SDotyczy")
      rs1("Uwagi")=""
      rs1("_UID")=Dession("uid")
      rs1("_UserName")=Dession("username")
      rs1("_DateTime")=Now
      rs1("CreatorUID")=Dession("uid")
      rs1("CreatorName")=Dession("username")
""" % (adocument.OID, adocument.Symbol, adocument.Nazwa, aczynnosc.Symbol, aczynnosc.OID, aczynnosc.Tresc, astate, aczynnosc.Department.OID, aczynnosc.Department.Nazwa, adocument.SourceTable.OID,
        )
    ret = ret + """
      rs1.Update
      Call SetItemHistory(rs1,"%s","Rejestracja czynnosci dla dokumentu")
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      set rs1=Nothing
Response.Write "<script language='javascript'>" & chr(10)
Response.Write "window.location='%s_so.asp?ioid=" & rs("_OID") & "';"  & chr(10)
Response.Write "</script>"
end if
""" % (aetapytable.NameSQL, btable.NameFile, )

    ret = ret + """
end if
"""
    return ret


#*********************************************************************************
def DocumentSelectSingleASP(adocument, aetapytable):
    fls = ['%s._OID' % adocument.SQLTable.NameSQL, '%s._Dotyczy' % adocument.SQLTable.NameSQL]
    for afield in adocument.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            fls.append(afield.NameSQL)
#   for afield in adocument.SourceTable.SQLTable.FieldsByTabID:
#      if afield.Name[:1]!='_' and afield.IsAliased and afield.IsInteractive:
#         fls.append(afield.NameSQL)
    sf = string.join(fls, ',')
    ret = """
if (Request.QueryString("ioid")="") or (Request.QueryString("ioid")="-1") then
  Response.Write "<!-- pusty rekord -->"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   Set rs=Nothing
   Response.End
end if
if (Request.QueryString("dnum")<>"") and (Request.QueryString("dnum")=Dession("doknumber")) then
   cn.Execute "DELETE %s WHERE _OID='" & Request.QueryString("ioid") & "'"
   cn.Execute "DELETE %s WHERE DokumentOID='" & Request.QueryString("ioid") & "'"
   cn.Execute "DELETE %s WHERE DokumentOID='" & Request.QueryString("ioid") & "'"
   cn.Execute "DELETE %s WHERE DokumentOID='" & Request.QueryString("ioid") & "'"
   cn.Execute "DELETE %s WHERE DokumentOID='" & Request.QueryString("ioid") & "'"
""" % (adocument.SQLTable.NameSQL, adocument.CRM.Table_DokumentyKontrahentow.NameSQL, adocument.CRM.Table_DokKreator.NameSQL, adocument.CRM.Table_Etapy.NameSQL, adocument.CRM.Table_Kreator.NameSQL)
    for awizard in adocument.Wizards:
        for astep in awizard.steps:
            ret = ret + """                                                    
   cn.Execute "DELETE %s WHERE _Dotyczy='" & Request.QueryString("ioid") & "'"
""" % (astep.SQLTable.NameSQL, )
    ret = ret + """
   SetItemHistoryByOID Request.QueryString("ioid"),"%s","Usuniecie dokumentu"
""" % (adocument.SQLTable.NameSQL, )
    ret = ret + """
%s
""" % (adocument.ASPSourceOnDelete, )
    ret = ret + """
   Response.Write "<script language='javascript'>" & chr(10)
   Response.Write "window.location='dep_%d.asp';"  & chr(10)
   Response.Write "</script>"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   Set rs=Nothing
   Response.End
end if
""" % (adocument.czynnosci[0].Department.OID, )
    ret = ret + """
if (Request.QueryString("ioid")<>"") and (Request.QueryString("ioid")<>"-1") then
   cn.Execute "update %s set CzynnoscDescription='' where DokumentOID='" & Request.QueryString("ioid") & "'"
end if
""" % (adocument.CRM.Table_Etapy.NameSQL, )
    ret = ret + """
rs.Open "SELECT %s FROM %s WHERE %s._OID='" & Request.QueryString("ioid") & "'", cn
Response.Write("<TABLE>")
""" % (sf, adocument.SQLTable.NameSQL, adocument.SQLTable.NameSQL)
    i = 2
    for afield in adocument.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class=objectseditdatafieldvalue>"\n' % (afield.PrettyName)
            if afield.Type == 'bool':
                ret = ret + """
if CBool(rs.Fields(%d).Value) then
   Response.Write "Tak"
else
   Response.Write "Nie"
end if
""" % (i, )
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield)
            elif afield.Type == 'external dict multiple':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDictMultiple(afield)
            elif afield.Type == 'money':
                ret = ret + '   Response.Write Currency2HTML(rs.Fields(%d).Value,0)\n' % (i, )
            else:
                ret = ret + '   Response.Write rs.Fields(%d).Value\n' % (i, )
            ret = ret + 'Response.Write ("</td>")\n'
            i = i + 1
    ret = ret + """
Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>Dotyczy:</td><td class=objectseditdatafieldvalue>"
Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_so.asp?ioid=" & rs.Fields(1).Value & "'>"
""" % (adocument.SourceTable.SQLTable.NameFile, )
    ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(adocument.SQLTable.FieldsByName('_Dotyczy'))
    ret = ret + """
Response.Write "</a></td></tr>"
Response.Write "</TABLE>"
Response.Write "<br>"
"""

    ret = ret + """
   cn.Execute "DELETE %s WHERE _OID NOT IN (SELECT KreatorOID FROM %s)"
""" % (adocument.CRM.Table_Kreator.NameSQL, adocument.CRM.Table_DokKreator.NameSQL, )
    for awizard in adocument.Wizards:
        if awizard.steps:
            ret = ret + """
if CheckUserAccess("%s")=1 then 'Wizard - AccessLevelView
   Set rs1=Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select _OID,DokumentID,DokumentOID,KreatorEtapID,KreatorEtapOID,KreatorID,KreatorOID,StanEtapu,_datetime,_UserName from %s WHERE DokumentOID='" & Request.QueryString("ioid") & "' AND KreatorID=%d AND KreatorEtapID=%d ORDER BY _datetime DESC"
   rs1.Open
   if not rs1.EOF then
      Response.Write("<span class='objectsviewcaption'>%s</span>")
      Response.Write("<TABLE class='objectsviewtable'>")
      Response.Write("<TR>")
      Response.Write "<TH class='objectsviewheader'>Ostatnio zmodyfikowany</TH>"
      Response.Write "<TH class='objectsviewheader'>Przez</TH>"
      Response.Write "<TH class='objectsviewheader'>Stan zaawansowania</TH>"
      Response.Write("</TR>")
      Do While Not rs1.EOF
         Response.Write "<TR class='objectsviewrow'>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "&doktypeid=" & rs1("DokumentID") & "&dokid=" & rs1("DokumentOID") & "'>" & rs1.Fields("_datetime").Value & "</a>"
            Response.Write "</TD>"
            Response.Write "<td class='objectsviewdataeven'>"
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "&doktypeid=" & rs1("DokumentID") & "&dokid=" & rs1("DokumentOID") & "'>" & rs1.Fields("_UserName").Value & "</a>"
            Response.Write "</TD>"
            if rs1.Fields("StanEtapu").Value>0 then
               Response.Write "<td class='objectsviewdataeven'>"
               sz="zakończony"
            else
               Response.Write "<td class='objectsviewdataeven' align=center>"
               sz="&nbsp;-&nbsp;"
            end if
            Response.Write "<a class='objectitemasanchor' href='WSTP_%d_so.asp?ioid=" & rs1("KreatorEtapOID") & "&doktypeid=" & rs1("DokumentID") & "&dokid=" & rs1("DokumentOID") & "'>" & sz & "</a>"
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
""" % (awizard.AccessLevelView, adocument.CRM.Table_DokKreator.NameSQL, awizard.OID, awizard.steps[0].OID, awizard.Title, awizard.steps[0].OID, awizard.steps[0].OID, awizard.steps[0].OID)
#awizard.steps[0].SQLTable
#         ret=ret+SQLTableGetSelectAllLinkedTablesASP(adocument.CRM.Table_DokKreator,alinkparam='&doktypeid='+str(adocument.OID),alinkfield='DokumentOID')

    ret1 = """
Set rs1 = Server.CreateObject("ADODB.Recordset") 
rs1.ActiveConnection = cn
rs1.CursorType = adOpenKeyset
rs1.LockType = adLockOptimistic
rs1.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,CzynnoscID,CzynnoscSymbol,CzynnoscName,CzynnoscDescription,CzynnoscState,CzynnoscDateTime,ObowiazujeOdDateTime,JednostkaID,JednostkaInfo,BZRID,BZROID,BZRInfo,Uwagi,_UID,_UserName,CreatorUID,CreatorName from %s where (DokumentID='%d') AND (DokumentOID='" & Request.QueryString("ioid") & "') order by CzynnoscSymbol"
rs1.Open

allowdelete=0

Response.Write "<span class='objectsviewcaption'>Czynności:</span>"
Response.Write "<TABLE class='objectsviewtable'>"
Response.Write "<TR>"
Response.Write "<TH class='objectsviewheader'>Symbol</TH>"
Response.Write "<TH class='objectsviewheader'>Stan</TH>"
Response.Write "<TH class='objectsviewheader'>Opis</TH>"
Response.Write "<TH class='objectsviewheader'>Jednostka organizacyjna</TH>"
Response.Write "<TH class='objectsviewheader'>Data ostatniej modyfikacji</TH>"
Response.Write "<TH class='objectsviewheader'>Obowiązuje od</TH>"
Response.Write "<TH class='objectsviewheader'>Utworzony przez</TH>"
Response.Write "<TH class='objectsviewheader'>Zatwierdzony przez</TH>"
Response.Write "</TR>"
Do While Not rs1.EOF
   ssym1=rs1("CzynnoscSymbol")
   if ssym1="T" then
      Response.Write "<TR class='objectsviewrow'>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscSymbol") & "</a></TD>"
      astate=rs1("CzynnoscState")
      if astate="0" then
         astate="czeka"
      end if
      if astate="1" then
         astate="w trakcie"
         allowdelete=1
      end if
      if astate="2" then
         astate="załatwione!"
      end if
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & astate & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscName") & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("JednostkaInfo") & "</a></TD>"

      if astate="w trakcie" then
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("ObowiazujeOdDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CreatorName") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'>&nbsp;</TD>"
      end if
      if astate="załatwione!" then
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("ObowiazujeOdDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CreatorName") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("_UserName") & "</a></TD>"
      end if

      Response.Write "</TR>"
   end if
   rs1.MoveNext
Loop
rs1.MoveFirst
Do While Not rs1.EOF
   ssym1=rs1("CzynnoscSymbol")
   if ssym1<>"T" then
      Response.Write "<TR class='objectsviewrow'>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscSymbol") & "</a></TD>"
      astate=rs1("CzynnoscState")
      if astate="0" then
         astate="czeka"
      end if
      if astate="1" then
         astate="w trakcie"
      end if
      if astate="2" then
         astate="załatwione!"
      end if
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & astate & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscName") & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("JednostkaInfo") & "</a></TD>"

      if astate="czeka" then
         Response.Write "<td class='objectsviewdataeven'>&nbsp;</TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("ObowiazujeOdDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'>&nbsp;</TD>"
         Response.Write "<td class='objectsviewdataeven'>&nbsp;</TD>"
      end if
      if astate="w trakcie" then
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("ObowiazujeOdDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CreatorName") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'>&nbsp;</TD>"
      end if
      if astate="załatwione!" then
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CzynnoscDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("ObowiazujeOdDateTime") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("CreatorName") & "</a></TD>"
         Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='dep_" & rs1("JednostkaID") & ".asp'>" & rs1("_UserName") & "</a></TD>"
      end if

      Response.Write "</TR>"
   end if
   rs1.MoveNext
Loop
Response.Write "</TABLE>"

if rs1.State<>adStateClosed then
   rs1.Close
end if
Set rs1=Nothing
""" % (aetapytable.NameSQL, adocument.OID)
    ret2 = """
Response.Write "<hr><a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_au.asp?ioid=" & Request.QueryString("ioid") & "'>Edycja danych</a><br>"
""" % (adocument.SQLTable.NameFile, )
    ret2 = ret2 + """
if allowdelete>0 then
   dnum=CStr(CLng(1e8*rnd(0)+Timer))
   Dession("doknumber")=dnum
   dhref="DOK_%d_so.asp?ioid=" & Request.QueryString("ioid") & "&dnum=" & dnum
   Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' onclick=""javascript:if (confirm('Czy na pewno chcesz wybrać tę pozycję?')) {this.href='" & dhref & "';} else {this.href='javascript:var umm=1;';} ;"" HREF=""javascript:var umm=1;"" >Usuń ten dokument</a><br>"
end if                                                             
""" % (adocument.OID, )

    if adocument.Wizards:
        ret2 = ret2 + """
  Response.Write "<BR>"
  abr=0
"""
    for awizard in adocument.Wizards:
        swt = awizard.Title
        if not swt:
            swt = 'Nowy kreator'
        ret2 = ret2 + """
if CheckUserAccess("%s")=1 then
   abr=1
   Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s.asp?doktypeid=%d&dokid=" & Request.QueryString("ioid") & "'>%s</a><br>"
end if
""" % (awizard.AccessLevelView, awizard.NewPage, adocument.OID, swt, )

    if adocument.pages:
        ret2 = ret2 + """
if abr=1 then
   Response.Write "<BR>"
end if
"""
    for apage in adocument.pages:
        print apage.Title
        ret2 = ret2 + """
if CheckUserAccess("%s")=1 then
  Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s?doktypeid=%d&dokid=" & Request.QueryString("ioid") & "'>%s</a><br>"
end if
""" % (apage.AccessLevelView, apage.PageFile, adocument.OID, apage.Title, )
    return [ret, ret1, ret2]


#*********************************************************************************
def SQLTableGetSelectAllDocumentsForCustomerASP(asourcetable, adocumentcustomertable, atabid=0):
    ret = ''
    if atabid:
        ret = """
if Request.QueryString("sheet")="%d" then
""" % atabid
    ret = ret + """
      Set rs1 = Server.CreateObject("ADODB.Recordset") 
      rs1.ActiveConnection = cn
      rs1.CursorType = adOpenKeyset
      rs1.LockType = adLockOptimistic
      rs1.Source = "select _OID,DokumentID,DokumentOID,DokumentSymbol,DokumentTitle,DokumentInfo,DokumentDateTime,BZROID,BZRID from %s WHERE (BZRID=%d) and (BZROID='" & Request.QueryString("ioid") & "') ORDER BY DokumentDateTime"
      rs1.Open
if not rs1.EOF then
Response.Write "<span class='objectsviewcaption'>Dokumenty</span>"
Response.Write "<TABLE class='objectsviewtable'>"
Response.Write "<TR>"
Response.Write "<TH class='objectsviewheader'>Symbol</TH>"
Response.Write "<TH class='objectsviewheader'>Nazwa</TH>"
Response.Write "<TH class='objectsviewheader'>Data wprowadzenia</TH>"
Response.Write "</TR>"
Do While Not rs1.EOF
   Response.Write "<TR class='objectsviewrow'>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='DOK_" & rs1("DokumentID") & "_so.asp?ioid=" & rs1("DokumentOID") & "'>" & rs1("DokumentSymbol") & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='DOK_" & rs1("DokumentID") & "_so.asp?ioid=" & rs1("DokumentOID") & "'>" & rs1("DokumentTitle") & "</a></TD>"
      Response.Write "<td class='objectsviewdataeven'><a class='objectitemasanchor' href='DOK_" & rs1("DokumentID") & "_so.asp?ioid=" & rs1("DokumentOID") & "'>" & rs1("DokumentDateTime") & "</a></TD>"
   Response.Write "</TR>"
   rs1.MoveNext   
Loop
Response.Write("</TABLE>")
end if
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      set rs1=Nothing
""" % (adocumentcustomertable.NameSQL, asourcetable.OID)
    if atabid:
        ret = ret + """
end if
"""
    return ret


#*********************************************************************************
def SQLTableGetSelectAllLinkedTablesASP(atable, btable, atabid=0, sfield='', alinkparam='', alinkfield='_Dotyczy', aorderby='', anodictfields=0, aextendfields=None, atablecaption=''):
    if aextendfields is None:
        aextendfields = []
    flexnames, flexaliases = [], []
    for afxname, afxalias in aextendfields:
        flexnames.append(afxname)
        flexaliases.append(afxalias)
    ret = ''
    if atabid:
        asecurity = atable.TabsByIDSecurity.get(atabid, '')
        #      asecurity=''
        #      if atabid in atable.TabsByIDSecurity.keys():
        #         asecurity=atable.TabsByIDSecurity[atabid]
        ret = """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 3</font></h1>")
   else
""" % (atabid, asecurity)
    fls = ['%s._OID' % (btable.NameSQL, ), ]
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            fls.append(afield.NameSQL)
    if not alinkfield in fls:
        fls.append(btable.NameSQL + '.' + alinkfield)
    fls.extend(flexnames)
    sf = string.join(fls, ',')
    if not sfield:
        ret = ret + """
if Request.QueryString("ioid")<>"" then
"""
    if sfield:
        swhere = sfield
    else:
        swhere = 'Request.QueryString("ioid")'
    if not aorderby:
        aorderby = btable.FieldsByTabID[0].NameSQL
    if not atablecaption:
        atablecaption = btable.TableCaption
    ret = ret + """
Set rs1 = Server.CreateObject("ADODB.Recordset") 
rs1.ActiveConnection = cn
rs1.CursorType = adOpenKeyset
rs1.LockType = adLockOptimistic
rs1.Source = "select %s from %s WHERE %s='" & %s & "' ORDER BY %s"
rs1.Open
if not rs1.EOF then
   Response.Write("<span class='objectsviewcaption'>%s</span>")
   Response.Write("<TABLE class='objectsviewtable'>")
   Response.Write("<TR>")
""" % (sf, btable.NameSQL, alinkfield, swhere, aorderby, atablecaption, )
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            if not (anodictfields and afield.Type in ['external dict', 'external dict multiple']):
                ret = ret + """
   Response.Write "<TH class='objectsviewheader'>%s</TH>"
""" % (afield.PrettyName, )
    for afxalias in flexaliases:
        ret = ret + """
   Response.Write "<TH class='objectsviewheader'>%s</TH>"
""" % (afxalias, )
    ret = ret + """
   Response.Write("</TR>")
   Do While Not rs1.EOF
      aoid=rs1.Fields(0).Value
      Response.Write "<TR class='objectsviewrow'>"
"""
    i = 1
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            if not (anodictfields and afield.Type in ['external dict', 'external dict multiple']):
                ret = ret + """
Response.Write "<td class='objectsviewdataeven'>"
Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s'>" & rs1.Fields(%d).Value & "</a>"
Response.Write "</TD>"
""" % (btable.NameFile, alinkparam, i)
            i = i + 1
    for afxname in flexnames:
        ret = ret + """
Response.Write "<td class='objectsviewdataeven'>"
Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s'>" & rs1.Fields("%s").Value & "</a>"
Response.Write "</TD>"
""" % (btable.NameFile, alinkparam, afxname)
        i = i + 1
    ret = ret + """
      Response.Write "</TR>"
      rs1.MoveNext
   Loop
   Response.Write("</TABLE>")
end if
if rs1.State<>adStateClosed then
   rs1.Close
end if
set rs1=Nothing
"""
    if not sfield:
        ret = ret + """
end if
"""
    if atabid:
        ret = ret + """
   end if
end if
"""
    return ret


#*********************************************************************************
def DocumentSelectAllASP(adocument):
    atable = adocument.SQLTable
    fls = ['_OID', ]
    for afield in atable.FieldsByTabID:
        fls.append(afield.Name)
    sf = string.join(fls, ',')
    ret = """   rs.Open "select %s from %s ORDER BY %s", cn
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (sf, atable.NameSQL, atable.FieldsByTabID[0].Name, atable.TableCaption, )
    for afield in atable.FieldsByTabID:
        ret = ret + """
Response.Write "<TH class='objectsviewheader'>%s</TH>"
""" % (afield.PrettyName, )
    ret = ret + """
Response.Write("</TR>")
Do While Not rs.EOF
   Response.Write "<TR class='objectsviewrow'>"
   aoid=rs.Fields(0).Value
   For i = 1 to rs.Fields.Count-1
      Response.Write "<td class='objectsviewdataeven'>"
      Response.Write "<a class='objectitemasanchor' href='%s.asp?ioid=" & cstr(aoid) & "'>" & rs.Fields(i).Value & "</a>"
      Response.Write "</TD>"
   Next
   Response.Write "</TR>"
   rs.MoveNext   
Loop
Response.Write("</TABLE>")
""" % (atable.NameFile + '_so', )
    return ret


#*********************************************************************************
def SQLTableSelectBaseTable(atable, btable):
    fls = ['%s._OID' % (atable.NameSQL, ), ]
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            fls.append(afield.NameSQL)
    sf = string.join(fls, ',')
    ret = """
sub DisplaySearchForm()
      Response.Write "<h1>Etap I</h1>"
      Response.Write "<p>Ta informacja jest powiązana z już istniejącymi danymi w systemie. Wpisz w poniższych polach informacje pozwalające znaleźć tę informację źródłową.</p>"
      Response.Write "<form %s name=form1 id=form1 METHOD='post' ACTION='%s_aun.asp'>"
      Response.Write "<input type=hidden id='search' name='search' size=1 value='1'>"
      Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%%' border=1>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), btable.NameFile,
       )
    i = 1
    for afield in atable.FieldsByTabID:
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money']:
            if afield.Name[:1] != '_' and afield.IsSearch and afield.IsInteractive:
                if i % 2:
                    snclass = 'objectseditdatafieldnameeven'
                    svclass = 'objectseditdatafieldvalueeven'
                else:
                    snclass = 'objectseditdatafieldnameodd'
                    svclass = 'objectseditdatafieldvalueodd'
                ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s><input type=text id=\'%s\' name=\'%s\' size=20 value=\'\' %s></td></tr>"\n' % (snclass, afield.PrettyName, svclass, afield.Name, afield.Name, GetFieldValidationText(afield, aissearch=1))
                i = i + 1
    ret = ret + """
      Response.Write("</TABLE>")
      Response.Write "<br><input class='pushbutton' TYPE='submit' VALUE='  Szukaj  ' tabIndex=1></form>"
end sub
   if Request.Form("search")="" then
      DisplaySearchForm
   else
      sp=""
"""
    i = 1
    for afield in atable.FieldsByTabID:
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money']:
            if afield.Name[:1] != '_' and afield.IsSearch and afield.IsInteractive:
                ret = ret + """
      if Request.Form("%s")<>"" then
         if sp<>"" then sp=sp & " AND "
         sp=sp & "%s LIKE '%%" & Replace(Request.Form("%s"), "'", "''") & "%%' "
      end if
""" % (afield.Name, afield.NameSQL, afield.Name, )
        i = i + 1
    ret = ret + """
      if sp="" then 
         DisplaySearchForm
      else
      ssql="select top 1000 %s from %s WHERE " & sp & " ORDER BY %s"
      rs.Open ssql, cn
""" % (sf, atable.NameSQL, atable.FieldsByTabID[0].NameSQL)
    ret = ret + """
Response.Write "<h1>Etap II</h1>"
Response.Write "<p>Z wyświetlonej listy wybierz właściwą pozycję, do której zostaną dopisane nowe dane. Klikając <a class=reflistoutnavy href='javascript:history.back();'>tutaj</a> wrócisz do parametrów wyszukiwania.</p>"
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (atable.TableCaption, )
    for afield in atable.FieldsByTabID:
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money'] and afield.IsAliased and afield.IsInteractive:
            ret = ret + 'Response.Write "<TH class=\'objectsviewheader\'>%s</TH>"\n' % (afield.PrettyName, )
    ret = ret + """
Response.Write("</TR>")
Do While Not rs.EOF
   Response.Write "<TR class='objectsviewrow'>"
   aoid=rs.Fields(0).Value
   For i = 1 to rs.Fields.Count-1
      Response.Write "<td class='objectsviewdataeven'>"
         sdv1=rs.Fields(i).Value
         if (rs.Fields(i).Type=7) or (rs.Fields(i).Type=133) or (rs.Fields(i).Type=134) or (rs.Fields(i).Type=135) then
            sdv1=getDateTimeAsStr(sdv1)
         end if
      Response.Write "<a class='objectitemasanchor' href='%s_au.asp?boid=" & cstr(aoid) & "'>" & sdv1 & "</a>"
      Response.Write "</TD>"
   Next 
   Response.Write "</TR>"
   rs.MoveNext   
Loop
Response.Write("</TABLE>")
   end if
end if

""" % (btable.NameFile, )
    return ret


#*********************************************************************************
def GetSingleObjectFramePage(atabs, afname, aeventsrc=None):
    ret = ''
    apanes = '100%'
    aencoding = 'utf-8'
    if aeventsrc:
        aencoding = aeventsrc.CRM.DefaultEncoding
    if len(atabs) > 1:
        apanes = apanes + ',0' * (len(atabs) - 1)
    ret = ret + """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><!-- #include file="../inc/_page_begin.asp" -->
<html>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=7">
<META content="text/html; charset=%s" http-equiv=Content-Type>
<title>ICOR SQL Interface</title>
</head>
<%%
CustomPage=0
""" % (aencoding, )
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeShowOne'):
        ret = ret + "\n' *** ASPSourceOnBeforeShowOne -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnBeforeShowOne
        ret = ret + "\n' *** ASPSourceOnBeforeShowOne -- END ***\n"
        ret = ret + """
%>
<!-- #include file="../inc/_page_end.asp" -->
<%
if Request.QueryString("chapterid")<>"" then
   achapterid=Request.QueryString("chapterid")
   achapterref="&chapterid=" & achapterid
elseif Request.Form("_CHAPTERID")<>"" then
   achapterid=Request.Form("_CHAPTERID")
   achapterref="&chapterid=" & achapterid
else
   achapterid=""
   achapterref=""
end if
"""
    ret = ret + """
if CustomPage=0 then
%%>
<frameset name="FRAMEOBJECTS" id="FRAMEOBJECTS" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="64,*">
  <frame name="OBJECTEDITMAIN" id="OBJECTEDITMAIN" scrolling="no" noresize src="%s?ioid=<%%=Request.QueryString("ioid")%%>&sheet=-1<%%=achapterref%%>" frameborder="0" marginheight="0" marginwidth="0">
  <frameset name="FRAMEPANES" id="FRAMEPANES" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="%s">
""" % (afname, apanes)
    for i in range(len(atabs)):
        tid, s, tav = atabs[i]
        if not i:
            #ret=ret+'   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize src="%s?ioid=<%%=Request.QueryString("ioid")%%>&sheet=%d" frameborder="0" marginheight="0" >\n'%(i,i,afname,tid)
            ret = ret + '   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize src="%s?ioid=<%%=Request.QueryString("ioid")%%>&aoidref=<%%=Request.QueryString("aoidref")%%>&wlocation=<%%=Request.QueryString("wlocation")%%>&areffield=<%%=Request.QueryString("areffield")%%>&sheet=%d<%%=achapterref%%>" frameborder="0" marginheight="0" >\n' % (i, i, afname, tid)
        else:
            ret = ret + '   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize frameborder="0" marginheight="0" >\n' % (i, i)
    ret = ret + """
</frameset></frameset>
<%
else
   Response.Write("</BODY>")
end if
%>
</html>
"""
    return ret


#*********************************************************************************
def GetSelectTextByTabID(atable, atext, atabid):
    ret = ''
    if atabid:
        asecurity = atable.TabsByIDSecurity.get(atabid, '')
        ret = """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 5</font></h1>")
   else
""" % (atabid, asecurity)
    ret = ret + atext
    if atabid:
        ret = ret + """
   end if
end if
"""
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
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='DOK_" & adoktypeid & "_so.asp?ioid=" & adokid & "'>Powrót do dokumentu</a><br>"
   else
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s.asp'>Powrót do listy</a><br>"
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
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, i, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'numeric':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'money':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'date':
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'datetime':
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),15\n' % (afield.Name, afield.Name, i, i)
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),1\n' % (afield.Name, afield.Name, i, i)
            elif afield.Type == 'bool':
                ret = ret + """
   if CBool(rs.Fields(%d).Value) then
      sd=" Checked"
   else
      sd=""
   end if
""" % (i, )
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\' " & sd & ">"\n' % (afield.Name, afield.Name)
            elif afield.Type == 'dict':
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
            elif afield.Type == 'external dict multiple':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelectionMultiple(afield)
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=6 %s>" & Server.HTMLEncode(rs.Fields(%d).Value) & "</textarea>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield), i)
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'" & rs.Fields(%d).Value & "\' %s>"\n' % (afield.Name, afield.Name, i, GetFieldValidationText(afield))
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
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'\' %s>"\n' % (afield.Name, afield.Name, ds, afield.Size, GetFieldValidationText(afield))
            elif afield.Type == 'numeric':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'money':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type == 'date':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'datetime':
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & year(now) & "/" & month(now) & "/" & day(now) & "\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),15\n' % (afield.Name, afield.Name, )
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),1\n' % (afield.Name, afield.Name, )
            elif afield.Type == 'bool':
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\'>"\n' % (afield.Name, afield.Name)
            elif afield.Type == 'dict':
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
            elif afield.Type == 'external dict multiple':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelectionMultiple(afield, aisnew=1)
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=6 %s></textarea>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, GetFieldValidationText(afield))
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
            elif afield.Type == 'numeric' or afield.Type == 'money':
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
            elif afield.Type == 'dict':
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict':
                #$$
                ret = ret + '         rs("%s") = Request.Form("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict multiple':
                #$$ na pewno BABOL
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
   Response.Write "<br><a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s.asp'>Powrót do listy</a><br>"
end if
Response.Write("<BR><TABLE>")
""" % (sf, astep.SQLTable.NameSQL, awizard.NameFile)
    i = 2
    for afield in astep.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            ret = ret + '   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class=objectseditdatafieldvalue>"\n' % (afield.PrettyName)
            if afield.Type == 'bool':
                ret = ret + """
if CBool(rs.Fields("%s")) then
   Response.Write "Tak"
else
   Response.Write "Nie"
end if
""" % (afield.Name, )
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield)
            elif afield.Type == 'external dict multiple':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDictMultiple(afield)
            elif afield.Type == 'money':
                ret = ret + '   Response.Write Currency2HTML(rs.Fields("%s").Value,0)\n' % (afield.Name, )
            else:
                ret = ret + '   Response.Write rs.Fields("%s").Value\n' % (afield.Name, )
            ret = ret + 'Response.Write ("</td>")\n'
            i = i + 1
    ret = ret + """
if adoktypeid<>"-1" then
   Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>Dotyczy:</td><td class=objectseditdatafieldvalue>"
   Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='DOK_" & adoktypeid & "_so.asp?ioid=" & rs.Fields("_Dotyczy") & "'>"
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
         Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='" & spref & "'>"
         Response.Write "Poprzedni</a>"
         if snref<>"" then
            Response.Write ","
         end if
      end if
      if snref<>"" then
         Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='" & snref & "'>"
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
Response.Write "<hr><a class='fg-button-single ui-state-default ui-corner-all uihover' href='wizard_%d_%d.asp?doktypeid=" & adoktypeid & "&ioid=" & Request.QueryString("ioid") & "&dokid=" & rs.Fields("_Dotyczy") & "'>Edycja danych</a><br>"
""" % (awizard.OID, astep.OID, )

    ret = ret + """
allowdelete=1
if allowdelete>0 then
   dnum=CStr(CLng(1e8*rnd(0)+Timer))
   Dession("doknumber")=dnum
   dhref="WSTP_%d_so.asp?koid=" & rs("_KreatorOID") & "&dnum=" & dnum & "&dokid=" & adokid & "&doktypeid=" & adoktypeid
   Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' onclick=""javascript:if (confirm('Czy na pewno chcesz wybrać tę pozycję?')) {this.href='" & dhref & "';} else {this.href='javascript:var umm=1;';} ;"" HREF=""javascript:var umm=1;"" >Usuń ten wpis</a><br>"
end if
""" % (astep.OID, )

    return ret


#*********************************************************************************
def GetWizardMainPage(awizard, akreatortable):
    ret = """
Response.Write "<br>"
if CheckUserAccess("%s")=1 then
   abr=1
   Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s.asp'>Nowy wpis</a><br>"
   Response.Write "<hr>"
end if
""" % (awizard.AccessLevelView, awizard.NewPage, )
    if awizard.steps:
        ret = ret + """
if CheckUserAccess("%s")=1 then 'Wizard - AccessLevelView
   Set rs1=Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select _OID,DokumentID,DokumentOID,KreatorEtapID,KreatorEtapOID,KreatorID,KreatorInfo,KreatorOID,StanEtapu,_datetime,_UserName from %s WHERE DokumentOID='-1' AND KreatorID=%d AND KreatorEtapID=%d ORDER BY _datetime DESC"
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
def GetDocumentSearchContainer(acontainer):
    ret = """
Response.Write "<h3>Wybierz sprawę:</h3>"
"""
    for adocument in acontainer.Items:
        ret = ret + """
Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='dok_%d_sd.asp'>%s</a><br>"
""" % (adocument.OID, adocument.Nazwa)
    return ret
