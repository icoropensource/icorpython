# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.projekt.mhtmlsqlgenlib as MHTMLSQLGenLib
from icorlib.wwwhtml.main import *
import icorlib.wwwhtml.fckmain as FCKMain
from icorlib.wwwhtml.worksheetmain import *
import string


class MHTMLSQLGenException(Exception):

    def __init__(self, errmsg=''):
        Exception.__init__(self, errmsg)


def ProcessFieldValueStore(atable, acheckexists=0):
    ret = ''
    i = 1
    #   woiddictref=0
    for afield in atable.FieldsByTabID:
        #      if string.lower(afield.Name)=='_oiddictref':
        #         woiddictref=1
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if acheckexists:
                ret = ret + '      if FormFields.Exists("%s") then\n' % (afield.Name, )
            if afield.Type == 'string':
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = Left(FormFields("%s"),%d)\n' % (afield.Name, afield.Name, afield.SizeAsNumber)
            elif afield.Type in ['numeric', 'money', 'float']:
                if afield.TypeDescription != 'Auto increment':
                    ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                    ret = ret + '         if IsNumeric(FormFields("%s")) then rs("%s") = FormFields("%s")\n' % (afield.Name, afield.Name, afield.Name)
            elif afield.Type == 'date':
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = getStrAsDateTime(FormFields("%s"),"","",%d)\n' % (afield.Name, afield.Name, afield.NoPastDate)
            elif afield.Type == 'datetime':
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = getStrAsDateTime(FormFields("%s"),FormFields("%s_h"),FormFields("%s_mi"),%d)\n' % (afield.Name, afield.Name, afield.Name, afield.Name, afield.NoPastDate)
            elif afield.Type == 'bool':
                ret = ret + """
if FormFields("%s")<>"" then 
   rs("%s") = "True"
else
   rs("%s") = "False"
end if
""" % (afield.Name, afield.Name, afield.Name, )
            elif afield.Type in ['dict', ]:
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = Left(CStr(FormFields("%s")),%d)\n' % (afield.Name, afield.Name, afield.SizeAsNumber)
            elif afield.Type in ['dict int', ]:
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = CStr(FormFields("%s"))\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict':
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + '         rs("%s") = CStr(FormFields("%s"))\n' % (afield.Name, afield.Name)
            elif afield.Type == 'external dict multiple':
                ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                ret = ret + """         rs("%s") = CStr(FormFields("%s")) ' $$MULTIPLE\n""" % (afield.Name, afield.Name)
            elif afield.Type == 'text':
                ret = ret + '         rs("%s") = FormFields("%s")\n' % (afield.Name, afield.Name)
                if afield.TypeDescription == 'Arkusz':
                    ret = ret + '         rs("%s_Src") = FormFields("%s")\n' % (afield.Name, afield.Name)
            elif afield.Type == 'integer':
                if afield.TypeDescription != 'Auto increment':
                    ret = ret + '         rsOldValues.Add "%s",rs("%s").Value\n' % (afield.Name, afield.Name, )
                    ret = ret + '         if IsNumeric(FormFields("%s")) then rs("%s") = FormFields("%s")\n' % (afield.Name, afield.Name, afield.Name)
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            if acheckexists:
                ret = ret + '      end if\n'
        i = i + 1
    return ret, i


#**********************************************************************************
def ProcessFieldValueChange(aeventsrc):
    ret = ''
    for afield in aeventsrc.SQLTable.FieldsByTabID:
        eobj = aeventsrc.GetFieldEventsObj(afield.Name)
        if not eobj:
            continue
        if afield.Name[:1] != '_' and afield.IsInteractive:
            w = 0
            if afield.Type == 'string':
                w = 1
            elif afield.Type in ['numeric', 'money', 'float']:
                if afield.TypeDescription != 'Auto increment':
                    w = 1
            elif afield.Type == 'date':
                w = 1
            elif afield.Type == 'datetime':
                w = 1
            elif afield.Type == 'bool':
                w = 0
            elif afield.Type in ['dict', ]:
                w = 1
            elif afield.Type in ['dict int', ]:
                w = 1
            elif afield.Type in ['external dict', 'external dict multiple']:
                w = 1
            elif afield.Type == 'text':
                w = 0
            elif afield.Type == 'integer':
                if afield.TypeDescription != 'Auto increment':
                    w = 1
            if w:
                ret = ret + 'afieldvalue_old=CStr(rsOldValues("%s"))\n' % (afield.Name, )
                ret = ret + 'afieldvalue_new=CStr(rs("%s"))\n' % (afield.Name, )
                ret = ret + 'afieldvalue_olddone="*OLD*"\n'
                ret = ret + 'afieldvalue_newdone="*NEW*"\n'
                ret = ret + 'if afieldvalue_old<>afieldvalue_new then\n'
                ret = ret + '   afieldvalue_new_copy=afieldvalue_new\n'
                ret = ret + '   do\n'
                ret = ret + '      wf=0\n'
                while eobj:
                    if eobj.EventKind.EventName == 'ASPSourceOnValueChange':
                        se = aeventsrc.GetFieldEventText(eobj)
                        if se:
                            ret = ret + '''
      if (afieldvalue_old="%s") and (afieldvalue_new="%s") and (afieldvalue_olddone<>afieldvalue_old) and (afieldvalue_newdone<>afieldvalue_new) then
         afieldvalue_new_copy2=afieldvalue_new
         afieldvalue_olddone=afieldvalue_old
         afieldvalue_newdone=afieldvalue_new
%s
         if afieldvalue_new_copy2<>afieldvalue_new then
            afieldvalue_old=afieldvalue_new_copy2
            wf=1
         end if
      end if
''' % (eobj.EventFromValue, eobj.EventToValue, se)
                    eobj.Next()
                ret = ret + '   loop while wf=1\n'
                ret = ret + '   if afieldvalue_new_copy<>afieldvalue_new then\n'
                ret = ret + '      rs("%s")=afieldvalue_new\n' % (afield.Name, )
                ret = ret + '      rs.Update\n'
                ret = ret + '   end if\n'
                ret = ret + 'end if\n'
    return ret


#**********************************************************************************
def GetFieldPickerText(atable, afieldname, apicker):
    ret = ''

    return ret


#**********************************************************************************
def SQLTableGetAddUpdateASP(atable, btable=None, apostupdatetext='', aeventsrc=None, asecurity=None, apluginsources=None):
    woiddictref, wchapterid = 0, 0
    ret = ''
    if asecurity is not None:
        ret = ret + """
   if CheckUserAccess("%s")=0 then 'SourceTable - AccessLevelEdit
      Response.Write "<h1><font color='red'>Brak wymaganych uprawnień</font></h1>"
      Response.End
   end if
""" % (asecurity.AccessLevelEdit, )
    ascript_ASPSourceShowAfter = ''
    dautocompletefields = {}
    lvalidations = []
    sTableElementHTMLName = 'elementFormTable_%s' % (atable.NameSQLID, )
    for afield in atable.FieldsByTabID:
        afieldnamelower = afield.Name.lower()
        if afieldnamelower == '_oiddictref':
            woiddictref = 1
        if afieldnamelower == '_chapterid':
            wchapterid = 1
    ret = ret + """
%>
<!-- #include file="../../../inc/md5.inc" -->
<!-- #include file="../../../inc/jtcalculator.inc" -->
<%
Set Form = New EnhancedFormClass
Set FormFields = Form.GetFormCollection()

if Request.QueryString("ioid")<>"" then
   aoid=Request.QueryString("ioid")
else
   aoid="-1"
end if
if Request.QueryString("boid")<>"" then
   boid=Request.QueryString("boid")
else    
   boid="-1"
end if
if Request.QueryString("aoidref")<>"" then
   aoidref=Request.QueryString("aoidref")
elseif FormFields("_aoidref")<>"" then
   aoidref=FormFields("_aoidref")
else
   aoidref="-1"
end if
if Request.QueryString("areffield")<>"" then
   areffield=Request.QueryString("areffield")
elseif FormFields("_areffield")<>"" then
   areffield=FormFields("_areffield")
else
   areffield="-1"
end if
areffields=Split(areffield,",")
if Request.QueryString("wlocation")<>"" then
   wlocation=Request.QueryString("wlocation")
elseif FormFields("_wlocation")<>"" then
   wlocation=FormFields("_wlocation")
else
   wlocation=""                
end if
if Request.QueryString("chapterid")<>"" then
   achapterid=Request.QueryString("chapterid")
   achapterref="&chapterid=" & achapterid
elseif FormFields("_CHAPTERID")<>"" then
   achapterid=FormFields("_CHAPTERID")
   achapterref="&chapterid=" & achapterid
else
   achapterid=""
   achapterref=""
end if
if Request.QueryString("elementoid")<>"" then
   aelementoid=Request.QueryString("elementoid")
elseif FormFields("_elementoid")<>"" then
   aelementoid=FormFields("_elementoid")
else
   aelementoid=""
end if

schapterid=CStr(achapterid)
StepRepeat=0
StepRepeatMessage=""
StepRepeatStatus=0
dim StepReturnArrayName()
dim StepReturnArrayValue()
lenStepReturnArray=0

sub StepRepeatFormValue(aname,avalue)
   redim preserve StepReturnArrayName(lenStepReturnArray)
   redim preserve StepReturnArrayValue(lenStepReturnArray)
   StepReturnArrayName(lenStepReturnArray)=aname
   StepReturnArrayValue(lenStepReturnArray)=avalue
   lenStepReturnArray=lenStepReturnArray+1
end sub

if Request.QueryString("repeatmsg")<>"" then
   Response.Write "<h1><font color=red>" & Request.QueryString("repeatmsg") & "</font></h1>"
end if
"""
    ret = ret + """
If (FormFields("_OID")="") and (Request.QueryString("mode")="") then
%%>
<script language="javascript">
var page_leave_warning=true;
window.onbeforeunload = function() { 
  if (page_leave_warning) {
    return 'Jeśli zmiany w treści nie zostały zapisane, to zostaną one utracone...';
  }
}

function doFormSubmit2() {
   s=jQuery("#mydziala1").html();
   if (s=='0') {
      jQuery("#form1").attr("action","%s_au.asp?mode=submit<%%=achapterref%%>");
      document.getElementById("form1").submit();
   } else {
      s=jQuery("#mymessage1").html();
      if (s!="") {
         jQuery("#divmessage1").html(s);
      }
      document.getElementById("mybutton1").disabled=false;
      page_leave_warning=true;
      try {
         jQuery(window).scrollTop(0);
      } catch (e) {}
   }
}

function doFormSubmit() {
//   if (form1.validate(event?event:window.event)==false)
//      return false;
   if (!jQuery("#form1").validate().form()) {
      alert("Proszę poprawić oznaczone pola przed zapamiętaniem.");
      return false;
   }
""" % (atable.NameFileSubmit, )
    if aeventsrc and hasattr(aeventsrc, 'ASPClientBeforeSubmit'):
        ret = ret + "\n// *** ASPClientBeforeSubmit -- START ***\n"
        ret = ret + aeventsrc.ASPClientBeforeSubmit
        ret = ret + "\n// *** ASPClientBeforeSubmit -- END ***\n"
    ret = ret + """
   page_leave_warning=false;
   document.getElementById("mybutton1").disabled=true;
   jQuery.ajax({
      async:false,
      cache:false,
      data:jQuery("#form1").serialize(),
      dataType:"html",
      success:function(data, textStatus, XMLHttpRequest) {
         jQuery("#myiframe1").html(data);
      },
      type:"POST",
      url:"%s_au.asp?mode=check<%%=achapterref%%>"
   });
}

</script>
<script language="javascript">
try {
   var fpselectedelement=0;
   var fpselectedelementshow=0;
   var fpPopup = null;
   if (isIE()) {
      fpPopup = window.createPopup();
   }
   function showPopupFP(asrc,aelement,afieldelement,aapprox){
      if (isIE()) {
         var xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
         var sa=afieldelement.split(".");
         var sf2=sa[sa.length-1];
         var sf1=sa.slice(0,-1).join('.');
         var aurl="%s_svf.asp?table="+sf1+"&field="+sf2+"&where="+escape(asrc.value)+"&approx="+aapprox;
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
} catch(e) {
}
</script>
<script language="javascript">
function showPopupFPDict(aurl,sinput,sframe){
   aurl=aurl+"?isdialog=1&dialoginput="+sinput+"&dialogframe="+sframe;
   if (document.getElementById(sframe).src=="") {
      document.getElementById(sframe).src=aurl;
   } else {
      if (document.getElementById(sframe).style.display=="") {
         document.getElementById(sframe).style.display="none";
      } else {
         document.getElementById(sframe).style.display="";
      }
   }
}
function doDialogShow1(){
   aframename=document.getElementById("myDialogFrameName1").innerHTML;
   document.getElementById(aframename).style.display="";
}
function doDialogSubmit1(){
   ainputname=document.getElementById("myDialogFrameInput1").innerHTML;
   aframename=document.getElementById("myDialogFrameName1").innerHTML;
   aframeoid=document.getElementById("myDialogFrameOID1").innerHTML;
   aframevalue=document.getElementById("myDialogFrameValue1").innerHTML;
   document.getElementById(aframename).style.display="none";
   document.getElementById(ainputname).value=aframeoid;
   document.getElementById(ainputname+"Visible").value=aframevalue;
}

function doCorectTDEvenOddClass() {
   var arow;
   var asuffix;
   var i=0;
   var aelement=document.getElementById('%s');
   for (var r=0; r<aelement.rows.length; r++) {
      arow=aelement.rows[r];
      if ((arow.style.display!='none')&&(arow.cells.length==2)) {
         if ((i %% 2)==0) {
            asuffix='even'
         } else {
            asuffix='odd'
         };
         arow.cells[0].className='objectseditdatafieldname'+asuffix;
         arow.cells[1].className='objectseditdatafieldvalue'+asuffix;
         i=i+1;
      }
   }
}
</script>

<div id=myiframe1 style="display:none;"></div>
<span id=myevenntcallerdialog1 onclick='doDialogSubmit1();' style='display:none;'></span>
<span id=myevenntcallerdialogshow1 onclick='doDialogShow1();' style='display:none;'></span>
<span id=myDialogFrameName1 style='display:none;'></span>
<span id=myDialogFrameInput1 style='display:none;'></span>
<span id=myDialogFrameOID1 style='display:none;'></span>
<span id=myDialogFrameValue1 style='display:none;'></span>

<%%
""" % (atable.NameFileSubmit, atable.NameFile, sTableElementHTMLName)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowBefore'):
        ret = ret + "\n' *** ASPSourceShowBefore -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowBefore
        ret = ret + "\n' *** ASPSourceShowBefore -- END ***\n"
    ret = ret + """
   Response.Write "<font color='red' size='+3'><div id=divmessage1></div></font>"
   Response.Write "<div id=divform1><form %s name=form1 id=form1 METHOD='post' ACTION='%s_au.asp'>"
""" % (MHTMLSQLGenLib.GetFormValidateParms(), atable.NameFileSubmit)
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowFieldsBefore'):
        ret = ret + "\n' *** ASPSourceShowFieldsBefore -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowFieldsBefore
        ret = ret + "\n' *** ASPSourceShowFieldsBefore -- END ***\n"
    ret = ret + """
   Response.Write "<input type=hidden id='_OID' name='_OID' size=20 value='" & CStr(aoid) & "'>"
   Response.Write "<input type=hidden id='_BOID' name='_BOID' size=20 value='" & CStr(boid) & "'>"
   Response.Write "<input type=hidden id='_WLOCATION' name='_WLOCATION' size=20 value='" & CStr(wlocation) & "'>"
   Response.Write "<input type=hidden id='_AOIDREF' name='_AOIDREF' size=20 value='" & CStr(aoidref) & "'>"
   Response.Write "<input type=hidden id='_AREFFIELD' name='_AREFFIELD' size=20 value='" & CStr(areffield) & "'>"
   Response.Write "<input type=hidden id='_CHAPTERID' name='_CHAPTERID' size=20 value='" & CStr(achapterid) & "'>"
   Response.Write "<input type=hidden id='_elementoid' name='_elementoid' size=20 value='" & CStr(aelementoid) & "'>"
   Response.Write "<TABLE id='%s' cellpadding=4 cellspacing=0 width='100%%' border='0'>"
""" % (sTableElementHTMLName, )
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowFieldsStart'):
        ret = ret + "\n' *** ASPSourceShowFieldsStart -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowFieldsStart
        ret = ret + "\n' *** ASPSourceShowFieldsStart -- END ***\n"
    ret = ret + """
   saclread=""
   saclwrite=""             
   sacldelete=""
   if aoid<>"-1" then
"""
    fls = ['%s._OID' % atable.NameSQL, ]
    fls1 = []
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_':
            if afield.IsInteractive:
                fls.append(afield.NameSQL)
            else:
                fls1.append(afield.NameSQL)
    fls.extend(fls1)
    if btable is not None:
        fls.append('%s._Dotyczy' % atable.NameSQL)
    try:
        sf = string.join(fls, ',')
    except:
        print atable.NameSQL
        print str(fls)
    # print 'sf: ',sf
    abeforesubmit = ''
    sfsecadd = ''
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        sfsecadd = '%s._ACLRead,%s._ACLWrite,%s._ACLDelete,' % (atable.NameSQL, atable.NameSQL, atable.NameSQL)
    if wchapterid:
        sfsecadd = sfsecadd + '%s._ChapterID,' % atable.NameSQL
    ret = ret + """
rs.Open "select %s,%s%s._DateTime from %s WHERE %s._OID='" & aoid & "'", cn
if rs.EOF or rs.BOF then
   Response.Write "<h1>Wybrana pozycja została usunięta bądź nie istnieje</h1>"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   cn.Close
   set rs=Nothing
   set cn=Nothing
   Response.End
end if
""" % (sf, sfsecadd, atable.NameSQL, atable.NameSQL, atable.NameSQL)
    if wchapterid:
        ret = ret + """
if (achapterid="") or (achapterid="-1") then
   schapterid=rs("_ChapterID")
end if          
"""
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
saclread=Bin2Hex(rs("_ACLRead"))
saclwrite=Bin2Hex(rs("_ACLWrite"))
sacldelete=Bin2Hex(rs("_ACLDelete"))
if CheckACLForRecord(%d,saclwrite,achapterid,"Edit")=0 then
   Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   cn.Close
   set rs=Nothing
   set cn=Nothing
   Response.End
end if
""" % (aeventsrc.CRM.OID, )    #atable.NameSQL,atable.NameSQL,atable.NameSQL,
    else:
        ret = ret + """
saclread=""
saclwrite=""
sacldelete=""
"""
    i = 1
    aTextField = 0
    aEditorScript = 0
    ahiddenfields = []
    aOnLoad1 = []
    lsheetfields = []
    alastgroup = ''
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if afield.Group != alastgroup:
                ret = ret + """
Response.Write "<TR id=""GROUP%s"" class=""ui-widget-header""><TD colspan=""2"">%s</TD></TR>"
""" % (afield.Name, afield.Group)
                alastgroup = afield.Group
#         afieldpreviewlink=atable.NameSQL+'.'+afield.Name
            afieldpreviewlink = '-'
            afieldautocomplete = 1
            if hasattr(afield, 'FieldValuePreviewLink') and afield.FieldValuePreviewLink:
                afieldpreviewlink = afield.FieldValuePreviewLink
                if afieldpreviewlink == '-':
                    afieldautocomplete = 0
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
                if afield.TypeDescription in ['HTML', 'Arkusz']:
                    #snclass='objectseditdatafieldnameleftaligneven'
                    snclass = ''
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
                if afield.TypeDescription in ['HTML', 'Arkusz']:
                    #snclass='objectseditdatafieldnameleftalignodd'
                    snclass = ''
            ret = ret + """
Response.Write "<TR id='ROW%s' VALIGN=top class=ui-widget-content>" 'objectseditrow
""" % (afield.Name, )
            if afield.ColorBackground:
                ascript_ASPSourceShowAfter = ascript_ASPSourceShowAfter + '''
   jQuery("#ROW%s td").attr("style","background:%s");
''' % (afield.Name, afield.ColorBackground, )

            if afield.Type in ['dict', 'dict int', 'external dict']:
                scolor = ''
                if afield.ColorSelectedValue:
                    scolor = '.attr("style","color:%s")' % (afield.ColorSelectedValue, )
                if 0:
                    ascript_ASPSourceShowAfter = ascript_ASPSourceShowAfter + '''
   jQuery("#%s option:selected").prependTo("#%s").attr("selected","1")%s;
''' % (afield.Name, afield.Name, scolor)
            if afield.Type == 'external dict multiple':
                pass    #$$ zmiana typu select na edytor multiple

            if afield.TypeDescription in ['HTML', 'Arkusz']:
                ret = ret + """
Response.Write "<td class='%s' colspan=2>%s:%s<br>"
""" % (snclass, afield.PrettyName, afield.DescriptionName)
            else:
                ret = ret + """
Response.Write "<td class=%s>%s:%s</td><td class=%s>" 'width=\'160px\' 
""" % (snclass, afield.PrettyName, afield.DescriptionName, svclass, )
            if afield.Type == 'string':
                ds = 2 + afield.SizeAsNumber
                if ds > 40:
                    ds = 40
                if afield.TypeDescription == 'Kolor':
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'" & Server.HTMLEncode(rs.Fields(%d).Value) & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                    ret = ret + 'Response.Write "<img src=\'/icormanager/images/icons/silk/icons/color_wheel.png\' style=\'cursor:pointer;\' onclick=\'showColorPicker(this,document.forms[""form1""].%s)\'>"\n' % (afield.Name, )
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
                else:
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=%d MAXLENGTH=%s value=\'" & Server.HTMLEncode(rs.Fields(%d).Value) & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    if afieldpreviewlink != '-':
                        ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                    if afieldautocomplete:
                        dautocompletefields[afield.Name] = 1
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type in ['numeric', 'float']:
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=18 MAXLENGTH=22 value=\'" & Server.HTMLEncode(rs.Fields(%d).Value) & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'money':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=18 MAXLENGTH=22 value=\'" & Server.HTMLEncode(rs.Fields(%d).Value) & "\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'date':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'datetime':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + '''
if Year(rs.Fields(%d).Value)=1900 then
   sdv1=""
else
   sdv1="" & Year(rs.Fields(%d).Value) & "/" & Month(rs.Fields(%d).Value) & "/" & Day(rs.Fields(%d).Value)
end if
''' % (i, i, i, i)
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'" & sdv1 & "\' %s>"\n' % (afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),15\n' % (afield.Name, afield.Name, i, i)
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(rs.Fields(%d).Value),Minute(rs.Fields(%d).Value),1\n' % (afield.Name, afield.Name, i, i)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
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
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + """
sd=rs.Fields(%d).Value
wsd=0
Response.Write "<SELECT id='%s' name='%s'>"
""" % (i, afield.Name, afield.Name, )
                if not afield.IsObligatory:
                    ret = ret + """
   if sd="" then
      sds="SELECTED "
      wsd=1
   else
      sds=""                  
   end if
   Response.Write "<OPTION " & sds & "value=''></OPTION>"
"""
                wproc = 0
                if len(afield.DictValuesParents.keys()):
                    wproc = 1
                    ret = ret + """
Response.Write "<optgroup label='Następny krok:'>"
"""
                for akey, avalue in afield.DictValues:
                    lp = afield.DictValuesParents.get(akey, None)
                    if wproc:
                        sw = 'sd=""'
                    else:
                        sw = '1=1'
                    if lp is not None:
                        sw = ''
                        for slp in lp:
                            if sw:
                                sw = sw + ' or '
                            sw = sw + 'sd="%s"' % (slp)
                    ret = ret + """
   if sd="%s" then
      sds="SELECTED "
      wsd=1
   else
      sds=""
   end if
   if sds<>"" or %s then
      Response.Write "<OPTION " & sds & "value='%s'>%s</OPTION>"
   end if
""" % (akey, sw, akey, avalue)
                ret = ret + """
if (wsd=0) and (sd<>"") then
   Response.Write "<OPTION SELECTED value='" & sd & "'>" & sd & "</OPTION>"
end if                      
"""
                if wproc:
                    if not afield.DisableDictShowAllValues:
                        ret = ret + """
Response.Write "<optgroup label='Wszystkie możliwości:'>"
"""
                        for akey, avalue in afield.DictValues:
                            ret = ret + """
      Response.Write "<OPTION value='%s'>%s</OPTION>"
""" % (akey, avalue)
                ret = ret + """
Response.Write "</SELECT>"
"""
                if afield.OID >= 0:
                    ret = ret + 'Response.Write "&nbsp;<a href=\'dictgraphs/%d_%d_%s.png\' target=\'_new\'><img valign=middle vspace=0 border=0 src=\'/icormanager/images/icons/silk/icons/share.png\' alt=\'Diagram przejść stanów\'></a>"\n' % (afield.CID, afield.OID, afield.Name, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'external dict':
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelection(afield, aissinglevalue=1, aisdialog=1)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'external dict multiple':
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelectionMultiple(afield, aissinglevalue=1, aisdialog=1)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'text':
                if afield.TypeDescription == 'HTML':
                    ahref = '%s_gfv.asp?ioid=<%%=aoid%%>&afield=%s' % (atable.NameFile, afield.Name)
                    aEditorScript = aEditorScript + 1
                    if aEditorScript == 1:
                        ackjssrc = FCKMain.GetScriptText()
                        ret = ret + 'response.write "%s"\n' % (ackjssrc, )
                    ret = ret + 'Response.Write "<textarea spellcheck=\'false\' style=\'display:none;\' id=\'%s\' name=\'%s\'></textarea>"\n' % (afield.Name, afield.Name, )
                    ret = ret + """
%>
"""
                    ret = ret + FCKMain.GetEditorText(aid=afield.Name, aheight="480px", ahref=ahref)
                    ret = ret + MHTMLSQLGenLib.GetEditorTemplatesAddOns(afield)
                    ret = ret + """
<%
"""
                elif afield.TypeDescription == 'HTML_old':
                    ahref = '%s_gfv.asp?ioid=<%%=aoid%%>&afield=%s' % (atable.NameFile, afield.Name)
                    aEditorScript = aEditorScript + 1
                    ahiddenfields.append('if(document.frames(""%sVisible"").document.body.innerText!=""""){document.getElementById(""%s"").value=document.frames(""%sVisible"").document.body.innerHTML}else{document.getElementById(""%s"").value=""""};' % (afield.Name, afield.Name, afield.Name, afield.Name))
                    #               ret=ret+'</table><table width="100%%"><tr><td width="100%%" colspan=3 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>'%(self.FieldNameAsDisplayed,)
                    ret = ret + """
%>"""
                    ret = ret + GetEditorText(aid=afield.Name, aheight="480px", ahref=ahref)
                    ret = ret + '<input type=hidden id=%s name=%s value=""></input>' % (afield.Name, afield.Name)
                    #               self.file.write('</td></tr></table><table width="100%">')
                    ret = ret + """
<%"""
#               ret=ret+'Response.Write "<b>HTML ADD!</b><textarea id=\'%s\' name=\'%s\' cols=32 rows=6 %s></textarea>"\n'%(afield.Name,afield.Name,MHTMLSQLGenLib.GetFieldValidationText(afield))
#               ret=ret+'Response.Write "<b>HTML EDITOR! EDIT</b><textarea id=\'%s\' name=\'%s\' cols=32 rows=6 %s>" & rs.Fields(%d).Value & "</textarea>"\n'%(afield.Name,afield.Name,MHTMLSQLGenLib.GetFieldValidationText(afield),i)
                elif afield.TypeDescription == 'Arkusz':
                    lsheetfields.append(afield)
                    ahref = '%s_gfv.asp?ioid=<%%=aoid%%>&afield=%s_Src' % (atable.NameFile, afield.Name)
                    aEditorScript = aEditorScript + 1
                    ahiddenfields.append('document.getElementById(""%s"").value=%sVisible.HTMLData;' % (afield.Name, afield.Name))
                    ret = ret + """
aarkuszid=""
Set rs1 = Server.CreateObject("ADODB.Recordset")
rs1.ActiveConnection = cn
rs1.CursorType = adOpenKeyset
rs1.LockType = adLockOptimistic
rs1.Source = "select _OID,NazwaTabeli,NazwaPola,OIDArkusza,NazwaArkusza,StanPrzeliczenia from TMP_SHEETINFO_0 WHERE (OIDArkusza='" & aoid & "') AND (NazwaPola='%s')"
rs1.Open
if not rs1.EOF then
   aarkuszid=rs1("NazwaArkusza")
end if
if rs1.State<>adStateClosed then
   rs1.Close
end if
set rs1=Nothing
Response.Write "<div align=left width='100%%' style='background:buttonface;'>&nbsp;&nbsp;ID Arkusza:&nbsp;"
Response.Write "<input type='text' id='%s_ID' name='%s_ID' REQUIRED='1' FILTER='[0-9_a-zA-Z]' REGEXP='^[A-Za-z][0-9_a-zA-Z]*$' value='" & aarkuszid & "'></input></div>"
%%>""" % (afield.Name, afield.Name, afield.Name,
                    )
                    atext, aonloadtext, aOnBeforeLoadText, aOnAfterLoadText = GetWorksheetText(aid=afield.Name, aheight="480px", ahref=ahref)
                    aOnLoad1.append([aonloadtext, aOnBeforeLoadText, aOnAfterLoadText])
                    ret = ret + atext
                    ret = ret + '<input type=hidden id=%s name=%s value=""></input>' % (afield.Name, afield.Name)
                    ret = ret + """
<%"""
                else:
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    aTextField = aTextField + 1
                    ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=%s rows=%s %s >" & Server.HTMLEncode(rs.Fields(%d).Value) & "</textarea>"\n' % (afield.Name, afield.Name, afield.TextCols, afield.TextRows, MHTMLSQLGenLib.GetFieldValidationText(afield), i)
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    ret = ret + 'Response.Write "&nbsp;<img onclick=\'javascript:processSpellCommand(document.getElementById(""%s""),this);\' alt=\'Sprawdź pisownię\' src=\'/icormanager/images/toolbar/spellcheck.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'>"\n' % (
                        afield.Name, )
#               ret=ret+'Response.Write "<table><tr><td>"\n'
#               ret=ret+'Response.Write "<textarea id=\'%s\' name=\'%s\' wrap=\'%s\' cols=%s rows=%s %s >" & rs.Fields(%d).Value & "</textarea>"\n'%(afield.Name,afield.Name,afield.TextNoWrap,afield.TextCols,afield.TextRows,MHTMLSQLGenLib.GetFieldValidationText(afield),i)
#               ret=ret+'Response.Write "</td><td align=left valign=top>"\n'
#               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""pl"")\' alt=\'polski\' src=\'/icormanager/images/flags/POLAND.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'><br>"\n'%(afield.Name,)
#               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""en"")\' alt=\'angielski\' src=\'/icormanager/images/flags/UNITEDKINGDOM.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'><br>"\n'%(afield.Name,)
#               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""de"")\' alt=\'niemiecki\' src=\'/icormanager/images/flags/GERMANY.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'>"\n'%(afield.Name,)
#               ret=ret+'Response.Write "</td></tr></table>"\n'
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'integer':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=14 MAXLENGTH=22 value=\'" & Server.HTMLEncode(rs.Fields(%d).Value) & "\' %s>"\n' % (afield.Name, afield.Name, i, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            ret = ret + 'Response.Write "</td></tr>"\n'
            i = i + 1
    if aEditorScript > 0:
        ret = ret + """
%>
"""
        #      ret=ret+GetScriptText()
        ret = ret + """
<%
"""
        abeforesubmit = string.join(ahiddenfields, '')
    ret = ret + """
else
"""

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
   if CheckACLForRecord(%d,"",achapterid,"Edit")=0 then
      Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
      if rs.State<>adStateClosed then
         rs.Close
      end if
      cn.Close
      set rs=Nothing
      set cn=Nothing
      Response.End
   end if
""" % (aeventsrc.CRM.OID, )
    i = 1
    aTextField = 0
    aEditorScript = 0
    ahiddenfields = []
    aOnLoad2 = []
    alastgroup = ''
    for afield in atable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsInteractive:
            if afield.Group != alastgroup:
                ret = ret + """
Response.Write "<TR id=""GROUP%s"" class=""ui-widget-header""><TD colspan=""2"">%s</TD></TR>"
""" % (afield.Name, afield.Group)
                alastgroup = afield.Group
#         afieldpreviewlink=atable.NameSQL+'.'+afield.Name
            afieldpreviewlink = '-'
            afieldautocomplete = 1
            if hasattr(afield, 'FieldValuePreviewLink') and afield.FieldValuePreviewLink:
                afieldpreviewlink = afield.FieldValuePreviewLink
                if afieldpreviewlink == '-':
                    afieldautocomplete = 0
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
                if afield.TypeDescription in ['HTML', 'Arkusz']:
                    #snclass='objectseditdatafieldnameleftaligneven'
                    snclass = ''
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
                if afield.TypeDescription in ['HTML', 'Arkusz']:
                    #snclass='objectseditdatafieldnameleftalignodd'
                    snclass = ''
            ret = ret + """
Response.Write "<TR id='ROW%s' VALIGN=top class=ui-widget-content>"
""" % (afield.Name, )
            if afield.TypeDescription in ['HTML', 'Arkusz']:
                ret = ret + """
Response.Write "<td class='%s' colspan=2>%s:%s<br>"
""" % (snclass, afield.PrettyName, afield.DescriptionName)
            else:
                ret = ret + """
Response.Write "<td class=%s>%s:%s</td><td class=%s>" 'width=\'160px\' 
""" % (snclass, afield.PrettyName, afield.DescriptionName, svclass, )
            if afield.Type == 'string':
                ds = 2 + afield.SizeAsNumber
                if ds > 40:
                    ds = 40
                if afield.TypeDescription == 'Kolor':
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    ret = ret + 'Response.Write "<input class=simple_color type=text id=\'%s\' name=\'%s\' size=%d MAXLENGTH=%s value=\'%s\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, afield.DefaultEntry, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                    ret = ret + 'Response.Write "<img src=\'/icormanager/images/icons/silk/icons/color_wheel.png\' style=\'cursor:pointer;\' onclick=\'showColorPicker(this,document.forms[""form1""].%s)\'>"\n' % (afield.Name, )
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
                else:
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=%d MAXLENGTH=%s value=\'%s\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, ds, afield.Size, afield.DefaultEntry, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    if afieldpreviewlink != '-':
                        ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                    if afieldautocomplete:
                        dautocompletefields[afield.Name] = 1
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type in ['numeric', 'float']:
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=18 MAXLENGTH=22 value=\'%s\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, afield.DefaultEntry, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'money':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=18 MAXLENGTH=22 value=\'%s\' %s>&nbsp;%s"\n' % (afield.Name, afield.Name, afield.DefaultEntry, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.TypeCaption)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'date':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                adef = afield.DefaultEntry
                if not adef:
                    adef = '" & year(now) & "/" & month(now) & "/" & day(now) & "'
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'%s\' %s>"\n' % (afield.Name, afield.Name, adef, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'datetime':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                adef = afield.DefaultEntry
                if not adef:
                    adef = '" & year(now) & "/" & month(now) & "/" & day(now) & "'
                ret = ret + 'Response.Write "&nbsp;rrrr/mm/dd:<input class=datepicker type=text id=\'%s\' name=\'%s\' size=10 maxlength=10 value=\'%s\' %s>"\n' % (afield.Name, afield.Name, adef, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                if afield.TypeDescription == 'Data i czas kwadrans':
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),15\n' % (afield.Name, afield.Name, )
                else:
                    ret = ret + 'writeTimeSelect "%s_h","%s_mi",Hour(Now),Minute(Now),1\n' % (afield.Name, afield.Name, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'bool':
                ret = ret + 'Response.Write "<input class=checkradio type=checkbox id=\'%s\' name=\'%s\'>"\n' % (afield.Name, afield.Name)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type in ['dict', 'dict int']:
                ret = ret + """
Response.Write "<SELECT id='%s' name='%s'>"
""" % (afield.Name, afield.Name, )
                if not afield.IsObligatory:
                    ret = ret + """
      Response.Write "<OPTION value=''></OPTION>"
"""
                wproc = 0
                if len(afield.DictValuesParents.keys()):
                    wproc = 1
                    ret = ret + """
Response.Write "<optgroup label='Następny krok:'>"
"""
                for akey, avalue in afield.DictValues:
                    lp = afield.DictValuesParents.get(akey, None)
                    sw = '1=1'
                    if lp is not None:
                        sw = '1=0'
                        for slp in lp:
                            if not slp:
                                sw = '1=1'
                                break
                    ret = ret + """
   sd="%s"
   sdv="%s"
   if %s then
      Response.Write "<OPTION value='" & sd & "'>" & sdv & "</OPTION>"
   end if
""" % (akey, avalue, sw)
                if wproc:
                    if not afield.DisableDictShowAllValues:
                        ret = ret + """
Response.Write "<optgroup label='Wszystkie możliwości:'>"
"""
                        for akey, avalue in afield.DictValues:
                            ret = ret + """
      Response.Write "<OPTION value='%s'>%s</OPTION>"
""" % (akey, avalue)
                ret = ret + """
Response.Write "</SELECT>"
"""
                if afield.OID >= 0:
                    ret = ret + 'Response.Write "&nbsp;<a href=\'dictgraphs/%d_%d_%s.png\' target=\'_new\'><img valign=middle vspace=0 border=0 src=\'/icormanager/images/icons/silk/icons/share.png\' alt=\'Diagram przejść stanów\'></a>"\n' % (afield.CID, afield.OID, afield.Name, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'external dict':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelection(afield, aissinglevalue=1, aisdialog=1)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'external dict multiple':
                #$$
                ret = ret + MHTMLSQLGenLib.ShowExternalDictSelectionMultiple(afield, aissinglevalue=1, aisdialog=1)
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'text':
                if afield.TypeDescription == 'HTML':
                    ahref = ''
                    aEditorScript = aEditorScript + 1
                    if aEditorScript == 1:
                        ackjssrc = FCKMain.GetScriptText()
                        ret = ret + 'response.write "%s"\n' % (ackjssrc, )
                    ret = ret + 'Response.Write "<textarea style=\'display:none;\' id=\'%s\' name=\'%s\' spellcheck=\'false\'></textarea>"\n' % (afield.Name, afield.Name, )
                    ret = ret + """
%>
"""
                    adefaulttext = ''
                    for akey, avalue in afield.DictValues:
                        if akey[:1] == '@':
                            adefaulttext = avalue
                    ret = ret + FCKMain.GetEditorText(aid=afield.Name, aheight="480px", ahref=ahref, adefaulttext=adefaulttext)
                    ret = ret + MHTMLSQLGenLib.GetEditorTemplatesAddOns(afield)
                    ret = ret + """
<%
"""
                elif afield.TypeDescription == 'HTML_old':
                    #               ahref='%s_gfv.asp?ioid=" & aoid & "&afield=%s'%(atable.NameFile,afield.Name)
                    ahref = ''
                    aEditorScript = aEditorScript + 1
                    ahiddenfields.append('if(document.frames(""%sVisible"").document.body.innerText!=""""){document.getElementById(""%s"").value=document.frames(""%sVisible"").document.body.innerHTML}else{document.getElementById(""%s"").value=""""};' % (afield.Name, afield.Name, afield.Name, afield.Name))
                    #               ret=ret+'</table><table width="100%%"><tr><td width="100%%" colspan=3 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>'%(self.FieldNameAsDisplayed,)
                    ret = ret + """
%>
"""
                    ret = ret + GetEditorText(aid=afield.Name, aheight="480px", ahref=ahref)
                    ret = ret + '<input type=hidden id=%s name=%s value=""></input>' % (afield.Name, afield.Name)
                    #               self.file.write('</td></tr></table><table width="100%">')
                    ret = ret + """
<%
"""

#               ret=ret+'Response.Write "<b>HTML ADD!</b><textarea id=\'%s\' name=\'%s\' cols=32 rows=6 %s></textarea>"\n'%(afield.Name,afield.Name,MHTMLSQLGenLib.GetFieldValidationText(afield))
                elif afield.TypeDescription == 'Arkusz':
                    ahref = ''
                    aEditorScript = aEditorScript + 1
                    ahiddenfields.append('document.getElementById(""%s"").value=%sVisible.HTMLData;' % (afield.Name, afield.Name))
                    ret = ret + """
Response.Write "<div align=left width='100%%' style='background:buttonface;'>&nbsp;&nbsp;ID Arkusza:&nbsp;"
Response.Write "<input type='text' id='%s_ID' name='%s_ID' REQUIRED='1' FILTER='[0-9_a-zA-Z]' REGEXP='^[A-Za-z][0-9_a-zA-Z]*$' value=''></input></div>"
%%>""" % (afield.Name, afield.Name, )
                    atext, aonloadtext, aOnBeforeLoadText, aOnAfterLoadText = GetWorksheetText(aid=afield.Name, aheight="480px", ahref=ahref)
                    aOnLoad2.append([aonloadtext, aOnBeforeLoadText, aOnAfterLoadText])
                    ret = ret + atext
                    ret = ret + '<input type=hidden id=%s name=%s value=""></input>' % (afield.Name, afield.Name)
                    ret = ret + """
<%"""
                else:
                    ##               ret=ret+'Response.Write "<textarea id=\'%s\' name=\'%s\' wrap=\'%s\' cols=%s rows=%s %s></textarea>"\n'%(afield.Name,afield.Name,afield.TextNoWrap,afield.TextCols,afield.TextRows,MHTMLSQLGenLib.GetFieldValidationText(afield))
                    ##               ret=ret+'Response.Write "&nbsp;<img onclick=\'checkSpelling(document.getElementById(""%s""))\' alt=\'Sprawdź pisownię\' src=\'/icormanager/images/toolbar/spellcheck.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'>"\n'%(afield.Name,)
                    #               ret=ret+'Response.Write "<table><tr><td>"\n'
                    #               ret=ret+'Response.Write "<textarea id=\'%s\' name=\'%s\' wrap=\'%s\' cols=%s rows=%s %s></textarea>"\n'%(afield.Name,afield.Name,afield.TextNoWrap,afield.TextCols,afield.TextRows,MHTMLSQLGenLib.GetFieldValidationText(afield))
                    #               ret=ret+'Response.Write "</td><td align=left valign=top>"\n'
                    #               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""pl"")\' alt=\'polski\' src=\'/icormanager/images/flags/POLAND.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'><br>"\n'%(afield.Name,)
                    #               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""en"")\' alt=\'angielski\' src=\'/icormanager/images/flags/UNITEDKINGDOM.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'><br>"\n'%(afield.Name,)
                    #               ret=ret+'Response.Write "<img onclick=\'checkSpelling(document.getElementById(""%s""),""de"")\' alt=\'niemiecki\' src=\'/icormanager/images/flags/GERMANY.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'>"\n'%(afield.Name,)
                    #               ret=ret+'Response.Write "</td></tr></table>"\n'
                    lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                    aTextField = aTextField + 1
                    ret = ret + 'Response.Write "<textarea id=\'%s\' name=\'%s\' spellcheck=\'false\' cols=%s rows=%s %s>%s</textarea>"\n' % (afield.Name, afield.Name, afield.TextCols, afield.TextRows, MHTMLSQLGenLib.GetFieldValidationText(afield), afield.DefaultEntry.replace('"', '""'))
                    ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                    ret = ret + 'Response.Write "&nbsp;<img onclick=\'javascript:processSpellCommand(document.getElementById(""%s""),this);\' alt=\'Sprawdź pisownię\' src=\'/icormanager/images/toolbar/spellcheck.png\' style=\'cursor:pointer;vertical-align:top;\' onmousedown=\'this.className=""tbButtonMouseOverDown"";\' class=\'tbButton\' onmouseover=\'this.className=""tbButtonMouseOverUp"";\' onmouseup=\'this.className=""tbButtonMouseOverUp"";\' onmouseout=\'this.className=""tbButton"";\'>"\n' % (
                        afield.Name, )
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            elif afield.Type == 'integer':
                lvalidations.extend(MHTMLSQLGenLib.GetFieldValidationScript(afield, afield.Name))
                ret = ret + 'Response.Write "<input type=text id=\'%s\' name=\'%s\' class=\'autocomplete\' size=14 MAXLENGTH=22 value=\'%s\' %s>"\n' % (afield.Name, afield.Name, afield.DefaultEntry, MHTMLSQLGenLib.GetFieldValidationText(afield))
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue
                ret = ret + 'Response.Write "&nbsp;<script type=\'text/javascript\'>calc_setup(\'form1\',\'%s\');</script>"\n' % (afield.Name, )
                if afieldpreviewlink != '-':
                    ret = ret + 'Response.Write "&nbsp;<IMG alt=\'podgląd wartości\' id=\'fieldpreviewdiv%d\' src=\'/icormanager/images/icon_preview.png\' style=\'cursor:pointer;\' onclick=\'javascript:showPopupFP(%s,fieldpreviewdiv%d,""%s"",0);\'>"\n' % (i, afield.Name, i, afieldpreviewlink)
                if afieldautocomplete:
                    dautocompletefields[afield.Name] = 1
                ret = ret + 'Response.Write "%s"\n' % afield.DescriptionValue2
            else:
                print 'Nieznany typ dla pola:', afield.Name, ' - ', afield.Type
            ret = ret + 'Response.Write "</td></tr>"\n'
            i = i + 1
    if aEditorScript > 0:
        ret = ret + """
%>
"""

        #      ret=ret+GetScriptText()
        ret = ret + """
<%
"""
        abeforesubmit = string.join(ahiddenfields, '')
    ret = ret + """
   end if          
"""
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowFields'):
        ret = ret + "\n' *** ASPSourceShowFields -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowFields
        ret = ret + "\n' *** ASPSourceShowFields -- END ***\n"
    ret = ret + """
   Response.Write("</TABLE>")
"""
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowFieldsAfter'):
        ret = ret + "\n' *** ASPSourceShowFieldsAfter -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowFieldsAfter
        ret = ret + "\n' *** ASPSourceShowFieldsAfter -- END ***\n"

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        apoid = aeventsrc.CRM.OID
        stoid = aeventsrc.OID
        ret = ret + """
%%>
<br>
<caption>Prawa dostępu do odczytu dla tego rekordu:</caption>
<div style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:200px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>
<%%
apoid=%d
stoid="%d"
ret=Proc_ExecuteMethodRetS(Application("DEFAULT_EXECUTOR"),"CLASSES\Library\DBBase\DMSWorkflow\Prototyp\Projekt\WWWGetUserProjectACLStrings", stoid, apoid, "Read:" & saclread & ":" & schapterid, "")
slist1=split(ret,SPLIT_CHAR_PARAM)
for ii1=lbound(slist1) to ubound(slist1)
   slist2=split(slist1(ii1),SPLIT_CHAR_VALUE)
   schecked=""
   if (slist2(2)="1") or (aoid="-1") then
      schecked="CHECKED "
   end if
   Response.Write "<input class=checkradio type=checkbox id='_ACL_View_" & CStr(ii1) & "' name='_ACL_View_" & CStr(ii1) & "' value='" & slist2(1) & "' tabindex=10 " & schecked & "><span class='checkdescription'>" & slist2(0) & "</span><br>"
next
Response.Write "<input type=hidden id='_ACL_View_Max' name='_ACL_View_Max' value='" & cstr(ii1) & "'>"
%%>
</div>
<br>
<caption>Prawa dostępu do zapisu/modyfikacji dla tego rekordu:</caption>
<div style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:200px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>
<%%
ret=Proc_ExecuteMethodRetS(Application("DEFAULT_EXECUTOR"),"CLASSES\Library\DBBase\DMSWorkflow\Prototyp\Projekt\WWWGetUserProjectACLStrings", stoid, apoid, "Edit:" & saclwrite & ":" & schapterid, "")
slist1=split(ret,SPLIT_CHAR_PARAM)
for ii1=lbound(slist1) to ubound(slist1)
   slist2=split(slist1(ii1),SPLIT_CHAR_VALUE)
   schecked=""
   if (slist2(2)="1") or (aoid="-1") then
      schecked="CHECKED "
   end if
   Response.Write "<input class=checkradio type=checkbox id='_ACL_Edit_" & CStr(ii1) & "' name='_ACL_Edit_" & CStr(ii1) & "' value='" & slist2(1) & "' tabindex=10 " & schecked & "><span class='checkdescription'>" & slist2(0) & "</span><br>"
next
Response.Write "<input type=hidden id='_ACL_Edit_Max' name='_ACL_Edit_Max' value='" & cstr(ii1) & "'>"
%%>
</div>
<br>
<caption>Prawa dostępu do usunięcia dla tego rekordu:</caption>
<div style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:200px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>
<%%
ret=Proc_ExecuteMethodRetS(Application("DEFAULT_EXECUTOR"),"CLASSES\Library\DBBase\DMSWorkflow\Prototyp\Projekt\WWWGetUserProjectACLStrings", stoid, apoid, "Delete:" & sacldelete & ":" & schapterid, "")
slist1=split(ret,SPLIT_CHAR_PARAM)
for ii1=lbound(slist1) to ubound(slist1)
   slist2=split(slist1(ii1),SPLIT_CHAR_VALUE)
   schecked=""
   if (slist2(2)="1") or (aoid="-1") then
      schecked="CHECKED "
   end if
   Response.Write "<input class=checkradio type=checkbox id='_ACL_Delete_" & CStr(ii1) & "' name='_ACL_Delete_" & CStr(ii1) & "' value='" & slist2(1) & "' tabindex=10 " & schecked & "><span class='checkdescription'>" & slist2(0) & "</span><br>"
next
Response.Write "<input type=hidden id='_ACL_Delete_Max' name='_ACL_Delete_Max' value='" & cstr(ii1) & "'>"
%%>
</div>
<%%
""" % (apoid, stoid)

    ret = ret + """
   Response.Write "<br></form></div>"
"""

    if aeventsrc and aeventsrc.CRM.ProjectVars.has_key('aBeforeSubmitChapterContentInfo'):
        ret = ret + """
      if (achapterid<>"") and (achapterid<>"-1") then
%>
"""
        ret = ret + aeventsrc.CRM.ProjectVars['aBeforeSubmitChapterContentInfo']
        ret = ret + """
<%   
      end if
"""
    ret = ret + """
   Response.Write "<button class='fg-button-single ui-state-default ui-corner-all uihover' id=mybutton1 onclick='%sdoFormSubmit();'>Zapamiętaj</button>"

   if aoid<>"-1"  or aoidref<>"-1" then
      if wlocation<>"" then
         locref=wlocation & achapterref
      else          
         locref="%s_so.asp?ioid=" & aoid & achapterref
      end if
      Response.Write "<script language='javascript'>setButtonBackAction('" & locref & "');</script>"
      Response.Write "&nbsp;&nbsp;<button class='fg-button-single ui-state-default ui-corner-all uihover' id=mybutton2 onclick=""jscript:page_leave_warning=false;window.location='" & locref & "';"">Anuluj</button>"
   end if
   Response.Write "<span id=myevenntcaller1 onclick='doFormSubmit2();'></span>"
""" % (abeforesubmit, atable.NameFile,
       )

    if ascript_ASPSourceShowAfter:
        ret = ret + """
%%>
<script type='text/javascript'>
jQuery(function(){
%s
});
</script>
<%%
""" % (ascript_ASPSourceShowAfter, )

    lvalidations2 = []
    lvalidations.sort()
    for s in lvalidations:
        if not s in lvalidations2:
            lvalidations2.append(s)
    ret = ret + """
%%>
<script type='text/javascript'>
jQuery(function(){
   jQuery("#form1").validate();   
%s
});
</script>
<%%
""" % (''.join(lvalidations2), )

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceShowAfter'):
        ret = ret + "\n' *** ASPSourceShowAfter -- START ***\n"
        ret = ret + aeventsrc.ASPSourceShowAfter
        ret = ret + "\n' *** ASPSourceShowAfter -- END ***\n"

    if aOnLoad1 or aOnLoad2:
        ret = ret + """
if aoid<>"-1" then
%>
<!-- ONLOAD - START -->
"""
        for atext in aOnLoad1:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                ret = ret + '\n' + aonbefore + '\n'
        wvb = 0
        for atext in aOnLoad1:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
            if atext:
                print 'VBScript Table 1 text: ', atext
            if not wvb:
                ret = ret + """
<script language="vbscript">
<!--
Sub Window_onLoad()
"""
                wvb = 1
            ret = ret + '\n' + atext + '\n'
        if wvb:
            ret = ret + """
End Sub
-->
</script>
"""
        for atext in aOnLoad1:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                ret = ret + '\n' + aafter + '\n'
        ret = ret + """
<!-- ONLOAD - FINISH 1 -->
<%
else
%>
"""
        for atext in aOnLoad2:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                ret = ret + '\n' + aonbefore + '\n'
        wvb = 0
        for atext in aOnLoad2:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
            if atext:
                print 'VBScript Table 2 text: ', atext
            if not wvb:
                ret = ret + """
<script language="vbscript">
<!--
Sub Window_onLoad()
"""
                wvb = 1
            ret = ret + '\n' + atext + '\n'
        if wvb:
            ret = ret + """
End Sub
-->
</script>
"""
        for atext in aOnLoad2:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                ret = ret + '\n' + aafter + '\n'
        ret = ret + """
<!-- ONLOAD - FINISH 2 -->
<%
end if
"""

    ret = ret + MHTMLSQLGenLib.WriteTableFieldsDescription(atable)

    if dautocompletefields:
        lafields = []
        for safield in dautocompletefields.keys():
            lafields.append('"%s"' % (safield, ))
        ret = ret + '''
%%>
<script type="text/javascript">
function htmlDecode(str) {
  var entMap={'quot':34,'amp':38,'apos':39,'lt':60,'gt':62};
  return str.replace(/&([^;]+);/g,function(m,n) {
    var code;
    if (n.substr(0,1)=='#') {
      if (n.substr(1,1)=='x') {
        code=parseInt(n.substr(2),16);
      } else {
        code=parseInt(n.substr(1),10);
      }
    } else {
      code=entMap[n];
    }
    return (code===undefined||code===NaN)?'&'+n+';':String.fromCharCode(code);
  });
}
jQuery(function(){            
   linputs=[%s];
   for (i in linputs) {
      asid=linputs[i];
      jQuery("#"+asid).after("&nbsp;<img src='/icorimg/silk/zoom.png' style='cursor:pointer;' id='img"+asid+"'>");
      jQuery("#"+asid).autoComplete({
         ajax:"%s_gfv.asp?mode=ac&fname="+asid,
         ajaxCache:false,
         useCache:true,
         autoFill:false,
         delay:850,
         newList:false,
         onShow:function(e,ui) {
            jQuery(ui.ul).css('width',jQuery(this).outerWidth())
            jQuery(ui.ul).maxZIndex();
         },
         onLoad:function(e,ui) {
            for (i=0; i<ui.list.length; i++) {
               ui.list[i].value=htmlDecode(ui.list[i].value);
            }
            return ui.list;
         }
      });
      jQuery("#img"+asid).click(function(bsid){return function(){
         jQuery("#"+bsid).autoComplete('button-ajax', {}, "cache_"+bsid);
      }}(asid));
   }
});
</script>
<%%
''' % (','.join(lafields), atable.NameFile)

    ret = ret + """
elseif Request.QueryString("mode")="check" then 'CHECK
   Response.Clear
"""
    lufields, dufields, lnfields = [], {}, []
    for afield in atable.FieldsByTabID:
        if afield.IsUnique:
            lufields.append(afield.NameSQL)
            lnfields.append([afield.Name, afield.NameSQL])
            dufields[afield.Name] = afield
    if lufields:
        ret = ret + """
sp=""
"""
        for asfname, assname in lnfields:
            ret = ret + """
if sp<>"" then
   sp=sp & " or "
end if
if Trim(FormFields("%s"))<>"" then
   sp=sp & "(%s='" & Trim(FormFields("%s")) & "')"
end if
""" % (asfname, assname, asfname)
        ret = ret + """
if sp<>"" then
   if (FormFields("_OID")<>"-1") and (FormFields("_OID")<>"") then
      sp="(" & sp & ") and %s._OID<>'" & FormFields("_OID") & "'"
   end if
   
   Set rs1 = Server.CreateObject("ADODB.Recordset")
   rs1.ActiveConnection = cn
   rs1.CursorType = adOpenKeyset
   rs1.LockType = adLockOptimistic
   rs1.Source = "select TOP 1000 %s._OID,%s from %s where " & sp
   rs1.Open
   
   Do While Not rs1.EOF
""" % (atable.NameSQL, atable.NameSQL, string.join(lufields, ','), atable.NameSQL)
        for asfname, assname in lnfields:
            ret = ret + """
      if Ucase(Trim(rs1("%s")))=Ucase(Trim(FormFields("%s"))) then
         StepRepeat=1
         if StepRepeatMessage<>"" then
            StepRepeatMessage=StepRepeatMessage & ", "
         end if
         StepRepeatMessage=StepRepeatMessage & "W polu <i>%s</i> wpisano wartość, która już istnieje w bazie danych<br>"
      end if
""" % (asfname, asfname, dufields[asfname].PrettyName)
        ret = ret + """
      rs1.MoveNext
   Loop
   if rs1.State<>adStateClosed then
      rs1.Close
   end if
   Set rs1=Nothing
end if
"""
    for asheetfield in lsheetfields:
        ret = ret + """
'if StepRepeat=0 then
      Set rs_ih = Server.CreateObject("ADODB.Recordset")      
      rs_ih.ActiveConnection = cn
      rs_ih.CursorType = adOpenKeyset
      rs_ih.LockType = adLockOptimistic
      boid=FormFields("_OID")
      if boid="-1" then
        stv_warunek=""
      else
        stv_warunek=" and OIDArkusza<>'" & boid & "'"
      end if
      rs_ih.Source="select _OID,NazwaTabeli,NazwaPola,OIDArkusza,NazwaArkusza,StanPrzeliczenia,_UID,_UserName from TMP_SHEETINFO_0 WHERE (NazwaArkusza='" & FormFields("%s_ID") & "') " & stv_warunek
      rs_ih.open
      if not rs_ih.EOF then
         StepRepeat=1
         if StepRepeatMessage<>"" then
            StepRepeatMessage=StepRepeatMessage & ", "
         end if
         StepRepeatMessage=StepRepeatMessage & " Arkusz o nazwie '" & FormFields("%s_ID") & "' już istnieje!"
      end if
      if rs_ih.State<>adStateClosed then
         rs_ih.Close
      end if
      set rs_ih=Nothing         
'end if
""" % (asheetfield.Name, asheetfield.Name)

    for afield in atable.FieldsByTabID:
        if afield.Type in ['string', 'dict']:
            ret = ret + """
if len(FormFields("%s"))>%d then
   StepRepeat=1
   StepRepeatMessage="Wartość w polu <i>%s</i> jest dłuższa niż %d znaków. UWAGA! 1 znak obcojęzyczny liczy się jak co najmniej 7 znaków."
end if
""" % (afield.Name, afield.SizeAsNumber, afield.PrettyName, afield.SizeAsNumber)

    # Walidacja PESEL,NIP,REGON - start
    ret = ret + """
%><!-- #include file="../../../inc/validatePeselEtc.inc" --><%
"""
    for afield in atable.FieldsByTabID:
        if afield.TypeDescription == 'Pesel':
            ret = ret + """
if (CStr(FormFields("%s"))<>"") and (ValidatePESEL(CStr(FormFields("%s")))=0) then
   StepRepeat=1
   StepRepeatMessage="Wartość w polu <i>%s</i> nie zawiera prawidłowego kodu PESEL."
end if
""" % (afield.Name, afield.Name, afield.PrettyName, )
        if afield.TypeDescription == 'NIP':
            ret = ret + """
if (CStr(FormFields("%s"))<>"") and (ValidateNIP(CStr(FormFields("%s")))=0) then
   StepRepeat=1
   StepRepeatMessage="Wartość w polu <i>%s</i> nie zawiera prawidłowego kodu NIP."
end if
""" % (afield.Name, afield.Name, afield.PrettyName, )
        if afield.TypeDescription == 'REGON':
            ret = ret + """
if (CStr(FormFields("%s"))<>"") and (ValidateREGON(CStr(FormFields("%s")))=0) then
   StepRepeat=1
   StepRepeatMessage="Wartość w polu <i>%s</i> nie zawiera prawidłowego kodu REGON."
end if
""" % (afield.Name, afield.Name, afield.PrettyName, )
    # Walidacja PESEL,NIP,REGON - koniec

    ret = ret + """
if StepRepeat=0 then
   On Error Resume Next
   StepRepeatStatus=0
   StepErrorStatus="Error in ASPSourcePreSubmitCheck"
"""

    if aeventsrc and hasattr(aeventsrc, 'ASPSourcePreSubmitCheck'):
        ret = ret + "\n' *** ASPSourcePreSubmitCheck -- START ***\n"
        ret = ret + aeventsrc.ASPSourcePreSubmitCheck
        ret = ret + "\n' *** ASPSourcePreSubmitCheck -- END ***\n"
    ret = ret + """
   acae=CheckASPException(err,StepErrorStatus,Form.AsString())
   if acae>0 then
      StepRepeat=1
      StepRepeatMessage="Błąd na stronie, skontaktuj się z administratorem i przekaż mu ten numer: " & CStr(acae)
   end if
   On Error Goto 0
end if
%>
<a name=msgbookmark id=msgbookmark></a>
<div id=mydziala1><%=CStr(StepRepeat)%></div>
<div id=mymessage1><%=StepRepeatMessage%></div>
<script language="javascript">
<%
if lenStepReturnArray>0 then
   for i=0 to lenStepReturnArray-1
      Response.Write "document.getElementById('" & StepReturnArrayName(i) & "').value='" & StepReturnArrayValue(i) & "';" & chr(10)
   next
end if
if StepRepeat<>0 then
   Response.Write "window.location='#msgbookmark'"
end if
%>
doFormSubmit2();
//window.parent.document.getElementById("myevenntcaller1").fireEvent("onclick");
</script>
<%
"""
    ret = ret + """
   Response.End
else 'submit
"""
    if woiddictref:
        sfwoid = ',_OIDDictRef'
    else:
        sfwoid = ''
    if wchapterid:
        sfwoid = sfwoid + ',_ChapterID'
    ret = ret + """
if StepRepeat=0 then
"""
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
         s1=""
         amax=CLng(FormFields("_ACL_View_Max"))
         for ii1=0 to amax
            if FormFields("_ACL_View_" & CStr(ii1))<>"" then
               s1=s1 & FormFields("_ACL_View_" & CStr(ii1)) & SPLIT_CHAR_VALUE
            end if
         next
         s1=s1 & SPLIT_CHAR_PARAM
         amax=CLng(FormFields("_ACL_Edit_Max"))
         for ii1=0 to amax
            if FormFields("_ACL_Edit_" & CStr(ii1))<>"" then
               s1=s1 & FormFields("_ACL_Edit_" & CStr(ii1)) & SPLIT_CHAR_VALUE
            end if
         next
         s1=s1 & SPLIT_CHAR_PARAM
         amax=CLng(FormFields("_ACL_Delete_Max"))
         for ii1=0 to amax
            if FormFields("_ACL_Delete_" & CStr(ii1))<>"" then
               s1=s1 & FormFields("_ACL_Delete_" & CStr(ii1)) & SPLIT_CHAR_VALUE
            end if
         next
"""
    ret = ret + """
   abfoid=FormFields("_OID")
"""
    if atable.FieldsByName('_ChapterID') is not None:
        ret = ret + """
   if (achapterid<>"") and (achapterid<>"-1") and aelementoid="" then
     if GetChapterIsTableView(achapterid)<>"1" then
       set rs1=cn.execute("select top 1 %s._OID from %s WHERE %s._ChapterId=" & achapterid)
       if not rs1.EOF then
          abfoid=rs1("_OID")
       end if
       if rs1.State<>adStateClosed then
          rs1.Close
       end if
       set rs1=Nothing
     end if
   end if
""" % (atable.NameSQL, atable.NameSQL, atable.NameSQL)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceSubmitBefore'):
        ret = ret + "\n' *** ASPSourceSubmitBefore -- START ***\n"
        ret = ret + aeventsrc.ASPSourceSubmitBefore
        ret = ret + "\n' *** ASPSourceSubmitBefore -- END ***\n"

    ret = ret + """
   if abfoid="-1" then
      rs.ActiveConnection = cn
      rs.CursorType = adOpenKeyset
      rs.LockType = adLockOptimistic
      rs.Source = "select %s,_UID,_UserName%s,%s_DateTime,* from %s WHERE _OID='-1'"
      rs.Open
""" % (sf, sfwoid, sfsecadd, atable.NameSQL)

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
   if CheckACLForRecord(%d,"",achapterid,"Edit")=0 then
      Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
      if rs.State<>adStateClosed then
         rs.Close
      end if
      cn.Close
      set rs=Nothing
      set cn=Nothing
      Response.End
   end if
""" % (aeventsrc.CRM.OID, )

    ret = ret + """
   cn.BeginTrans
   call RSAddNew(rs)
   Set rsOldValues = Server.CreateObject("Scripting.Dictionary")
"""
    s, i = ProcessFieldValueStore(atable)
    ret = ret + s

    if woiddictref:
        ret = ret + """
            if aoidref<>"-1" then
               rs("_OIDDictRef") = aoidref
            end if
"""
    if wchapterid:
        ret = ret + """
   if (achapterid<>"") and (achapterid<>"-1") then
      rs("_ChapterID") = achapterid
   end if
"""
    ret = ret + """
   if FormFields("_BOID")<>"-1" then
      rs("_Dotyczy")=FormFields("_BOID")
   end if
   rs("_UID")=Dession("uid")
   rs("_UserName")=Dession("username")
   rs("_DateTime")=Now
   rs.Update
   cbfoid=rs("_OID")
   Call SetItemHistory(rs,"%s","Nowy rekord w tabeli")
""" % (atable.NameSQL, )

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        apoid = aeventsrc.CRM.OID
        stoid = aeventsrc.OID
        ret = ret + """
         s1=s1 & SPLIT_CHAR_SEPTR & Bin2Hex(rs("_ACLRead")) & SPLIT_CHAR_PARAM & Bin2Hex(rs("_ACLWrite")) & SPLIT_CHAR_PARAM & Bin2Hex(rs("_ACLDelete"))
         ret=Proc_ExecuteMethodRetS(Application("DEFAULT_EXECUTOR"),"CLASSES\Library\DBBase\DMSWorkflow\Prototyp\Projekt\WWWGetUserProjectACLHex", "%d", %d, s1, "")
         slist1=split(ret,SPLIT_CHAR_PARAM)
         cn.Execute "update %s Set _ACLRead=0x" & slist1(0) & ", _ACLWrite=0x" & slist1(1) & ", _ACLDelete=0x" & slist1(2) & " where _OID='" & CStr(rs("_OID")) & "'"
""" % (stoid, apoid, atable.NameSQL)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceSubmit'):
        ret = ret + "\n' *** ASPSourceSubmit -- START ***\n"
        ret = ret + aeventsrc.ASPSourceSubmit
        ret = ret + "\n' *** ASPSourceSubmit -- END ***\n"

    if aeventsrc and hasattr(aeventsrc, 'GetFieldEventsObj'):
        ret = ret + "\n' *** ASPSourceOnValueChange -- START ***\n"
        ret = ret + ProcessFieldValueChange(aeventsrc)
        ret = ret + "\n' *** ASPSourceOnValueChange -- END ***\n"

    # manage plugins
    if apluginsources and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
'''
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('ASPSourceSubmit', dd=ddict)
            if apluginret:
                ret = ret + apluginret
        ret = ret + '''
'''

    ret = ret + """
   Set rsOldValues = Nothing

   Response.Write "<script language='javascript'>" & chr(10)
   if wlocation<>"" then
      Response.Write "window.location='" & wlocation & achapterref & "';"  & chr(10)
   else
      Response.Write "window.location='%s_so.asp?ioid=" & rs("_OID") & achapterref & "';"  & chr(10)
   end if
   Response.Write "</script>"
""" % (atable.NameFile, )

    if atable.HasVersions:
        ret = ret + '''
   Call SetItemVersion("sp_%s_SetVersion",rs("_OID"),"INSERT")
''' % (atable.VersionTable.NameSQLID, )
    for asheetfield in lsheetfields:
        ret = ret + '''
   Call RegisterSheetChange(rs,"%s","%s",FormFields("%s_ID"))
''' % (atable.NameSQL, asheetfield.Name, asheetfield.Name)

    if woiddictref:
        sfwoid = ',%s._OIDDictRef' % (atable.NameSQL, )
    else:
        sfwoid = ''
    if wchapterid:
        sfwoid = sfwoid + ',%s._ChapterID' % (atable.NameSQL, )
    ret = ret + """
   cn.CommitTrans
else
   rs.ActiveConnection = cn
   rs.CursorType = adOpenKeyset
   rs.LockType = adLockOptimistic
   rs.Source = "select %s,_UID,_UserName%s,%s%s._DateTime,* from %s WHERE %s._OID='" & abfoid & "'"
   rs.Open
""" % (sf, sfwoid, sfsecadd, atable.NameSQL, atable.NameSQL, atable.NameSQL)
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        apoid = aeventsrc.CRM.OID
        stoid = aeventsrc.OID
        ret = ret + """
   if CheckACLForRecord(%d,Bin2Hex(rs("_ACLWrite")),achapterid,"Edit")=0 then
      Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
      if rs.State<>adStateClosed then
         rs.Close
      end if
      cn.Close
      set rs=Nothing
      set cn=Nothing
      Response.End
   end if
         s1=s1 & SPLIT_CHAR_SEPTR & Bin2Hex(rs("_ACLRead")) & SPLIT_CHAR_PARAM & Bin2Hex(rs("_ACLWrite")) & SPLIT_CHAR_PARAM & Bin2Hex(rs("_ACLDelete"))
         ret=Proc_ExecuteMethodRetS(Application("DEFAULT_EXECUTOR"),"CLASSES\Library\DBBase\DMSWorkflow\Prototyp\Projekt\WWWGetUserProjectACLHex", "%d", %d, s1, "")
         slist1=split(ret,SPLIT_CHAR_PARAM)
""" % (aeventsrc.CRM.OID, stoid, apoid)
    ret = ret + """
   cn.BeginTrans
   if not rs.EOF then
      Set rsOldValues = Server.CreateObject("Scripting.Dictionary")
"""
    s, i = ProcessFieldValueStore(atable)
    ret = ret + s
    if woiddictref:
        ret = ret + """
            if aoidref<>"-1" then
               rs("_OIDDictRef") = aoidref
            end if
"""
    if wchapterid:
        ret = ret + """
   if (achapterid<>"") and (achapterid<>"-1") then
      rs("_ChapterID") = achapterid
   end if
"""
    ret = ret + """
         rs("_UID")=Dession("uid")
         rs("_UserName")=Dession("username")
         rs("_DateTime")=Now
         rs.MoveFirst
         rs.Update
         Call SetItemHistory(rs,"%s","Modyfikacja rekordu w tabeli")
""" % (atable.NameSQL, )

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
      cn.Execute "update %s Set %s._ACLRead=0x" & slist1(0) & ", %s._ACLWrite=0x" & slist1(1) & ", %s._ACLDelete=0x" & slist1(2) & " where %s._OID='" & CStr(rs("_OID")) & "'"
""" % (atable.NameSQL, atable.NameSQL, atable.NameSQL, atable.NameSQL, atable.NameSQL)

    if aeventsrc and hasattr(aeventsrc, 'ASPSourceSubmit'):
        ret = ret + "\n' *** ASPSourceSubmit -- START ***\n"
        ret = ret + aeventsrc.ASPSourceSubmit
        ret = ret + "\n' *** ASPSourceSubmit -- END ***\n"

    # manage plugins
    if apluginsources and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
'''
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('ASPSourceSubmit', dd=ddict)
            if apluginret:
                ret = ret + apluginret
        ret = ret + '''
'''

    if aeventsrc and hasattr(aeventsrc, 'GetFieldEventsObj'):
        ret = ret + "\n' *** ASPSourceOnValueChange -- START ***\n"
        ret = ret + ProcessFieldValueChange(aeventsrc)
        ret = ret + "\n' *** ASPSourceOnValueChange -- END ***\n"

    ret = ret + apostupdatetext
    ret = ret + '''
         Set rsOldValues = Nothing
      else
         Response.Write "EOF reached... "
      end if
   Response.Write "<script language='javascript'>" & chr(10)

   if wlocation<>"" then
      Response.Write "window.location='" & wlocation & achapterref & "';"  & chr(10)
   else
      Response.Write "window.location='%s_so.asp?ioid=" & abfoid & achapterref & "';"  & chr(10)
   end if
   Response.Write "</script>"

''' % (atable.NameFile, )
    if atable.HasVersions:
        ret = ret + '''
   Call SetItemVersion("sp_%s_SetVersion",abfoid,"UPDATE")
''' % (atable.VersionTable.NameSQLID, )
    for asheetfield in lsheetfields:
        ret = ret + '''
   Call RegisterSheetChange(rs,"%s","%s",FormFields("%s_ID"))
''' % (atable.NameSQL, asheetfield.Name, asheetfield.Name)

    ret = ret + '''
   cbfoid=abfoid
   cn.CommitTrans
   end if
'''
    if aeventsrc and aeventsrc.CRM.newsletters:
        ret = ret + '''
   if aelementoid<>"" then
      set rs1=cn.execute("update %sNEWSLETTERELEMENTS_0 set OIDRefElement='" & cbfoid & "', Status='Z', TableIDElement='" & aTableID & "' where _oid='" & aelementoid & "'")
      if rs1.State<>adStateClosed then
         rs1.Close
      end if
      set rs1=Nothing
   end if
''' % (aeventsrc.CRM.BaseNameModifier, )
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceAfterCommit'):
        ret = ret + "\n' *** ASPSourceAfterCommit -- START ***\n"
        ret = ret + aeventsrc.ASPSourceAfterCommit
        ret = ret + "\n' *** ASPSourceAfterCommit -- END ***\n"

    # manage plugins
    if apluginsources and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
   if (achapterid<>"") and (achapterid<>"-1") then
'''
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('OnAppPageAUChapterChanged', dd=ddict)
            if apluginret:
                ret = ret + apluginret
        ret = ret + '''
   end if
'''
    #finish dodatkow

    if 0 and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
   Proc_ExecuteMethodRetS Application("DEFAULT_EXECUTOR"),"CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura_WWWGenerateSingleChapter","0",%d,"#" & achapterid,""
''' % (aeventsrc.OID, )

    ret = ret + '''
 else
   Response.Write "<script language='javascript'>" & chr(10)
   sst=""
   if StepRepeatMessage<>"" then
      sst=sst & "&repeatmsg=" & Server.HTMLEncode(StepRepeatMessage)
   end if
   if StepRepeatStatus<>0 then
      sst=sst & "&repeatstatus=" & CStr(StepRepeatStatus)
   end if
   if wlocation<>"" then
      sst=sst & "&wlocation=" & Server.HTMLEncode(wlocation)
   end if
   if achapterref<>"" then
      sst=sst & achapterref
   end if
   Response.Write "window.location='%s_au.asp?ioid=" & FormFields("_OID") & sst & achapterref & "';" & chr(10)
   Response.Write "</script>"
 end if
end if
''' % (atable.NameFileSubmit, )

    if aEditorScript > 0 or aTextField > 0:
        ret = ret + """
%>
"""
        #      ret=ret+GetScriptText()
        ret = ret + GetSpellOnlyScriptText()
        ret = ret + """
<%
"""

    if aEditorScript > 0:
        ret = ret + """
%>
"""
        #      ret=ret+GetScriptText()
        #      ret=ret+GetSpellOnlyScriptText()
        ret = ret + """
<%
"""
    elif aTextField > 0:
        ret = ret + """
%>
"""
        #      ret=ret+GetSpellOnlyScriptText()
        ret = ret + """
<%
"""
    return ret


#*********************************************************************************
def SQLTableGetSearchDataASP(atable):
    df = {}
    fls = [atable.NameSQL + '._OID', ]
    df[atable.NameSQL + '._OID'] = 0
    dfcnt = 1
    for afield in atable.FieldsByTabID:
        #      if afield.IsSearch and afield.IsInteractive and afield.Type in ['string','numeric','date','datetime','text','integer','money','dict','external dict','bool']:
        if (afield.IsInteractive or afield.IsAliased) and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'external dict', 'external dict multiple', 'bool', 'float']:
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
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
            if i % 2:
                snclass = 'objectseditdatafieldnameeven'
                svclass = 'objectseditdatafieldvalueeven'
            else:
                snclass = 'objectseditdatafieldnameodd'
                svclass = 'objectseditdatafieldvalueodd'
            ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s><input type=text id=\'%s\' name=\'%s\' size=20 value=\'\' %s></td></tr>"\n' % (snclass, afield.PrettyName, svclass, afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield, aissearch=1))
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
        if afield.IsSearch and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'bool', 'float']:
            if not afield.Type in ['string', 'text', 'dict', 'dict int', 'date', 'datetime']:
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
        elif (afield.IsInteractive or afield.IsAliased) and afield.Type in ['external dict', 'external dict multiple'] and afield.DictSourceTable is None:
            raise MHTMLSQLGenException('$$$ pole słownikowe bez przypisanej tabeli: ' + atable.NameSQL + ' ' + afield.NameSQL)
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
            i = i + 1
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
        if afield.IsAliased and afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'external dict', 'external dict multiple', 'bool', 'float']:
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
            if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'dict', 'dict int', 'float']:
                ret = ret + """
      sdv1=rs.Fields(%d).Value
      if (rs.Fields(%d).Type=7) or (rs.Fields(%d).Type=133) or (rs.Fields(%d).Type=134) or (rs.Fields(%d).Type=135) then
         sdv1=getDateTimeAsStr(sdv1)
      end if
Response.Write server.htmlencode(sdv1)
""" % (df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], df[afield.NameSQL], )
            elif afield.Type in ['bool', ]:
                ret = ret + """
at1rsvalue=rs.Fields(%d).Value
if not isnull(at1rsvalue) then
   if CBool(at1rsvalue) then
      Response.Write "Tak"
   else
      Response.Write "Nie"
   end if
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
def SQLTableGetSelectSingleASP(atable, asourcetable=None, areffield='', btable=None, atabs=None, afname='', asecurity=None, aTableLinks=None, aeventsrc=None, apluginsources=None):
    sald = ''
    sale = ''
    salfu = ''
    atablenamemsg = ''
    if asecurity is not None:
        sald = asecurity.AccessLevelDelete
        sale = asecurity.AccessLevelEdit
        salfu = asecurity.AccessLevelFilesUpload
        salv = asecurity.AccessLevelView
        atablenamemsg = '\\n\\n' + ICORUtil.strUpperPL(asecurity.Nazwa)

    ret = """          
if Request.QueryString("sheet")<>"-1" then
   if Request.QueryString("wlocation")<>"" then
      wlocation=Request.QueryString("wlocation")
   else
      wlocation=""
   end if
   wlocationback="%s_so.asp?ioid=" & Request.QueryString("ioid")
end if
""" % (atable.NameFile, )

    ret3 = """
if Request.QueryString("sheet")<>"-1" then
"""
    apagetabid_1 = 1
    if aeventsrc and hasattr(aeventsrc, 'PageTabCnt'):
        apagetabid_1 = aeventsrc.PageTabCnt
        aeventsrc.PageTabCnt = 3 + aeventsrc.PageTabCnt
    apagetabid_2, apagetabid_3 = apagetabid_1 + 1, apagetabid_1 + 2

    sandallowedit, sandallowdelete = '', ''
    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret3 = ret3 + """
   aallowrecordedit=CheckACLForRecord(%d,Bin2Hex(rs("_ACLWrite")),achapterid,"Edit")
   aallowrecorddelete=CheckACLForRecord(%d,Bin2Hex(rs("_ACLDelete")),achapterid,"Delete")
""" % (aeventsrc.CRM.OID, aeventsrc.CRM.OID, )
        sandallowedit = 'and aallowrecordedit=1 '
        sandallowdelete = 'and aallowrecorddelete=1 '
    ret3 = ret3 + """
   whr=0
   adivbuttons="<div class='fg-toolbar ui-corner-all ui-helper-clearfix'><div class='fg-buttonset ui-helper-clearfix'>"
   if CheckUserAccess("%s")=1 %sthen 'SourceTable - AccessLevelEdit
      response.write adivbuttons
      'Response.Write "<br><br><div class=""rounded background_pastelparadise_red""><div class=""roundedContent background_default"">"
      Response.Write "<a id='btnedit_%s' class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_au.asp?ioid=" & Request.QueryString("ioid") & "&aoidref=" & Request.QueryString("aoidref") & "&wlocation=" & Request.QueryString("wlocation") & "&areffield=" & Request.QueryString("areffield") & achapterref & "'>Edycja danych</a>"
      whr=1
   end if
   if CheckUserAccess("%s")=1 %sthen 'SourceTable - AccessLevelDelete
      if whr=0 then
         response.write adivbuttons
         'Response.Write "<br><br><div class=""rounded background_pastelparadise_red""><div class=""roundedContent background_default"">"
         whr=1
'      else
'         Response.Write "<br>"
      end if
      Response.Write "<a id='btndelete_%s' class='fg-button-single ui-state-default ui-corner-all uihover' onclick=""javascript:if (confirm('Czy na pewno chcesz usunąć pozycję%s?')) {this.href='%s_dr.asp?ioid=" & Request.QueryString("ioid") & "&aoidref=" & Request.QueryString("aoidref") & "&wlocation=" & Request.QueryString("wlocation") & "&areffield=" & Request.QueryString("areffield") & achapterref & "';} else {this.href='javascript:var umm=1;';} ;"" HREF=""javascript:var umm=1;"">Usuń pozycję</a>"
   end if
""" % (sale, sandallowedit, atable.NameSQLID, atable.NameFile, sald, sandallowdelete, atable.NameSQLID, atablenamemsg, atable.NameFile)

    if 0 and aTableLinks and asecurity.Nazwa != 'Disabled':
        wl0 = 0
        for alink in aTableLinks:
            for asrcfield, adstfield in alink.LinkFields:
                if asrcfield == "_OID":
                    aTabName = ''
                    for aTab in atabs:
                        if aTab[0] == alink.TabID and aTab[0] != 10:
                            aTabName = aTab[1]
                            break
                    if aTabName == '':
                        aTabName = alink.DstTable
                    if alink.LinkHrefCaptionNewItem:
                        atlname = alink.LinkHrefCaptionNewItem
                    else:
                        atlname = '%s - nowa pozycja' % (aTabName, )
                    if atlname != '-':
                        if not wl0:
                            wl0 = 1
                            ret3 = ret3 + """
   response.write "<br>"
"""
                        wback = 'server.urlencode(wlocationback)'
                        if alink.IsLocationBackDisabled:
                            wback = '""'
                        ret3 = ret3 + """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=1 %sthen 'DestTable - AccessLevelEdit
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_au.asp?aoidref=" & Request.QueryString("ioid") & "&wlocation=" & %s & "&areffield=%s'>%s</a>"
      whr=1
   end if
end if
""" % (alink.TabID, alink.DstTable.AccessLevelEdit, sandallowedit, alink.DstTable.SQLTable.NameFile, wback, adstfield, atlname)
        if wl0:
            ret3 = ret3 + """
   response.write "<br>"
"""

    if aeventsrc and hasattr(aeventsrc, 'xmldata'):
        ret3 = ret3 + """
'   response.write "<br>"
"""
        for axmldata in aeventsrc.xmldata:
            if axmldata.IsObjectMenu:
                ret3 = ret3 + """
   wlocationback="%s_so.asp?ioid=" & Request.QueryString("ioid")
   if CheckUserAccess("%s")=1 then
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='%s_au.asp?ioid=" & Request.QueryString("ioid") & "&aoidref=" & Request.QueryString("aoidref") & "&wlocation=" & Request.QueryString("wlocation") & "&areffield=" & Request.QueryString("areffield") & achapterref & "'>%s</a><br>"
      whr=1
   end if
""" % (atable.NameFile, axmldata.AccessLevelView, axmldata.PageFile, axmldata.Title)

    if aeventsrc and aeventsrc.CRM.BaseNameModifier:
        aoiddictreffield = atable.FieldsByName('_OIDDictRef')
        if aoiddictreffield is not None:
            ret3 = ret3 + """
            if CStr(rs("_OIDDictRef"))<>"" then
               Set rsoref = Server.CreateObject("ADODB.Recordset")
               rsoref.ActiveConnection = cn
               rsoref.CursorType = adOpenKeyset
               rsoref.LockType = adLockOptimistic
               rsoref.Open "select top 1 ItemTable from %sHISTORIAZMIAN_0 where itemoid='" & CStr(rs("_OIDDictRef")) & "' order by %sHISTORIAZMIAN_0._datetime desc",cn
               if not rsoref.EOF and not rsoref.BOF then
                  st=rsoref("ItemTable")
                  stl=Split(st,".")
                  st=stl(UBound(stl))
                  sta=Split(st,"BZR_")
                  Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='BZR_" & sta(ubound(sta)) & "_so.asp?ioid=" & CStr(rs("_OIDDictRef")) & "&chapterid=" & achapterid & "'>Dane źródłowe</a>"
               end if
               if rsoref.State<>0 then
                  rsoref.Close
               end if
               set rsoref=Nothing
            end if
""" % (aeventsrc.CRM.BaseNameModifier, aeventsrc.CRM.BaseNameModifier,
            )

    ret3 = ret3 + """
'   if CheckUserAccess("%s")=1 %sthen 'SourceTable - AccessLevelEdit
""" % (sale, sandallowedit, )
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable'):
        ret3 = ret3 + "\n' *** ASPSourceOnAfterShowOneTable -- START ***\n"
        ret3 = ret3 + aeventsrc.ASPSourceOnAfterShowOneTable
        ret3 = ret3 + "\n' *** ASPSourceOnAfterShowOneTable -- END ***\n"

    # manage plugins
    if apluginsources and aeventsrc:
        if not atabs:
            print '$$ EMPTY TABS for table:', atable.NameFile
        ret3 = ret3 + '''
if Request.QueryString("sheet")="%d" then ' PLUGINS START       
''' % (atabs[0][0], )
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('OnAppPageSOButton', dd=ddict)
            if apluginret:
                ret3 = ret3 + apluginret
        ret3 = ret3 + '''
end if ' PLUGINS END
'''
    #finish dodatkow

    ret3 = ret3 + """
'   end if
   If wlocation<>"" then
      Response.Write "<a class='fg-button-single ui-state-default ui-corner-all uihover' href='" & wlocation & "'>Powrót</a><br>"
      whr=1
   end if
   if whr=1 then
      Response.Write "</div></div>"
   end if

end if
"""

    ret = ret + """
if Request.QueryString("sheet")="-1" then
"""
    ret4 = ''

    if atabs:
        ret = ret + WriteSheetsHeader(atabs, afname)
    ret = ret + """
else
"""
    if aeventsrc:
        ret = ret + """
   if CheckUserAccess("%s")=0 then 'SourceTable - AccessLevelView
      Response.Write "<h1><font color='red'>Brak wymaganych uprawnień</font></h1>"
      Response.End
   end if
""" % (salv, )

    if btable is not None:
        ret = ret + SQLTableGetSelectSingleASPDotyczy(atable, btable, atabs, aeventsrc=aeventsrc)
    else:
        fls = ['%s._OID' % (atable.NameSQL, ), '%s._DateTime' % (atable.NameSQL, ), '%s._UserName' % (atable.NameSQL, )]
        for afield in atable.FieldsByTabID:
            fls.append(afield.NameSQL)
        if areffield:
            fls.append(areffield)
        sf = string.join(fls, ',')
        sfsec = ''
        if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
            sfsec = ',%s._ACLRead,%s._ACLWrite,%s._ACLDelete' % (atable.NameSQL, atable.NameSQL, atable.NameSQL)
        ret = ret + """
   if (Request.QueryString("ioid")="") or (Request.QueryString("ioid")="-1") then
     Response.Write "<!-- pusty rekord -->"
      if rs.State<>adStateClosed then
         rs.Close
      end if
      Set rs=Nothing
      Response.End
   end if
rs.Open "select %s%s from %s WHERE %s._OID='" & Request.QueryString("ioid") & "'", cn
if rs.EOF or rs.BOF then
    Response.Write "<h1>Wybrana pozycja została usunięta bądź nie istnieje</h1>"
    if rs.State<>adStateClosed then
       rs.Close
    end if
    cn.Close
    set rs=Nothing
    set cn=Nothing
    Response.End
end if
""" % (sf, sfsec, atable.NameSQL, atable.NameSQL)
        if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
            ret = ret + """
if CheckACLForRecord(%d,Bin2Hex(rs("_ACLRead")),achapterid,"View")=0 then
   Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
   if rs.State<>adStateClosed then
      rs.Close
   end if
   cn.Close
   set rs=Nothing
   set cn=Nothing
   Response.End
end if
""" % (aeventsrc.CRM.OID, )
        if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeShowOneTable'):
            ret = ret + "\n' *** ASPSourceOnBeforeShowOneTable -- START ***\n"
            ret = ret + aeventsrc.ASPSourceOnBeforeShowOneTable
            ret = ret + "\n' *** ASPSourceOnBeforeShowOneTable -- END ***\n"
        if atabs:
            ret = ret + """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 2</font></h1>")
   else
""" % (atabs[0][0], atabs[0][2])

        # manage plugins
        if apluginsources and aeventsrc:
            for apluginsource in apluginsources:
                ddict = {'Table': atable, 'EventSource': aeventsrc}
                apluginret = apluginsource.ProcessEventsInternal('OnAppPageBeforeMainTab', dd=ddict)
                if apluginret:
                    ret = ret + apluginret
        #finish dodatkow

        ret = ret + """
Response.Write "<div id=pagetab%d>"
'Response.Write "<br><br><div class=""rounded background_pasteldark_blue""><div class=""roundedContent background_default"">"
""" % (apagetabid_1, )

        # wyswietlenie jednego rekordu
        aOnLoad1 = []
        sret = MHTMLSQLGenLib.GetShowSingleSelectTable(atable, aeventsrc=aeventsrc, aOnLoad1=aOnLoad1)
        ret = ret + sret

        ret = ret + ret3

        ret4 = ret4 + """
   'Response.Write "</div></div>"
   Response.Write "</div>"
if Request.QueryString("sheet")="%d" then ' PLUGINS START       
   Response.Write "<script type='text/javascript'>ltabscontainer.push(['pagetab%d','Dane']);</script>"
end if
""" % (atabs[0][0], apagetabid_1, )

        if aOnLoad1:
            ret4 = ret4 + """
%>
<!-- ONLOAD - START -->
"""
            for atext in aOnLoad1:
                if type(atext) == type([]):
                    atext, aonbefore, aafter = atext
                    ret4 = ret4 + '\n' + aonbefore + '\n'
            wvb = 0
            for atext in aOnLoad1:
                if type(atext) == type([]):
                    atext, aonbefore, aafter = atext
                if not wvb:
                    ret4 = ret4 + """
<script language="vbscript">
<!--
Sub Window_onLoad()
"""
                    wvb = 1
                print 'VBScript Single text: ', atext
                ret4 = ret4 + '\n' + atext + '\n'
            if wvb:
                ret4 = ret4 + """
End Sub
-->
</script>
"""
            for atext in aOnLoad1:
                if type(atext) == type([]):
                    atext, aonbefore, aafter = atext
                    ret4 = ret4 + '\n' + aafter + '\n'
            ret = ret + """
<!-- ONLOAD - FINISH 1 -->
<%
"""

        if atabs:
            ret4 = ret4 + """
   end if
end if
"""
    ret4 = ret4 + """
end if
"""

    ret1 = """
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

if Request.QueryString("sheet")<>"-1" then
"""
    # manage plugins
    if apluginsources and aeventsrc:
        ret1 = ret1 + '''
if Request.QueryString("sheet")="%d" then ' PLUGINS START       
''' % (atabs[0][0], )
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('OnAppPageSOSection', dd=ddict)
            if apluginret:
                ret1 = ret1 + apluginret
        ret1 = ret1 + '''
end if ' PLUGINS END
'''
    #finish dodatkow
    ret1 = ret1 + """
else
%%>
<SCRIPT language='javascript'>
try {
  lasttab=getParentFrame('NAVBAR').GetSheetForCid('%s');
  if (lasttab!=undefined)
    change_display(lasttab.nr,lasttab.id);
} catch(e) {}
</SCRIPT>
<%%
end if
""" % (afname, )
    return [ret, ret4, ret1]


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
   Response.Write "<br><br><div class=""rounded background_pasteldark_blue""><div class=""roundedContent background_default"">"
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
    ahtmltableid = 'lt_%d_%d' % (atable.OID, btable.OID)
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
   Response.Write("<TABLE id=%s>")
   Response.Write("<thead><TR>")
""" % (sf, btable.NameSQL, alinkfield, swhere, aorderby, atablecaption, ahtmltableid)
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            if not (anodictfields and afield.Type in ['external dict', 'external dict multiple']):
                ret = ret + """
   Response.Write "<TH>%s</TH>"
""" % (afield.PrettyName, )
    for afxalias in flexaliases:
        ret = ret + """
   Response.Write "<TH>%s</TH>"
""" % (afxalias, )
    ret = ret + """
   Response.Write("</TR></thead><TBODY>")
   Do While Not rs1.EOF
      aoid=rs1.Fields(0).Value
      Response.Write "<TR>"
"""
    i = 1
    for afield in btable.FieldsByTabID:
        if afield.Name[:1] != '_' and afield.IsAliased and afield.IsInteractive:
            if not (anodictfields and afield.Type in ['external dict', 'external dict multiple']):
                ret = ret + """
Response.Write "<td>"
Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s'>" & rs1.Fields(%d).Value & "</a>"
Response.Write "</td>"                               
""" % (btable.NameFile, alinkparam, i)
            i = i + 1
    for afxname in flexnames:
        ret = ret + """
Response.Write "<td>"
Response.Write "<a class='objectitemasanchor' href='%s_so.asp?ioid=" & cstr(aoid) & "%s'>" & rs1.Fields("%s").Value & "</a>"
Response.Write "</td>"
""" % (btable.NameFile, alinkparam, afxname)
        i = i + 1
    ret = ret + """
      Response.Write "</TR>"
      rs1.MoveNext
   Loop
   Response.Write("</TBODY></TABLE>")
   Response.Write "<script type='text/javascript'>jQuery(function (){makeTable('#%s');});</script>"
end if
if rs1.State<>adStateClosed then
   rs1.Close
end if
set rs1=Nothing
""" % (ahtmltableid, )
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
def GetSelectTextByTabID(atable, atext, atabid, aisinternal=0, atabcnt=0, atabtitle=''):
    ret = ''
    if atabid:
        asecurity = atable.TabsByIDSecurity.get(atabid, '')
        ret = """
if Request.QueryString("sheet")="%d" then
   if CheckUserAccess("%s")=0 then
      Response.Write("<h1><font color='red'>Nie masz wymaganych uprawnień! 5</font></h1>")
   else
""" % (atabid, asecurity)
    if aisinternal:
        ret = ret + '''
         Response.Write "<div id=""pagetab_int_%d"">"
''' % (atabcnt, )
    ret = ret + atext
    if aisinternal:
        ret = ret + '''
         Response.Write "</div>"
'''
    if atabid:
        ret = ret + """
   end if
end if
"""
    if aisinternal:
        atabtitle = atabtitle.replace('"', '`')
        atabtitle = atabtitle.replace("'", '`')
        ret = ret + '''
if Request.QueryString("sheet")="%d" then
   Response.Write "<script type='text/javascript'>ltabscontainer.push(['pagetab_int_%d','%s']);</script>"
end if
''' % (atabid, atabcnt, atabtitle)
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
<meta http-equiv="X-UA-Compatible" content="IE=8">
<META content="text/html; charset=%s" http-equiv=Content-Type>
<title>ICOR Application Server - Table Frame</title>
</head>
<%%
CustomPage=0
""" % (aencoding, )
    if aeventsrc and hasattr(aeventsrc, 'AccessLevelView'):
        ret = ret + """
   if CheckUserAccess("%s")=0 then 'SourceTable - AccessLevelView
      Response.Write "<h1><font color='red'>Brak wymaganych uprawnień</font></h1>"
      Response.End
   end if
""" % (aeventsrc.AccessLevelView, )

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
DataOID=GetSafeOID(Request.QueryString("ioid"))
"""
    aitemdesc = 'Pozycja danych'
    if aeventsrc:
        aitemdesc = 'Pozycja danych: ' + aeventsrc.NazwaObiektu
    ret = ret + """
call RegisterVisitHistory("%s","","","showone")
""" % (aitemdesc, )

    ret = ret + """
if CustomPage=0 then
%%>
<frameset name="FRAMEOBJECTS" id="FRAMEOBJECTS" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="64,*">
  <frame name="OBJECTEDITMAIN" id="OBJECTEDITMAIN" scrolling="no" noresize src="%s?ioid=<%%=DataOID%%>&sheet=-1<%%=achapterref%%>" frameborder="0" marginheight="0" marginwidth="0">
  <frameset name="FRAMEPANES" id="FRAMEPANES" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="%s">
""" % (afname, apanes)
    for i in range(len(atabs)):
        tid, s, tav = atabs[i]
        if not i:
            #ret=ret+'   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize src="%s?ioid=<%%=DataOID%%>&sheet=%d" frameborder="0" marginheight="0" >\n'%(i,i,afname,tid)
            ret = ret + '   <frame name="OBJECTEDITPANE%d" id="OBJECTEDITPANE%d" scrolling="auto" noresize src="%s?ioid=<%%=DataOID%%>&aoidref=<%%=Request.QueryString("aoidref")%%>&wlocation=<%%=Request.QueryString("wlocation")%%>&areffield=<%%=Request.QueryString("areffield")%%>&sheet=%d<%%=achapterref%%>" frameborder="0" marginheight="0" >\n' % (i, i, afname, tid)
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
def GetSingleObjectFramePageTabsOne(atabs, afname, aeventsrc=None):
    ret = ''
    aencoding = 'utf-8'
    if aeventsrc:
        aencoding = aeventsrc.CRM.DefaultEncoding
    ret = ret + """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><!-- #include file="../inc/_page_begin.asp" -->
<html>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=8">
<META content="text/html; charset=%s" http-equiv=Content-Type>
<title>ICOR Application Server - Table Frame</title>
</head>
<%%
CustomPage=0
""" % (aencoding, )
    if aeventsrc and hasattr(aeventsrc, 'AccessLevelView'):
        ret = ret + """
   if CheckUserAccess("%s")=0 then 'SourceTable - AccessLevelView
      Response.Write "<h1><font color='red'>Brak wymaganych uprawnień</font></h1>"
      Response.End
   end if
""" % (aeventsrc.AccessLevelView, )

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
DataOID=GetSafeOID(Request.QueryString("ioid"))
"""
    aitemdesc = 'Pozycja danych'
    if aeventsrc:
        aitemdesc = 'Pozycja danych: ' + aeventsrc.NazwaObiektu
    ret = ret + """
call RegisterVisitHistory("%s","","","showone")
""" % (aitemdesc, )

    ret = ret + """
if CustomPage=0 then
   response.redirect "%s?ioid=" & DataOID & "&aoidref=" & Request.QueryString("aoidref") & "&wlocation=" & Request.QueryString("wlocation") & "&areffield=" & Request.QueryString("areffield") & "&sheet=10" & achapterref & ""
%%>
""" % (afname, )

    ret = ret + """
<%
else
   Response.Write("</BODY>")
end if
%>
</html>
"""
    return ret


#*********************************************************************************
def GetSingleObjectFramePageTabs(atabs, afname, afnameso, aeventsrc=None, atitle='', afiletype=''):
    ret = ''
    if aeventsrc and hasattr(aeventsrc, 'AccessLevelView'):
        ret = ret + """
   if CheckUserAccess("%s")=0 then 'SourceTable - AccessLevelView
      Response.Write "<h1><font color='red'>Brak wymaganych uprawnień</font></h1>"
      Response.End
   end if

   aTableID=%d
""" % (aeventsrc.AccessLevelView, aeventsrc.OID)
    else:
        ret = ret + """
aTableID=-1
"""
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnBeforeShowOne'):
        ret = ret + "\n' *** ASPSourceOnBeforeShowOne -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnBeforeShowOne
        ret = ret + "\n' *** ASPSourceOnBeforeShowOne -- END ***\n"

    ret = ret + """
achapterid=""
achapterref=""
acmsid=""
if Request.QueryString("chapterid")<>"" then
   if ValidateInteger(Request.QueryString("chapterid")) then
      achapterid=Request.QueryString("chapterid")
      achapterref="&chapterid=" & achapterid
   end if
elseif Request.Form("_CHAPTERID")<>"" then
   if ValidateInteger(Request.Form("_CHAPTERID")) then
      achapterid=Request.Form("_CHAPTERID")
      achapterref="&chapterid=" & achapterid
   end if
end if
if achapterid<>"" then
   acmsid=GetChapterCMSID(achapterid)
end if
DataOID=GetSafeOID(Request.QueryString("ioid"))
thisFileType="%s"
aPageTitle="%s"
if (achapterid<>"") and (achapterid<>"-1") then
   aPageTitle=GetChapterCaption(achapterid)
end if
""" % (afiletype, atitle.replace('"', "'"),
       )
    aprojectname = ''
    if aeventsrc and hasattr(aeventsrc, 'CRM'):
        apoid = aeventsrc.CRM.OID
        aprojectname = aeventsrc.CRM.Project
        ret = ret + """
POID=%d
""" % (apoid, )
    else:
        ret = ret + """
POID=-1
"""
    aitemdesc = 'Pozycja danych'
    if aeventsrc:
        aitemdesc = 'Pozycja danych: ' + aeventsrc.NazwaObiektu
    ret = ret + """
call RegisterVisitHistory("%s","","","showone")
""" % (aitemdesc, )

    ret = ret + """
if CustomPage=0 then
%>
"""

    ret = ret + '''
<SCRIPT LANGUAGE=javascript>
ltabs=[];
'''
    if 0:
        ret = ret + '''
DataOID='<%=DataOID%>';
TableID='<%=aTableID%>';
POID='<%=POID%>';
ChapterID='<%=achapterid%>';
CMSID='<%=acmsid%>';
'''
    for i in range(len(atabs)):
        tid, s, tav = atabs[i]
        asrc = 'appdata/%s/crm/%s?ioid=<%%=DataOID%%>&aoidref=<%%=Request.QueryString("aoidref")%%>&wlocation=<%%=Request.QueryString("wlocation")%%>&areffield=<%%=Request.QueryString("areffield")%%>&sheet=%d<%%=achapterref%%>' % (aprojectname, afname, tid)
        s = s.replace("'", "`")
        ret = ret + '''ltabs.push(['%s','%s']);
''' % (s, asrc)
    ret = ret + '''
</SCRIPT>

<style>
.myframe {
   width:98%;
   height:98%;
   border: none;
   padding:0px;
   margin:0px;
}

#tabscontainer { 
    display: inline-block; 
}

.ui-tabs .ui-tabs-panel {
   padding:0px;
}
</style>

<!-- $$I2
<div id="tabscontainer">
   <ul>
'''
    for i in range(len(atabs)):
        tid, s, tav = atabs[i]
        ret = ret + '<li><a href="#dpage%d">%s</a></li>\n' % (i, s)
    ret = ret + '''
   </ul>
'''
    for i in range(len(atabs)):
        tid, s, tav = atabs[i]
        if not i:
            asrc = 'src="%s?ioid=<%%=Request.QueryString("ioid")%%>&aoidref=<%%=Request.QueryString("aoidref")%%>&wlocation=<%%=Request.QueryString("wlocation")%%>&areffield=<%%=Request.QueryString("areffield")%%>&sheet=%d<%%=achapterref%%>" ' % (afname, tid)
        else:
            asrc = ''
        ret = ret + '<div id="dpage%d"><iframe id="myframe%d" %sclass="myframe" frameborder="0" height="98%%" width="98%%" marginheight="0" marginwidth="0" scrolling="auto"></iframe></div>\n' % (i, i, asrc, )
    ret = ret + '''
</div>
-->

<SCRIPT LANGUAGE=javascript>
function resizeUi() {
    var h = jQuery(window).height();
    var w = jQuery(window).width();
    jQuery("#tabscontainer").css('width', w-7 );
    jQuery("#tabscontainer").css('height', h-7 );
    jQuery(".ui-tabs-panel").css('height', h-46-15 );
};

jQuery(function() {
   return // $$I2
   jQuery('#tabscontainer').tabs({
      selected:0,
      select: function(event, ui) { 
'''
    tid, s, tav = atabs[0]
    ret = ret + '''
         if (ui.index==0) {
            getParentFrame('NAVBAR').SetSheetForCid('%s',ui.index,%d);
         }
''' % (afnameso, tid)
    for i in range(1, len(atabs)):
        tid, s, tav = atabs[i]
        asrc = '%s?ioid=<%%=Request.QueryString("ioid")%%>&aoidref=<%%=Request.QueryString("aoidref")%%>&wlocation=<%%=Request.QueryString("wlocation")%%>&areffield=<%%=Request.QueryString("areffield")%%>&sheet=%d<%%=achapterref%%>' % (afname, tid)
        ret = ret + '''
         if (ui.index==%d) {
            if (jQuery("#myframe%d").attr("src")) {
               return;
            }
            asrc="%s";  
            jQuery("#myframe%d").attr("src",asrc);
            getParentFrame('NAVBAR').SetSheetForCid('%s',ui.index,%d);
         }                      
''' % (i, i, asrc, i, afnameso, tid)
    ret = ret + '''
      }
   });
   var resizeTimer = null;
   jQuery(window).bind('resize', function() {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resizeUi, 100);
   });
   resizeUi();
});
</SCRIPT>
'''
    ret = ret + """
<%
else
   Response.Write("</BODY>")
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
def SQLTableGetSelectAllASP(atable):
    fls = ['%s._OID' % (atable.NameSQL, ), ]
    for afield in atable.FieldsByTabID:
        if afield.IsAliased and afield.IsInteractive:
            fls.append(afield.NameSQL)
    sf = string.join(fls, ',')
    if not len(atable.Fields):
        print '$$ tabela bez pol:', atable.NameSQL
        return ''
    atop = 10000
    if atable.Top:
        atop = atable.Top
    ret = """
rs.Open "select top %d %s from %s ORDER BY %s", cn
Response.Write("<span class='objectsviewcaption'>%s</span>")
Response.Write("<TABLE class='objectsviewtable'>")
Response.Write("<TR>")
""" % (atop, sf, atable.NameSQL, atable.Fields[0].NameSQL, atable.TableCaption, )
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
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'float']:
            if afield.Name[:1] != '_' and afield.IsSearch and afield.IsInteractive:
                if i % 2:
                    snclass = 'objectseditdatafieldnameeven'
                    svclass = 'objectseditdatafieldvalueeven'
                else:
                    snclass = 'objectseditdatafieldnameodd'
                    svclass = 'objectseditdatafieldvalueodd'
                ret = ret + '         Response.Write "<TR VALIGN=top class=objectseditrow><td width=\'160px\' class=%s>%s:</td><td class=%s><input type=text id=\'%s\' name=\'%s\' size=20 value=\'\' %s></td></tr>"\n' % (snclass, afield.PrettyName, svclass, afield.Name, afield.Name, MHTMLSQLGenLib.GetFieldValidationText(afield, aissearch=1))
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
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'float']:
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
        if afield.Type in ['string', 'numeric', 'date', 'datetime', 'text', 'integer', 'money', 'float'] and afield.IsAliased and afield.IsInteractive:
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
def SQLTableDeleteRemoveSingleASP(atable, asecurity=None, aeventsrc=None, apluginsources=None):
    sald = ''
    if asecurity is not None:
        sald = asecurity.AccessLevelDelete
    ret = """
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
   AllowDeleteThisRecord=1
   if CheckUserAccess("%s")=1 then 'SourceTable - AccessLevelDelete
""" % (sald, )

    if aeventsrc and hasattr(aeventsrc, 'IsSecurityEnabled') and aeventsrc.IsSecurityEnabled:
        ret = ret + """
rs.ActiveConnection = cn
rs.CursorType = adOpenKeyset
rs.LockType = adLockOptimistic
rs.Source = "select %s._OID,%s._ACLDelete from %s WHERE %s._OID='" & Request.QueryString("ioid") & "'"
rs.Open
if CheckACLForRecord(%d,Bin2Hex(rs("_ACLDelete")),achapterid,"Delete")=0 then
   Response.Write "<h1>Nie masz wystarczających uprawnień.</h1>"
   if rs.State<>adStateClosed then
      rs.Close      
   end if
   cn.Close
   set rs=Nothing
   set cn=Nothing
   Response.End
end if
""" % (atable.NameSQL, atable.NameSQL, atable.NameSQL, atable.NameSQL, aeventsrc.CRM.OID,
        )

    ret = ret + """
   cn.BeginTrans
"""
    if aeventsrc and hasattr(aeventsrc, 'ASPSourceOnDelete'):
        ret = ret + "\n' *** ASPSourceOnDelete -- START ***\n"
        ret = ret + aeventsrc.ASPSourceOnDelete
        # manage plugins
        if apluginsources and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
            for apluginsource in apluginsources:
                ddict = {'Table': atable, 'EventSource': aeventsrc}
                apluginret = apluginsource.ProcessEventsInternal('ASPSourceOnDelete', dd=ddict)
                if apluginret:
                    ret = ret + apluginret
        #finish dodatkow
        ret = ret + "\n' *** ASPSourceOnDelete -- END ***\n"
    ret = ret + '''
   if AllowDeleteThisRecord=1 then
      SetItemHistoryByOID Request.QueryString("ioid"),"%s","Usuniecie pozycji w tabeli"
''' % (atable.NameSQL, )
    if atable.HasVersions:
        ret = ret + '''
      Call SetItemVersion("sp_%s_SetVersion",Request.QueryString("ioid"),"DELETE")
''' % (atable.VersionTable.NameSQLID, )
    else:
        ret = ret + '''
         cn.Execute "DELETE %s WHERE _OID='" & Request.QueryString("ioid") & "'"
''' % (atable.NameSQL, )
        if aeventsrc:
            if 0:
                ret = ret + '''
         cn.Execute "DELETE FROM %s WHERE OIDArkusza='" & Request.QueryString("ioid") & "'"
''' % (aeventsrc.CRM.Table_SheetInfo.NameSQL, )
    ret = ret + '''
   end if
   cn.CommitTrans
'''

    # manage plugins
    if apluginsources and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
   if (achapterid<>"") and (achapterid<>"-1") then
'''
        for apluginsource in apluginsources:
            ddict = {'Table': atable, 'EventSource': aeventsrc}
            apluginret = apluginsource.ProcessEventsInternal('OnAppPageAUChapterChanged', dd=ddict)
            if apluginret:
                ret = ret + apluginret
        ret = ret + '''
   end if
'''
    #finish dodatkow

    if 0 and aeventsrc and hasattr(aeventsrc, 'DocumentsTabID') and hasattr(aeventsrc, 'ASPSourceOnAfterShowOneTable') and hasattr(aeventsrc, 'IsVersionControl') and aeventsrc.IsVersionControl:    #tylko eventsrc, ktore sa typu SourceTable
        ret = ret + '''
   Proc_ExecuteMethodRetS Application("DEFAULT_EXECUTOR"),"CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura_WWWGenerateSingleChapter","0",%d,"#" & achapterid,""
''' % (aeventsrc.OID, )

    ret = ret + """
      if AllowDeleteThisRecord=1 then
         Response.Write "<h1>Pozycja została usunięta</h1>"
      end if
      if Request.QueryString("wlocation")<>"" then
         wlocation=Request.QueryString("wlocation")
      else
         wlocation=""
      end if
      If wlocation<>"" then
         Response.Write "<br><a class='fg-button-single ui-state-default ui-corner-all uihover' href='" & wlocation & achapterref & "'>Powrót</a><br>"
      else
         Response.Write "<script language='javascript'>" & chr(10)
         Response.Write "window.location='/icormanager/icormain.asp?jobtype=lastvisithistory&id=searchform'" & chr(10)
         Response.Write "</script>" & chr(10)      
      end if
   else
      SetItemHistoryByOID Request.QueryString("ioid"),"%s","Nieuprawniona proba usuniecia pozycji w tabeli"
      Response.Write "<h1>Twoja nieuprawniona próba usunięcia tej pozycji została zarejestrowana.</h1>"
   end if
""" % (atable.NameSQL, )
    return ret
