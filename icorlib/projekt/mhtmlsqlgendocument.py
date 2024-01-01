# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil
import icorlib.projekt.mhtmlsqlgenlib as MHTMLSQLGenLib
from icorlib.wwwhtml.main import *
import icorlib.wwwhtml.fckmain as FCKMain
from icorlib.wwwhtml.worksheetmain import *
import string


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
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
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
        if (afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
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
        if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
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
        if (afield.IsAliased or afield.IsSearch) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
            if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
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
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'float']:
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
""" % (aselect.FieldsDict[afield.DBName], aselect.FieldsDict[afield.DBName], aselect.FieldsDict[afield.DBName], aselect.FieldsDict[afield.DBName], aselect.FieldsDict[afield.DBName],
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
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
            elif afield.Type in ['numeric', 'float']:
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=18 MAXLENGTH=22 value=\'\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
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
            elif afield.Type == 'text':
                ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=32 rows=6 %s></textarea>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
            elif afield.Type == 'integer':
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=14 MAXLENGTH=22 value=\'\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
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
    ret = ret + MHTMLSQLGenLib.WriteTableFieldsDescription(btable)
    ret = ret + """
else
      rs.ActiveConnection = cn
      rs.CursorType = adOpenKeyset
      rs.LockType = adLockOptimistic
      rs.Source = "select %s,_Dotyczy,_UID,_UserName,_DateTime from %s WHERE _OID='-1'"
      rs.Open
""" % (sf, btable.NameSQL)
    ret = ret + """
rs.AddNew
"""
    i = 1
    for afield in btable.FieldsByTabID:
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
def DocumentSelectSingleASP(adocument, aetapytable):
    fls = ['%s._OID' % adocument.SQLTable.NameSQL, '%s._Dotyczy' % adocument.SQLTable.NameSQL]
    for afield in adocument.SQLTable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            fls.append(afield.DBName)
#   for afield in adocument.SourceTable.SQLTable.FieldsByTabID:
#      if afield.Name[:1]!='_' and afield.IsAliased and afield.IsInteractive:
#         fls.append(afield.DBName)
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
at1rsvalue=rs.Fields(%d).Value
if not isnull(at1rsvalue) then
   if CBool(at1rsvalue) then
      Response.Write "Tak"
   else
      Response.Write "Nie"
   end if
end if
""" % (i, )
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield)
            elif afield.Type == 'money':
                ret = ret + '   Response.Write Currency2HTML(rs.Fields(%d).Value,0)\n' % (i, )
            else:
                ret = ret + '   Response.Write rs.Fields(%d).Value\n' % (i, )
            ret = ret + 'Response.Write ("</td>")\n'
            i = i + 1
    ret = ret + """
Response.Write "<TR VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src='/icormanager/images/smttr_lb.png'>Dotyczy:</td><td class=objectseditdatafieldvalue>"
Response.Write "<a class=reflistoutnavy href='%s_so.asp?ioid=" & rs.Fields(1).Value & "'>"
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
Response.Write "<hr><a class=reflistoutnavy href='%s_au.asp?ioid=" & Request.QueryString("ioid") & "'>Edycja danych</a><br>"
""" % (adocument.SQLTable.NameFile, )
    ret2 = ret2 + """
if allowdelete>0 then
   dnum=CStr(CLng(1e8*rnd(0)+Timer))
   Dession("doknumber")=dnum
   dhref="DOK_%d_so.asp?ioid=" & Request.QueryString("ioid") & "&dnum=" & dnum
   Response.Write "<a class=reflistoutnavy onclick=""javascript:if (confirm('Czy na pewno chcesz wybrać tę pozycję?')) {this.href='" & dhref & "';} else {this.href='javascript:var umm=1;';} ;"" HREF=""javascript:var umm=1;"" >Usuń ten dokument</a><br>"
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
   Response.Write "<a class=reflistoutnavy href='%s.asp?doktypeid=%d&dokid=" & Request.QueryString("ioid") & "'>%s</a><br>"
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
  Response.Write "<a class=reflistoutnavy href='%s?doktypeid=%d&dokid=" & Request.QueryString("ioid") & "'>%s</a><br>"
end if
""" % (apage.AccessLevelView, apage.PageFile, adocument.OID, apage.Title, )
    return [ret, ret1, ret2]


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
Response.Write "<a class=reflistoutnavy href='newdoc_%d.asp?doid=%d'>%s - %s</a><!-- &nbsp;"
Response.Write "-&nbsp;<a  class=reflistoutnavy href='%s_sa.asp'>wszystkie dokumenty</a> --><br>"
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

   Response.Write "<td class='objectsviewdatanowrap'><a id='oTipped" &CStr(atipcnt) & "' class=reflistoutnavy href='DOK_" & rs("DokumentID") & "_so.asp?ioid=" & rs("DokumentOID") & "'>" & rs("DokumentSymbol") & "</a><tool:tip element='oTipped" & CStr(atipcnt) & "' avoidmouse='false'>" & rs("DokumentSymbol") & " - " & rs("DokumentTitle") & "</tool:tip>&nbsp;</td>"
   atipcnt=atipcnt+1
   Response.Write "<td class='objectsviewdatanowrap'><a id='oTipped" & CStr(atipcnt) & "' class=reflistoutnavy href='BZR_" & rs("BZRID") & "_so.asp?ioid=" & rs("BZROID") & "'>" & GetTextAsCaption(rs("BZRInfo"),20) & "</a><tool:tip element='oTipped" & CStr(atipcnt) & "' avoidmouse='false'>" & rs("BZRInfo") & "</tool:tip>&nbsp;</td>"
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
