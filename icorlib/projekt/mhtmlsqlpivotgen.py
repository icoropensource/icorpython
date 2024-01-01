# -*- coding: utf-8 -*-
from icorlib.icorinterface import *


def GetMainPivotPage(axmldata, aquerysql):
    ret = """
Application.Lock
atmpfilecounter=CStr(Dession("TmpClientFileCounter"))
Dession("TmpClientFileCounter")=1+Dession("TmpClientFileCounter")
if Dession("TmpClientFileCounter")>10 then
   Dession("TmpClientFileCounter")=1
end if
Application.UnLock
%%>
<div id=myinfo1><h1>Proszę czekać, trwa ładowanie danych do tabeli przestawnej...</h1></div>
<div id=mypivot1 style="display:none;">
<br>
<TABLE class='objectsviewtable'><CAPTION class='objectsviewcaption'>%s</CAPTION><TR><TD>
<object classid=clsid:0002E520-0000-0000-C000-000000000046 id="PTable1">
</object>
</TD></TR></TABLE>
</div>

<SCRIPT LANGUAGE=VBScript>
Function GetTempFileName
   Set fso = CreateObject("Scripting.FileSystemObject")
   Set tfolder = fso.GetSpecialFolder(2) 'TempFolder
   tpath=tfolder.Path
   GetTempFileName = fso.BuildPath(tpath, "pivot_tmp_data_<%%=atmpfilecounter%%>.bin")
   If fso.FileExists(GetTempFileName) Then
      fso.DeleteFile GetTempFileName,True
   End If
   Set tfolder=Nothing
   Set fso=Nothing
End Function

Function LoadData
      Set rs1 = CreateObject("ADODB.Recordset")
      afname=GetTempFileName()
      rs1.open window.location.protocol & "//" & window.location.hostname & "/icormanager/%s%s"
      rs1.Save afname, 0 'adPersistADTG
      if rs1.State<>0 then 'adStateClosed
         rs1.Close
      end if
      set rs1=Nothing
      PTable1.ConnectionString = "provider=mspersist"
      PTable1.CommandText = afname
      PTable1.BackColor="Ivory"
      With PTable1.ActiveView
""" % (axmldata.Title, axmldata.CRM.AppPath, axmldata.PageFile + '_xr.asp',
       )
    for afield in aquerysql.PivotRowFields:
        ret = ret + """
         .RowAxis.InsertFieldSet .FieldSets("%s")
""" % (afield.PrettyName)
    for afield in aquerysql.PivotColumnFields:
        ret = ret + """
         .ColumnAxis.InsertFieldSet .FieldSets("%s")
""" % (afield.PrettyName)
    for afield in aquerysql.PivotDataFields:
        ret = ret + """
         .DataAxis.InsertTotal .AddTotal("%s Total", _
            .FieldSets("%s").Fields(0), PTable1.Constants.plFunctionSum)
         .Totals("%s Total").NumberFormat = "#"
""" % (afield.PrettyName, afield.PrettyName, afield.PrettyName, )
    ret = ret + """
         PTable1.AllowDetails = False
         '.Fieldsets("Rodzaj").Fields(0).SubTotals(1) = True
         .FilterAxis.Label.Visible = False
         PTable1.DisplayToolbar = True
         PTable1.AllowPropertyToolbox = True
         .TitleBar.Visible = False
         .TotalBackColor = "Ivory"
         .FieldLabelBackColor = "DarkBlue"
         .FieldLabelFont.Color = "White"
         .ColumnAxis.Fieldsets(0).Fields(0).SubTotalBackColor = "LightSteelBlue"
         .RowAxis.Fieldsets(0).Fields(0).SubTotalBackColor = "LightSteelBlue"
         .MemberBackColor = "Lavender"
      End With
   document.getElementById("myinfo1").style.display="none"
   document.getElementById("mypivot1").style.display=""
End Function

window.setTimeout GetRef("LoadData")
</SCRIPT>
<%
"""
    return ret


def GetXMLRecordsetPage(axmldata, querysql):
    ret = """
<%%@ LANGUAGE="VBSCRIPT" %%>
<!-- #include file="%sadovbs.inc" -->
<%%
Response.ContentType = "application/octet-stream"
Set cn = Server.CreateObject("ADODB.Connection")
'cn.CursorLocation=adUseClient
cn.Open "%s"
cn.CommandTimeout=0
aispivot=1
%s
Set rs=Server.CreateObject("ADODB.Recordset")
rs.ActiveConnection = cn
rs.Source="%s"
rs.Open
if not rs.EOF then
   rs.Save Response, adPersistASTG
else
   Response.Write "<h1>Brak danych</h1>"
end if
if rs.State<>adStateClosed then
   rs.Close
end if
Set rs=Nothing
Set cn=Nothing
%%>
""" % (axmldata.CRM.IncPath, axmldata.CRM.SQLCreator.ConnectionString, axmldata.ASPSourceOnBeforeGetData, querysql.SQLString)
    return ret
