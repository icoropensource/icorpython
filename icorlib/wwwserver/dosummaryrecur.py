# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORSummary import ICORSummary, SummarySpace2HTML, GenerateAsHTML, GenerateAsHTML_TDC
from icorlib.icormdspace import ICORMDSpace
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import time


def GenerateSummaryRecur(file, rfield, summoid, bcid, boid):
    aspace = ICORMDSpace()
    asummary = ICORSummary(summoid, aspace)
    bclass = aICORDBEngine.Classes[bcid]
    afield = bclass.FieldsByName(rfield)
    arefs = afield.GetRefList(boid)
    start = time.clock()
    acnt = asummary.ProcessAll(arefs.AsObject())

    ipath = FilePathAsSystemPath(aICORWWWServerInterface.AppOutputPath)
    #   GenerateAsHTML(asummary,aspace,file,0,ipath)
    GenerateAsHTML_TDC(asummary, aspace, file, 0, ipath, acnt)

    finish = time.clock()
    if acnt > 0:
        s = '<br><br><hr><br>\n'
        s = s + '<table width="100%"><tr>'
        s = s + '<td>data utworzenia: <B>%s</B></td><td>czas pracy serwera: <B>%0.2f<B> sek.</td>' % (ICORUtil.tdate2fmtstr(ICORUtil.tdatetime()), finish - start)
        s = s + '</tr></table>'
        file.write(s)
    return
