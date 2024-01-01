# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import string


def GenerateMenuAsSummaryList(file, aoid, uid=0):
    amenu = ICORWWWMenuItem(0, aoid)
    if not amenu.IsVisibleByProfile(uid):
        return
    file.write('<center><P class=menuaspagecaption>%s</P>\n' % amenu.AsPageCaption)
    file.write('<P class=menuaspagesubcaption>%s</P></center>\n' % amenu.AsPageSubCaption)
    s = amenu.AsPageDescription
    if s != '':
        file.write('<p>%s</p>\n' % s)
    sclass = aICORDBEngine.Classes[amenu.ParamItem]
    if sclass is None:
        return
    cobj = aICORDBEngine.Classes.MetaClass[sclass.CID]
    sobj = cobj.aSummaries
    sclass = sobj.Class
    slist = []
    sdict = {}
    while sobj.Exists():
        if sobj.Class.WWWDisabled.ValuesAsInt(sobj.OID) != 1:
            gname = sobj.SummaryData1
            if not sdict.has_key(gname):
                sdict[gname] = []
                slist.append(gname)
            sdict[gname].append(sobj.OID)
        sobj.Next()
    for gname in slist:
        w = 0
        olist = sdict[gname]
        i = 1
        for aoid in olist:
            if not w:
                file.write('<UL>%s\n' % (gname))
                w = 1
            sobj = sclass[aoid]
            s = '<li><a class="fg-button-single ui-state-default ui-corner-all uihover" HREF="icormain.asp?jobtype=summaryparameters&OID=%d">%d. %s</a></li>\n' % (aoid, i, sobj.Name)
            file.write(s)
            i = i + 1
        if w:
            file.write('</UL>\n')
    return
