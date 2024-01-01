# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORSummary import ICORSummary, SummarySpace2HTML, GenerateAsHTML, GenerateAsHTML_TDC
from icorlib.icormdspace import ICORMDSpace
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import CLASSES_Library_NetBase_WWW_HTML_Office_OWC_ASP_SummaryUtil as SummaryUtil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import time
import string
import cStringIO


def GenerateSummaryExecute(file, OID, areport=None):
    if areport is None:
        formdict = {}
    else:
        formdict = areport
    aspace = ICORMDSpace()
    asummary = ICORSummary(OID, aspace, formdict)
    start = time.clock()
    ipath = FilePathAsSystemPath(aICORWWWServerInterface.AppOutputPath)
    if (formdict.get('MIMESave', '') == '1') or (formdict.get('MIMEExcel', '') == '1') or (formdict.get('MIMEWord', '') == '1') or (formdict.get('SimpleSummary', '') == '1'):
        acnt = asummary.ProcessAll()
        GenerateAsHTML(asummary, aspace, file, 0, asimple=1)
        return
    elif formdict.get('XMLData', '') == '1':
        acnt = asummary.ProcessAll()
        SummaryUtil.GenerateAsXMLData(asummary, aspace, file, acnt)
        return
    elif asummary.IsPivot:
        acnt = 1
        SummaryUtil.GenerateAsOWCPivot(asummary, aspace, file)
    else:
        acnt = asummary.ProcessAll()
        GenerateAsHTML_TDC(asummary, aspace, file, 0, ipath, acnt)

    finish = time.clock()
    if not acnt:
        file.write('<h1>Brak danych spełniających zadane warunki.</h1>')


#   else:
#      s='<br><br>'
##      alink='icormainexcel.asp?jobtype=outputpageget&page=SE_%d.html&mimetype=excel'%(OID)
##      s=s+'<a class=reflistoutred HREF="%s">Przenieś zestawienie do MS Excel</a><br>\n'%(alink)
#      s=s+'<table width="100%"><tr>'
#      s1=ICORUtil.tdatetime2fmtstr(ICORUtil.tdatetime())
#      s1=string.replace(s1,' ','&nbsp;')
#      s=s+'<td><font size="-3"><i>utworzono:</i>&nbsp;<B>%s</B></font></td><td><font size="-3"><i>czas&nbsp;pracy&nbsp;serwera:</i>&nbsp;<B>%0.2f<B>&nbsp;sek.</font></td>'%(s1,finish-start)
#      s=s+'</tr></table>'
#      file.write(s)
    return
