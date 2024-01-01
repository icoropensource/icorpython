# -*- coding: utf-8 -*-
import string

from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorwwwinterface import *
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import appplatform.wserverutil.webutil as webutil


def GenerateDefaultMenuItem(file, aoid, uid=0, aparam='', brcid=-1, broid=-1, checkaction='', jsonres=None):
    amenu = ICORWWWMenuItem(uid, aoid, aparam, brcid=brcid, broid=broid, jsonres=jsonres)
    if not amenu.IsVisibleByProfile(uid):
        return
    if checkaction == '1':
        arefCID, arefOID, arefField = amenu.WWWParam
        ret={
           'action': amenu.Action,
           'refCID': arefCID,
           'refOID': arefOID,
           'refField': arefField,
        } # yapf: disable
        v = webutil.GetJSONResult(ret, 0, '')
        file.write(v)
        return
    file.write('<div class="ui-widget">')    #ui-widget
    file.write('<script type="text/javascript">\n')
    file.write('thisPageTitle="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageCaption)))
    file.write('thisPageSubTitle="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageSubCaption)))
    file.write('thisPageAction="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.Action)))
    file.write('thisPageDescription="%s"\n' % (XMLUtil.GetAsXMLStringSimple(amenu.AsPageDescription)))
    file.write('</script>\n')
    if amenu.Action in ['ObjectApplyMethods', ]:
        file.write('<div class="ui-widget-content">')    #ui-widget-content
        sl = string.split(aparam, '_')
        mname = sl[2]
        mclass = aICORDBEngine.Classes[int(sl[0])]
        try:
            amethod = mclass.MethodsByName(mname)
            if ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, uid):
                mname = amethod.MethodPath
                mname = mname.replace('\\', '_')
                mname = mname.replace('/', '_')
                pagemethod = __import__(mname)
                pageevent = getattr(pagemethod, 'OnWWWAction')
                if pageevent is not None:
                    mobj = mclass[int(sl[1])]
                    ret = apply(pageevent, (mobj, amenu, file))
                    if ret == 2:
                        fref = 'icormain.asp?jobtype=objectedit&OID=%d&CID=%d&brCID=%d&brOID=%d' % (mobj.OID, mobj.CID, brcid, broid)
                        file.write('<hr><BUTTON class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:window.location=\'%s\';">Powrót</BUTTON>' % fref)
                    elif ret:
                        fref = 'icormain.asp?jobtype=objectedit&OID=%d&CID=%d&brCID=%d&brOID=%d' % (mobj.OID, mobj.CID, brcid, broid)
                        file.write('<hr><a class="fg-button-single ui-state-default ui-corner-all uihover" ')
                        file.write(' HREF="%s">Powrót</a> ' % fref)
        except:
            print 'Error during default menu action:', amenu.Action, ' - ', mname
            raise
        file.write('</div>')    #ui-widget-content
    else:
        pass
        #file.write('<div class="ui-widget-header">') #ui-widget-header
        #file.write('<center><P class=menuaspagecaption>%s</P>\n'%amenu.AsPageCaption)
        #file.write('<P class=menuaspagesubcaption>%s</P></center>\n'%amenu.AsPageSubCaption)
        #file.write('<div class="ui-widget-content">') #ui-widget-content
        #s=amenu.AsPageDescription
        #if s!='':
        #   file.write('<p>%s</p>\n' % s)
        #file.write('</div>') #ui-widget-content
        #file.write('</div>') #ui-widget-header
    if amenu.Action in ['ObjectAdd', 'ObjectEdit', 'ObjectDelete']:
        file.write('<div class="ui-widget-content">')    #ui-widget-content
        w = 1
        if len(amenu.WWWParam) == 3:
            arefCID, arefOID, arefField = amenu.WWWParam
            rclass = aICORDBEngine.Classes[arefCID]
            arefobj = rclass[arefOID]
            if amenu.Action in ['ObjectAdd', ]:
                pclass2 = aICORDBEngine.Classes[amenu.ParamItem]
                aseclev = 0
                if pclass2 is not None:
                    aseclev = pclass2.CID == rclass.CID
                w = ICORSecurity.CheckRecursiveAccessLevelForUser(arefobj, 'AccessLevelEdit', uid, aseclev)
            elif amenu.Action in ['ObjectEdit', ]:
                w = ICORSecurity.CheckRecursiveAccessLevelForUser(arefobj, 'AccessLevelEdit', uid)
            elif amenu.Action in ['ObjectDelete', ]:
                w = ICORSecurity.CheckRecursiveAccessLevelForUser(arefobj, 'AccessLevelDelete', uid)
        if w:
            mname = amenu.ParamItem
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            mclass = aICORDBEngine.Classes[mname]
            if mclass.IsMethodInClass('OnWWWAction'):
                try:
                    pagemethod = __import__(mname + '_OnWWWAction')
                    pageevent = getattr(pagemethod, 'OnWWWAction')
                    if pageevent is not None:
                        apply(pageevent, (mclass, amenu, file))
                except:
                    print 'Error during default menu action:', amenu.Action, ' - ', mname + '_OnWWWAction'
                    raise
            else:
                awwweditor = RegisterFields(mclass, amenu, file)
                awwweditor.WWWAction()
        else:
            file.write('<h2><font color="red">Brak uprawnień do wykonania tej operacji</font><h2><button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:history.back();"> Powrót </button>')
        file.write('</div>')    #ui-widget-content
    if 0:
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
        #      file.write('<hr>\n')
        file.write('<div class="ui-widget-content">')    #ui-widget-content
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
        file.write('</div>')    #ui-widget-content
    s = amenu.PageHTMLInfo
    if s != '':
        file.write('<div class="ui-widget-content">')    #ui-widget-content
        file.write(s)
        file.write('</div>')    #ui-widget-content
    s = amenu.PageHTML
    if s != '':
        file.write('<div class="ui-widget-content">')    #ui-widget-content
        file.write('<hr>' + ICORUtil.GetTextAsHTMLText(s, aengine=aICORDBEngine))
        file.write('</div>')    #ui-widget-content
    if amenu.IsVisibleForEdit(uid):
        #      eref=amenu.GetMenuRef(aedit=1,amode='',nobodytags=1,noscripttags=1)
        #      if eref!='':
        #        file.write('<hr><a class=reflistoutnavy ')
        #         file.write(' HREF="%s">Edycja</a> ' % eref)
        #
        #         fref='icormain.asp?jobtype=objectedit&CID=%d&OID=%d'%(amenu.MenuClass.CID,amenu.oid)
        #         file.write(' | <a class=reflistoutnavy ')
        #         file.write(' HREF="%s">Edycja HTML (1)</a> ' % fref)
        ameoid = -1
        mobj = amenu.MenuClass.GetWWWMenuRefs().AsObject()
        while mobj:
            if mobj.Action.Name == 'ObjectEdit':
                ameoid = mobj.OID
            mobj.Next()
        if ameoid >= 0:
            file.write('<div class="ui-widget-content">')    #ui-widget-content
            fref = 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_&brCID=%d&brOID=%d' % (ameoid, amenu.MenuClass.CID, amenu.oid, brcid, broid)
            file.write('<hr><a class="fg-button-single ui-state-default ui-corner-all uihover" href="%s">Edycja strony</a> ' % fref)
            file.write('</div>')    #ui-widget-content

    file.write('</div>')    #ui-widget
