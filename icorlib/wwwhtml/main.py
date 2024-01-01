# -*- coding: utf-8 -*-


def GetSpellOnlyScriptText():
   aScriptText="""
<script language="javascript">
var drPopup=null;
if (isIE()) {
   drPopup = window.createPopup();
}
var drBase = 0;

function processCheckSpelling(avalue) {
   if (isIE()) {
      drPopup.hide();
   }
   checkSpelling(drBase,avalue);
}

function processSpellCommand(abase,arelative) {
   abase.focus();
   drBase=abase;
   if (isIE()) {
      drPopup.document.body.innerHTML=oContextSpelling.innerHTML;
      drPopup.show(0, 20, 120, 80, arelative);
   }
}
</SCRIPT>

<DIV ID="oContextSpelling" STYLE="display:none;">
    <DIV ONCLICK="parent.processCheckSpelling('pl');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer;"><font size="1"><img border="0" src="/icormanager/images/flags/lang_pl.png" alt="polski">&nbsp;- polski</font></DIV>
    <DIV ONCLICK="parent.processCheckSpelling('en');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1"><img border="0" src="/icormanager/images/flags/lang_en.png" alt="angielski">&nbsp;- angielski</font></DIV>
    <DIV ONCLICK="parent.processCheckSpelling('de');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1"><img border="0" src="/icormanager/images/flags/lang_de.png" alt="niemiecki">&nbsp;- niemiecki</font></DIV>
</DIV>
"""
   return aScriptText
def GetScriptText():
   aScriptText="""
<script language="javascript">
var drPopup=null;
if (isIE()) {
   drPopup = window.createPopup();
}
var dLastCommand = "";
var drBase = 0;
var drDoc = "";

function showPopupDR(abase,asrc,dx,dy) {
   if (dx<0) {
     dx=300;
   }
   if (dy<0) {
     dy=200;
   }
   drBase=abase;
   dLastCommand=window.event.srcElement.mCommand;
   if (isIE()) {
      drPopup.document.body.innerHTML = asrc.innerHTML;
      drPopup.show(0, 20, dx, dy, window.event.srcElement);
   }
}

function processPopup(avalue) {
   drBase.document.execCommand(dLastCommand,1,avalue);
   if (isIE()) {
      drPopup.hide();
   }
}

function processCheckSpelling(avalue) {
   if (isIE()) {
      drPopup.hide();
   }
   checkSpelling(document.getElementById(drDoc),avalue);
}

function processMTCommand(abase) {
   abase.focus();
   var aelm=window.event.srcElement;
   var acmd=aelm.mCommand;
   if (acmd==undefined) {
      return;
   }
   if (acmd=="FontName") {
      showPopupDR(abase,oContextFontNames,-1,-1);
      return;
   }
   if (acmd=="FontSize") {
      showPopupDR(abase,oContextFontSizes,-1,-1);
      return;
   }
   if (acmd=="BackColor") {
      showPopupDR(abase,oContextColors,-1,-1);
      return;
   }
   if (acmd=="ForeColor") {
      showPopupDR(abase,oContextColors,-1,-1);
      return;
   }
   if (acmd=="FormatBlock") {
      showPopupDR(abase,oContextFormats,-1,-1);
      return;
   }
   if (acmd=="CheckSpelling") {
      drDoc=aelm.mDoc;
      showPopupDR(abase,oContextSpelling,150,80);
      return;
   }
   abase.document.execCommand(acmd);
}

var swapToMode='CODE';
function swapDisplayMode(adoc) {
  if(swapToMode=='CODE') {
     try {
        adoc.document.body.clearAttributes;
        adoc.document.body.style.fontFamily='Courier New';
        adoc.document.body.style.fontSize='10pt';
        adoc.document.body.innerText=adoc.document.body.innerHTML;
        swapToMode='RICH';
     }
     catch(e) {
     }
  } else {
     try {
        adoc.document.body.style.fontFamily='';
        adoc.document.body.style.fontSize='';
        adoc.document.body.innerHTML=adoc.document.body.innerText;
        swapToMode='CODE';
     } 
     catch(e) {
     }
  };
}
</script>

<DIV ID="oContextFontSizes" STYLE="display:none;">
<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:200px; border-bottom:2px solid black;" >
    <DIV ONCLICK="parent.processPopup('1');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><font size="1">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('2');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="2">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('3');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="3">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('4');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="4">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('5');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="5">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('6');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="6">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('7');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="7">ABCDEFabcdef...</font></DIV>
</div>
</DIV>

<DIV ID="oContextSpelling" STYLE="display:none;">
    <DIV ONCLICK="parent.processCheckSpelling('pl');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer;"><font size="1"><img border="0" src="/icormanager/images/flags/lang_pl.png" alt="polski">&nbsp;- polski</font></DIV>
    <DIV ONCLICK="parent.processCheckSpelling('en');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1"><img border="0" src="/icormanager/images/flags/lang_en.png" alt="angielski">&nbsp;- angielski</font></DIV>
    <DIV ONCLICK="parent.processCheckSpelling('de');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1"><img border="0" src="/icormanager/images/flags/lang_de.png" alt="niemiecki">&nbsp;- niemiecki</font></DIV>
</DIV>

<DIV ID="oContextFormats" STYLE="display:none;">
<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:200px; border-bottom:2px solid black;" >
    <DIV ONCLICK="parent.processPopup('<h1>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><h1>Nagłówek 1</h1></DIV>
    <DIV ONCLICK="parent.processPopup('<h2>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><h2>Nagłówek 2</h2></DIV>
    <DIV ONCLICK="parent.processPopup('<h3>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><h3>Nagłówek 3</h3></DIV>
    <DIV ONCLICK="parent.processPopup('<h4>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><h4>Nagłówek 4</h4></DIV>
    <DIV ONCLICK="parent.processPopup('<h5>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><h5>Nagłówek 5</h5></DIV>
    <DIV ONCLICK="parent.processPopup('<h6>');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><h6>Nagłówek 6</h6></DIV>
</div>
</DIV>

<DIV ID="oContextFontNames" STYLE="display:none;">
<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:200px; border-bottom:2px solid black;" >
    <DIV ONCLICK="parent.processPopup('Arial');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><font size="1">Arial:<br></font><font face="Arial">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('Verdana');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Verdana:<br></font><font face="Verdana">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('Tahoma');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Tahoma:<br></font><font face="Tahoma">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('Times New Roman');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Times New Roman:<br></font><font face="Times New Roman">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('Courier New');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Courier New:<br></font><font face="Courier New">ABCDEFabcdef...</font></DIV>
    <DIV ONCLICK="parent.processPopup('Wingdings');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Wingdings:<br></font><font face="Wingdings">ABCDEabcde</font></DIV>
    <DIV ONCLICK="parent.processPopup('Symbol');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black"><font size="1">Symbol:<br></font><font face="Symbol">ABCDEFabcdef...</font></DIV>
</div>
</DIV>

<DIV ID="oContextColors" STYLE="display:none;">
<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:200px; border-bottom:2px solid black;" >
    <DIV ONCLICK="parent.processPopup('black');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#000000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;black</font></DIV>
    <DIV ONCLICK="parent.processPopup('navy');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#000080;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;navy</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00008b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#0000cd;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('blue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#0000ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;blue</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#006400;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('green');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#008000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;green</font></DIV>
    <DIV ONCLICK="parent.processPopup('teal');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#008080;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;teal</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkcyan');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#008b8b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkcyan</font></DIV>
    <DIV ONCLICK="parent.processPopup('deepskyblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00bfff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;deepskyblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkturquoise');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00ced1;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkturquoise</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumspringgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00fa9a;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumspringgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('lime');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00ff00;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lime</font></DIV>
    <DIV ONCLICK="parent.processPopup('springgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00ff7f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;springgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('aqua');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00ffff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;aqua</font></DIV>
    <DIV ONCLICK="parent.processPopup('cyan');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#00ffff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;cyan</font></DIV>
    <DIV ONCLICK="parent.processPopup('midnightblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#191970;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;midnightblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('dodgerblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#1e90ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;dodgerblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightseagreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#20b2aa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightseagreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('forestgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#228b22;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;forestgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('seagreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#2e8b57;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;seagreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkslategray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#2f4f4f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkslategray</font></DIV>
    <DIV ONCLICK="parent.processPopup('limegreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#32cd32;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;limegreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumseagreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#3cb371;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumseagreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('turquoise');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#40e0d0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;turquoise</font></DIV>
    <DIV ONCLICK="parent.processPopup('royalblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#4169e1;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;royalblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('steelblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#4682b4;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;steelblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkslateblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#483d8b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkslateblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumturquoise');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#48d1cc;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumturquoise</font></DIV>
    <DIV ONCLICK="parent.processPopup('indigo');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#4b0082;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;indigo</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkolivegreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#556b2f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkolivegreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('cadetblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#5f9ea0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;cadetblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('cornflower');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#6495ed;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;cornflower</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumaquamarine');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#66cdaa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumaquamarine</font></DIV>
    <DIV ONCLICK="parent.processPopup('dimgray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#696969;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;dimgray</font></DIV>
    <DIV ONCLICK="parent.processPopup('slateblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#6a5acd;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;slateblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('olivedrab');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#6b8e23;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;olivedrab</font></DIV>
    <DIV ONCLICK="parent.processPopup('slategray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#708090;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;slategray</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightslategray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#778899;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightslategray</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumslateblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#7b68ee;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumslateblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('lawngreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#7cfc00;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lawngreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('chartreuse');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#7fff00;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;chartreuse</font></DIV>
    <DIV ONCLICK="parent.processPopup('aquamarine');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#7fffd4;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;aquamarine</font></DIV>
    <DIV ONCLICK="parent.processPopup('maroon');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#800000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;maroon</font></DIV>
    <DIV ONCLICK="parent.processPopup('purple');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#800080;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;purple</font></DIV>
    <DIV ONCLICK="parent.processPopup('olive');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#808000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;olive</font></DIV>
    <DIV ONCLICK="parent.processPopup('gray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#808080;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;gray</font></DIV>
    <DIV ONCLICK="parent.processPopup('skyblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#87ceeb;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;skyblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightskyblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#87cefa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightskyblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('blueviolet');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#8a2be2;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;blueviolet</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkred');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#8b0000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkred</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkmagenta');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#8b008b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkmagenta</font></DIV>
    <DIV ONCLICK="parent.processPopup('saddlebrown');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#8b4513;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;saddlebrown</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkseagreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#8fbc8b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkseagreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#90ee90;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumpurple');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#9370db;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumpurple</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkviolet');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#9400d3;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkviolet</font></DIV>
    <DIV ONCLICK="parent.processPopup('palegreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#98fb98;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;palegreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkorchid');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#9932cc;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkorchid</font></DIV>
    <DIV ONCLICK="parent.processPopup('yellowgreen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#9acd32;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;yellowgreen</font></DIV>
    <DIV ONCLICK="parent.processPopup('sienna');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#a0522d;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;sienna</font></DIV>
    <DIV ONCLICK="parent.processPopup('brown');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#a52a2a;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;brown</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkgray');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#a9a9a9;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkgray</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#add8e6;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('greenyellow');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#adff2f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;greenyellow</font></DIV>
    <DIV ONCLICK="parent.processPopup('paleturquoise');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#afeeee;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;paleturquoise</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightsteelblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#b0c4de;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightsteelblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('powderblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#b0e0e6;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;powderblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('firebrick');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#b22222;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;firebrick</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkgoldenrod');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#b8860b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkgoldenrod</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumorchid');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ba55d3;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumorchid</font></DIV>
    <DIV ONCLICK="parent.processPopup('rosybrown');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#bc8f8f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;rosybrown</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkkhaki');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#bdb76b;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkkhaki</font></DIV>
    <DIV ONCLICK="parent.processPopup('silver');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#c0c0c0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;silver</font></DIV>
    <DIV ONCLICK="parent.processPopup('mediumvioletred');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#c71585;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mediumvioletred</font></DIV>
    <DIV ONCLICK="parent.processPopup('indianred');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#cd5c5c;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;indianred</font></DIV>
    <DIV ONCLICK="parent.processPopup('peru');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#cd853f;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;peru</font></DIV>
    <DIV ONCLICK="parent.processPopup('chocolate');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#d2691e;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;chocolate</font></DIV>
    <DIV ONCLICK="parent.processPopup('tan');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#d2b48c;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;tan</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightgrey');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#d3d3d3;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightgrey</font></DIV>
    <DIV ONCLICK="parent.processPopup('thistle');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#d8bfd8;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;thistle</font></DIV>
    <DIV ONCLICK="parent.processPopup('orchid');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#da70d6;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;orchid</font></DIV>
    <DIV ONCLICK="parent.processPopup('goldenrod');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#daa520;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;goldenrod</font></DIV>
    <DIV ONCLICK="parent.processPopup('palevioletred');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#db7093;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;palevioletred</font></DIV>
    <DIV ONCLICK="parent.processPopup('crimson');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#dc143c;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;crimson</font></DIV>
    <DIV ONCLICK="parent.processPopup('gainsboro');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#dcdcdc;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;gainsboro</font></DIV>
    <DIV ONCLICK="parent.processPopup('plum');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#dda0dd;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;plum</font></DIV>
    <DIV ONCLICK="parent.processPopup('burlywood');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#deb887;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;burlywood</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightcyan');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#e0ffff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightcyan</font></DIV>
    <DIV ONCLICK="parent.processPopup('lavender');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#e6e6fa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lavender</font></DIV>
    <DIV ONCLICK="parent.processPopup('darksalmon');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#e9967a;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darksalmon</font></DIV>
    <DIV ONCLICK="parent.processPopup('violet');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ee82ee;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;violet</font></DIV>
    <DIV ONCLICK="parent.processPopup('palegoldenrod');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#eee8aa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;palegoldenrod</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightcoral');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f08080;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightcoral</font></DIV>
    <DIV ONCLICK="parent.processPopup('khaki');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f0e68c;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;khaki</font></DIV>
    <DIV ONCLICK="parent.processPopup('aliceblue');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f0f8ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;aliceblue</font></DIV>
    <DIV ONCLICK="parent.processPopup('honeydew');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f0fff0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;honeydew</font></DIV>
    <DIV ONCLICK="parent.processPopup('azure');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f0ffff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;azure</font></DIV>
    <DIV ONCLICK="parent.processPopup('sandybrown');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f4a460;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;sandybrown</font></DIV>
    <DIV ONCLICK="parent.processPopup('wheat');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f5deb3;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;wheat</font></DIV>
    <DIV ONCLICK="parent.processPopup('beige');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f5f5dc;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;beige</font></DIV>
    <DIV ONCLICK="parent.processPopup('whitesmoke');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f5f5f5;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;whitesmoke</font></DIV>
    <DIV ONCLICK="parent.processPopup('mintcream');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f5fffa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mintcream</font></DIV>
    <DIV ONCLICK="parent.processPopup('ghostwhite');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#f8f8ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;ghostwhite</font></DIV>
    <DIV ONCLICK="parent.processPopup('salmon');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fa8072;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;salmon</font></DIV>
    <DIV ONCLICK="parent.processPopup('antiquewhite');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#faebd7;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;antiquewhite</font></DIV>
    <DIV ONCLICK="parent.processPopup('linen');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#faf0e6;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;linen</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightgoldenrodyellow');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fafad2;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightgoldenrodyellow</font></DIV>
    <DIV ONCLICK="parent.processPopup('oldlace');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fdf5e6;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;oldlace</font></DIV>
    <DIV ONCLICK="parent.processPopup('red');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff0000;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;red</font></DIV>
    <DIV ONCLICK="parent.processPopup('fuchsia');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff00ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;fuchsia</font></DIV>
    <DIV ONCLICK="parent.processPopup('magenta');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff00ff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;magenta</font></DIV>
    <DIV ONCLICK="parent.processPopup('deeppink');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff1493;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;deeppink</font></DIV>
    <DIV ONCLICK="parent.processPopup('orangered');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff4500;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;orangered</font></DIV>
    <DIV ONCLICK="parent.processPopup('tomato');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff6347;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;tomato</font></DIV>
    <DIV ONCLICK="parent.processPopup('hotpink');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff69b4;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;hotpink</font></DIV>
    <DIV ONCLICK="parent.processPopup('coral');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff7f50;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;coral</font></DIV>
    <DIV ONCLICK="parent.processPopup('darkorange');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ff8c00;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;darkorange</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightsalmon');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffa07a;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightsalmon</font></DIV>
    <DIV ONCLICK="parent.processPopup('orange');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffa500;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;orange</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightpink');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffb6c1;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightpink</font></DIV>
    <DIV ONCLICK="parent.processPopup('pink');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffc0cb;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;pink</font></DIV>
    <DIV ONCLICK="parent.processPopup('gold');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffd700;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;gold</font></DIV>
    <DIV ONCLICK="parent.processPopup('peachpuff');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffdab9;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;peachpuff</font></DIV>
    <DIV ONCLICK="parent.processPopup('navajowhite');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffdead;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;navajowhite</font></DIV>
    <DIV ONCLICK="parent.processPopup('moccasin');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffe4b5;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;moccasin</font></DIV>
    <DIV ONCLICK="parent.processPopup('bisque');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffe4c4;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;bisque</font></DIV>
    <DIV ONCLICK="parent.processPopup('mistyrose');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffe4e1;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;mistyrose</font></DIV>
    <DIV ONCLICK="parent.processPopup('blanchedalmond');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffebcd;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;blanchedalmond</font></DIV>
    <DIV ONCLICK="parent.processPopup('papayawhip');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffefd5;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;papayawhip</font></DIV>
    <DIV ONCLICK="parent.processPopup('lavenderblush');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fff0f5;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lavenderblush</font></DIV>
    <DIV ONCLICK="parent.processPopup('seashell');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fff5ee;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;seashell</font></DIV>
    <DIV ONCLICK="parent.processPopup('cornsilk');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fff8dc;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;cornsilk</font></DIV>
    <DIV ONCLICK="parent.processPopup('lemonchiffon');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fffacd;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lemonchiffon</font></DIV>
    <DIV ONCLICK="parent.processPopup('floralwhite');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fffaf0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;floralwhite</font></DIV>
    <DIV ONCLICK="parent.processPopup('snow');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fffafa;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;snow</font></DIV>
    <DIV ONCLICK="parent.processPopup('yellow');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffff00;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;yellow</font></DIV>
    <DIV ONCLICK="parent.processPopup('lightyellow');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffffe0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;lightyellow</font></DIV>
    <DIV ONCLICK="parent.processPopup('ivory');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#fffff0;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;ivory</font></DIV>
    <DIV ONCLICK="parent.processPopup('white');" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='wheat'" STYLE="font-family:verdana; height:20px; background:wheat; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;"><span style="background:#ffffff;width:100;height:16;"></span><font size="1">&nbsp;-&nbsp;white</font></DIV>
</div>
</DIV>
"""
   return aScriptText

def GetEditorText(aid='0',awidth='100%',aheight='100%',avalue='',ahref=''):
   ddict={'EditorWidth':awidth,
         'EditorHeight':aheight,
         'ID':aid,
         'Value':avalue,
         'HRefSrc':ahref}
   aEditorText="""
<div align=center style="height:%(EditorHeight)s; width:%(EditorWidth)s; background-color:silver; border:outset;" UNSELECTABLE="on">
   <div align="left" UNSELECTABLE="on">
      <span onclick="javascript:void(processMTCommand(%(ID)sVisible));" UNSELECTABLE="on">
         &nbsp;&nbsp;<img src="images/dots/_.gif" width=1 height=24>
         <img mCommand="Copy" alt="Kopiuj" src="/icormanager/images/toolbar/copy.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Cut" alt="Wytnij" src="/icormanager/images/toolbar/cut.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Paste" alt="Wklej" src="/icormanager/images/toolbar/paste.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Delete" alt="Skasuj" src="/icormanager/images/toolbar/delete.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img onclick="swapDisplayMode(document.frames('%(ID)sVisible'))" alt="Tryb TEXT/HTML" src="/icormanager/images/toolbar/displaymode.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="CheckSpelling" mDoc="%(ID)sVisible" alt="Sprawdź pisownię" src="/icormanager/images/toolbar/spellcheck.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="Undo" alt="Cofnij" src="/icormanager/images/toolbar/undo.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Redo" alt="Powtórz" src="/icormanager/images/toolbar/redo.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="Bold" alt="Pogrubienie" src="/icormanager/images/toolbar/bold.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Italic" alt="Pochylenie" src="/icormanager/images/toolbar/italic.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Underline" alt="Podkreślenie" src="/icormanager/images/toolbar/underline.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="FontName" alt="Czcionka" src="/icormanager/images/toolbar/fontcase.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="FontSize" alt="Rozmiar czcionki" src="/icormanager/images/toolbar/fontsize.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="BackColor" alt="Kolor tła" src="/icormanager/images/toolbar/backcolor.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="ForeColor" alt="Kolor liter" src="/icormanager/images/toolbar/forecolor.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="Superscript" alt="Indeks górny" src="/icormanager/images/toolbar/superscript.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Subscript" alt="Indeks dolny" src="/icormanager/images/toolbar/subscript.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="InsertUnorderedList" alt="Lista" src="/icormanager/images/toolbar/unorderedlist.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="InsertOrderedList" alt="Lista numerowana" src="/icormanager/images/toolbar/orderedlist.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="Outdent" alt="Przesuń w lewo" src="/icormanager/images/toolbar/dedent.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Indent" alt="Przesuń w prawo" src="/icormanager/images/toolbar/indent.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="JustifyLeft" alt="Wyrównaj do lewego marginesu" src="/icormanager/images/toolbar/alignleft.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="JustifyCenter" alt="Wycentruj" src="/icormanager/images/toolbar/aligncenter.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="JustifyRight" alt="Wyrównaj do prawego marginesu" src="/icormanager/images/toolbar/alignright.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="JustifyFull" alt="Wyjustuj" src="/icormanager/images/toolbar/alignjustify.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;
         <img mCommand="FormatBlock" alt="Format" src="/icormanager/images/toolbar/format.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Overwrite" alt="Nadpisywanie/wstawianie" src="/icormanager/images/toolbar/overwrite.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
<!--         &nbsp;&nbsp;
         <img mCommand="CreateLink" src="/icormanager/images/toolbar/hyperlink.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         <img mCommand="Unlink" src="/icormanager/images/toolbar/unlink.png" style="cursor:pointer;" onmousedown='this.className="tbButtonMouseOverDown";' class="tbButton" onmouseover="this.className='tbButtonMouseOverUp';" onmouseup="this.className='tbButtonMouseOverUp';" onmouseout="this.className='tbButton';">
         &nbsp;&nbsp;-->
      </span>
   </div>
  <iframe name=%(ID)sVisible src="%(HRefSrc)s" id=%(ID)sVisible contenteditable align="left" class="normal" style="height:100%%; width:100%%;background-color:WINDOW; border:inset; overflow=auto;">%(Value)s</iframe>
</div>
<script language="javascript">
//try {
//   %(ID)sVisible.document.designMode="On";
//}
//catch(e) {
//}
</script>

<SCRIPT FOR=%(ID)sVisible EVENT=onload LANGUAGE="javascript">
   if (%(ID)sVisible.document.readyState=='complete') {
      %(ID)sVisible.document.charset="utf-8";
      %(ID)sVisible.document.designMode="On";
   }
</SCRIPT>
"""%ddict
   return aEditorText
