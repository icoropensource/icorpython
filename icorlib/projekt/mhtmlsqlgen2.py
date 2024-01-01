# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.projekt.mhtmlsqlgenlib as MHTMLSQLGenLib
import icorlib.projekt.msqlquery as MSQLQuery
import string


#*********************************************************************************
def SQLTableGetSearchDataASPAdvancedPageTitle1():
    ret = """isdialog="0"
if Request.QueryString("isdialog")="1" then
   isdialog="1"
end if
if isdialog<>"1" then                 
"""
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASPAdvancedPageTitle2():
    ret = """
else
%>
<script language="javascript">
/*
window.parent.document.getElementById('myDialogFrameName1').innerHTML='<%=Request.QueryString("dialogframe")%>';
window.parent.document.getElementById("myevenntcallerdialogshow1").fireEvent("onclick");
*/                                                                    
   jQuery('#myDialogFrameName1', window.parent.document).html('<%=Request.QueryString("dialogframe")%>');
   jQuery('#myevenntcallerdialogshow1', window.parent.document).trigger('click');
</script>
<%
end if
"""
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASPAdvanced(afilename, afields, asp, asortedfields='', aownerfilename='', amainoidfieldname='_OID', aurlparams='', amarkergroups=None, aquerysql=None, asearchactions=None, aprojectoid=-1, achaptertable='', aaspsourceonbeforegetdata='', aaspsourceonaftersearch='', aaspsourceonfilter='', aaspsourceonfieldvalue=''):
    #   print '@@@@@',afilename
    if asearchactions is None:
        asearchactions = []
    bfields = []
    i = 0
    achapteridfield = None
    for afield in afields:
        bfields.append([afield.SearchTabID, i, afield])
        #      print '    @@@###',afield.NameSQL,afield.Name
        if afield.Name == '_ChapterID':
            achapteridfield = afield
#         print '    @@@###  --- ',achapteridfield.NameSQL,achapteridfield.Name
        i = i + 1
    if achaptertable:
        achaptertable = achaptertable + '.'
    bfields.sort()
    afields = []
    for aid, acnt, afield in bfields:
        afields.append(afield)
    if aurlparams:
        aurlparams = '&' + aurlparams
    if not aownerfilename:
        aownerfilename = afilename
    ret = '''
%%>
<script language="javascript">
var fpselectedelement=0;
var fpselectedelementshow=0;
var fpPopup=null;

if (isIE()) {
   fpPopup = window.createPopup();
}
function showPopupFP(asrc,aelement,afieldelement){
   if (isIE()) {
      var xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
      var sa=afieldelement.value.split(".");
      var sf2=sa[sa.length-1];
      var sf1=sa.slice(0,-1).join('.');
      var aurl="%s_svf.asp?table="+sf1+"&field="+sf2+"&where="+escape(asrc.value);
      fpselectedelement=asrc;
      fpselectedelementshow=aelement;
      xmlHttp.open('POST', aurl, false);
      xmlHttp.send("");
      var src=xmlHttp.responseText;
      fpPopup.document.body.innerHTML=src;
      var stext=fpPopup.document.getElementById("myinfo1").innerText;
      if (stext=="OK") {
         fpPopup.show(0, 0, 300, 200, fpselectedelementshow);
      } else {
         alert(stext);
      }
      xmlHttp=null;
   }
} 

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
function doSubmitCustom(avalue,atarget,isdialog) {
   jQuery("#searchcustom").val(avalue);
   jQuery("#form1").attr('target',atarget);
   if (isdialog=="1") {
      var aaction=jQuery("#form1").attr('action');
      aaction=aaction.replace('isdialog=0','isdialog=1');
      jQuery("#form1").attr('action',aaction);
   }
   document.getElementById("form1").submit();
}
function GetFieldType(afieldname){
''' % (afilename, )
    sfl, sft, sfc = [], [], []
    for afield in afields:
        if (afield.IsSearch or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', 'external dict multiple']:
            sfl.append('"' + afield.NameSQL + '"')
            sft.append(str(afield.TypeID))
            sfc.append(str(ICORUtil.str2bool(str(afield.IsContainer))))
    ret = ret + '''
   var afields = new Array(%s);
   var atypes  = new Array(%s);
   var acontainers = new Array(%s);
''' % (string.join(sfl, ','), string.join(sft, ','), string.join(sfc, ','))
    ret = ret + '''
   nfields=afields.length;
   for(i=0; i<nfields; i++){
      if (afields[i]==afieldname) {
         return acontainers[i] + atypes[i];
      }
   }
   return -1;
}
function showHidePickers(aelement,adatebutton,apreviewbutton){
   if (aelement!=''){
      atype=GetFieldType(aelement.value);
      if (atype==96) {
         jQuery("#"+adatebutton).datepicker({buttonImageOnly: true,showOn:'button'});
      } else {
         jQuery("#"+adatebutton).datepicker('destroy');
      }
      if ((atype==32) || (atype==64) || (atype==96) || (atype==112) || (atype==144))
         apreviewbutton.style.display=''
      else
         apreviewbutton.style.display='none';
   }
}
'''
    ret = ret + '''
function doPivotSubmit() {
   jQuery("#search").val("3");
   document.getElementById("form1").submit();
}
</script>
<%
'''
    ret = ret + '''
amode=""
atitlemodifer=""
if Request.Form("search")="3" then
   atitlemodifer=" - tabela przestawna"
end if
if Request.Form("iPageNo")<>"" then
   atitlemodifer=" - strona nr <b>" & cstr(Request.Form("iPageNo")) & "</b>"
   if Request.Form("search")<>"3" then
      amode="searchform"
   end if
end if
aformdata=GetFormValuesAsString()
if isdialog<>"1" then
   call RegisterVisitHistory("Wyszukiwarka - <b>" & aPageTitle & atitlemodifer & "</b>","",aformdata,amode)
end if
'''
    ret = ret + '''
if Request.Form("_QUERYSTRING")<>"" then
   aquerystring=Request.Form("_QUERYSTRING")
else
   aquerystring=Request.QueryString
end if
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

function getDateAsSQLDate(sdatetime)
   dim i,sarr,sdarr,sdate,stime
   sdatetime=Replace(Replace(Replace(trim(sdatetime),".","/"),"-","/"),"\\","/")
   if Not IsDate(sdatetime) or len(sdatetime)<8 then
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
'      Response.Write "<p>Wpisz szukany ciąg znaków do odpowiednich pól:</p>"
   End if
'''
    ret = ret + '''
   Response.Write "<form validate='onchange' invalidColor='gold' mark year4 name=form1 id=form1 METHOD='post' ACTION='%s_sv.asp?isdialog=" & isdialog & "&dialogframe=" & Request.QueryString("dialogframe") & "&dialoginput=" & Request.QueryString("dialoginput") & "'>"
''' % (afilename)
    ret = ret + '''
   Response.Write "<input type=hidden id='search' name='search' size=1 value='1'>"
   Response.Write "<input type=hidden id='searchcustom' name='searchcustom' size=50 value=''>"
   Response.Write "<input type=hidden id='iPageNo' name='iPageNo' value='1'>"
   Response.Write "<input type=hidden id='_CHAPTERID' name='_CHAPTERID' value='" & achapterid & "' >"
   Response.Write "<input type=hidden id='_QUERYSTRING' name='_QUERYSTRING' value='" & aquerystring & "' >"
   if ahidden=0 then
      'Response.Write "<TABLE cellpadding=4 cellspacing=0 width='100%' border=1>"
      'Response.Write "<TR VALIGN=top class=objectseditrow>"
      'Response.Write "<td class=objectseditdatafieldvalueeven><br style='line-height:40%;'>"
      Response.Write "<div class=""ui-tabs ui-widget ui-widget-content ui-corner-all"">"
      for i=1 to 5
         ss=CStr(i)
         Response.Write "<div id='fOperators" & ss & "'><span>&nbsp;&nbsp;</span><input type=radio class=checkradio id='fLinksand" & ss & "' name='fLinks" & ss & "' value='AND' "
         if ssearch<>"2" or Request.Form("fLinks" & ss)="AND" then
            Response.Write schecked
         end if   
         Response.Write "><span>&nbsp;i"
         Response.Write "&nbsp;&nbsp;</span><input type=radio class=checkradio id='fLinksor" & ss & "' name='fLinks" & ss & "' value='OR' "
         if Request.Form("fLinks" & ss)="OR" then
            Response.Write schecked
         end if           
         Response.Write "><span>&nbsp;lub"
         Response.Write "&nbsp;&nbsp;</span><input type=radio class=checkradio id='fLinksandnot" & ss & "' name='fLinks" & ss & "' value='AND NOT' "
         if Request.Form("fLinks" & ss)="AND NOT" then
            Response.Write schecked
         end if                    
         Response.Write "><span>&nbsp;i&nbsp;nie</span></div>"
         Response.Write "<div id='aRowDiv" & ss & "' name='aRowDiv" & ss & "'>"
         Response.Write "<span>&nbsp;" & ss & ".&nbsp;</span>"
         Response.Write "<select id='fFieldName" & ss & "' name='fFieldName" & ss & "' onchange='javascript:showHidePickers(this,""fValue" & ss & """,fieldpreviewdiv" & ss & ");'>"
         Response.Write "<option value=''></option>"
'''
    i = 0
    for afield in afields:
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
            if not i:
                ret = ret + '''
         Response.Write "<option value='%s' "
         if i=1 and ssearch<>"2" or Request.Form("fFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.NameSQL, afield.NameSQL, afield.PrettyNameDisplayed, )
            else:
                ret = ret + '''
         Response.Write "<option value='%s' "
         If Request.Form("fFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.NameSQL, afield.NameSQL, afield.PrettyNameDisplayed, )
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
         Response.Write "<input type=text id='fValue" & ss & "' name='fValue" & ss & "' size=20 value='" & Request.Form("fValue" & ss) & "'>"
         Response.Write "&nbsp;<IMG alt='podgląd wartości' id='fieldpreviewdiv" & ss & "' src='/icormanager/images/icon_preview.png' style='display:none; cursor:pointer;' onclick='javascript:showPopupFP(fValue" & ss & ",fieldpreviewdiv" & ss & ",fFieldName" & ss & ");'>"
%>
<script language=javascript>
jQuery(function(){
   showHidePickers(document.getElementById("fFieldName<%=ss%>"),"fValue<%=ss%>",document.getElementById("fieldpreviewdiv<%=ss%>"));
});
</script>
<%
         Response.Write "<br></div>"
      next

      Response.Write "<br style='line-height:60%;'>"
'''
    w1 = 1
    w2 = 1
    sb1 = 'Szukaj'
    sb2 = 'Pokaż tabelę przestawną'
    if aquerysql is not None:
        sb1 = aquerysql.ButtonSearchCaption
        sb2 = aquerysql.ButtonPivotCaption
        if aquerysql.ButtonSearchDisable:
            w1 = 0
        if aquerysql.ButtonPivotDisable:
            w2 = 0
    if w1:
        ret = ret + '''
      Response.Write "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input class='fg-button-single ui-state-default ui-corner-all uihover' TYPE='submit' VALUE='%s'>"
''' % (sb1, )
    if aquerysql is not None and aquerysql.IsPivot:
        if w2:
            ret = ret + '''
      if isdialog<>"1" then
         Response.Write "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input align=right type=button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doPivotSubmit();' VALUE='%s'>"
      end if
''' % (sb2, )

    ret = ret + '''
%>
<SCRIPT LANGUAGE=javascript>
function toggleCheckBoxes(aelement,afieldname,amax) {
   if(aelement.src.indexOf("icon_toggle_off")<0){
      aelement.src="/icormanager/images/icon_toggle_off.png";
   }else{
      aelement.src="/icormanager/images/icon_toggle_on.png";
   };
   for(i=0;i<amax;i++){
      document.getElementById(afieldname+i.toString()).checked=!document.getElementById(afieldname+i.toString()).checked;
   };
}
</SCRIPT>
<%
'''
    for afield in afields:
        if afield.IsSearchByValue:
            ret = ret + '''
      Set rsc1 = Server.CreateObject("ADODB.Recordset")
      rsc1.CursorType = adOpenKeyset
      rsc1.LockType = adLockOptimistic
      rsc1.ActiveConnection = cn
      rsc1.CursorType = adOpenKeyset
      rsc1.LockType = adLockOptimistic
      rsc1.Source="SELECT TOP 500 %s FROM %s GROUP BY %s ORDER BY %s"
      rsc1.Open
      if Not rsc1.EOF then
         Response.Write "<br><br style='line-height:60%%;'>"
         Response.Write "<TABLE cellpadding=1 cellspacing=0 border=0 width='412px' style='margin-left:5px' >"
         Response.Write "<TR VALIGN=top class=objectseditrow><td align=left>"
         Response.Write "%s:"
         Response.Write "</td><td align=right>"
         Response.Write "<img valign='center' alt='zaznacz/odznacz pozycje' style='cursor:pointer;' src='/icormanager/images/icon_toggle_on.png' onclick='javascript:toggleCheckBoxes(this,""checkb_%s_""," & CStr(rsc1.RecordCount)& ")'>"
         Response.Write "</td></tr>"
         Response.Write "<TR VALIGN=top class=objectseditrow><td colspan=2>"
         Response.Write "<div style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:200px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>"
         stv_i=0
         Do While Not rsc1.EOF
            sv=CStr(rsc1("%s"))
            schecked=""
            for each acrule in request.form("checkb_%s")
              if acrule=sv then
                 schecked="checked"
                 exit for
              end if
            next
            svv=sv
''' % (afield.Name, afield.Table.NameSQL, afield.Name, afield.Name, afield.PrettyNameDisplayed, afield.Name, afield.Name, afield.Name,
            )
            for sdk, sdv in afield.DictValues:
                ret = ret + '''
            if sv="%s" then
               svv="%s"
            end if
''' % (sdk, sdv)
            ret = ret + '''
            Response.Write "&nbsp;<input type=checkbox class=checkradio id=checkb_%s_" & CStr(stv_i) & " name=checkb_%s value='" & server.htmlencode(sv) & "' " & schecked & ">&nbsp;&nbsp;" & server.htmlencode(svv) & "<br>"
            rsc1.MoveNext
            stv_i=stv_i+1
         Loop
         Response.Write "</DIV>"
         Response.Write "</td></tr></table>"
      end if
      if rsc1.State<>adStateClosed then
         rsc1.Close
      end if
      set rsc1=Nothing
''' % (afield.Name, afield.Name,
            )

    ret = ret + '''
      'Response.Write "<br><br style='line-height:40%;'></td></tr>"
      'Response.Write "<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldvalueodd>"
      Response.Write "</div>"
      Response.Write "<div class=""ui-tabs ui-widget ui-widget-content ui-corner-all"">"
      Response.Write "Porządek sortowania:<br><br style='line-height:40%;'>"
   for i=1 to 3
         ss=CStr(i)
         Response.Write "&nbsp;" & ss & ".&nbsp;"
         Response.Write "<select id='fOrderFieldName" & ss & "' name='fOrderFieldName" & ss & "'>"
         Response.Write "<option value=''></option>"
'''
    for afield in afields:
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
            if not i:
                ret = ret + '''
         Response.Write "<option value='%s' "
         if i=1 and ssearch<>"2" or Request.Form("fOrderFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.NameSQL, afield.NameSQL, afield.PrettyNameDisplayed, )
            else:
                ret = ret + '''
         Response.Write "<option value='%s' "
         If Request.Form("fOrderFieldName" & ss)="%s" then
            Response.Write sselected
         end if
         Response.Write ">%s</option>"
''' % (afield.NameSQL, afield.NameSQL, afield.PrettyNameDisplayed, )
            i = i + 1

    ret = ret + '''
         Response.Write "</select>&nbsp;&nbsp;"

         Response.Write "<select id='fOrderDirection" & ss & "' name='fOrderDirection" & ss & "'>"
         Response.Write "<option value='ASC' "
         if Request.Form("fOrderDirection" & ss)="ASC" then
            Response.Write sselected
         end if
         Response.Write ">rosnąco</option>"
         Response.Write "<option value='DESC' "
         if Request.Form("fOrderDirection" & ss)="DESC" then
            Response.Write sselected
         end if   
         Response.Write ">malejąco</option>"
         Response.Write "</select><br><br style='line-height:60%;'>"
      next
'''
    ret = ret + '''
      'Response.Write "</td></tr>"
      'Response.Write "<TR VALIGN=top class=objectseditrow>"
      'Response.Write "<td class=objectseditdatafieldvalueeven><br style='line-height:40%;'>"
      Response.Write "</div>"
      Response.Write "<div class=""ui-tabs ui-widget ui-widget-content ui-corner-all"">"
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
      if isdialog<>"1" then
         Response.Write "&nbsp;<input type=checkbox class=checkradio id='iForPrinting' name='iForPrinting' value='1'> w formacie do wydruku"
         'Response.Write "&nbsp;<input type=checkbox class=checkradio id='iForExcel' name='iForExcel' value='1'> w postaci arkusza"
      end if
      'Response.Write "<br><br style='line-height:40%;'></td></tr>"
      'Response.Write "</TABLE>"
      Response.Write "</div>"
      Application.Lock
      atmpfilecnt=Dession("TmpServerFileCounter")
      Dession("TmpServerFileCounter")=1+Dession("TmpServerFileCounter")
'      if Dession("TmpServerFileCounter")>10 then
'         Dession("TmpServerFileCounter")=1
'      end if
      Application.UnLock
      Response.Write "<input type=hidden id='datasource' name='datasource' value='/icormanager/output/xmlsrcdata_" & CStr(Dession.SessionID) & "_" & atmpfilecnt & ".bin' >"
      Response.Write "<input type=hidden id='datasourcefilename' name='datasourcefilename' value='xmlsrcdata_" & CStr(Dession.SessionID) & "_" & atmpfilecnt & ".bin' >"
   else
      Response.Write "<input type=hidden id='iForPrinting' name='iForPrinting' value='" & Request.Form("iForPrinting") & "' >"
      Response.Write "<input type=hidden id='iForExcel' name='iForExcel' value='" & Request.Form("iForExcel") & "' >"
      Response.Write "<input type=hidden id='iRecsPerPage' name='iRecsPerPage' value='" & Request.Form("iRecsPerPage") & "' >"
      for i=1 to 5
         Response.Write "<input type=hidden id='fLinks" & CStr(i) & "' name='fLinks" & CStr(i) & "' value='" & Request.Form("fLinks" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fFieldName" & CStr(i) & "' name='fFieldName" & CStr(i) & "' value='" & Request.Form("fFieldName" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fOperator" & CStr(i) & "' name='fOperator" & CStr(i) & "' value='" & Request.Form("fOperator" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fValue" & CStr(i) & "' name='fValue" & CStr(i) & "' value='" & Request.Form("fValue" & CStr(i)) & "' >"
      next
      for i=1 to 3
         Response.Write "<input type=hidden id='fOrderFieldName" & CStr(i) & "' name='fOrderFieldName" & CStr(i) & "' value='" & Request.Form("fOrderFieldName" & CStr(i)) & "' >"
         Response.Write "<input type=hidden id='fOrderDirection" & CStr(i) & "' name='fOrderDirection" & CStr(i) & "' value='" & Request.Form("fOrderDirection" & CStr(i)) & "' >"
      next
      Response.Write "<input type=hidden id='datasource' name='datasource' value='" & Request.Form("datasource") & "' >"
      Response.Write "<input type=hidden id='datasourcefilename' name='datasourcefilename' value='" & Request.Form("datasourcefilename") & "' >"

'''
    for afield in afields:
        if afield.IsSearchByValue:
            ret = ret + '''
      for each acrule in request.form("checkb_%s")
         Response.Write "<input type=hidden name='checkb_%s' id='checkb_%s' value='" & acrule & "' >"
      next
''' % (afield.Name, afield.Name, afield.Name, )
    ret = ret + '''
   end if
'''
    if aquerysql is not None and aquerysql.IsPivot:
        d = {}
        d['pivotcaption'] = aquerysql.PivotCaption
        d['rowaxis'] = aquerysql.PivotRowFields[0].PrettyName
        for i in range(1, 6):
            if i < len(aquerysql.PivotRowFields):
                d['rowaxis%d' % i] = aquerysql.PivotRowFields[i].PrettyName
            else:
                d['rowaxis%d' % i] = ''
        d['columnaxis'] = aquerysql.PivotColumnFields[0].PrettyName
        for i in range(1, 6):
            if i < len(aquerysql.PivotColumnFields):
                d['columnaxis%d' % i] = aquerysql.PivotColumnFields[i].PrettyName
            else:
                d['columnaxis%d' % i] = ''
        d['dataaxis'] = aquerysql.PivotDataFields[0].PrettyName
        d['dataaxistotalfunction'] = aquerysql.PivotDataFields[0].PivotDataAxisTotalFunction
        d['dataaxisnumberformat'] = aquerysql.PivotDataFields[0].PivotDataAxisNumberFormat
        for i in range(1, 12):
            if i < len(aquerysql.PivotDataFields):
                d['dataaxis%d' % i] = aquerysql.PivotDataFields[i].PrettyName
                d['dataaxistotalfunction%d' % i] = aquerysql.PivotDataFields[i].PivotDataAxisTotalFunction
                d['dataaxisnumberformat%d' % i] = aquerysql.PivotDataFields[i].PivotDataAxisNumberFormat
            else:
                d['dataaxis%d' % i] = ''
                d['dataaxistotalfunction%d' % i] = ''
                d['dataaxisnumberformat%d' % i] = ''
        d['showchart'] = aquerysql.ShowChart
        d['chartcaption'] = aquerysql.ChartCaption
        d['chartid'] = aquerysql.ChartID
        d['subtotals'] = aquerysql.PivotSubtotals
        d['pivotshowdetails'] = aquerysql.PivotShowDetails

        acfield, arfield = None, None
        if aquerysql.PivotColumnFields[0].PivotExcludeColumnMetric:
            acfield = aquerysql.PivotColumnFields[0]
            d['columnaxis'] = acfield.PrettyName + ' ' + acfield.PivotExcludeColumnMetric
            d['columnaxis'] = d['columnaxis'][:22]
        elif len(aquerysql.PivotColumnFields) > 1 and aquerysql.PivotColumnFields[1].PivotExcludeColumnMetric:
            acfield = aquerysql.PivotColumnFields[1]
            d['columnaxis1'] = acfield.PrettyName + ' ' + acfield.PivotExcludeColumnMetric
            d['columnaxis1'] = d['columnaxis1'][:22]
        if aquerysql.PivotRowFields[0].PivotExcludeRowMetric:
            arfield = aquerysql.PivotRowFields[0]
            d['rowaxis'] = arfield.PrettyName + ' ' + arfield.PivotExcludeRowMetric
            d['rowaxis'] = d['rowaxis'][:22]
        elif len(aquerysql.PivotRowFields) > 1 and aquerysql.PivotRowFields[1].PivotExcludeRowMetric:
            arfield = aquerysql.PivotRowFields[1]
            d['rowaxis1'] = arfield.PrettyName + ' ' + arfield.PivotExcludeRowMetric
            d['rowaxis1'] = d['rowaxis1'][:22]
        if acfield is not None:
            d['excludecolumnmetric'] = acfield.PrettyName + ' ' + acfield.PivotExcludeColumnMetric
            d['excludecolumnmetric'] = d['excludecolumnmetric'][:22]
            d['excludecolumnaxisfield1'] = str(acfield.IsPivotExcludeColumnAxisField1)
            d['excludecolumnaxisfield2'] = str(acfield.IsPivotExcludeColumnAxisField2)
            d['excludecolumnaxisfield3'] = str(acfield.IsPivotExcludeColumnAxisField3)
            d['excludecolumnaxisfield4'] = str(acfield.IsPivotExcludeColumnAxisField4)
        if arfield is not None:
            d['excluderowmetric'] = arfield.PrettyName + ' ' + arfield.PivotExcludeRowMetric
            d['excluderowmetric'] = d['excluderowmetric'][:22]
            d['excluderowaxisfield1'] = str(arfield.IsPivotExcludeRowAxisField1)
            d['excluderowaxisfield2'] = str(arfield.IsPivotExcludeRowAxisField2)
            d['excluderowaxisfield3'] = str(arfield.IsPivotExcludeRowAxisField3)
            d['excluderowaxisfield4'] = str(arfield.IsPivotExcludeRowAxisField4)
        s = ''
        if aquerysql.FilterAxisFields:
            s = aquerysql.FilterAxisFields[0].PrettyName
        d['filteraxisfield'] = s
        ret = ret + '''
   Response.Write "<input type=hidden id='pivotcaption' name='pivotcaption' value='%(pivotcaption)s' >"
   Response.Write "<input type=hidden id='rowaxis' name='rowaxis' value='%(rowaxis)s' >"
   Response.Write "<input type=hidden id='rowaxis1' name='rowaxis1' value='%(rowaxis1)s' >"
   Response.Write "<input type=hidden id='rowaxis2' name='rowaxis2' value='%(rowaxis2)s' >"
   Response.Write "<input type=hidden id='rowaxis3' name='rowaxis3' value='%(rowaxis3)s' >"
   Response.Write "<input type=hidden id='rowaxis4' name='rowaxis4' value='%(rowaxis4)s' >"
   Response.Write "<input type=hidden id='rowaxis5' name='rowaxis5' value='%(rowaxis5)s' >"
   Response.Write "<input type=hidden id='columnaxis' name='columnaxis' value='%(columnaxis)s' >"
   Response.Write "<input type=hidden id='columnaxis1' name='columnaxis1' value='%(columnaxis1)s' >"
   Response.Write "<input type=hidden id='columnaxis2' name='columnaxis2' value='%(columnaxis2)s' >"
   Response.Write "<input type=hidden id='columnaxis3' name='columnaxis3' value='%(columnaxis3)s' >"
   Response.Write "<input type=hidden id='columnaxis4' name='columnaxis4' value='%(columnaxis4)s' >"
   Response.Write "<input type=hidden id='columnaxis5' name='columnaxis5' value='%(columnaxis5)s' >"

   Response.Write "<input type=hidden id='dataaxis' name='dataaxis' value='%(dataaxis)s Razem' >"
   Response.Write "<input type=hidden id='dataaxistotalfunction' name='dataaxistotalfunction' value='%(dataaxistotalfunction)s' >"
   Response.Write "<input type=hidden id='dataaxisfieldset' name='dataaxisfieldset' value='%(dataaxis)s' >"
   Response.Write "<input type=hidden id='dataaxisnumberformat' name='dataaxisnumberformat' value='%(dataaxisnumberformat)s' >"
''' % d
        for i in range(1, 12):
            d['i'] = i
            if d['dataaxis%d' % i]:
                d['idataaxistotal'] = d['dataaxis%d' % i] + ' Razem'
                d['idataaxis'] = d['dataaxis%d' % i]
            else:
                d['idataaxistotal'] = ''
                d['idataaxis'] = ''
            d['idataaxistotalfunction'] = d['dataaxistotalfunction%d' % i]
            d['idataaxisnumberformat'] = d['dataaxisnumberformat%d' % i]
            ret = ret + '''
   Response.Write "<input type=hidden id='dataaxis%(i)d' name='dataaxis%(i)d' value='%(idataaxistotal)s' >"
   Response.Write "<input type=hidden id='dataaxistotalfunction%(i)d' name='dataaxistotalfunction%(i)d' value='%(idataaxistotalfunction)s' >"
   Response.Write "<input type=hidden id='dataaxisfieldset%(i)d' name='dataaxisfieldset%(i)d' value='%(idataaxis)s' >"
   Response.Write "<input type=hidden id='dataaxisnumberformat%(i)d' name='dataaxisnumberformat%(i)d' value='%(idataaxisnumberformat)s' >"
''' % d
        ret = ret + '''
   Response.Write "<input type=hidden id='SubTotals' name='SubTotals' value='%(subtotals)s' >"
   Response.Write "<input type=hidden id='FilterAxisField' name='FilterAxisField' value='%(filteraxisfield)s' >"

   Response.Write "<input type=hidden id='showchart' name='showchart' value='%(showchart)s' >"
   Response.Write "<input type=hidden id='pivotshowdetails' name='pivotshowdetails' value='%(pivotshowdetails)s' >"
   Response.Write "<input type=hidden id='charttitle' name='charttitle' value='%(chartcaption)s' >"
   Response.Write "<input type=hidden id='chartid' name='chartid' value='%(chartid)s' >"
''' % d
        if acfield is not None:
            ret = ret + '''
   Response.Write "<input type=hidden id='ExcludeColumnMetric' name='ExcludeColumnMetric' value='%(excludecolumnmetric)s' >"
   Response.Write "<input type=hidden id='ExcludeColumnAxisField1' name='ExcludeColumnAxisField1' value='%(excludecolumnaxisfield1)s' >"
   Response.Write "<input type=hidden id='ExcludeColumnAxisField2' name='ExcludeColumnAxisField2' value='%(excludecolumnaxisfield2)s' >"
   Response.Write "<input type=hidden id='ExcludeColumnAxisField3' name='ExcludeColumnAxisField3' value='%(excludecolumnaxisfield3)s' >"
   Response.Write "<input type=hidden id='ExcludeColumnAxisField4' name='ExcludeColumnAxisField4' value='%(excludecolumnaxisfield4)s' >"
''' % d
        if arfield is not None:
            ret = ret + '''
   Response.Write "<input type=hidden id='ExcludeRowMetric' name='ExcludeRowMetric' value='%(excluderowmetric)s' >"
   Response.Write "<input type=hidden id='ExcludeRowAxisField1' name='ExcludeRowAxisField1' value='%(excluderowaxisfield1)s' >"
   Response.Write "<input type=hidden id='ExcludeRowAxisField2' name='ExcludeRowAxisField2' value='%(excluderowaxisfield2)s' >"
   Response.Write "<input type=hidden id='ExcludeRowAxisField3' name='ExcludeRowAxisField3' value='%(excluderowaxisfield3)s' >"
   Response.Write "<input type=hidden id='ExcludeRowAxisField4' name='ExcludeRowAxisField4' value='%(excluderowaxisfield4)s' >"
''' % d
    ret = ret + '''
   if ahidden=0 then
'*** ASPSourceOnFilter -- START ***
%s
'*** ASPSourceOnFilter -- END ***
   End if
   Response.Write "</form>"
end sub
''' % (aaspsourceonfilter, )
    ret = ret + '''
Sub doShowControls(aPasek)
   dim i,istart,iend,ipages,scnt,imax,ssep,acarr
   if intNumberOfPages<=1 then
      Exit Sub
   End if
   ipages=5   
   'ssep="|"
   ssep="&nbsp;"

   response.write "<table  class=""ui-widget"" cellpaddding=""0"" cellspacing=""0""><tr>"
   if intNumberOfPages>0 and aPageNumber>1 then
      Response.Write "<td><div class=""ui-state-default ui-corner-all clickable"" title=""Pierwsza strona"" onclick=""javascript:doSubmit(1);""><span class=""ui-icon ui-icon-seek-first""></span></div></td>"
   else
      Response.Write "<td><div class=""ui-state-disabled ui-corner-all"" title=""Pierwsza strona""><span class=""ui-icon ui-icon-seek-first""></span></div></td>"
   end if
   if aPageNumber>1 and aPageNumber>1 then
      Response.Write "<td><div class=""ui-state-default ui-corner-all clickable"" title=""Poprzednia strona"" onclick=""javascript:doSubmit(" &  aPageNumber-1 & ");""><span class=""ui-icon ui-icon-seek-prev""></span></div></td>"
   else
      Response.Write "<td><div class=""ui-state-disabled ui-corner-all"" title=""Poprzednia strona""><span class=""ui-icon ui-icon-seek-prev""></span></div></td>"
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
         Response.Write "<td><div class=""ui-state-disabled ui-corner-all"">&nbsp;" & scnt & "&nbsp;</div></td>"
      else
         Response.Write "<td><div class=""ui-state-default ui-corner-all clickable"" onclick=""javascript:doSubmit(" & CStr(i) & ");"">&nbsp;" & scnt & "&nbsp;</div></td>"
      end if
   next
   if aPageNumber<intNumberOfPages and aPageNumber<intNumberOfPages then
      Response.Write "<td><div class=""ui-state-default ui-corner-all clickable"" title=""Następna strona"" onclick=""javascript:doSubmit(" & aPageNumber+1 & ");""><span class=""ui-icon ui-icon-seek-next""></span></div></td>"
   else
      Response.Write "<td><div class=""ui-state-disabled ui-corner-all"" title=""Następna strona""><span class=""ui-icon ui-icon-seek-next""></span></div></td>"
   end if
   if intNumberOfPages>1 and aPageNumber<intNumberOfPages then
      Response.Write "<td><div class=""ui-state-default ui-corner-all clickable"" title=""Ostatnia strona"" onclick=""javascript:doSubmit(" & intNumberOfPages & ");""><span class=""ui-icon ui-icon-seek-end""></span></div></td>"
   else
      Response.Write "<td><div class=""ui-state-disabled ui-corner-all"" title=""Ostatnia strona""><span class=""ui-icon ui-icon-seek-end""></span></div></td>"
   end if
   Response.Write "</tr>"
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
'''
    sactionmodifier = ''
    for asaction in asearchactions:
        ret = ret + '''
' *** SEARCHACTION -- %s -- START ***
%sif Request.Form("searchcustom")="%d" then '%s
   aForPrinting=0
   aForExcel=0
   ReturnValue=0
   MoreRecords=0
   aRecsPerPage=99999999
   aPageNumber=1
   aQueryString=Request.Form("_QUERYSTRING")
   Call GetSQLDataToRS(0)
%s
   Do While Not rs.EOF
      arow=rs.Fields("_Row").Value
      aoid=rs.Fields("%s__OID").Value
%s
      rs.MoveNext
   Loop
%s
' *** SEARCHACTION -- %s -- END ***
''' % (asaction.Name, sactionmodifier, asaction.OID, asaction.Name, asaction.OnBeforeIteration, afields[0].Table.NameSQL, asaction.OnIteration, asaction.OnAfterIteration, asaction.Name)
        sactionmodifier = 'else'
    ret = ret + '''
%sif Request.Form("search")="" or Request.Form("search")="2" then
   DisplaySearchForm 0
elseif Request.Form("search")="1" then
Function GetFieldType(afieldname)
   dim afields,atypes,i
   GetFieldType=-1
''' % sactionmodifier
    ret = ret + '''
   afields = Array(%s)
   atypes  = Array(%s)
   acontainers  = Array(%s)
''' % (string.join(sfl, ','), string.join(sft, ','), string.join(sfc, ','))
    ret = ret + '''
   for i=0 to UBound(afields)
      if afields(i)=afieldname then
         GetFieldType=atypes(i)+acontainers(i)
         Exit For
      end if
   next
End Function

Function CreateSingleSQLQueryConstraint(snumber,sp,sp1,iandcnt,iorcnt)
   dim afieldname,avalue,avalue1,atype,aoperator,alink
   afieldname=Request.Form("fFieldName" & snumber)
   avalue=Replace(Request.Form("fValue" & snumber), "'", "''")
   avalue1=avalue
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
      if (atype=144) then 'string '$$
         avalue="'" & avalue & "'"
      elseif (atype=145) then 
         avalue="'" & avalue & "'"
         if aOperator<>"Like" then
            afieldname=" CAST(" & afieldname & " as varchar(200)) "
         end if
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
        afieldname=" Replace(CONVERT(varchar(40)," & afieldname & ",120),'-','') "
        avalue1=getDateAsSQLDate(avalue1) & "%"
        if avalue1="%" then
           avalue1=Replace(Replace(Replace(avalue,"-",""),"/",""),"\\","")
        end if
        avalue="'" & avalue1 & "'"
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
'''
    ret = ret + '''
Sub GetSQLDataToRS(aispivot)
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
'*** ASPSourceOnBeforeGetData -- START ***
   %s
'*** ASPSourceOnBeforeGetData -- END ***
''' % (aaspsourceonbeforegetdata, )
    for afield in afields:
        if afield.IsSearchByValue:
            ret = ret + '''
acrules=""
asep="'"
for each acrule in request.form("checkb_%s")
''' % (afield.Name, )

            if afield.Type in ['bool', ]:
                ret = ret + '''
   if acrule="Prawda" then
      acrule="True"
   end if
   if acrule="Fałsz" then
      acrule="False"
   end if
'''
            ret = ret + '''
   acrules=acrules & asep & replace(acrule,"'","''") & "'"
   asep=",'"
next
if acrules<>"" then
   if sp<>"" then
     sp=sp & " AND "
   end if
   sp=sp & "%s in (" & acrules & ")"
end if
''' % (afield.NameSQL, )

    if achapteridfield is not None:
        ret = ret + '''
if achapterid<>"" and not instr(aquerystring,"nochapterid=1")>0 then
   sp=sp & " AND (%s_ChapterID=" & achapterid & ") "
end if 
''' % (achaptertable, )

    ret = ret + '''
'Response.Write "<h2>SP:" & request.form & "</h2>"

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
   if Request.Form("iForPrinting")<>"" then
      aForPrinting=1
   else
      aForPrinting=0
   end if
   if Request.Form("iForExcel")<>"" then
      aForExcel=1
      aForPrinting=1
   else
      aForExcel=0
   end if
'''
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
   sob2=""
   for i=1 to 3
      afieldname=Request.Form("fOrderFieldName" & CStr(i))
      if afieldname<>"" then
         wfn=True
         for j=1 to i-1
            if Request.Form("fOrderFieldName" & CStr(j))=afieldname then
               wfn=False
            end if
         next
         if wfn then
            afieldname=afieldname & " " & Request.Form("fOrderDirection" & CStr(i))
            if sob2<>"" then
               sob2=sob2 & " , "
            end if
            sob2=sob2 & afieldname
         end if
      end if
   next
   if sob2<>"" then
      sob=sob2
   end if
   Cmd1.Parameters("@sWhere").Value=sp
   Cmd1.Parameters("@sOrder").Value=sob
   Cmd1.Parameters("@UserName").Value=Dession("username")
   Cmd1.Parameters("@IsPivot").Value=aIsPivot
''' % (asp.Name, asortedfields)
    if aprojectoid >= 0:
        ret = ret + '''
   Cmd1.Parameters("@UserRights").Value=GetUserProjectACL(%d)
''' % (aprojectoid, )
    ret = ret + '''
   set rs=cmd1.Execute
   ReturnValue=CLng(cmd1.Parameters.Item(0).Value)
   MoreRecords=CLng(cmd1.Parameters("@MoreRecords").Value)
End Sub

   aForPrinting=0
   aForExcel=0
   ReturnValue=0
   MoreRecords=0
   Dession("DefaultSQLRecordsPerPage")=Request.Form("iRecsPerPage")
   aRecsPerPage=Clng(Request.Form("iRecsPerPage"))
   aPageNumber=Clng(Request.Form("iPageNo"))
   aQueryString=Request.Form("_QUERYSTRING")
   Call GetSQLDataToRS(0)
   alegend=""
   if MoreRecords>0 then
      intNumberOfPages=int(MoreRecords / aRecsPerPage)
      if (MoreRecords mod aRecsPerPage)>0 then
         intNumberOfPages=intNumberOfPages+1
      end if
      if aForPrinting<>1 then
         Response.Write "<div class=""ui-tabs ui-widget ui-widget-content ui-corner-all"">"
         doShowControls 0
      end if
      if aForPrinting<>1 then
         Response.Write("<span class='objectsviewcaption'>Tabela wynikowa</span>")
      end if
      if aForPrinting=1 then
         if aForExcel=1 then
            Response.Write("<div id='mytablediv1' name='mytablediv1' style='display:none;'>")
         end if
         Response.Write("<table border='1' onactivate='javascript:window.clipboardData.setData(""Text"",this.outerHTML);'>")
         Response.Write("<caption><font size='-3'>Tabela wynikowa</font></caption>")
      else
         if isdialog="1" then
%>
<script language="javascript">
var doid2values={}  
function processDialogSelection(aoid) {
/*
   window.parent.document.getElementById('myDialogFrameName1').innerHTML='<%=Request.QueryString("dialogframe")%>';
   window.parent.document.getElementById('myDialogFrameInput1').innerHTML='<%=Request.QueryString("dialoginput")%>';
   window.parent.document.getElementById('myDialogFrameOID1').innerHTML=aoid;
   window.parent.document.getElementById('myDialogFrameValue1').innerHTML=doid2values[aoid];
   window.parent.document.getElementById("myevenntcallerdialog1").fireEvent("onclick");
*/
   jQuery('#myDialogFrameName1', window.parent.document).html('<%=Request.QueryString("dialogframe")%>');
   jQuery('#myDialogFrameInput1', window.parent.document).html('<%=Request.QueryString("dialoginput")%>');
   jQuery('#myDialogFrameOID1', window.parent.document).html(aoid);
   jQuery('#myDialogFrameValue1', window.parent.document).html(doid2values[aoid]);
   jQuery('#myevenntcallerdialog1', window.parent.document).trigger('click');
} 
</script>
<%
         end if
         Response.Write("<TABLE class='ui-widget-content'><TR>")
      end if
      if aForPrinting=1 then
         Response.Write "<TH><font size='-3'>l.p.</font></TH>"
'''
    for afield in afields:
        if MHTMLSQLGenLib.CheckFieldColumnVisibility(afield):
            ret = ret + '''
            Response.Write "<TH><font size='-3'>%s</font></TH>"
''' % (afield.PrettyName, )
    if amarkergroups is None or not len(amarkergroups):
        ret = ret + '''
      else
         Response.Write "<TH class='ui-widget-header'>l.p.</TH>"
'''
    else:
        ret = ret + '''
      else
         Response.Write "<TH class='ui-widget-header' colspan=2>l.p.</TH>"
'''
    for afield in afields:
        if MHTMLSQLGenLib.CheckFieldColumnVisibility(afield):
            ret = ret + '''
         Response.Write "<TH class='ui-widget-header'>%s</TH>"
''' % (afield.PrettyName, )
    ret = ret + '''
      end if
      Response.Write("</TR>")
'''
    if not (amarkergroups is None or not len(amarkergroups)):
        for akey, amarkers in amarkergroups.items():
            if amarkers:
                bmarker = amarkers[0]
                if bmarker.Description:
                    ret = ret + '''
         %s=False
''' % (bmarker.MarkerID, )
    ret = ret + '''
      sjRows=""
      aLpFirst=rs.Fields("_Row").Value
      Do While Not rs.EOF
         aVisibleValue=""
         aLpLast=rs.Fields("_Row").Value
         if CLng(aLpLast) mod 500 = 0 then
            Response.flush()
         end if
         aoid=rs.Fields("%s").Value
         if sjRows<>"" then
            sjRows=sjRows & ","
         end if
         sjRows=sjRows & "'" & aoid & "'"
         if aForPrinting=1 then
            Response.Write "<TR>"
         else
            Response.Write "<TR class='ui-state-default' id='ir" & aoid & "'>"
         end if
         if aForPrinting=1 then 'l.p.
            Response.Write "<td><font size='-3'><DIV align=center>"
         else
            Response.Write "<td class='objectsviewdataeven'>"
            if isdialog<>"1" then
               Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s" & "&" & aQueryString & "'>"
            else
               Response.Write "<a class='objectitemasanchor' style='cursor:pointer;' onclick='javascript:return processDialogSelection(""" & cstr(aoid) & """);'>"
            end if
         end if
         arsValue=rs.Fields("_Row").Value
         if arsValue<>"" then
            Response.Write server.htmlencode(arsValue)
         else
            Response.Write "&nbsp;"
         end if   
         if aForPrinting=1 then
            Response.Write "</div></font></td>"
         else
            Response.Write "</a></td>"
''' % (amainoidfieldname, aownerfilename, aurlparams)
    if not (amarkergroups is None or not len(amarkergroups)):
        akeys = amarkergroups.keys()
        akeys.sort()
        ret = ret + '''
      amarker=""
'''
        for akey in akeys:
            arules = []
            amarkers = amarkergroups[akey]
            amarkers.reverse()
            bmarker = None
            for amarker in amarkers:
                bmarker = amarker
                arules.extend(amarker.Rules)
            if bmarker:
                ret = ret + '''
         wmarker=0
'''
                for arule in arules:
                    ret = ret + '''
         arsValue=rs.Fields("%s").Value
         if %s then
            wmarker=wmarker+1
         end if
''' % (arule.Marker.Field.UniqueName, arule.AsVB('arsValue'))
                ret = ret + '''
         if wmarker=%d then
            if aMarker<>"" then
               aMarker=aMarker & "<br>"
            end if
''' % (len(arules), )
                if bmarker.Description:
                    ret = ret + '''
            if not %s then
               %s=True
               alegend=alegend & "&nbsp;&nbsp;<font face='%s' size='%s' color='%s'>%s</font><span class='normal'> - %s</span><br>"
            end if
''' % (bmarker.MarkerID, bmarker.MarkerID, bmarker.FontFace, bmarker.FontSize, bmarker.Color, bmarker.Character, bmarker.Description)
                ret = ret + '''
            aMarker=aMarker & "<font face='%s' size='%s' color='%s'>%s</font>"
         end if
''' % (bmarker.FontFace, bmarker.FontSize, bmarker.Color, bmarker.Character)
        ret = ret + '''
            if aMarker="" then
               aMarker="&nbsp;"
            end if   
            Response.Write "<td class='objectsviewdataeven'><span style='line-height:100%'>" & aMarker & "</span></td>"
'''
    ret = ret + '''
         end if
'''
    i = 2
    print 'GENERATE ADVSEARCH: %s' % afilename
    for afield in afields:
        wverbose = 0
        #if afield.UniqueName=='V01_BZR_200020_DataRozpoczecia':
        #wverbose=1
        wfv = MHTMLSQLGenLib.CheckFieldColumnVisibility(afield, averbose=wverbose)
        #print '  FIELD: %s - type: %s, aliased: %s, search: %s, visible: %s'%(afield.UniqueName,afield.Type,str(afield.IsAliased),str(afield.IsSearch),str(wfv))
        if (afield.IsAliased or afield.IsSearch) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float', 'external dict multiple']:
            if MHTMLSQLGenLib.CheckFieldColumnVisibility(afield):
                """
mso-number-format:\@ 
text 
mso-number-format:"0\.000" 
3 decimals 
mso-number-format:\#\,\#\#0\.000 
comma separators (and 3 decimals) 
mso-number-format:"mm\/dd\/yy" 
Date format 
mso-number-format:"d\\-mmm\\-yyyy" 
another date format 
mso-number-format:Percent 
percent
"""
                wtext = 0
                smsotype = """ style='mso-number-format:""\@"";'"""
                if afield.Type in ['numeric', 'integer', 'money', 'float']:
                    salign = 'right'
                    swrap = 'nowrap'
                    smsotype = """ style='mso-number-format:""General Number"";'"""
                elif afield.Type in ['date', 'datetime']:
                    salign = 'center'
                    swrap = 'nowrap'
                    smsotype = """ style='mso-number-format:""Short Date"";'"""
                elif afield.Type in ['bool', ]:
                    salign = 'center'
                    swrap = 'nowrap'
                    smsotype = """ style='mso-number-format:""General Number"";'"""
                else:
                    salign = 'left'
                    swrap = 'nowrap'    #bylo wrap
                    wtext = 1
                ret = ret + '''
         if aForPrinting=1 then '%s
            Response.Write "<td%s><font size='-3'><DIV align=%s %s>"
         else
            Response.Write "<td class='objectsviewdataeven' align=%s %s>"

            if isdialog<>"1" then
               Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s" & "&" & aQueryString & "'>"
            else
               Response.Write "<a class='objectitemasanchor' style='cursor:pointer;' onclick='javascript:return processDialogSelection(""" & cstr(aoid) & """);'>"
            end if

         end if
         arsFieldName="%s"
         arsFieldType="%s"
         arsValue=rs.Fields("%s").Value
         arsType=rs.Fields("%s").Type
         if (arsType=7) or (arsType=133) or (arsType=134) or (arsType=135) then
            arsValue=getDateTimeAsStr(arsValue)
         end if
         brsValue=""
''' % (afield.PrettyNameDisplayed, smsotype, salign, swrap, salign, swrap, aownerfilename, aurlparams, afield.UniqueName, afield.Type, afield.UniqueName, afield.UniqueName)
                ret = ret + '''
'*** ASPSourceOnFieldValue -- START ***
   %s                              
'*** ASPSourceOnFieldValue -- END ***
''' % (aaspsourceonfieldvalue, )

                if afield.Type == 'bool':
                    ret = ret + """
         if brsValue<>"" then
            Response.Write brsValue
         else
            if not isnull(arsValue) then
               if CBool(arsValue) then
                  Response.Write "Tak"
               else
                  Response.Write "Nie"
               end if
            end if
         end if
"""
                elif afield.Type in ['date', 'datetime', ]:
                    ret = ret + '''
         arsValue=trim(arsValue)
         if brsValue<>"" then
            aVisibleValue=aVisibleValue & ", " & brsValue
            Response.Write brsValue
         else
            if arsValue<>"" then
               aVisibleValue=aVisibleValue & ", " & arsValue
               Response.Write arsValue
            else
               Response.Write "&nbsp;"
            end if
         end if
'''
                elif afield.Type in ['money', ]:
                    ret = ret + '''
         if brsValue<>"" then
            Response.Write brsValue
         else
            Response.Write Currency2HTML(arsValue,1)
         end if
'''
                elif afield.Type in ['external dict multiple', ]:
                    qfield = afield
                    qtable = qfield.ExternalDictTable
                    ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDictMultiple(qfield, arsnum=1, arsbasenum=-1, anoref=1, afieldid=afield.UniqueName, dbtable=qtable, aseparator='<hr>')
                else:
                    if wtext:
                        ret = ret + '''
if aForExcel=1 and arsValue<>"" then
   arsValue="'" & arsValue
end if
if aForExcel=1 and brsValue<>"" then
   brsValue="'" & brsValue
end if
'''
                    ret = ret + '''
         arsValue=trim(arsValue)
         if brsValue<>"" then
            aVisibleValue=aVisibleValue & ", " & brsValue
            Response.Write server.htmlencode(brsValue)
         else
            if arsValue<>"" then
               aVisibleValue=aVisibleValue & ", " & arsValue
               Response.Write server.htmlencode(arsValue)
            else
               Response.Write "&nbsp;"
            end if
         end if
'''
                ret = ret + '''
         if aForPrinting=1 then
            Response.Write "</div></font></td>"
         else
            Response.Write "</a></td>"
         end if
'''
            i = i + 1
    ret = ret + '''
         if isdialog="1" then
%>
<script language="javascript">
doid2values["<%=aoid%>"]="<%=server.htmlencode(trim(Mid(aVisibleValue,2)))%>";
</script>
<%         
         end if
'''
    ret = ret + '''
         Response.Write "</TR>"
         rs.MoveNext
      Loop
      Response.Write("</TABLE>")
      if aForExcel=1 then
         Response.Write("</div>")
      end if
      if aForPrinting<>1 then
         if intNumberOfPages>1 then
            Response.Write "Wiersze " & CStr(aLpfirst) & " - " & CStr(aLpLast) & " z " & CStr(MoreRecords)
         end if
         doShowControls 1
         if alegend<>"" then
            Response.Write "<hr>"
            Response.Write "<span class='objectsviewcaption'>Legenda:</span><br>"
            Response.Write alegend
         end if
         Response.Write "<hr>"
         Response.Write "<button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:document.location.reload();'>Odśwież</button>"         
         Response.Write "&nbsp;&nbsp;<button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doSubmitRepeat()'>Powrót</button>"
'''
    for asaction in asearchactions:
        ret = ret + '''
         Response.Write "&nbsp;&nbsp;<button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:if(confirm(""Czy na pewno chcesz wykonać tę akcję?"")){doSubmitCustom(""%d"",""%s"",""%s"")};'>%s</button>"
''' % (asaction.OID, asaction.Parameters.get('target', ''), asaction.Parameters.get('isdialog', ''), asaction.Name)
    ret = ret + '''
         Response.Write "</div>"
      end if
'*** ASPSourceOnAfterSearch -- START ***
   %s                              
'*** ASPSourceOnAfterSearch -- END ***
''' % (aaspsourceonaftersearch, )
    ret = ret + '''
      if aForExcel=1 then
%>
<OBJECT classid=clsid:0002E559-0000-0000-C000-000000000046 name=mySheet1 id=mySheet1 style="width=100%;height=75%;"></OBJECT>
<SCRIPT language="vbscript" DEFER>
document.getElementById("mySheet1").HTMLData = document.getElementById("mytablediv1").InnerHTML
document.getElementById("mySheet1").Refresh
document.getElementById("mySheet1").ActiveSheet.UsedRange.AutoFitColumns
document.getElementById("mySheet1").Range("A1").Select
'document.getElementById("mySheet1").TitleBar.Caption = "Zestawienie"
document.getElementById("mySheet1").DisplayTitleBar = False
'document.getElementById("mySheet1").Cells.Clear
'document.getElementById("mySheet1").DataType = "HTMLURL"
'document.getElementById("mySheet1").HTMLURL = ""
'document.getElementById("mySheet1").DisplayColHeaders = False
'document.getElementById("mySheet1").DisplayRowHeaders = False
'document.getElementById("mySheet1").DisplayToolbar = False
'document.getElementById("mySheet1").AllowPropertyToolbox = False
'document.getElementById("mySheet1").Cells.Locked = True
'document.getElementById("mySheet1").ActiveSheet.Protection.Enabled = True
Window.Status=""
</SCRIPT>
<%         
      end if
   Else
      Response.Write "<h1>Brak danych spełniających zadane warunki</h1><br>"
      Response.Write "<button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doSubmitRepeat()'>Powrót</button>"
   End if
elseif Request.Form("search")="3" then ' Pivot Page
'''
    if aquerysql is not None and aquerysql.IsPivot:
        ret = ret + '''
'   Response.Write "<h1>%s</h1>"
''' % (aquerysql.SQLString, )
        ret = ret + '''
   if GetInputValue("pivotshowdetails")="1" then
%%>
%s
<%%                      
   end if
''' % (aquerysql.EventPivotDetails, )
        ret = ret + '''
   atmpfname=Request.Form("datasourcefilename")
   ReturnValue=0
   MoreRecords=0
   aRecsPerPage=100
   aPageNumber=1
   Call GetSQLDataToRS(1)
   if rs.RecordCount>0 then
      on error resume next
      strFullName=Application("DefaultOutputPath") & "\\" & atmpfname
      Set objFSO = CreateObject("Scripting.FileSystemObject")
      if objFSO.FileExists(strFullName) then
         objFSO.DeleteFile strFullName,True
      end if
      Set objFSO=Nothing      
      rs.Save strFullName, 0 'adPersistADTG
      on error goto 0
%>

<!-- #include file="../../../inc/_pivot_default.asp" -->

<%                            
   else
      Response.Write "<h1>Brak danych spełniających zadane warunki</h1>"
   end if
'''
    ret = ret + '''
   Response.Write "<br><button class='fg-button-single ui-state-default ui-corner-all uihover' onclick='javascript:doSubmitRepeat()'>Powrót</button>"
End If
%>
<SCRIPT LANGUAGE=javascript>
jQuery(function() {
   jQuery("#fValue1").focus();
});
</SCRIPT>
<%
'''
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASPAdvancedPicker(afilename, afields, asp, asortedfields='', aownerfilename='', amainoidfieldname='_OID', aurlparams='', amarkergroups=None):
    ret = '''
rs.ActiveConnection = cn
rs.CursorType = adOpenKeyset
rs.LockType = adLockOptimistic      

sw=" WHERE CONVERT(VARCHAR(200)," & Request.QueryString("field") & ")<>''"
if Request.QueryString("where")<>"" then
   sw1=""
   if Request.QueryString("approx")="1" then
      sw1="%"
   end if
   sw= sw & " AND CONVERT(VARCHAR(200)," & Request.QueryString("field") & ") LIKE '" & sw1 & Request.QueryString("where") & "%'"
end if
if Request.QueryString("reffield")<>"" and Request.QueryString("refvalue")<>"" then
   sw= sw & " AND CONVERT(VARCHAR(200)," & Request.QueryString("reffield") & ") ='" & Request.QueryString("refvalue") & "'"
end if

src="SELECT TOP 200 " & Request.QueryString("field") & " FROM " & Request.QueryString("table") & sw & " GROUP BY " & Request.QueryString("field") & " ORDER BY " & Request.QueryString("field")
afield=CStr(Request.QueryString("field"))
rs.Source=src
rs.Open
'response.write("<b>" & src & "</b><hr>")
sb=""
if Not rs.EOF then
   Response.Write "<span id=myinfo1 style=""display:none;"">OK</span>"
   Response.Write "<div style=""position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300; height:200px; border-bottom:2px solid black;"" >"
   sv=rs(afield)
   on error resume next
   st=TypeName(sv)
   on error goto 0
   if st="Boolean" then
      Response.Write "<DIV ONCLICK=""parent.fpselectedelement.value='1';parent.fpPopup.hide();"" onmouseover=""this.style.background='#ffffff'"" onmouseout=""this.style.background='wheat'"" STYLE=""font-family:verdana; font-size:8pt; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer;" & sb & """>Tak</DIV>"
      Response.Write "<DIV ONCLICK=""parent.fpselectedelement.value='0';parent.fpPopup.hide();"" onmouseover=""this.style.background='#ffffff'"" onmouseout=""this.style.background='wheat'"" STYLE=""font-family:verdana; font-size:8pt; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer;border-top:0px solid black"">Nie</DIV>"
   else
      Do While Not rs.EOF
         Response.Write "<DIV ONCLICK=""parent.fpselectedelement.value=this.innerText;parent.fpPopup.hide();"" onmouseover=""this.style.background='#ffffff'"" onmouseout=""this.style.background='wheat'"" STYLE=""font-family:verdana; font-size:8pt; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer;" & sb & """>" & CStr(rs(afield)) & "</DIV>"
         sb=" border-top:0px solid black"
         rs.MoveNext
      Loop
   end if
   Response.write "</div>"
else
   smessage="Brak danych"
   if sw<>"" then
      if Request.QueryString("approx")="1" then
         smessage=smessage & " zawierających """ & CStr(Request.QueryString("where")) & """"
      else
         smessage=smessage & " rozpoczynających się od """ & CStr(Request.QueryString("where")) & """"
      end if
   end if
   Response.Write "<span id=myinfo1 style=""display:none;"">" & smessage & "</span>"
end if
'''
    return ret


#*********************************************************************************
def SQLTableGetSingleFieldValue(atable, acrm):
    ret = '''<%%@ CodePage=%s LANGUAGE="VBSCRIPT" %%><!-- #include file="../../../inc/validation.inc" --><!-- #include file="../../../inc/class_upload.asp" --><!-- #include file="../inc/_page_begin.asp" --><%%
IsRAWPage=1
   Response.Charset = "%s"
'   Response.CodePage = %s
   Response.CacheControl = "Private"
   Response.ExpiresAbsolute = #1/1/1999 1:10:00 AM#

if Request.QueryString("ioid")<>"" then
   aoid=ReplaceIllegalCharsLev0Text(left(Request.QueryString("ioid"),44))
else
   aoid=""
end if
if Request.QueryString("afield")<>"" then
   afield=ReplaceIllegalCharsLev0Text(left(Request.QueryString("afield"),200))
else
   afield=""
end if

amode=ReplaceIllegalCharsLev0Text(mid(Request.QueryString("mode"),1,10))

if amode="" then
   if aoid<>"" and afield<>"" then
      rs.Open "select _OID," & afield & " from %s WHERE _OID='" & aoid & "'", cn
      if not(rs.EOF or rs.BOF) then
         response.Write rs.Fields(1)
      end if
   end if
end if
                              
if amode="ac" then
   bfname=ReplaceIllegalCharsLev0Text(mid(Request.QueryString("fname"),1,90))
   if bfname<>"" then
      ret=""
      avalue=ReplaceIllegalCharsLev0Text(mid(Request.Form("value"),1,90))
      if instr(avalue,"cache_")=1 then
         rs.Open "SELECT distinct top 500 " & bfname & " as myfield FROM %s ORDER BY "+bfname+"",cn
      else
         rs.Open "SELECT distinct top 500 " & bfname & " as myfield FROM %s WHERE " & bfname & " LIKE '" & avalue & "%%' ORDER BY "+bfname+"",cn
      end if
      do while not rs.EOF and not rs.BOF
         if ret<>"" then
            ret=ret & ","
         end if
         avalue=JSONEncode(CStr(rs("myfield")))
         if avalue<>"" then
            ret=ret & "{""value"":""" & avalue & """,""display"":""" & avalue & """}"
         end if
         rs.MoveNext
      Loop
      ret="[" + ret & "]"
      Response.Write ret
   end if
end if

%%><!-- #include file="../inc/_page_end.asp" -->''' % (acrm.DefaultCodePage, acrm.DefaultEncoding, acrm.DefaultCodePage, atable.NameSQL, atable.NameSQL, atable.NameSQL,
                                                       )
    return ret


#*********************************************************************************
def GetSelectLinkedTable(atablelink, aeventsrc=None, asecurity=None, abasers=-1, anewrs=-1):
    if abasers <= 0:
        abasers = 0
        sbasers = ''
    else:
        sbasers = str(abasers)
    if anewrs < 0:
        anewrs = abasers + 1
    asecuritytable = asecurity
    sandallowedit, sandallowdelete = '', ''
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret3 = ret3 + """
   aallowrecordedit=CheckACLForRecord(%d,Bin2Hex(rs%s("_ACLWrite")),achapterid,"Edit")
   aallowrecorddelete=CheckACLForRecord(%d,Bin2Hex(rs%s("_ACLDelete")),achapterid,"Delete")
""" % (aeventsrc.CRM.OID, sbasers, aeventsrc.CRM.OID, sbasers)
        sandallowedit = 'and aallowrecordedit=1 '
        sandallowdelete = 'and aallowrecorddelete=1 '

    ret = ''
    ret2 = ''
    ahtmlid = 'tb_%d' % atablelink.OID
    if atablelink.TabID:
        asecurity = atablelink.SrcTable.TabsByIDSecurity.get(atablelink.TabID, '')
        #      asecurity=''
        #      if atablelink.TabID in atablelink.SrcTable.TabsByIDSecurity.keys():
        #         asecurity=atablelink.SrcTable.TabsByIDSecurity[atablelink.TabID]
        ret = ret + """
''''''''''''''''' START GETSELECTLINKEDTABLE
if Request.QueryString("sheet")="%d" then
   sscript_%s=""
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 4</font></h1>")
   else
""" % (atablelink.TabID, ahtmlid, asecurity)
    amodelxml = atablelink.GetModelXMLData()
    if amodelxml:
        amodelxml.Parse(anoassql=1)
        aquery = amodelxml.Parser.querysql
    else:
        aquery = MSQLQuery.QuerySQL(atop=1000, aisaliased=1)
        aquery.DisableHiddenDictFields = 1    #$$
        aquery.RecurTables.append(atablelink.SrcTable.SQLTable)
        aquery.PushTable(atablelink.DstTable.SQLTable)    #.DictSourceTable
    aquery.Clear()
    if 0:
        print '  --- OID:', atablelink.OID
        print 1, aquery.ThisTable
        print 2, atablelink.SrcTable
        print 3, atablelink.DstTable
        print 4, atablelink.SrcField
        print 5, atablelink.DstField
    if 0:
        sdbname = atablelink.DstTable.SQLTable.NameSQL + '.' + atablelink.DstField[0]
        print 6, aquery.FieldsDict.has_key(sdbname), sdbname
        print 7, aquery.ThisTable.Fields
    for asrcfield, adstfield in atablelink.LinkFields:
        d = {'type': 'eq', 'value': 'rs%s("%s")' % (sbasers, asrcfield), 'asasp': '1'}
        if aquery.ThisTable is None:
            print 'Tabela bazowa dla wzorca zapytania jest pusta:',
            print atablelink
            continue
        if not aquery.ThisTable.Fields.has_key(adstfield):
            print 'Polaczenie:', atablelink
            print 'Pole', adstfield, 'nie istnieje w tabeli', aquery.ThisTable
            print 'Lista pol:', aquery.ThisTable.Fields
        aoidfield = aquery.ThisTable.Fields[adstfield]
        aoidfield.AddRule(d)

    if atablelink.LinkConstraint:
        aquery.ThisTable.ParentExtConstraint = atablelink.LinkConstraint

    if aquery.ThisTable is not None:
        aquery.ThisTable.IsASPSQLConstraint = 1
        aquery.ThisTable.ASPSQLConstraintPrefix = 'TABLELINK_' + str(atablelink.OID)
        ret = ret + """
      if isempty(extrule_%s_%s) then
         extrule_%s_%s=""
      end if
""" % (aquery.ThisTable.ASPSQLConstraintPrefix, aquery.ThisTable.NameSQLID, aquery.ThisTable.ASPSQLConstraintPrefix, aquery.ThisTable.NameSQLID, )

    aquery.AsSQL()
    ret = ret + """
if Request.QueryString("ioid")<>"" then
"""
    dd = {'anewrs': anewrs, 'asqlstring': aquery.SQLString, }
    ret = ret + """
      Set rs%(anewrs)d = Server.CreateObject("ADODB.Recordset")
      rs%(anewrs)d.ActiveConnection = cn
      rs%(anewrs)d.CursorType = adOpenKeyset
      rs%(anewrs)d.LockType = adLockOptimistic
      rs%(anewrs)d.Source="%(asqlstring)s"
      rs%(anewrs)d.Open
""" % dd
    bfields = []
    i = 0
    for afield in aquery.FieldsList:
        bfields.append([afield.SearchTabID, i, afield])
        i = i + 1
    bfields.sort()
    afields = []
    for aid, acnt, afield in bfields:
        afields.append(afield)

    alinkname = atablelink.LinkName
    if alinkname:
        alinkname = alinkname + ': '
    alinkname = alinkname + atablelink.DstTable.SQLTable.TableCaption
    if atablelink.IsInternalTab:
        apagetabid_1 = 1
        if aeventsrc and hasattr(aeventsrc, 'PageTabCnt'):
            apagetabid_1 = aeventsrc.PageTabCnt
            aeventsrc.PageTabCnt = 1 + aeventsrc.PageTabCnt
        ret = ret + '''
   Response.Write "<div id=pagetab%d>"
''' % (apagetabid_1, )
    ret = ret + """
wlinkoid=""
if not (rs%d.EOF or rs%d.BOF) then
""" % (anewrs, anewrs)
    if not atablelink.IsExtension:
        ret = ret + """
'   Response.Write "<br><br><div class=""rounded background_pastelparadise_lightblue""><div class=""roundedContent background_default"">"
   Response.Write("<span class='objectsviewcaption'>%s</span>")
   Response.Write("<TABLE id=%s>")
   Response.Write("<THEAD>")
   Response.Write("<TR>")
   Response.Write "<TH>l.p.</TH>"
""" % (alinkname, ahtmlid)
        #(atablelink.SrcField,sf,atablelink.DstTable.SQLTable.NameSQL,atablelink.DstField,atablelink.DstTable.SQLTable.FieldsByTabID[0].Name,atablelink.DstTable.SQLTable.TableCaption,)
        for afield in afields:
            if afield.Name[:1] != '_' and afield.IsAliased and afield.TypeDescription != 'HTML' and not afield.Name in atablelink.DstField:    # and afield.Type!='external dict':
                if (amodelxml is not None) and (afield.Type in ['external dict', 'external dict multiple']):
                    continue
                ret = ret + """
   Response.Write "<TH>%s</TH>"
""" % (afield.PrettyName, )
        afieldoidalias = '0'
        if amodelxml is not None:
            afieldioid = aquery.ThisTable.Fields.get('_OID', None)
            if afieldioid is not None:
                afieldoidalias = '"' + afieldioid.PrettyName + '"'
        ret = ret + """
   Response.Write "</TR>"
   Response.Write "</THEAD>"
   Response.Write "<TBODY>"
   WLOCATION="%s_so.asp?ioid=" & Request.QueryString("ioid")
   stv_lp=1
   Do While Not rs%d.EOF
      aoid=rs%d.Fields(%s).Value
""" % (atablelink.SrcTable.SQLTable.NameFile, anewrs, anewrs, afieldoidalias)
        ret = ret + """
Response.Write "<TR class=""elclickredirect"" data-url=""%s_so.asp?ioid=" & cstr(aoid) & "&aoidref=" & Request.QueryString("ioid") & "&wlocation=" & server.urlencode(WLOCATION) & "&areffield=%s"">"
Response.Write "<td>"
Response.Write CStr(stv_lp)
Response.Write "</td>"   
""" % (atablelink.DstTable.SQLTable.NameFile, atablelink.DstFieldStr, )
        #   i=1
        for afield in afields:
            if afield.Name[:1] != '_' and afield.IsAliased and not afield.Name in atablelink.DstField and afield.TypeDescription != 'HTML':    # and afield.Type!='external dict':
                if (amodelxml is not None) and (afield.Type in ['external dict', 'external dict multiple']):
                    continue
                if afield.Type in ['numeric', 'integer', 'money', 'float']:
                    salign = 'right'
                    swrap = 'nowrap'
                elif afield.Type in ['date', 'datetime', 'bool']:
                    salign = 'center'
                    swrap = 'nowrap'
                else:
                    salign = 'left'
                    swrap = 'nowrap'    #bylo wrap
                ret = ret + """
'Response.Write "<td align=%s %s>"
Response.Write "<td>"
""" % (salign, swrap)
                if afield.Type == 'bool':
                    ret = ret + """
at1rsvalue=rs%d.Fields(%d).Value
if not isnull(at1rsvalue) then
   if CBool(at1rsvalue) then
      Response.Write "Tak"
   else
      Response.Write "Nie"
   end if
end if
""" % (anewrs, aquery.FieldsDict[afield.NameSQL], )
                elif afield.Type == 'external dict':
                    if amodelxml is None:
                        ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDict(afield.SQLField, arsnum=anewrs + 1, arsbasenum=anewrs, anoref=1, afieldid=aquery.FieldsDict[afield.NameSQL])
                elif afield.Type == 'external dict multiple':
                    if amodelxml is None:
                        ret = ret + MHTMLSQLGenLib.ShowSingleValueFromExternalDictMultiple(afield.SQLField, arsnum=anewrs + 1, arsbasenum=anewrs, anoref=1, afieldid=aquery.FieldsDict[afield.NameSQL])
                elif afield.Type in ['dict', 'dict int']:
                    ret = ret + """
sd=rs%d.Fields(%d).Value
if isnull(sd) then
   sd=""
else
   sd=CStr(sd)
end if
sds=sd
""" % (anewrs, aquery.FieldsDict[afield.NameSQL], )
                    if amodelxml is None:
                        ldvalues = afield.SQLField.DictValues
                    else:
                        ldvalues = afield.DictValues
                    for akey, avalue in ldvalues:
                        ret = ret + """
if sd="%s" then
    sds="%s"
end if
""" % (akey, avalue)
                    ret = ret + """
if (sds="") and (sd<>"") then
   sds=sd                        
end if
if sds="" then
   sds="&nbsp;"
end if
Response.Write sds
"""
                elif afield.Type == 'money':
                    ret = ret + """
sds=Currency2HTML(rs%d.Fields(%d).Value,1)
if sds="" then
   sds="&nbsp;"
end if
Response.Write sds
""" % (anewrs, aquery.FieldsDict[afield.NameSQL], )
                else:
                    ret = ret + """
arsValue=rs%d.Fields(%d).Value
arsType=rs%d.Fields(%d).Type
if (arsType=7) or (arsType=133) or (arsType=134) or (arsType=135) then
   arsValue=getDateTimeAsStr(arsValue)
end if
if arsValue="" then
   arsValue="&nbsp;"
end if
Response.Write arsValue
""" % (anewrs, aquery.FieldsDict[afield.NameSQL], anewrs, aquery.FieldsDict[afield.NameSQL], )
                ret = ret + """
Response.Write "</TD>"
"""


#         i=i+1
        ret = ret + """
      Response.Write "</TR>"
      stv_lp=stv_lp+1
      if stv_lp mod 100=0 then
         Response.flush
      end if
      rs%d.MoveNext
   Loop
   Response.Write("<TBODY></TABLE>")
   'Response.Write "<script type='text/javascript'>jQuery(function(){tableToGrid('#%s',{height:600,rownumbers:true});});</script>"
   sscript_%s=sscript_%s & "<script type='text/javascript'>jQuery(window).load(function(){makeTable('#%s');});</script>"
""" % (anewrs, ahtmlid, ahtmlid, ahtmlid, ahtmlid)
    else:    #atablelink.IsExtension
        # wyswietlenie jednego rekordu
        if not atablelink.IsInternalTab:
            ret = ret + """
Response.Write "<div class='ui-widget-header'>%s</div>"
""" % (atablelink.DstTable.SQLTable.TableCaption, )
        ret = ret + """
wlinkoid=rs%d("%s__OID")
""" % (anewrs, atablelink.DstTable.SQLTable.NameSQLID, )
        aOnLoad1 = []
        sret = MHTMLSQLGenLib.GetShowSingleSelectTable(atablelink.DstTable.SQLTable, abasers=anewrs, aeventsrc=atablelink.DstTable, aOnLoad1=aOnLoad1, lfields=afields, afieldsdict=aquery.FieldsDict)
        ret = ret + sret

    ret = ret + """                                
'   Response.Write("</div></div>")
end if
"""

    wl = 1
    if asecuritytable and asecuritytable.Nazwa == 'Disabled':
        wl = 0
    if wl:
        for asrcfield, adstfield in atablelink.LinkFields:
            if asrcfield == "_OID":
                if atablelink.LinkHrefCaptionNewItem:
                    atlname = atablelink.LinkHrefCaptionNewItem
                    atlnameedit = atablelink.LinkHrefCaptionEditItem
                else:
                    atlname = '%s - nowa pozycja' % (atablelink.DstTable, )
                    atlnameedit = '%s - edycja' % (atablelink.DstTable, )
                if atlname != '-':
                    dd = {'atabid': atablelink.TabID, 'accessleveledit': atablelink.DstTable.AccessLevelEdit, 'sandallowedit': sandallowedit, 'atlname': atlname, 'atlnameedit': atlnameedit, 'anamefile': atablelink.DstTable.SQLTable.NameFile, 'adstfield': adstfield, }
                    ret = ret + """
if Request.QueryString("sheet")="%(atabid)d" then
   if CheckUserAccess("%(accessleveledit)s")=1 %(sandallowedit)sthen 'DestTable - AccessLevelEdit
      if wlinkoid="" then
         atlu1=""
         atltext="%(atlname)s"
      else
         atlu1="ioid=" & wlinkoid & "&"
         atltext="%(atlnameedit)s"
         Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%(anamefile)s_so.asp?" & atlu1 & "aoidref=" & Request.QueryString("ioid") & "&wlocation=" & server.urlencode(wlocationback) & "&areffield=%(adstfield)s&chapterid=" & achapterid & "'>Więcej..</a>&nbsp;"
      end if
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%(anamefile)s_au.asp?" & atlu1 & "aoidref=" & Request.QueryString("ioid") & "&wlocation=" & server.urlencode(wlocationback) & "&areffield=%(adstfield)s&chapterid=" & achapterid & "'>" & atltext & "</a><br>"
      whr=1
   end if
end if
""" % dd

    if atablelink.IsInternalTab:
        ret = ret + '''
   Response.Write "</div>"
'''
        atabname = atablelink.LinkName
        if not atabname:
            atabname = atablelink.DstTable.SQLTable.TableCaption
        atabname = atabname.replace("'", "`")
        atabname = atabname.replace('"', "`")
        ret2 = ret2 + '''
if Request.QueryString("sheet")="%d" then
   Response.Write "<script type='text/javascript'>ltabscontainer.push(['pagetab%d','%s']);</script>"
end if
''' % (atablelink.TabID, apagetabid_1, atabname, )

    ret2 = ret2 + '''
if Request.QueryString("sheet")="%d" then
   response.write sscript_%s
end if
''' % (atablelink.TabID, ahtmlid, )

    ret = ret + """
if rs%d.State<>adStateClosed then
   rs%d.Close
end if
set rs%d=Nothing

end if                 
""" % (anewrs, anewrs, anewrs)
    if atablelink.TabID:
        ret = ret + """
   end if
end if
''''''''''''''''' END GETSELECTLINKEDTABLE
"""
    return [ret, ret2]
