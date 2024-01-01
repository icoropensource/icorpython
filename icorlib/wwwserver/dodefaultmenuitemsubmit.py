# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorwwwinterface import *
from serverutil import ICORReport
import cStringIO


def DoDefaultMenuItemSubmitJSON(menuoid, oid, cid, broid, brcid, areport, UID, jsonres):
    # file,OID,areport,UID
    if menuoid < 0:
        jsonres['status'] = 1
        jsonres['info'] = 'bad data'
        return
    file = cStringIO.StringIO()
    amenu = ICORWWWMenuItem(UID, menuoid, jsonres=jsonres)
    DoDefaultMenuItemSubmit(file, menuoid, areport, UID, amenu=amenu)


def DoDefaultMenuItemSubmit(file, OID, areport, UID, amenu=None):
    if OID < 0:
        return
    areport['menuoid'] = areport['OID']
    if amenu is None:
        amenu = ICORWWWMenuItem(UID, OID)
    if not amenu.IsVisibleByProfile(UID):
        if amenu.asJSON:
            amenu.jsonres['status'] = 1
            amenu.jsonres['info'] = 'brak dostepu'
        return
    if len(amenu.WWWParam) < 3:
        amenu.WWWParam = int(areport.refCID), int(areport.refOID), areport.refField
    if amenu.Action in ['ObjectApplyMethods', ]:
        mname = areport.refField
        mclass = aICORDBEngine.Classes[int(areport.refCID)]
        try:
            amethod = mclass.MethodsByName(mname)
            mname = amethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            pageevent = getattr(pagemethod, 'OnWWWActionSubmit')
            if pageevent is not None:
                mobj = mclass[int(areport.refOID)]
                apply(pageevent, (mobj, amenu, areport, file))
        except:
            print 'Error during default menu action:', amenu.Action, ' - ', mname
            raise
    if amenu.Action in ['ObjectAdd', 'ObjectEdit', 'ObjectDelete', ]:
        mname = amenu.ParamItem
        mname = mname.replace('\\', '_')
        mname = mname.replace('/', '_')
        mclass = aICORDBEngine.Classes[mname]
        if mclass.IsMethodInClass('OnWWWAction'):
            pagemethod = __import__(mname + '_OnWWWAction')
            if pagemethod is not None:
                pageevent = getattr(pagemethod, 'OnWWWActionSubmit')
                if pageevent is not None:
                    apply(pageevent, (mclass, amenu, areport, file))
        else:
            awwweditor = RegisterFields(mclass, amenu, file, -1, areport)
            awwweditor.WWWActionSubmit()

    if amenu.asJSON:
        return

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
    s = amenu.PageHTMLInfo
    if s != '':
        file.write(s)
    s = amenu.PageHTML
    if s != '':
        file.write('<hr>' + s)
    if amenu.IsVisibleForEdit(UID):
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
            fref = 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_' % (ameoid, amenu.MenuClass.CID, amenu.oid)
            file.write('<hr><a class="fg-button-single ui-state-default ui-corner-all uihover" href="%s">Edycja strony</a> ' % fref)
