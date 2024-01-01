# -*- coding: utf-8 -*-
from icorlib.icorinterface import *

def GetWorksheetText(aid='0',awidth='100%',aheight='100%',avalue='',ahref='',aviewonly=0):
   ddict={'EditorWidth':awidth,
         'EditorHeight':aheight,
         'ID':aid,
         'Value':avalue,
         'HRefSrc':ahref}
   aEditorText="""
<OBJECT classid=clsid:0002E559-0000-0000-C000-000000000046 name=%(ID)sVisible id=%(ID)sVisible style="width=100%%;height=%(EditorHeight)s;"></OBJECT>
"""%ddict
   aOnBeforeLoadText="""
<SCRIPT language="vbscript">
Set axmlhttp%(ID)s = CreateObject("MSXML2.XMLHTTP")

Function xmlHTTPReadyStateChange%(ID)s
   if axmlhttp%(ID)s.ReadyState=4 then
      document.getElementById("%(ID)sVisible").HTMLData = axmlhttp%(ID)s.ResponseText
      Set axmlhttp%(ID)s = Nothing
      document.getElementById("%(ID)sVisible").Refresh
      'document.getElementById("%(ID)sVisible").ActiveSheet.UsedRange.AutoFitColumns
      document.getElementById("%(ID)sVisible").Range("A1").Select
"""%ddict
   aOnLoadText="""
'document.getElementById("%(ID)sVisible").TitleBar.Caption = "Zestawienie"
document.getElementById("%(ID)sVisible").DisplayTitleBar = False
document.getElementById("%(ID)sVisible").Cells.Clear
document.getElementById("%(ID)sVisible").DataType = "HTMLURL"
'document.getElementById("%(ID)sVisible").HTMLURL = "%(HRefSrc)s"
if "%(HRefSrc)s"<>"" then
   document.getElementById("%(ID)sVisible").Cells(1,1).Value="Proszę czekać trwa ładowanie danych..."
   axmlhttp%(ID)s.Open "POST", "%(HRefSrc)s", True
   axmlhttp%(ID)s.Send ""
   axmlhttp%(ID)s.OnReadyStateChange=getRef("xmlHTTPReadyStateChange%(ID)s")
   Window.Status="proszę czekać, trwa ładowanie danych..."
end if
"""%ddict
   aOnAfterLoadText="""
"""%ddict
   if aviewonly:
      aOnBeforeLoadText=aOnBeforeLoadText+"""
'document.getElementById("%(ID)sVisible").DisplayColHeaders = False
'document.getElementById("%(ID)sVisible").DisplayRowHeaders = False
'document.getElementById("%(ID)sVisible").DisplayToolbar = False
document.getElementById("%(ID)sVisible").AllowPropertyToolbox = False
document.getElementById("%(ID)sVisible").Cells.Locked = True
'document.getElementById("%(ID)sVisible").ActiveSheet.Protection.Enabled = True
"""%ddict
   aOnBeforeLoadText=aOnBeforeLoadText+"""
   End If
   Window.Status=""
End Function
</SCRIPT>
"""%ddict
   return aEditorText,aOnLoadText,aOnBeforeLoadText,aOnAfterLoadText
