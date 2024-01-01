# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from CLASSES_Library_NetBase_WWW_Server_DoContentsView import *
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import cStringIO

apagesrc = r"""
<SCRIPT LANGUAGE=javascript>

function button1_onclick() {
   if (window.parent.frames("DHTMLEDITPANE1").document.getElementById("tbContentElement").Busy) return;
   if (window.parent.frames("DHTMLEDITPANE2").document.getElementById("tbContentElement").Busy) return;
   atext1=window.parent.frames("DHTMLEDITPANE1").document.getElementById("tbContentElement").DOM.body.innerHTML;
   document.getElementById("me_pagehtmlinfo").value=atext1;
   atext2=window.parent.frames("DHTMLEDITPANE2").document.getElementById("tbContentElement").DOM.body.innerHTML;
   document.getElementById("me_pagehtml").value=atext2;
   document.getElementById("me_pagehtml").value=atext2;
   document.getElementById("form1").submit();
}
</SCRIPT>
"""


def GenerateMenuItemEditor(file, aoid, uid=0):
    amenu = ICORWWWMenuItem(0, aoid)
    if not amenu.IsVisibleByProfile(uid):
        return
    aserver = ICORWWWServer()
    aserver.file = file
    file.write('<SCRIPT LANGUAGE=javascript>\n')
    file.write('function onMenuPageLoad() {\n')
    file.write('   DHTMLEditPageInfo.AbsoluteDropMode= true;\n')
    file.write('   DHTMLEditPageInfo.ShowBorders = false;\n')
    file.write('   DHTMLEditPageInfo.Refresh();\n')
    s = amenu.PageHTMLInfo
    aline = ICORUtil.GetTextAsHTMLText(s)
    aline = ICORUtil.GetStringAsSafeScriptString(aline)
    #   aline=string.replace(aline,chr(13),'')
    #   for c in ['"',"'",'%']: #"
    #      aline=string.replace(aline,c,'&#'+str(ord(c))+';')
    #   aline=string.replace(aline,chr(10),' \\\n')
    file.write('   atext=\'<html><head><meta http-equiv="X-UA-Compatible" content="IE=8"><meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8"></head><body>\'+"' + aline + '"+"</body></html>";\n')    #'
    file.write('   DHTMLEditPageInfo.DocumentHTML=atext;\n')
    file.write('   DHTMLEditPage.Refresh();\n')
    s = amenu.PageHTML
    aline = ICORUtil.GetTextAsHTMLText(s)
    aline = ICORUtil.GetStringAsSafeScriptString(aline)
    #   aline=string.replace(aline,chr(13),'')
    #   aline=string.replace(aline,'"','""') #"
    #   aline=string.replace(aline,"'","''") #'
    #   aline=string.replace(aline,chr(10),' \\\n')
    file.write('   atext=\'<html><head><meta http-equiv="X-UA-Compatible" content="IE=8"><meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8"></head><body>\'+"' + aline + '"+"</body></html>";\n')    #'
    file.write('   DHTMLEditPage.DocumentHTML=atext;\n')
    file.write('}\n')
    file.write('</SCRIPT>\n')

    file.write(apagesrc)
    file.write('<form ID=form1 METHOD="post" ACTION="icormain.asp?jobtype=menuitemeditsubmit&OID=%d">\n' % (amenu.oid))
    file.write('<table>\n')
    file.write('<tr><td align="right">Nagłówek: </td><td><INPUT type="text" id=me_caption name=me_caption size=60 value="%s"></td></tr>\n' % (amenu.Caption))
    file.write('<tr><td align="right">Nagłówek strony: </td><td><INPUT type="text" id=me_aspagecaption name=me_aspagecaption size=60 value="%s"></td></tr>\n' % (amenu.AsPageCaption))
    file.write('<tr><td align="right">Podnagłówek strony: </td><td><INPUT type="text" id=me_aspagesubcaption name=me_aspagesubcaption size=60 value="%s"></td></tr>\n' % (amenu.AsPageSubCaption))
    file.write('<tr><td align="right">Krótki opis strony: </td><td><textarea id=me_aspageshortdescription name=me_aspageshortdescription spellcheck="false" cols=60 rows=6>%s</textarea></td></tr>\n' % (amenu.AsPageShortDescription))
    file.write('<tr><td align="right">Opis strony: </td><td><textarea id=me_aspagedescription name=me_aspagedescription spellcheck="false" cols=60 rows=6>%s</textarea></td></tr>\n' % (amenu.AsPageDescription))

    file.write('</table>\n')
    file.write('<INPUT type="hidden" id=me_pagehtmlinfo name=me_pagehtmlinfo value="">')
    file.write('<INPUT type="hidden" id=me_pagehtml name=me_pagehtml value="">')
    #   file.write('<br><br><input TYPE="submit" VALUE=" Zapamiętaj zmiany " tabIndex=1></FORM>\n')
    file.write('</FORM>\n')

    file.write('Informacje o stronie<br><P align=center><OBJECT classid="clsid:2D360200-FFF5-11d1-8D03-00A0C959BC0A" id=DHTMLEditPageInfo height="75%" width="100%" VIEWASTEXT></OBJECT></P>\n')
    file.write('Zawartość strony<br><P align=center><OBJECT classid="clsid:2D360200-FFF5-11d1-8D03-00A0C959BC0A" id=DHTMLEditPage height="75%" width="100%" VIEWASTEXT></OBJECT></P>')
    file.write('<br><br><input TYPE="button" ID=button1 VALUE=" Zapamiętaj zmiany " tabIndex=1 LANGUAGE=javascript onclick="return button1_onclick()">\n')


def GenerateMenuItemFramePage(file, aoid, avalue, uid=0):
    amenu = ICORWWWMenuItem(uid, aoid)
    if not amenu.IsVisibleByProfile(uid):
        pfile.write('<h1><font color="red">Brak uprawnień do edycji strony!</font></h1>')
        return
    if avalue == "":
        fn1 = amenu.GetMenuRef(1, 'parms')
        fn2 = amenu.GetMenuRef(1, 'edesc', 1, 1)
        fn3 = amenu.GetMenuRef(1, 'evalue', 1, 1)
        amainframepagesrc = """
<frameset NAME="MENUEDITFRAMESET" id="MENUEDITFRAMESET" FRAMEBORDER="0" FRAMESPACING="0" BORDER="NO" rows="100%%,0,0">
  <frame NAME="MENUPARAMETERS" id="MENUPARAMETERS" SRC="%s" SCROLLING="YES">
  <frame NAME="DHTMLEDITPANE1" id="DHTMLEDITPANE1" SRC="%s" scrolling="auto">
  <frame NAME="DHTMLEDITPANE2" id="DHTMLEDITPANE2" SRC="%s" scrolling="auto">
</frameset>
      """ % (fn1, fn2, fn3)
        file.write(amainframepagesrc)
        return
    elif avalue == 'parms':
        #   file.write(apagesrc)
        file.write("""
<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick='window.parent.document.getElementById("MENUEDITFRAMESET").rows="100%%,0,0"'>Parametry strony</button>
<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick='window.parent.document.getElementById("MENUEDITFRAMESET").rows="64px,90%%,0"'>Opis strony</button>
<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick='window.parent.document.getElementById("MENUEDITFRAMESET").rows="64px,0%,90%%"'>Treść</button>
""")
        file.write(apagesrc)
        file.write('<form ID=form1 METHOD="post" ACTION="icormain.asp?jobtype=menuitemeditsubmit&OID=%d">\n' % (amenu.oid))
        file.write('<table>\n')
        file.write('<tr><td align="right">Nagłówek: </td><td><INPUT type="text" id=me_caption name=me_caption size=60 value="%s"></td></tr>\n' % (amenu.Caption))
        file.write('<tr><td align="right">Nagłówek strony: </td><td><INPUT type="text" id=me_aspagecaption name=me_aspagecaption size=60 value="%s"></td></tr>\n' % (amenu.AsPageCaption))
        file.write('<tr><td align="right">Podnagłówek strony: </td><td><INPUT type="text" id=me_aspagesubcaption name=me_aspagesubcaption size=60 value="%s"></td></tr>\n' % (amenu.AsPageSubCaption))
        file.write('<tr><td align="right">Krótki opis strony: </td><td><textarea id=me_aspageshortdescription name=me_aspageshortdescription spellcheck="false" cols=60 rows=6>%s</textarea></td></tr>\n' % (amenu.AsPageShortDescription))
        file.write('<tr><td align="right">Opis strony: </td><td><textarea id=me_aspagedescription name=me_aspagedescription spellcheck="false" cols=60 rows=6>%s</textarea></td></tr>\n' % (amenu.AsPageDescription))
        file.write('</table>\n')
        file.write('<INPUT type="hidden" id=me_pagehtmlinfo name=me_pagehtmlinfo value="">')
        file.write('<INPUT type="hidden" id=me_pagehtml name=me_pagehtml value="">')
        file.write('</FORM>\n')
        file.write('<br><br><input TYPE="button" ID=button1 VALUE=" Zapamiętaj zmiany " tabIndex=1 LANGUAGE=javascript onclick="return button1_onclick()">\n')
        file.write("""
""")

    elif avalue == 'edesc':
        fname = FilePathAsSystemPath(aICORWWWServerInterface.AppPath + 'inc/FullEdit1a.htm')
        fin = open(fname, 'r')
        try:
            file.write(fin.read())
        finally:
            fin.close()

        file.write('<SCRIPT LANGUAGE=javascript>\n')
        file.write('function onMenuPageLoad() {\n')
        file.write('   tbContentElement.Refresh();\n')
        aline = ICORUtil.GetTextAsHTMLText(amenu.PageHTMLInfo)
        aline = ICORUtil.GetStringAsSafeScriptString(aline)
        file.write('   atext=\'<html><head><meta http-equiv="X-UA-Compatible" content="IE=8"><meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8"></head><body>\'+"' + aline + '"+"</body></html>";\n')    #'
        file.write('   tbContentElement.DocumentHTML=atext;\n')
        file.write('}\n')
        file.write('</SCRIPT>\n')

        file.write('<body LANGUAGE="javascript" onload="window_onload(); return onMenuPageLoad();">')

        fname = FilePathAsSystemPath(aICORWWWServerInterface.AppPath + 'inc/FullEdit1b.htm')
        fin = open(fname, 'r')
        try:
            file.write(fin.read())
        finally:
            fin.close()
    elif avalue == 'evalue':
        fname = FilePathAsSystemPath(aICORWWWServerInterface.AppPath + 'inc/FullEdit1a.htm')
        fin = open(fname, 'r')
        try:
            file.write(fin.read())
        finally:
            fin.close()

        file.write('<SCRIPT LANGUAGE=javascript>\n')
        file.write('function onMenuPageLoad() {\n')
        file.write('   tbContentElement.Refresh();\n')
        aline = ICORUtil.GetTextAsHTMLText(amenu.PageHTML)
        aline = ICORUtil.GetStringAsSafeScriptString(aline)
        file.write('   atext=\'<html><head><meta http-equiv="X-UA-Compatible" content="IE=8"><meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8"></head><body>\'+"' + aline + '"+"</body></html>";\n')    #'
        file.write('   tbContentElement.DocumentHTML=atext;\n')
        file.write('}\n')
        file.write('</SCRIPT>\n')

        file.write('<body LANGUAGE="javascript" onload="window_onload(); return onMenuPageLoad();">')

        fname = FilePathAsSystemPath(aICORWWWServerInterface.AppPath + 'inc/FullEdit1b.htm')
        fin = open(fname, 'r')
        try:
            file.write(fin.read())
        finally:
            fin.close()
    return


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    if OID < 0:
        return


#   fname=FilePathAsSystemPath(aICORWWWServerInterface.OutputPath+'MIE_'+str(OID)+'_'+Value+'.html')
    file = cStringIO.StringIO()
    #   file=open(fname,'wb')
    #   try:
    GenerateMenuItemFramePage(file, OID, Value, UID)
    #   finally:
    #      file.close()
    return file.getvalue()
