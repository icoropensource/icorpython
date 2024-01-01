# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.icorsecurity as ICORSecurity


def GetClassIcon(aclass):
    ret = ''
    arefs = aclass.WWWMenuImageClosedClass
    if arefs:
        ret = arefs.Location[arefs.OID]
    else:
        arefs = aclass.WWWMenuImageClass
        if arefs:
            ret = arefs.Location[arefs.OID]
    return ret.replace('\\', '/')


def GetClassObjectIcon(aclass):
    ret = ''
    arefs = aclass.WWWMenuImageClosedObject
    if arefs:
        ret = arefs.Location[arefs.OID]
    else:
        arefs = aclass.WWWMenuImageObject
        if arefs:
            ret = arefs.Location[arefs.OID]
    return ret.replace('\\', '/')


def GetClassImageSrc(aclass, asobject=1):
    ret = ''
    arefs1 = aclass.WWWMenuImageClosedObject
    if arefs1:
        ret = arefs1.Location[arefs1.OID]
    if not ret:
        arefs2 = aclass.WWWMenuImageObject
        if arefs2:
            ret = arefs2.Location[arefs2.OID]
    if not ret:
        arefs2 = aclass.WWWMenuImageClosedClass
        if arefs2:
            ret = arefs2.Location[arefs2.OID]
    if not ret:
        arefs2 = aclass.WWWMenuImageClass
        if arefs2:
            ret = arefs2.Location[arefs2.OID]
    if not ret:
        if asobject:
            ret = '/icormanager/images/icons/silk/icons/folder_page.png'
        else:
            ret = '/icormanager/images/icons/silk/icons/folder.png'
    return ret


def GetClassContextMenu(aclass, aoid, UID, brcid=-1, broid=-1):
    ret = []
    mrefs = aclass.GetWWWMenuRefs()
    aid = 1
    #   print 'menu:',aclass.CID,aoid
    #   print '   GetClassContextMenu(aclass,',aoid,UID,brcid,broid
    while mrefs:
        amenu = ICORWWWMenuItem(UID, mrefs.OID, brcid=brcid, broid=broid)
        if amenu.IsVisibleByProfile(UID):
            if amenu.Action in ['ObjectAdd', 'ObjectEdit']:
                mobj = aclass[aoid]
                if ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelEdit', UID):
                    iclass = aICORDBEngine.Classes[amenu.ParamItem]
                    if iclass is None:
                        iclass = aclass
                    aicon = GetClassObjectIcon(iclass)
                    if not aicon:
                        aicon = GetClassIcon(iclass)
                    d = {'text': XMLUtil.GetAsXMLStringNoPL(amenu.Caption), 'icon': aicon, 'id': str(aid), 'action': 'redirect', 'value': amenu.GetMenuRef() + '&param=' + str(aclass.CID) + '_' + str(aoid) + '_'}
                    #               print d
                    ret.append(d)
                    aid = aid + 1
            elif amenu.Action in ['ObjectApplyMethods']:
                amlist = aclass.GetMethodsList()
                for amname in amlist:
                    amethod = aclass.MethodsByName(amname)
                    if amethod is None:
                        continue
                    if not amethod.WWWMethod:
                        continue
                    if not ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, UID):
                        continue
                    res = 1
                    blink = ''
                    try:
                        mname = amethod.MethodPath
                        mname = mname.replace('\\', '_')
                        mname = mname.replace('/', '_')
                        pagemethod = __import__(mname)
                        if hasattr(pagemethod, 'OnBeforeWWWAction'):
                            pageevent = getattr(pagemethod, 'OnBeforeWWWAction')
                            if pageevent is not None:
                                mobj = aclass[aoid]
                                res = apply(pageevent, (mobj, amenu, ICORUtil.Response()))
                                if res:
                                    if hasattr(pagemethod, 'OnWWWActionGetLink'):
                                        pageevent = getattr(pagemethod, 'OnWWWActionGetLink')
                                        if pageevent is not None:
                                            blink = apply(pageevent, (mobj, amenu))
                                            if blink is None:
                                                blink = ''
                                            if blink and blink[:1] != '&':
                                                blink = '&' + blink
                    except:
                        print 'Error during object edit:', amenu.Action, ' - ', amname
                        raise
                    if not res:
                        continue
                    alink = 'icormain.asp?jobtype=menuitem&OID=' + str(amenu.oid) + '&param=' + str(aclass.CID) + '_' + str(aoid) + '_' + amethod.Name + blink
                    alink = alink + '&brCID=%d&brOID=%d&xxx=2' % (brcid, broid)
                    #               print '      link:',brcid,broid,alink
                    smname = amethod.WWWDescription
                    if not smname:
                        smname = amethod.Name
                    if not amethod.WWWConfirmExecute:
                        d = {'text': XMLUtil.GetAsXMLStringNoPL(smname), 'icon': '/icorimg/silk/page_forward.png', 'id': str(aid), 'action': 'redirect', 'value': alink}
                        #                  print d
                        ret.append(d)
                        aid = aid + 1
        mrefs.Next()
    return ret


def GetClassContextMenuSubmit(aclass, aoid, aid, UID, brcid=-1, broid=-1):
    ret = []
    l = GetClassContextMenu(aclass, aoid, UID, brcid, broid)
    for d in l:
        if d['id'] == aid:
            ret.append(d)
            break
    return ret
