# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
from CLASSES_Library_NetBase_WWW_Server_ServerUtil import ICORReport
from CLASSES_Library_NetBase_WWW_Server_DoSiteMap import DoReportMenu
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string


def DoReportSubmit(file, OID, areport, UID):
    areportoid = areport['ReportOID']
    areport['reportoid'] = areportoid
    amenu = ICORWWWMenuItem(UID, OID)
    #   fnamemodifier=areport.formdict.get('FileNameModifier','')
    #   if fnamemodifier!='':
    #      fnamemodifier='_'+fnamemodifier
    #   fname=FilePathAsSystemPath(aICORWWWServerInterface.OutputPath+'RS_'+str(OID)+'_'+str(areport.reportoid)+fnamemodifier+'.html')
    #   openoutputfile=1
    #   if areport.formdict.get('UseCached','0')=='1' and ICORUtil.FileExists(fname):
    #      if areport.formdict.get('UseLoggedCached','')=='1':
    #         openoutputfile=0
    #      else:
    #         return
    #   if openoutputfile:
    #      file=open(fname,'wb')
    #   else:
    #      file=None
    #   print 'fname:',fname
    #   print 'openoutputfile:',openoutputfile
    #   try:
    if amenu.ViewAs == 'MSWord-MenuTree':
        for rmenu in amenu.ReferredMenu:
            atocnumber = int(areport['firstTOCNumber', '0'])
            if atocnumber == -2:
                atocnumber = areport['firstTOCValue', '1']
            DoReportMenu(rmenu, file, areport['showInfoPages', ''] == '1', areport['MIMEWord', ''] == '1', atocnumber)
    else:
        amenu.Reports.First()
        while amenu.Reports.position >= 0:
            if amenu.Reports.OID == areport.reportoid:
                mname = amenu.Reports.PageMethod[amenu.Reports.OID]
                mname = mname.replace('\\', '_')
                mname = mname.replace('/', '_')
                pagemethod = __import__(mname)
                pageevent = getattr(pagemethod, amenu.Reports.PageMethodEvent[amenu.Reports.OID] + 'Submit')
                if pageevent is not None:
                    apply(pageevent, (amenu, areport, file))
            amenu.Reports.Next()
