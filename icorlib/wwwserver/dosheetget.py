# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.icorobjectsviewer import *
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorlib.wwwhtml.worksheetmain import *
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import string
import icorwwwlib
import random
import cStringIO


def WriteCoolbarScript(file):
    file.write("""
<SCRIPT LANGUAGE="JScript"><!--
   // SET SOME "CONSTANT" VALUES FOR THE SCRIPT
   // MAKES PLAYING WITH LOOK AND FEEL A LOT EASIER

   var sOffBackColor = "threedface";
   var sOffTextColor = "menutext"
   var sOffBorderColor = "threedface";
   var sOffPadding = "1px 1px 1px 1px";

   var sOverBackColor = "threedface";
   var sOverTextColor = "menutext"
   var sOverBorderColor = "threedhighlight threedshadow threedshadow threedhighlight";
   var sOverPadding = "1px 1px 1px 1px";

   var sDownBackColor = "silver"
   var sDownTextColor = "menutext"
   var sDownBorderColor = "threedshadow threedhighlight threedhighlight threedshadow";
   var sDownPadding = "2px 0px 0px 2px";

   var sPaneName = "";
   var eActiveButton = null;

   // TWO HELPER FUNCTIONS
   // ONE TO SET BUTTON PADDING AND ONE TO SET BUTTON IMAGE

   function SetButtonPadding(eButton,sPaddingStyle)
   {
      eButton.rows[0].cells[0].style.padding = sPaddingStyle;
      eButton.rows[0].cells[1].style.padding = sPaddingStyle;
   }
   
   function SetButtonImage(eButton,sState)
   {
      var eImg = eButton.rows[0].cells[0].children[0];
      if (eImg) 
      {
         var sImgSrc = eImg.src;
         if (sImgSrc.match(/_(\w+)\.gif/)) 
         {
            eImg.src = sImgSrc.replace(RegExp.$1,sState);
         }
      }
   }
   
   // FOUR EVENT-HANDLER FUNCTIONS

   function button_over(eButton)
   {

      // IF WE'RE JUST MOUSING ABOUT WITHIN THE BUTTON, THEN BAIL

      if (window.event && eButton.contains(window.event.fromElement)) return false;

      // OTHERWISE CHANGE BUTTON STYLE

      eButton.style.backgroundColor = sOverBackColor;
      eButton.style.color = sOverTextColor;
      if (eActiveButton != eButton)
      {
         eButton.style.borderColor = sOverBorderColor;
         SetButtonImage(eButton,"over");
      }
   }


   function button_out(eButton)
   {
      // IF WE'RE JUST MOUSING ABOUT WITHIN THE BUTTON, THEN BAIL
      
      if (window.event && eButton.contains(window.event.toElement)) return false;

      // OTHERWISE CHANGE BUTTON STYLE

      if (eActiveButton != eButton)
      {
         eButton.style.backgroundColor = sOffBackColor;
         eButton.style.borderColor = sOffBorderColor;
         eButton.style.color = sOffTextColor;
         SetButtonPadding(eButton,sOffPadding);
         SetButtonImage(eButton,"off")
      }
      else
      {
         eButton.style.backgroundColor = sDownBackColor;
         eButton.style.borderColor = sDownBorderColor;
         eButton.style.color = sDownTextColor;
      }
   }

   function button_down(eButton)
   {
      eButton.style.borderColor = sDownBorderColor;
      SetButtonPadding(eButton,sDownPadding);
   }

   function button_up(eButton)
   {

      // IF ANOTHER BUTTON IS ACTIVE, RESET IT

      if (null != eActiveButton && eButton != eActiveButton)
      {
         eActiveButton.style.backgroundColor = sOffBackColor;
         eActiveButton.style.borderColor = sOffBorderColor;
         eActiveButton.style.color = sOffTextColor;
         SetButtonImage(eActiveButton,"off");
         SetButtonPadding(eActiveButton,sOffPadding);
         eActiveButton = null; 

         // insert code here for button hiding 
         window.status = window.defaultStatus;
      }

      // IF THE BUTTON WE CLICKED IS NOT THE ACTIVE BUTTON, MAKE IT ACTIVE

      if (eButton != eActiveButton)  
      {
         eActiveButton = eButton;
         eActiveButton.style.borderColor = sDownBorderColor;
         eActiveButton.style.color = sDownTextColor;
         SetButtonPadding(eActiveButton,sDownPadding);
         sPaneName = eActiveButton.id.replace(/tbl(.*)Button/,"$1");

         // insert code here for button showing 
//         window.status = "Now showing: " + sPaneName;
      }

      // OTHERWISE, RESET IT

      else  
      {
         eActiveButton.style.backgroundColor = sOverBackColor;
         eActiveButton.style.borderColor = sOverBorderColor;
         eActiveButton.style.color = sOverTextColor;
         SetButtonPadding(eActiveButton,sOverPadding);
         eActiveButton = null;

         // insert code here for button hiding 
         window.status = window.defaultStatus;
      }

   }

   function button_keypress(eButton)
   {
      if ("13" == window.event.keyCode)
      {
         button_down(eButton);
         button_up(eButton);
      }
   }
//--></SCRIPT>
""")


def WriteHeader2(afile, aclass, sheetsinfo, aoid):
    s = """
<SCRIPT language=jscript>
function change_display(atoframe) {
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
            aframe.src="icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet="+atoframe.toString();
            }
      } else {
         s=s+'0';
      }
      i=i+1;
   }
   window.parent.document.getElementById("FRAMEPANES").rows=s;
}
</SCRIPT>
""" % (len(sheetsinfo.keys()), aclass.CID, aoid)
    afile.write(s)
    vkeys = sheetsinfo.keys()
    vkeys.sort()
    if len(vkeys) > 1:
        WriteCoolbarScript(afile)
        afile.write("""
      <div id="mycoolbardiv1" style="position=absolute;left=30px;top=0px;z-index=-5;">
      <font name="verdana" size="60%%">
<TABLE ID="tblCoolbar" CELLPADDING="0" CELLSPACING="0" BORDER="0" WIDTH="100%%" ONSELECTSTART="return false;">
<TR VALIGN="middle">
<TD><div style="width:32;height:0;"></div></TD>
""")
        for akey in vkeys:
            if sheetsinfo[akey][2] <= 0:
                afile.write("""
<TD><TABLE TABINDEX="1" ID="tblCoolButton%d" CELLPADDING="0" CELLSPACING="0" BORDER="0" ONMOUSEOVER="button_over(this);" ONMOUSEOUT="button_out(this);" ONMOUSEDOWN="button_down(this);" ONMOUSEUP="button_up(this);" ONFOCUS="button_over(this);" ONBLUR="button_out(this);" ONKEYPRESS="button_keypress(this);" TITLE="%s">
<TR VALIGN="middle"><TD></TD>
<TD onclick="return change_display(%d);">%s&nbsp;&nbsp;&nbsp;</TD>
</TR></TABLE></TD>""" % (akey, sheetsinfo[akey][0], akey, sheetsinfo[akey][0],
                         ))
        afile.write("""
<TD WIDTH="100%%"></TD></TR></TABLE></font>
</div>
<div id="buttoncontroldiv" style="position:absolute;left:0;top:0;z-index:-4">
   <img style="cursor:pointer;position:relative;left:4;top:0;"
      src="/icormanager/images/scroll_coolbar_left.png"
      onmouseover="javascript:this.src='/icormanager/images/scroll_coolbar_left_in.png';"
      onmouseout="javascript:this.src='/icormanager/images/scroll_coolbar_left.png';"
      onclick="document.body.scrollLeft-=250;window.document.getElementById('buttoncontroldiv').style.pixelLeft=document.body.scrollLeft;"
      alt="przewiń w lewo">
   <img style="cursor:pointer;position:relative;left:8;top:0;"
      src="/icormanager/images/scroll_coolbar_right.png"
      onmouseover="javascript:this.src='/icormanager/images/scroll_coolbar_right_in.png';"
      onmouseout="javascript:this.src='/icormanager/images/scroll_coolbar_right.png';"
      onclick="document.body.scrollLeft+=250;window.document.getElementById('buttoncontroldiv').style.pixelLeft=document.body.scrollLeft;"
      alt="przewiń w prawo">
</div>
<div id="myispacediv" style="width:0;height:0;"></div>
<SCRIPT LANGUAGE="JScript"><!--
   button_over(tblCoolButton0);
   button_up(tblCoolButton0);
   button_out(tblCoolButton0);
   document.getElementById("myispacediv").style.height=document.getElementById("mycoolbardiv1").offsetHeight;
//--></SCRIPT>
""")
    else:
        afile.write('<div id="myispacediv" style="width:0;height:0;"></div>')
    afile.write("""
<SCRIPT LANGUAGE="JScript"><!--
   window.parent.document.getElementById("FRAMEOBJECTS").rows=document.getElementById("myispacediv").offsetHeight.toString()+',*';
//--></SCRIPT>
""")


def GetSingleObjectFramePageTabs(afile, aclass, sheetsinfo, aoid, atabs=None, afname=None, aeventsrc=None):
    afile.write('''
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

<div id="tabscontainer">
   <ul>
''')
    vkeys = sheetsinfo.keys()
    vkeys.sort()
    amaxsheet = 0
    for akey in vkeys:
        if sheetsinfo[akey][2] <= 0:
            sheetsinfo[akey][2] = amaxsheet
            amaxsheet = amaxsheet + 1
        else:
            sheetsinfo[akey][2] = -1
    if amaxsheet < 2:
        asrc = 'icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=%d' % (aclass.CID, aoid, 0)
        afile.write('''
<SCRIPT LANGUAGE=javascript>
window.location.href='%s';
</SCRIPT>
''' % (asrc, ))
    else:
        for akey in vkeys:
            if sheetsinfo[akey][2] >= 0:
                s = string.replace(sheetsinfo[akey][0], ' ', '&nbsp;')
                afile.write('<li><a href="#dpage%d">%s</a></li>\n' % (sheetsinfo[akey][2], s))
    afile.write('''
   </ul>
''')
    w = 0
    for akey in vkeys:
        if sheetsinfo[akey][2] >= 0:
            i = sheetsinfo[akey][2]
            if not w:
                asrc = 'src="icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=%d" ' % (aclass.CID, aoid, i)
            else:
                asrc = ''
            afile.write('<div id="dpage%d"><iframe id="myframe%d" %sclass="myframe" frameborder="0" height="98%%" width="98%%" marginheight="0" marginwidth="0" scrolling="auto"></iframe></div>\n' % (i, i, asrc, ))
            w = 1
    afile.write('''
</div>

<SCRIPT LANGUAGE=javascript>
function resizeUi() {
    var h = jQuery(window).height();
    var w = jQuery(window).width();
    jQuery("#tabscontainer").css('width', w-7 );
    jQuery("#tabscontainer").css('height', h-26 );
    jQuery(".ui-tabs-panel").css('height', h-46-15 );
};

jQuery(function() {
   jQuery('#tabscontainer').tabs({
      selected:0,
      select: function(event, ui) { 
''')
    w = 0
    for akey in vkeys:
        if sheetsinfo[akey][2] >= 0:
            if not w:
                w = 1
                continue
            i = sheetsinfo[akey][2]
            asrc = 'icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=%d' % (aclass.CID, aoid, i)
            afile.write('''
         if (ui.index==%d) {
            if (jQuery("#myframe%d").attr("src")) {
               return;
            }
            asrc="%s";
            jQuery("#myframe%d").attr("src",asrc);
         }
''' % (i, i, asrc, i))
    afile.write('''
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
''')


def GetSingleObjectFramePageTabs20(afile, aclass, sheetsinfo, aoid, atabs=None, afname=None, aeventsrc=None):
    vkeys = sheetsinfo.keys()
    vkeys.sort()
    amaxsheet = 0
    for akey in vkeys:
        if sheetsinfo[akey][2] <= 0:
            sheetsinfo[akey][2] = amaxsheet
            amaxsheet = amaxsheet + 1
        else:
            sheetsinfo[akey][2] = -1
    afile.write('''
<SCRIPT LANGUAGE=javascript>
ltabs=[];
''')
    for akey in vkeys:
        if sheetsinfo[akey][2] >= 0:
            i = sheetsinfo[akey][2]
            atitle = sheetsinfo[akey][0].replace("'", "`")
            asrc = 'icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet=%d' % (aclass.CID, aoid, i)
            afile.write('''ltabs.push(['%s','%s']);
''' % (atitle, asrc))
    afile.write('''
</SCRIPT>
''')


def WriteHeader(afile, aclass, sheetsinfo, aoid):
    GetSingleObjectFramePageTabs20(afile, aclass, sheetsinfo, aoid, atabs=None, afname=None, aeventsrc=None)
    return
    vkeys = sheetsinfo.keys()
    vkeys.sort()
    amaxsheet = 0
    for akey in vkeys:
        if sheetsinfo[akey][2] <= 0:
            sheetsinfo[akey][2] = amaxsheet
            amaxsheet = amaxsheet + 1
        else:
            sheetsinfo[akey][2] = -1
    s = """
<SCRIPT language="javascript">
function set_frame(atoframe) {
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
            aframe.src="icormain.asp?jobtype=sheetget&CID=%d&OID=%d&sheet="+atoframe.toString();
            }
      } else {
         s=s+'0';
      }
      i=i+1;
   }
   window.parent.document.getElementById("FRAMEPANES").rows=s;
}

var last_tab=0;
var max_tab=%d;
document.body.topMargin=0;
function change_display(atoframe) {
   if (atoframe==last_tab)
      return;
   if (last_tab==0) {
      s1img="images/tabs/tab_ng.png";
   } else {
      s1img="images/tabs/tab_gg.png";
   }
   if (last_tab==max_tab) {
      s2img="images/tabs/tab_gn.png";
   } else {
      s2img="images/tabs/tab_gg.png";
   }
   jQuery('#imgtab'+last_tab.toString()).attr('src',s1img);
   jQuery('#imgtab'+(last_tab+1).toString()).attr('src',s2img);
   jQuery('#infotab'+last_tab.toString()).removeClass("tabselected").addClass("tabunselected");
   if (atoframe==0) {
      s1img="images/tabs/tab_ns.png";
   } else {
      s1img="images/tabs/tab_gs.png";
   }
   if (atoframe==max_tab) {
      s2img="images/tabs/tab_sn.png";
   } else {
      s2img="images/tabs/tab_sg.png";
   }
   jQuery('#imgtab'+atoframe.toString()).attr('src',s1img);
   jQuery('#imgtab'+(atoframe+1).toString()).attr('src',s2img);
   jQuery('#infotab'+atoframe.toString()).removeClass("tabunselected").addClass("tabselected");
   last_tab=atoframe;
   set_frame(atoframe);
}
</SCRIPT>
""" % (len(sheetsinfo.keys()), aclass.CID, aoid, amaxsheet - 1,
       )
    afile.write(s)

    if amaxsheet > 1:
        afile.write("""
<div style="position:absolute;left:30px;top:0px;">
<TABLE cellSpacing=0 cellPadding=0 border=0>
<TBODY>
<TR>
""")
        for akey in vkeys:
            if sheetsinfo[akey][2] >= 0:
                if sheetsinfo[akey][2] == 0:
                    afile.write("""
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="images/tabs/tab_ns.png" border=0></TD>
          <TD align=middle></TD>
""" % (sheetsinfo[akey][2], ))
                elif sheetsinfo[akey][2] == 1:
                    afile.write("""
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="images/tabs/tab_sg.png" border=0></TD>
          <TD align=middle></TD>
""" % (sheetsinfo[akey][2], ))
                else:
                    afile.write("""
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="images/tabs/tab_gg.png" border=0></TD>
          <TD align=middle></TD>
""" % (sheetsinfo[akey][2], ))
        afile.write("""
          <TD vAlign=bottom align=middle rowSpan=3><IMG id=imgtab%d src="images/tabs/tab_gn.png" border=0></TD>
        </TR>
        <TR>
""" % (amaxsheet, ))
        for akey in vkeys:
            if sheetsinfo[akey][2] >= 0:
                if sheetsinfo[akey][2] == 0:
                    s = 'tabselected'
                else:
                    s = 'tabunselected'
                afile.write("""
          <TD id=infotab%d align=middle class="%s">
            <span class=tabtext onclick="javascript:change_display(%d);">%s</span></TD>
""" % (sheetsinfo[akey][2], s, sheetsinfo[akey][2], string.replace(sheetsinfo[akey][0], ' ', '&nbsp;')))
        afile.write("""
        </TR>
        <TR>
          <TD style="height:1px" align=middle bgColor=ivory colspan=%d></TD>
        </TR>
</TBODY></TABLE>
</div>
""" % (amaxsheet * 2, ))
        afile.write("""
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
""")
    else:
        afile.write("""
<SCRIPT LANGUAGE="JScript"><!--
   window.parent.document.getElementById("FRAMEOBJECTS").rows='0,*';
//--></SCRIPT>
""")


def FieldFunc(aclass, afield, aoid, file, onload=None, acntid=0):
    if onload is None:
        onload = []
    ftid = int(afield.FieldTypeID)
    if ftid <= MAX_ICOR_SYSTEM_TYPE:
        #print '$$FIELDFUNC:',afield.FID,afield.Name,aoid,afield[aoid]
        fclass = 'objectseditdatafieldvalue'
        #      if ftid in [mt_Integer,mt_Double]:
        #         fclass='objectseditdatafieldvaluenumeric'
        #      else:
        #         fclass='objectseditdatafieldvalue'
        if afield.FieldEditor == 'Worksheet$$$':
            if afield[aoid] != '':
                ahref = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s' % (aclass.CID, aoid, afield.Name)
                file.write('</table><table width="100%%"><tr><td width="100%%" colspan=2 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>' % (afield.FieldNameAsDisplayed, ))
                atext, aonloadtext, aOnBeforeLoadText, aOnAfterLoadText = GetWorksheetText(aid=afield.Name, aheight="480px", ahref=ahref, aviewonly=1)
                onload.append([aonloadtext, aOnBeforeLoadText, aOnAfterLoadText])
                file.write(atext)
                file.write('</td></tr></table><table>')
        elif afield.FieldEditor == 'XML':
            if afield[aoid] != '':
                ahref = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s&XMLData=1' % (aclass.CID, aoid, afield.Name)
                file.write('</table><table width="100%%" old_height="60%%"><tr><td width="100%%" colspan=2 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br><iframe width="100%%" height="100%%" src="%s"></iframe></td></tr></table><table>' % (afield.FieldNameAsDisplayed, ahref))
        elif 0 and afield.FieldEditor == 'SourceCode' and afield.IsMemo:
            v = afield.ValuesFmt(aoid)
            if v != '':
                vl = string.split(v, '\n')
                v = string.join(map(XMLUtil.GetAsXMLStringNoPL, vl), '<br>')
                v = string.replace(v, ' ', '&nbsp;')
                if not afield.WWWSingleValue and string.strip(v):
                    #               v="<pre class='prettyprint' style='PADDING-LEFT: 5px; WHITE-SPACE: nowrap; background:window;overflow:scroll; width:400px; height:220px; border-left: 1 solid Black;border-top: 1 solid Black; border-bottom: 1 solid Black;FONT-FAMILY:Arial,Verdana; FONT-SIZE: 8pt;'>%s</pre><br>"%v
                    v = "<pre style='PADDING-LEFT: 5px; WHITE-SPACE: nowrap; background:window;overflow:scroll; width:400px; height:220px; border-left: 1 solid Black;border-top: 1 solid Black; border-bottom: 1 solid Black;FONT-FAMILY:Arial,Verdana; FONT-SIZE: 8pt;'>%s</pre><br>" % v
                s = '<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class="%s" >%s</td></tr>\n' % (afield.FieldNameAsDisplayed, fclass, v)
                file.write(s)
        else:
            if ftid == mt_Bool:
                if afield.ValuesAsInt(aoid):
                    v = 'Tak'
                else:
                    v = 'Nie'
            else:
                v = afield.ValuesFmt(aoid)
            if ftid == mt_String and not afield.IsMemo:
                v = XMLUtil.GetAsXMLStringNoPL(v)
            if afield.IsMemo and not afield.FieldEditor == 'HTML':
                vl = string.split(v, '\n')
                v = string.join(map(XMLUtil.GetAsXMLStringNoPL, vl), '<br>')
                v = string.replace(v, ' ', '&nbsp;')
                if not afield.WWWSingleValue and string.strip(v):
                    v = "<div style='PADDING-LEFT: 5px; WHITE-SPACE: nowrap; background:window;overflow:scroll; width:440px; height:220px; border-left: 1 solid Black;border-top: 1 solid Black; border-bottom: 1 solid Black;FONT-SIZE: 8pt;'>%s</div><br>" % v
            if afield.IsMemo and afield.FieldEditor == 'HTML':
                if not afield.WWWSingleValue and string.strip(v):
                    v = "<div style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:320px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>%s</div><br>" % v
            if v != '':
                if afield.FieldEditor == 'URL':
                    s = '<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src="/icormanager/images/smttr_lb.png">%s:</td><td class=objectseditdatafieldvalue><a href="%s">%s</a></td></tr>\n' % (afield.FieldNameAsDisplayed, v, v)
                elif afield.IsMemo:
                    if afield.FieldEditor == 'SourceCode':
                        s = '<tr><td width="100%%" colspan=2 class=objectseditdatafieldnameleftalign>%s</td></tr></table><table width="100%%" old_height="60%%"><tr><td class=objectseditdatafieldvalue style="font-family:DejaVu Sans Mono, Courier New, Courier, monospaced;">%s</td></tr></table><table>\n' % (afield.FieldNameAsDisplayed, v)
                    else:
                        #                  s='<tr><td width="100%%" colspan=2 class=objectseditdatafieldnameleftalign>%s</td></tr></table><table width="100%%" old_height="60%%"><tr><td class=objectseditdatafieldvalue>%s</td></tr></table><table>\n' % (afield.FieldNameAsDisplayed,v)
                        s = '<tr><td width="100%%" colspan=2 class=objectseditdatafieldnameleftalign>%s</td></tr></table><table width="100%%" old_height="60%%"><tr><td class=objectseditdatafieldvalue style="font-family:DejaVu Sans Mono, Courier New, Courier, monospaced;">%s</td></tr></table><table>\n' % (afield.FieldNameAsDisplayed, v)
                else:
                    s = '<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldname>%s:</td><td class="%s" >%s</td></tr>\n' % (afield.FieldNameAsDisplayed, fclass, v)
                file.write(s)
    else:
        aspace = ICORMDSpace()
        aspace.Caption = afield.FieldNameAsDisplayed
        cov = ICORClassObjectsViewer(afield.ClassOfType, aspace, afield, aoid)
        fname = cov.Process(-1, -1)
        if afield.WWWSingleValue or afield.FieldEditor == 'ObjectsList':
            if afield.WWWBackRefField:
                aobj = afield.GetRefObject(aoid)
                if aobj:
                    file.write('<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src="/icormanager/images/smttr_lb.png">%s:</td><td class="objectseditdatafieldvalue">' % (afield.FieldNameAsDisplayed, ))
                    l = []
                    cnt = 10
                    while aobj and cnt:
                        lv = aobj.AsColumnValues()
                        s = '<A class="reflistoutnavy objectitemasanchor" href="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d">%s</A>' % (aobj.CID, aobj.OID, random.randint(1, 10000000), string.join(lv, ', '))
                        l.append(s)
                        bfields = aobj.Class.GetFieldsList()
                        cfield = None
                        for bfname in bfields:
                            bfield = aobj.Class.FieldsByName(bfname)
                            if bfield.WWWBackRefField:
                                cfield = bfield
                                break
                        if cfield:
                            aobj = cfield.GetRefObject(aobj.OID)
                        else:
                            aobj = None
                        cnt = cnt - 1
                    file.write(string.join(l, ' | '))
                    file.write('</td></tr>\n')
            else:
                titerator = ICORClassObjects2HTMLLinks(cov.space, file)
                titerator.ForEachNotEmptyRow()
                if len(titerator.Links) > 0:
                    v = string.join(titerator.Links, ', ')
                    fclass = 'objectseditdatafieldvalue'
                    s = '<tr VALIGN=top class=objectseditrow><td class=objectseditdatafieldname><img src="/icormanager/images/smttr_lb.png">%s:</td><td class="%s" >%s</td></tr>\n' % (afield.FieldNameAsDisplayed, fclass, v)
                    file.write(s)
        else:
            if cov.ObjectsCount > 0:
                file.write('</table><br>\n')
                asorted = 1
                if afield.WWWSortable:
                    asorted = 0
                titerator = ICORClassObjects2HTMLSorted(cov.space, file, 0, 'RefObjectsView', asorted=asorted, aid=acntid)
                #            titerator=ICORClassObjects2XMLDSO(cov.space,file,0,'RefObjectsView')
                titerator.ForEachNotEmptyRow()
                file.write('<br><table>\n')


#         else:
#            file.write('<table>\n')


def WriteFieldSheet(afile, asheetname, afields, asheetid, aclass, aoid, UID, brcid=-1, broid=-1):
    #   afile.write('\n<script type="text/javascript" src="inc/sortabletable.js"></script>\n')
    if not aclass.WWWDisableDescription:
        afile.write('<script type="text/javascript">\n')
        afile.write('thisPageTitle="%s"\n' % (XMLUtil.GetAsXMLStringSimple(aclass.WWWDescription)))
        afile.write('</script>\n')

    afile.write('<div class="ui-widget">')
    #if not aclass.WWWDisableDescription:
    #afile.write('<div class="ui-widget-header">')
    #afile.write('<H3>%s</H3>\n' % aclass.WWWDescription)
    #afile.write('</div>')

    afile.write('<div class="ui-widget-content">')

    hobj = aclass.WWWEditPageTopHTML
    while hobj:
        afile.write(hobj.HTMLText)
        hobj.Next()

    afile.write('<BR><TABLE>\n')

    emethod = aclass.MethodsByName('OnWWWSheetFieldGet')
    onbeforesheetoutput = None
    onbeforefieldoutputevent = None
    onafterfieldoutputevent = None
    onaftersheetoutput = None
    onfieldoutputevent = None
    if emethod is not None:
        mname = emethod.MethodPath
        mname = mname.replace('\\', '_')
        mname = mname.replace('/', '_')
        sheetmethod = __import__(mname)
        try:
            onbeforesheetoutput = getattr(sheetmethod, 'OnBeforeSheetOutput')
        except:
            onbeforesheetoutput = None
        try:
            onbeforefieldoutputevent = getattr(sheetmethod, 'OnBeforeFieldOutput')
        except:
            onbeforefieldoutputevent = None
        try:
            onfieldoutputevent = getattr(sheetmethod, 'OnFieldOutput')
        except:
            onfieldoutputevent = None
        try:
            onafterfieldoutputevent = getattr(sheetmethod, 'OnAfterFieldOutput')
        except:
            onafterfieldoutputevent = None
        try:
            onaftersheetoutput = getattr(sheetmethod, 'OnAfterSheetOutput')
        except:
            onaftersheetoutput = None
    if onbeforesheetoutput:
        apply(onbeforesheetoutput, (aclass, aoid, asheetid, afile))
    pfields = []
    onload = []
    acntid = 0
    for afitem in afields:
        ftid, fnameasdisplayed, afield = afitem
        pfields.append(afield.Name)
        w = 1
        if onbeforefieldoutputevent:
            eret = apply(onbeforefieldoutputevent, (aclass, afield, aoid, asheetid, afile, afields))
            if eret is not None:
                w = eret
        if w:
            w1 = 1
            if onfieldoutputevent:
                eret = apply(onfieldoutputevent, (aclass, afield, aoid, asheetid, afile, afields))
                if eret is not None:
                    w1 = eret
            if w1:
                FieldFunc(aclass, afield, aoid, afile, onload, acntid)
        if onafterfieldoutputevent:
            apply(onafterfieldoutputevent, (aclass, afield, aoid, asheetid, afile, afields))
        acntid = acntid + 1
    afile.write('</TABLE>\n')
    if onaftersheetoutput:
        apply(onaftersheetoutput, (aclass, aoid, asheetid, afile, pfields))
    if onload:
        for atext in onload:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                afile.write(aonbefore)
        wvb = 0
        for atext in onload:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
            if atext:
                print 'VBScript Sheet text: ', atext
            if not wvb:
                afile.write("""
<script language="vbscript">
<!--
Sub Window_onLoad()
""")
                wvb = 1
            afile.write(atext)
        if wvb:
            afile.write("""
End Sub
-->
</script>
""")
        for atext in onload:
            if type(atext) == type([]):
                atext, aonbefore, aafter = atext
                afile.write(aafter)
    w = 1
    mrefs = aclass.GetWWWMenuRefs()
    while mrefs:
        amenu = ICORWWWMenuItem(UID, mrefs.OID, brcid=brcid, broid=broid)
        if amenu.IsVisibleByProfile(UID):
            if w:
                afile.write('<hr>')
                w = 0
            WriteClassMenu(afile, aclass, amenu, aoid, 0)
        mrefs.Next()

    hobj = aclass.WWWEditPageBottomHTML
    while hobj:
        afile.write(hobj.HTMLText)
        hobj.Next()


#   afile.write('\n<script type="text/javascript" src="inc/prettify.js"></script>\n')
#   afile.write('\n<script type="text/javascript">\nprettyPrint()\n</script>\n')

    afile.write('</div>')


def WriteClassMenu(file, eclass, amenu, OID, alevel):
    sisrc = ''
    slineseparator = '<br>'
    if amenu.Action == 'ObjectApplyMethods':
        amlist = eclass.GetMethodsList()
        mobj = eclass[OID]
        for amname in amlist:
            amethod = eclass.MethodsByName(amname)
            if amethod is None:
                continue
            if not amethod.WWWMethod:
                continue
            if not ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, amenu.uid):
                continue
            res = 1
            blink = ''
            try:
                mname = amethod.MethodPath
                mname = mname.replace('\\', '_')
                mname = mname.replace('/', '_')
                pagemethod = __import__(mname)
                if hasattr(pagemethod, 'OnBeforeWWWAction'):
                    pageevent = getattr(pagemethod, 'OnBeforeWWWAction')
                    if pageevent is not None:
                        res = apply(pageevent, (mobj, amenu, file))
                if res:
                    if hasattr(pagemethod, 'OnWWWActionGetLink'):
                        pageevent = getattr(pagemethod, 'OnWWWActionGetLink')
                        if pageevent is not None:
                            blink = apply(pageevent, (mobj, amenu))
                            if blink is None:
                                blink = ''
                            if blink and blink[:1] != '&':
                                blink = '&' + blink
            except:
                print 'Error during object edit:', amenu.Action, ' - ', amname
                raise
            if not res:
                continue
            alink = 'icormain.asp?jobtype=menuitem&OID=' + str(amenu.oid) + '&param=' + str(eclass.CID) + '_' + str(OID) + '_' + amethod.Name + blink
            alink = alink + '&brCID=' + str(amenu.BackRefCID) + '&brOID=' + str(amenu.BackRefOID)
            smname = amethod.WWWDescription
            if not smname:
                smname = amethod.Name
            if amethod.WWWConfirmExecute:
                sfmname = string.replace(smname, '"', '')
                sfmname = string.replace(sfmname, "'", '')
                sfmname = ICORUtil.strLowerPL(sfmname)
                aclick = 'onclick="javascript:if (confirm(\'Czy na pewno chcesz wykonać metodę %s?\')) {this.href=\'%s\';} else {this.href=\'javascript:var umm=1;\';} ;" ' % (sfmname, alink, )
                alink = 'javascript:var umm=1;'
            else:
                aclick = ''
            file.write('&nbsp;' * alevel)
            file.write('<a class="fg-button-single ui-state-default ui-corner-all uihover" %sHREF="%s">' % (aclick, alink))    #
            irefs = amethod.WWWMenuImageLink
            wi = 0
            if irefs:
                file.write('<img align=middle align=top vspace=0 src="%s">&nbsp;' % (irefs.Location[irefs.OID], ))
                wi = 1
            if not wi:
                file.write('<img align=middle align=top vspace=0 src="/icormanager/images/icons/silk/icons/page_forward.png">&nbsp;')
                wi = 1
            file.write('%s</a>%s' % (smname, slineseparator))
    else:
        wmenushow = 1
        if amenu.Action in ['ObjectAdd', ]:
            mobj = eclass[OID]
            pclass = aICORDBEngine.Classes[amenu.ParamItem]
            aseclev = 0
            if pclass is not None:
                aseclev = pclass.CID == eclass.CID
                sisrc = icorwwwlib.GetClassImageSrc(pclass)
            wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelEdit', amenu.uid, aseclev)
        elif amenu.Action in ['ObjectEdit', ]:
            mobj = eclass[OID]
            #         print '*** Object Edit ACL Check:',mobj,'***'
            wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelEdit', amenu.uid)
            sisrc = icorwwwlib.GetClassImageSrc(eclass)


#         print 'wmenushow=',wmenushow
        elif amenu.Action in ['ObjectDelete', ]:
            mobj = eclass[OID]
            wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelDelete', amenu.uid)
            sisrc = icorwwwlib.GetClassImageSrc(eclass)
        emethod = eclass.MethodsByName('OnWWWAction')
        if wmenushow and emethod is not None:
            try:
                mname = emethod.MethodPath
                mname = mname.replace('\\', '_')
                mname = mname.replace('/', '_')
                pagemethod = __import__(mname)
                if hasattr(pagemethod, 'OnBeforeWWWAction'):
                    pageevent = getattr(pagemethod, 'OnBeforeWWWAction')
                    if pageevent is not None:
                        mobj = eclass[OID]
                        wmenushow = apply(pageevent, (mobj, amenu, file))
            except:
                print 'Error during default menu class link action:', amenu.Action, ' - ', emethod.MethodPath
                raise
        if wmenushow:
            scaption = amenu.AsPageCaption + ' ' + amenu.AsPageSubCaption
            sfcaption = string.replace(scaption, '"', '')
            sfcaption = string.replace(sfcaption, "'", '')
            sfcaption = ICORUtil.strLowerPL(sfcaption)
            alink = 'icormain.asp?jobtype=menuitem&OID=' + str(amenu.oid) + '&param=' + str(eclass.CID) + '_' + str(OID) + '_'    #+fieldname
            alink = alink + '&brCID=' + str(amenu.BackRefCID) + '&brOID=' + str(amenu.BackRefOID)
            if amenu.ConfirmHRef:
                aclick = 'onclick="javascript:if (confirm(\'Czy na pewno chcesz wybrać %s?\')) {this.href=\'%s\';} else {this.href=\'javascript:var umm=1;\';} ;" ' % (sfcaption, alink, )
                alink = 'javascript:var umm=1;'
            else:
                aclick = ''
            file.write('&nbsp;' * alevel)
            file.write('<a class="fg-button-single ui-state-default ui-corner-all uihover" %sHREF="%s">' % (aclick, alink))    #
            wi = 0
            if amenu.ImageLocation:
                file.write('<img align=middle align=top vspace=0 src="%s">&nbsp;' % (amenu.ImageLocation, ))
                wi = 1
            if not wi and sisrc:
                file.write('<img align=middle align=top vspace=0 src="%s">&nbsp;' % (sisrc, ))
                wi = 1
            if not wi:
                file.write('<img align=middle align=top vspace=0 src="/icormanager/images/icons/silk/icons/page_go.png">&nbsp;')
                wi = 1
            file.write('%s</a>%s' % (scaption, slineseparator))
    for smenu in amenu.SubMenus:
        if smenu.IsVisibleByProfile(amenu.uid):
            WriteClassMenu(file, eclass, smenu, OID, alevel + 3)


def GetSheetsInfo(vclass):
    srefs = vclass.EditorSheets
    sheetsinfo = {}
    i = 0
    while srefs.position >= 0:
        sheetsinfo[i] = [srefs.Name[srefs.OID], [], srefs.WWWDisabled.ValuesAsInt(srefs.OID)]
        i = i + 1
        srefs.Next()
    if sheetsinfo == {}:
        sheetsinfo[0] = [vclass.NameOfClass, [], 0]

    def ffunc(aclass, afield, sheetsinfo):
        if afield.WWWDisabled or afield.IsInteractive != '1':
            return
        fsi = int(afield.FieldSheetID)
        fti = int(afield.FieldTabIndex)
        if not sheetsinfo.has_key(fsi):
            fsi = 0
        s = afield.FieldNameAsDisplayed
        if s == '':
            s = afield.Name
        sheetsinfo[fsi][1].append([fti, s, afield])

    vclass.ForEachField(ffunc, sheetsinfo)
    for akey in sheetsinfo.keys():
        afields = sheetsinfo[akey][1]
        afields.sort()
        sheetsinfo[akey][1] = afields
    return sheetsinfo


def DoSheetGet(file, acid, OID, asheet, UID, brcid=-1, broid=-1):
    eclass = aICORDBEngine.Classes[acid]
    sheetsinfo = GetSheetsInfo(eclass)
    if asheet < 0:
        WriteHeader(file, eclass, sheetsinfo, OID)
    else:
        WriteFieldSheet(file, sheetsinfo[asheet][0], sheetsinfo[asheet][1], asheet, eclass, OID, UID, brcid=brcid, broid=broid)
