# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import string
import cStringIO


def GenerateMenuAsPage(file, aoid, uid=0):
    amenu = ICORWWWMenuItem(uid, aoid)
    if not amenu.IsVisibleByProfile(uid):
        return
    #file.write('<center><P class=menuaspagecaption>%s</P>\n'%amenu.AsPageCaption)
    #file.write('<P class=menuaspagesubcaption>%s</P></center>\n'%amenu.AsPageSubCaption)
    file.write('<script type="text/javascript">\n')
    file.write('thisPageTitle="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageCaption)))
    file.write('thisPageSubTitle="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageSubCaption)))
    file.write('thisPageAction="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.Action)))
    file.write('thisPageDescription="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageDescription)))
    file.write('</script>\n')
    #s=amenu.AsPageDescription
    #if s!='':
    #   file.write('<p>%s</p>\n' % s)
    amenu.Reports.First()
    while amenu.Reports.position >= 0:
        mname = amenu.Reports.PageMethod[amenu.Reports.OID]
        mname = mname.replace('\\', '_')
        mname = mname.replace('/', '_')
        pagemethod = __import__(mname)
        pageevent = getattr(pagemethod, amenu.Reports.PageMethodEvent[amenu.Reports.OID])
        if pageevent is not None:
            apply(pageevent, (amenu, file))
        amenu.Reports.Next()
    if amenu.SubMenus != []:
        file.write('<hr>\n')
        file.write('<table>\n')
        for smenu in amenu.SubMenus:
            if not smenu.IsVisibleByProfile(uid):
                continue
            file.write('<tr><td><a')
            alink = 'icormain.asp?jobtype=menuaspage&OID=' + str(smenu.oid)
            file.write(' HREF="%s" ' % alink)
            s = smenu.AsPageSubCaption
            if s != '':
                s = smenu.AsPageCaption + ' ' + s
            else:
                s = smenu.AsPageCaption
            file.write('>%s</a></td>\n' % s)
            file.write('<td>%s</td></tr>\n' % smenu.AsPageShortDescription)
        file.write('</table>\n')
