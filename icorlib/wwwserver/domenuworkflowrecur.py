# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.icorsecurity as ICORSecurity
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem, JSONMenu, JSONContext, JSONContextSubmit
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_WWW_Server_ICORWWWLib as ICORWWWLib
import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
import string


def DoGetEffects(robj, xmlfile, UID):
    fobj = robj.EffectSkins
    if fobj:
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Wybrane skórki efektów'), 'icon': '/icormanager/images/icons/silk/icons/style.png'}
        d['openIcon'] = d['icon']
        xmlfile.TagOpen('tree', d)
        DoMenuClassRecur.DoGetObjects(fobj, xmlfile, UID, aprocessevents=0, asortdisable=0, brcid=-1, broid=-1)
        xmlfile.TagClose()
    eobj = robj.Effects
    if eobj:
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Efekty'), 'icon': '/icormanager/images/icons/silk/icons/folder.png'}
        d['openIcon'] = d['icon']
        xmlfile.TagOpen('tree', d)
        DoMenuClassRecur.DoGetObjects(eobj, xmlfile, UID, aprocessevents=0, asortdisable=0, brcid=-1, broid=-1)
        xmlfile.TagClose()


def DoGetObjects(sobj, aobj, robj, xmlfile, UID, anogrouping=0):
    lo = []
    aapppath = sobj.Projekt.AppPath
    if aapppath[-1:] != '/':
        aapppath = aapppath + '/'
#   abasenamemodifier=sobj.Projekt.BaseNameModifier
    if robj:
        tobj = robj.TabelaZrodlowa
        if tobj:
            if robj.Class.SGIsTableView.ValuesAsInt(robj.OID) > 0:
                ##            d={'text':'Szukaj','action':'icormain.asp?jobtype=workflowmenustruct&OID=%d&coid=%d'%(sobj.OID,aobj.OID)}
                ##            d['icon']='/icormanager/images/wfxtree/items/Comment_Show_Comment.png'
                ##            d['openicon']=d['icon']
                ##            lo.append(['Szukaj',d])
                #            aaction='%sBZR_%s_au.asp?chapterid=%d'%(aapppath,tobj.OID,robj.OID)
                #            d={'text':'Nowa pozycja','action':aaction}
                #            d['icon']='/icormanager/images/wfxtree/items/Comment_Insert_Comment.png'
                #            d['openicon']=d['icon']
                #            lo.append(['Nowa pozycja',d])
                pass
            else:
                pass


#            d={'text':'Edycja','action':'icormain.asp?jobtype=workflowmenustruct&OID=%d&coid=%d'%(sobj.OID,aobj.OID)}
#            d['icon']='/icormanager/images/wfxtree/items/Comment_Edit_Comment.png'
#            d['openicon']=d['icon']
#            lo.append(['Edycja',d])
    fCMSIcon = aobj.Class.FieldsByName('CMSIcon')
    fCMSIconOpen = aobj.Class.FieldsByName('CMSIconOpen')
    aclass = aobj.Class
    while aobj:
        if anogrouping:
            if aobj.GrupaRozdzialow:
                aobj.Next()
                continue
        if not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', UID):
            aobj.Next()
            continue
        aname = aobj.NaglowekMenu
        if not aname:
            aname = aobj.Naglowek
        tobj = aobj.TabelaZrodlowa
        aaction = ''
        aistableview = 0
        if tobj:
            aistableview = aobj.Class.SGIsTableView.ValuesAsInt(aobj.OID)
            if aistableview:
                s = tobj.DomyslnaWyszukiwarka
                if s:
                    aaction = '%s%s?chapterid=%d' % (aapppath, s, aobj.OID)
                else:
                    aaction = '%sBZR_%s_sv.asp?chapterid=%d' % (aapppath, tobj.OID, aobj.OID)
            else:
                aaction = '%sMENUCHAPTER.asp?coid=%d&toid=%d' % (aapppath, aobj.OID, tobj.OID)
        elif aobj.SGHref:
            #         aaction=ICORUtil.URLAddParam(aobj.SGHref,'chapterid=%d'%(aobj.OID,))
            aaction = aobj.SGHref
        if aobj.SGHrefApp:
            aaction = ICORUtil.URLAddParam(aobj.SGHrefApp, 'chapterid=%d' % (aobj.OID, ))
        d = {'text': XMLUtil.GetAsXMLStringNoPL(aname), 'action': aaction}

        si1, si2 = '', ''
        if fCMSIcon:
            irefs = fCMSIcon.GetRefList(aobj.OID)
            if irefs:
                si1 = irefs.Class.Location[irefs.OID]
        if fCMSIconOpen:
            irefs = fCMSIconOpen.GetRefList(aobj.OID)
            if irefs:
                si2 = irefs.Class.Location[irefs.OID]
        if si1 != '' and si2 == '':
            si2 = si1
        elif si2 != '' and si1 == '':
            si1 = si2
        if si1 == '' and si2 == '':
            if aobj.Class.SGIsMenuDisabled.ValuesAsInt(aobj.OID) > 0:
                si1 = '/icormanager/images/wfxtree/items/book_closed_grey.png'
                si2 = '/icormanager/images/wfxtree/items/book_open_grey.png'
            elif aobj.Class.SGIsTableView.ValuesAsInt(aobj.OID) > 0:
                si1 = '/icormanager/images/wfxtree/items/book_closed_green.png'
                si2 = '/icormanager/images/wfxtree/items/book_open_green.png'
            elif not tobj and aobj.SGHref:
                si1 = '/icormanager/images/icons/silk/icons/bookmark_go.png'
                si2 = '/icormanager/images/icons/silk/icons/bookmark_go.png'
            else:
                arefs1 = aobj.Class.WWWMenuImageClosedObject
                if arefs1:
                    si1 = arefs1.Location[arefs1.OID]
                arefs2 = aobj.Class.WWWMenuImageObject
                if arefs2:
                    si2 = arefs2.Location[arefs2.OID]
                if not si2:
                    si2 = si1
        if si1:
            d['icon'] = si1
            d['openIcon'] = si2
        pobj = aobj.PodRozdzialy
        eobj = aobj.Effects
        fobj = aobj.EffectSkins
        wr = 0
        if pobj or eobj or fobj:    # or aobj['SGIsTableView']: # or tobj
            wr = 1
        else:
            wr = DoMenuClassRecur.ProcessObjectWWWEventCheck(aobj, xmlfile, UID)
        if wr:
            d['src'] = 'icormain.asp?jobtype=workflowmenustruct&OID=%d&coid=%d&XMLData=1' % (sobj.OID, aobj.OID)
        d['context'] = 'icormain.asp?jobtype=workflowmenustructcontext&OID=%d&coid=%d&XMLData=1' % (sobj.OID, aobj.OID)
        if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelEdit', UID):
            d['allowmove'] = '1'
            d['coid'] = str(aobj.OID)
            d['rel'] = 'chapter'
            #if tobj and not aistableview:
            #d['allowattachmentdrop']='1'
        lo.append([aname, d])
        aobj.Next()
    for aname, d in lo:
        xmlfile.TagOpen('tree', d)
        #bobj=aclass[int(d['coid'])]
        #DoGetEffects(bobj,xmlfile,UID)
        #DoMenuClassRecur.ProcessObjectWWWEvent(bobj,xmlfile,UID)
        xmlfile.TagClose('tree')


def DoMenuWorkflowRecur(file, aoid, coid, aparam, UID, xmlfile=None, ajson=0):
    bclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
    rclass = bclass.Rozdzialy.ClassOfType
    aclose = 0
    if xmlfile is None:
        aclose = 1
        if ajson:
            xmlfile = JSONMenu(file)
        else:
            xmlfile = XMLUtil.MXMLFile(file, aattrascdata=1)
            xmlfile.Header()
        xmlfile.TagOpen('tree')
    aobj = bclass[aoid]
    if not aobj:
        pass
    elif coid < 0:
        gobj = aobj.GrupyRozdzialow
        while gobj:
            if ICORSecurity.CheckRecursiveAccessLevelForUser(gobj, 'AccessLevelView', UID):
                d = {'text': XMLUtil.GetAsXMLStringNoPL(gobj.Nazwa), }
                if gobj['SGIsSEODisabled', mt_Integer]:
                    d['icon'] = '/icormanager/images/icons/silk/icons/sitemap_color.png'
                    d['openIcon'] = '/icormanager/images/icons/silk/icons/sitemap_color.png'
                else:
                    d['icon'] = '/icormanager/images/icons/silk/icons/chart_organisation.png'
                    d['openIcon'] = '/icormanager/images/icons/silk/icons/chart_organisation.png'
                d['rel'] = 'chaptergroup'
                d['coid'] = str(gobj.OID)
                d['context'] = 'icormain.asp?jobtype=menuclassrecurcontext&CID=%d&OID=%d&XMLData=1&brCID=%d&brOID=%d' % (gobj.CID, gobj.OID, -1, -1)
                xmlfile.TagOpen('tree', d, aclosetag=0)
                robj = gobj.Rozdzialy
                DoGetObjects(aobj, robj, None, xmlfile, UID)
                xmlfile.TagClose('tree')
            gobj.Next()
        robj = aobj.Rozdzialy
        DoGetObjects(aobj, robj, None, xmlfile, UID, anogrouping=1)
    elif coid >= 0:
        robj = rclass[coid]
        pobj = robj.PodRozdzialy
        DoGetEffects(robj, xmlfile, UID)
        DoMenuClassRecur.ProcessObjectWWWEvent(robj, xmlfile, UID)
        DoGetObjects(aobj, pobj, robj, xmlfile, UID, anogrouping=1)
    else:
        print 'bad workflow recur parameters: aoid:', aoid, 'coid:', coid, 'aparam:', afieldname, 'UID:', UID
    if aclose:
        xmlfile.TagClose('tree')
        xmlfile.close()


def DoMenuWorkflowRecurContext(file, aoid, coid, aparam, UID, ajson=0):
    bclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
    rclass = bclass.Rozdzialy.ClassOfType
    if ajson:
        xmlfile = JSONContext(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file)
        xmlfile.Header()
    axmldata = '1'
    if ajson:
        axmldata = 'json'
    xmlfile.TagOpen('menu')
    aobj = bclass[aoid]
    robj = rclass[coid]
    tobj = robj.TabelaZrodlowa
    wacledit = ICORSecurity.CheckRecursiveAccessLevelForUser(robj, 'AccessLevelEdit', UID)
    wacltableedit = ICORSecurity.CheckRecursiveAccessLevelForUser(robj, 'AccessLevelTableEdit', UID)
    wi = 0
    w = 0
    while tobj:
        w1 = 0
        xobj = None
        if tobj:
            xobj = tobj.XMLData
        wx = 0
        if xobj:
            aicon = ICORWWWLib.GetClassObjectIcon(xobj.Class)
            if not aicon:
                aicon = ICORWWWLib.GetClassIcon(xobj.Class)
            while xobj:
                waclxml = ICORSecurity.CheckRecursiveAccessLevelForUser(xobj, 'AccessLevelView', UID)
                if waclxml:
                    if w and not w1:
                        d = {'text': '-', 'action': 'none'}
                        xmlfile.TagOpen('menuitem', d, aclosetag=1)
                        w1 = 1
                    d = {'text': XMLUtil.GetAsXMLStringNoPL(xobj.Name), 'icon': aicon, 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=8&XMLData=%s' % (aobj.OID, robj.OID, xobj.OID, axmldata)}
                    xmlfile.TagOpen('menuitem', d, aclosetag=1)
                    w = 1
                    wx = 1
                xobj.Next()
        if wacltableedit and tobj:
            if w and not w1:
                d = {'text': '-', 'action': 'none'}
                xmlfile.TagOpen('menuitem', d, aclosetag=1)
                w1 = 1
            if not robj['SGIsTableView'] and not wi:
                d = {'text': XMLUtil.GetAsXMLStringNoPL('Edycja danych'), 'icon': '/icorimg/silk/page_edit.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=4&XMLData=%s' % (aobj.OID, robj.OID, tobj.OID, axmldata)}
                xmlfile.TagOpen('menuitem', d, aclosetag=1)
                d = {'text': XMLUtil.GetAsXMLStringNoPL('Nowe pliki'), 'icon': '/icorimg/silk/page_attach.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=5&XMLData=%s' % (aobj.OID, robj.OID, tobj.OID, axmldata)}
                xmlfile.TagOpen('menuitem', d, aclosetag=1)
                d = {'text': XMLUtil.GetAsXMLStringNoPL('Zarządzaj plikami'), 'icon': '/icorimg/silk/attach.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=6&XMLData=%s' % (aobj.OID, robj.OID, tobj.OID, axmldata)}
                xmlfile.TagOpen('menuitem', d, aclosetag=1)
            else:
                sit = ''
                sitn = ''
                if not wi:
                    sitn = 'Nowa pozycja'
                else:
                    sit = tobj.NazwaTabeli
                    if not sit:
                        sit = tobj.Nazwa
                    sitn = 'Dodaj: ' + sit
                d = {'text': XMLUtil.GetAsXMLStringNoPL(sitn), 'icon': '/icorimg/silk/page_add.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=7&XMLData=%s' % (aobj.OID, robj.OID, tobj.OID, axmldata)}
                xmlfile.TagOpen('menuitem', d, aclosetag=1)
                if wi and not wx:
                    d = {'text': XMLUtil.GetAsXMLStringNoPL('Lista: ' + sit), 'icon': '/icorimg/silk/page_find.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&param=%d&id=15&XMLData=%s' % (aobj.OID, robj.OID, tobj.OID, axmldata)}
                    xmlfile.TagOpen('menuitem', d, aclosetag=1)
    #      if robj['IsGenerateDisabled',mt_Integer]:
            w = 1
        wi = 1
        tobj.Next()
    if w:
        d = {'text': '-', 'action': 'none'}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Publikuj dane'), 'icon': '/icorimg/silk/book_go.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=9&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)

    if wacledit:
        if w:
            d = {'text': '-', 'action': 'none'}
            xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Edycja rozdziału'), 'icon': '/icorimg/silk/page_white_edit.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=1&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Wybór ikonek'), 'icon': '/icorimg/silk/page_white_picture.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=11&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Wybór efektów'), 'icon': '/icorimg/silk/page_white_lightning.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=12&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Zmiana wyglądu rozdziału'), 'icon': '/icorimg/silk/page_white_paint.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=14&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Nowy rozdział'), 'icon': '/icorimg/silk/page_white_add.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=2&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)
        #      d={'text':XMLUtil.GetAsXMLStringNoPL('Przenies rozdział'),'action':'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=3&XMLData=%s'%(aobj.OID,robj.OID,axmldata)}
        #      xmlfile.TagOpen('menuitem',d,aclosetag=1)
        d = {'text': XMLUtil.GetAsXMLStringNoPL('Publikuj szablon'), 'icon': '/icorimg/silk/book_next.png', 'action': 'icormain.asp?jobtype=workflowmenustructcontextsubmit&OID=%d&coid=%d&id=10&XMLData=%s' % (aobj.OID, robj.OID, axmldata)}
        xmlfile.TagOpen('menuitem', d, aclosetag=1)

    xmlfile.TagClose('menu')
    xmlfile.close()


def DoMenuWorkflowRecurContextSubmit(file, aoid, coid, aparam, aid, UID, ajson=0):
    bclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Struktura']
    rclass = bclass.Rozdzialy.ClassOfType
    aobj = bclass[aoid]
    apppath = aobj.Projekt.AppPath
    if not apppath[-1:] in ['/', '\\']:
        apppath = apppath + '/'
    robj = rclass[coid]
    tobj = robj.TabelaZrodlowa
    if ajson:
        xmlfile = JSONContext(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file)
        xmlfile.Header()
    xmlfile.TagOpen('result')
    mrefs = rclass.GetWWWMenuRefs()
    moid = -1
    while mrefs:
        amenu = ICORWWWMenuItem(UID, mrefs.OID)
        if amenu.Action == 'ObjectApplyMethods':
            moid = mrefs.OID
            break
        mrefs.Next()
    if aid == '1':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterEdit' % (moid, rclass.CID, robj.OID)}
    elif aid == '2':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterNew' % (moid, rclass.CID, robj.OID)}
    elif aid == '3':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterMove' % (moid, rclass.CID, robj.OID)}
    elif aid == '4':
        d = {'action': 'redirect', 'value': apppath + 'MENUCHAPTER.asp?coid=%d&toid=%s&action=edit' % (robj.OID, aparam)}
    elif aid == '5':
        d = {'action': 'redirect', 'value': apppath + 'MENUCHAPTER.asp?coid=%d&toid=%s&action=fileadd' % (robj.OID, aparam)}
    elif aid == '6':
        d = {'action': 'redirect', 'value': apppath + 'MENUCHAPTER.asp?coid=%d&toid=%s&action=filemanage' % (robj.OID, aparam)}
    elif aid == '7':
        d = {'action': 'redirect', 'value': apppath + 'BZR_%s_au.asp?chapterid=%d' % (aparam, robj.OID, )}
    elif aid == '8':
        d = {'action': 'redirect', 'value': apppath + 'xmldata_bzr_%s_sv.asp?chapterid=%d' % (aparam, robj.OID, )}
    elif aid == '9':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterGenerate' % (moid, rclass.CID, robj.OID)}
    elif aid == '10':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterGenerateTemplate' % (moid, rclass.CID, robj.OID)}
    elif aid == '11':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterEditImages' % (moid, rclass.CID, robj.OID)}
    elif aid == '12':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterSelectEffects' % (moid, rclass.CID, robj.OID)}
    elif aid == '14':
        d = {'action': 'redirect', 'value': 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_WWWChapterSelectTemplate' % (moid, rclass.CID, robj.OID)}
    elif aid == '15':
        d = {'action': 'redirect', 'value': apppath + 'BZR_%s_sv.asp?chapterid=%d' % (aparam, robj.OID, )}
    aname = robj.NaglowekMenu
    if not aname:
        aname = robj.Naglowek
    d['text'] = XMLUtil.GetAsXMLStringNoPL(aname)
    xmlfile.TagOpen('item', d, aclosetag=1)
    xmlfile.TagClose('result')
    xmlfile.close()
