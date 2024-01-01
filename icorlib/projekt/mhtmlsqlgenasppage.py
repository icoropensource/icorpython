# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import appplatform.startutil as startutil
import icorlib.wwwserver.icorwwwinterfaceutil as ICORWWWInterfaceUtil
import os
import types


#*********************************************************************************
def GetASPPageBegin(acrm, arefresh='', apage='', anocss=0, anobodytarget=0, aheadertext='', aencoding='', acodepage='', acompatibility='8'):
    if not aencoding:
        aencoding = acrm.DefaultEncoding
    if not acodepage:
        acodepage = acrm.DefaultCodePage
    ret = """<%%@ CodePage=%s LANGUAGE="VBSCRIPT" %%><!-- #include file="../inc/_page_begin.asp" -->
<html>
<head>
""" % (acodepage, )
    if acompatibility:
        ret = ret + """<meta http-equiv="X-UA-Compatible" content="IE=%s">
""" % (acompatibility, )
    if not anocss:
        ret = ret + ICORWWWInterfaceUtil.GetScriptCSS()
    if anobodytarget:
        abasetarget = ''
    else:
        abasetarget = '<!--<base target="TEXT">-->'
    ret = ret + """
<meta HTTP-EQUIV="Content-Type" content="text/html; charset=%s">
<meta http-equiv="Content-Language" content="pl">
<meta name="description" content="Opis strony">
<meta name="pragma" content="no-cache">
<meta name="keywords" content="ICOR object oriented database WWW information management repository">
<meta name="author" content="%s">
<META NAME="generator" CONTENT="ICOR"> 
<META HTTP-EQUIV="expires" CONTENT="Mon, 1 Jan 2001 01:01:01 GMT">
""" % (aencoding,startutil.appconfig.IParams['meta_author'])
    if arefresh and apage:
        ret = ret + """
<META HTTP-EQUIV="refresh" CONTENT="%s; URL=%s"> 
""" % (arefresh, apage)
    ret = ret + """
<title>Main page</title>
%s
""" % (abasetarget, )
    ret = ret + ICORWWWInterfaceUtil.GetScriptHeader(aheadertext=aheadertext)
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
DataOID=""
aTableID=""
POID=""
achapterid=""
acmsid=""
aPageTitle=""
thisFileType=""
""" % ('')
    return ret


#*********************************************************************************
def GetASPPageEnd(acreator, fname):
    abname = os.path.basename(fname)
    ret = """
%%>
<SCRIPT LANGUAGE=javascript>
jQuery(function() {
   try {
      if (ltabscontainer && ltabscontainer.length>1) {
         s='';
         for (i in ltabscontainer) {
            s+='<li><a href="#'+ltabscontainer[i][0]+'"><span>'+ltabscontainer[i][1]+'</span></a></li>'
            jQuery("#"+ltabscontainer[i][0]).append("<br>").appendTo("#tabscontainer-1");
         }
//         s+="<div style='clear:both;'></div>";
         jQuery('#tabscontainer-1 > ul').append(s);
         var apageid='BZR_<%%=aTableID%%>_sot.asp';
         if (getParentFrame('NAVBAR').tablesheets===undefined) {
            getParentFrame('NAVBAR').tablesheets={};
         }
         var atabid=getParentFrame('NAVBAR').tablesheets[apageid] || 0;
         jQuery('#tabscontainer-1').tabs({
            selected:atabid,
            select: function( event, ui ) {
               getParentFrame('NAVBAR').tablesheets[apageid]=ui.index;
            }
         });
      }
      var lasttab=getParentFrame('NAVBAR').GetSheetForCid('%s');
      jQuery('#tabscontainer').tabs('select',lasttab.nr);
   } catch(e) {}
});
</SCRIPT>
""" % (abname)
    ret = ret + ICORWWWInterfaceUtil.GetScriptInit()
    ret = ret + """
<SCRIPT LANGUAGE=javascript>
DataOID='<%=DataOID%>';
TableID='<%=aTableID%>';
POID='<%=POID%>';
ChapterID='<%=achapterid%>';
CMSID='<%=acmsid%>';
aPageTitle="<%=JSONEncode(CStr(aPageTitle))%>";
thisFileType="<%=thisFileType%>"
var dp={
   type: 'setDBDataViewStart',
   poid: POID,
   ioid: DataOID,
   tid: TableID,
   chapterid: ChapterID,
   cmsid: CMSID
};
dp['thisPageTitle']=''
dp['thisPageSubTitle']=''
dp['thisPageAction']=''
dp['thisPageDescription']=''
try {
  dp['filetype']=thisFileType
} catch (e) {
}
try {
  dp['tabs']=ltabs
} catch (e) {
}
try {
  dp['thisPageTitle']=thisPageTitle
} catch (e) {
}
try {
  if (aPageTitle!=='') {
    dp['thisPageTitle']=aPageTitle
  }
} catch (e) {
}
try {
  dp['thisPageSubTitle']=thisPageSubTitle
} catch (e) {
}
try {
  dp['thisPageAction']=thisPageAction
} catch (e) {
}
try {
  dp['thisPageDescription']=thisPageDescription
} catch (e) {
}
dp['documentURL']=window.location.href;
function listenTabWindowMessage(event) {
   try {
      if (event.data.type === 'tabInfo') {
         window.ownerTab=event.data.ownerTab
         window.ownerSheet=event.data.ownerSheet
         dp['ownerTab']=event.data.ownerTab
         dp['ownerSheet']=event.data.ownerSheet
         window.parent.postMessage(dp,'*');
      }
      if ((event.data.type === 'editorButtonClickSubmit') && (event.data.ownerTab === window.ownerTab) && (event.data.ownerSheet === window.ownerSheet)) {
         CKEDITOR.instances[event.data.fieldname].insertHtml(event.data.fieldvalue);
      }
   } catch (e) {
   }
}
if (window.addEventListener) {
   window.addEventListener('message', listenTabWindowMessage, false)
} else {
   window.attachEvent('onmessage', listenTabWindowMessage)
}

/*
   window.onbeforeunload = function() {
      window.parent.postMessage({
         type:'setDBDataViewFinish',
         poid: POID,
         ioid: DataOID,
         tid: TableID,
         chapterid: ChapterID,
         cmsid: CMSID
      },'*');
   }
*/
</SCRIPT>

<!-- #include file="../inc/_page_end.asp" -->
</body>
</html>
"""
    return ret


#*********************************************************************************
def GetPageTitle(atitle, acrm, atableid='', anewsletters=None, atabid=10, anorequestform=0, afiletype=''):
    if anewsletters is None:
        anewsletters = []
    if not isinstance(atableid, types.StringTypes):
        atableid = str(atableid)
    ret = """
if Request.QueryString("chapterid")<>"" then
   achapterid=Request.QueryString("chapterid")
   achapterref="&chapterid=" & achapterid
"""
    if not anorequestform:
        ret = ret + """                  
elseif Request.Form("_CHAPTERID")<>"" then
   achapterid=Request.Form("_CHAPTERID")
   achapterref="&chapterid=" & achapterid
"""
    ret = ret + """
else
   achapterid=""
   achapterref=""
end if
thisFileType="%s"
aPageTitle=""
DataOID=GetSafeOID(Request.QueryString("ioid"))
POID="%d"
acmsid=""
if achapterid<>"" then
   acmsid=GetChapterCMSID(achapterid)
end if

if Request.QueryString("sheet")<>"-1" then
   aPageTitle="%s"
   if (achapterid<>"") and (achapterid<>"-1") then
      aPageTitle=GetChapterCaption(achapterid)
   end if
%%>
<!-- $$ pobrac link do tej pozycji!
<div id=mainHeader class="fg-toolbar ui-widget ui-widget-content ui-corner-all ui-helper-clearfix"><div id=mainHeaderButtons class="fg-buttonset ui-helper-clearfix">
<A class="fg-button ui-state-default ui-corner-all" id=pageTitleButtonLastSearch onclick='javascript:window.location="/icormanager/icormain.asp?jobtype=lastvisithistory&id=searchform";' href="#">
   <IMG align=middle src="/icormanager/images/icons/silk/icons/table_refresh.png">&nbsp;Ostatnia wyszukiwarka
</A>
<A class="fg-button ui-state-default ui-corner-all" id=pageTitleButtonBack href="#" onclick="javascript:history.back();">
   <IMG align=middle src="/icormanager/images/icons/silk/icons/page_back.png">&nbsp;Powrót
</A>
<%%
aTableID="%s"
if (Request.QueryString("ioid")<>"") and (Request.QueryString("ioid")<>"-1") and (aTableID<>"") then
%%>
<A class="fg-button ui-state-default ui-corner-all" href="#" onclick='javascript:window.clipboardData.setData("Text","<a href=u2u.asp?t=1&amp;v1=<%%=Request.QueryString("ioid")%%>&amp;v2=<%%=aTableID%%>><%%=Server.HTMLEncode(Replace(Replace(aPageTitle,"%s","`"),"'","`"))%%></a>");alert("Uniwersalny link został skopiowany do schowka.");'>
   <IMG align=middle src="/icormanager/images/icons/silk/icons/link_add.png">&nbsp;Skopiuj link do tej pozycji
</A>
<%%
end if
%%>
<A class="fg-button ui-state-default ui-corner-all" href="#" onclick="javascript:window.print();">
   <IMG align=middle src="/icormanager/images/icons/silk/icons/printer.png">&nbsp;Drukuj
</A>
</div></div>
-->
<!-- jQuery UI theme switcher -->
<!--
<script type="text/javascript" src="http://ui.jquery.com/applications/themeroller/themeswitchertool/"></script>
<script type="text/javascript"> jQuery(function(){ jQuery('<div style="position:absolute;right:20px;"></div>').insertAfter('#mainHeaderButtons').themeswitcher({height:220,buttonPreText:'Skórka:',initialText:'Zmiana skórki'});});</script>
-->
<!--
<div class="fg-toolbar ui-widget ui-widget-header">
&nbsp;<%%=aPageTitle%%>
</div>
-->
<script type="text/javascript">
function setButtonBackAction(atext) {
   jQuery("#pageTitleButtonBack").click(function(){
      window.location=atext;
   });
//   var pageTitleBBFunction = new Function("window.location='"+atext+"'");
//   window.document.getElementById("pageTitleButtonBack").onclick=pageTitleBBFunction;
}
</script>
<script type="text/javascript">
ltabscontainer=[];
</script>
<div id="tabscontainer-1">
   <ul>
   </ul>
</div>
""" % (afiletype, acrm.OID, atitle, atableid, '""')
    ret = ret + """
<%
end if
"""
    #<!--
    #<img alt='Skopiuj link do tej pozycji' align=middle align=top vspace=0 src='/icormanager/images/icons/silk/icons/link_add.png' style='cursor:pointer;' onclick='javascript:window.clipboardData.setData("Text","<a href=u2u.asp?t=1&amp;v1=<%%=Request.QueryString("ioid")%%>&amp;v2=<%%=aTableID%%>><%%=Server.HTMLEncode(Replace(Replace(aPageTitle,"%s","`"),"'","`"))%%></a>");alert("Uniwersalny link został skopiowany do schowka.");'>
    #-->
    return ret
