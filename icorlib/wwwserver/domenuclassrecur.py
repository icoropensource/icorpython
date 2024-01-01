# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_NetBase_WWW_Server_ICORWWWLib as ICORWWWLib
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.wwwmenu.menuutil as MenuUtil
import string
import types


def ProcessObjectWWWEventCheck(bobj, xmlfile, UID):
    ret = 0
    pageevent = None
    emethod = bobj.Class.MethodsByName('OnWWWAction')
    if emethod is not None:
        try:
            mname = emethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            if hasattr(pagemethod, 'OnWWWMenuObjRecurCheck'):
                pageevent = getattr(pagemethod, 'OnWWWMenuObjRecurCheck')
        except:
            print 'Error during www object recur check action:', emethod.MethodPath
            import traceback
            traceback.print_exc()
    if pageevent:
        ret = apply(pageevent, (xmlfile, bobj, UID))
    return ret


def ProcessObjectWWWEvent(bobj, xmlfile, UID):
    pageevent = None
    emethod = bobj.Class.MethodsByName('OnWWWAction')
    if emethod is not None:
        try:
            mname = emethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            if hasattr(pagemethod, 'OnWWWMenuObjRecur'):
                pageevent = getattr(pagemethod, 'OnWWWMenuObjRecur')
        except:
            print 'Error during www object recur action:', emethod.MethodPath
            import traceback
            traceback.print_exc()
    if pageevent:
        apply(pageevent, (xmlfile, bobj, UID))


def DoGetObjects(aobj, xmlfile, UID, aprocessevents=0, asortdisable=0, brcid=-1, broid=-1, onGetCaption=None, anogrouping=0):
    #   print 'dgo: cid:',aobj.CID,'oid:',aobj.OID
    if not aobj:
        return
    aclass = aobj.Class
    wcontext = aclass.IsMethodInClass('OnWWWContextMenu')
    lfields = aclass.GetFieldsList()
    rfields = []
    gfields = []
    for afname in lfields:
        bfield = aclass.FieldsByName(afname)
        if bfield.WWWTreeRecur:
            if bfield.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
                if not anogrouping:
                    gfields.append(bfield)
            else:
                rfields.append(bfield)
    dlo = {}
    asecfield = aclass.FieldsByName('AccessLevelView')
    if asecfield is None:
        asecfield = aclass.FieldsByName('AccessLevel')
    asecfieldname = ''
    if asecfield is not None:
        asecfieldname = asecfield.Name

    pageevent = None
    onGetIcon = None
    emethod = aclass.MethodsByName('OnWWWAction')
    if emethod is not None:
        try:
            mname = emethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            if hasattr(pagemethod, 'OnWWWMenuObjRecur'):
                pageevent = getattr(pagemethod, 'OnWWWMenuObjRecur')
            if (onGetCaption is None) and hasattr(pagemethod, 'OnGetCaption'):
                onGetCaption = getattr(pagemethod, 'OnGetCaption')
            if hasattr(pagemethod, 'onGetIcon'):
                onGetIcon = getattr(pagemethod, 'onGetIcon')
        except:
            pass

    dgimages = {}
    fCMSIcon = aclass.FieldsByName('CMSIcon')
    fCMSIconOpen = aclass.FieldsByName('CMSIconOpen')
    while aobj:
        if not aobj.Exists():
            aobj.Next()
            continue
        if asecfieldname and not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, asecfieldname, UID):
            aobj.Next()
            continue
        lt = []
        l = aobj.AsColumnValues(amaxcol=aclass.WWWMaxColDictDescription, aretvaluesbytype=lt, anowwwtreerecur=1, aappendemptyvalues=1)
        if onGetCaption:
            l = onGetCaption(aobj, l)
        lts = []
        for ss in lt:
            if isinstance(ss, types.StringTypes):
                lts.append(ICORUtil.strLowerPL(ss))
            else:
                lts.append(ss)
        lt = lts
        for i in range(len(l)):
            #l[i]=XMLUtil.GetAsXMLStringNoPL(l[i]) #$$UTF
            if i == 1 and l[1]:
                l[1] = '<font color=navy>' + XMLUtil.GetAsXMLStringNoPL(l[1]) + '</font>'
            if i == 2 and l[2]:
                l[2] = '<font color=green>' + XMLUtil.GetAsXMLStringNoPL(l[2]) + '</font>'
            if i == 3 and l[3]:
                l[3] = '<font color=brown>' + XMLUtil.GetAsXMLStringNoPL(l[3]) + '</font>'
            if i == 4 and l[4]:
                l[4] = '<em>' + XMLUtil.GetAsXMLStringNoPL(l[4]) + '</em>'
        aname = string.join([s for s in l if s], ', ')
        if aname[:1] != '___':
            d = {'text': aname, 'action': 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&brCID=%d&brOID=%d' % (aobj.CID, aobj.OID, brcid, broid)}

            si1, si2 = '', ''
            if fCMSIcon:
                irefs = fCMSIcon.GetRefList(aobj.OID)
                if irefs:
                    si1 = irefs.Class.Location[irefs.OID]
            if fCMSIconOpen:
                irefs = fCMSIconOpen.GetRefList(aobj.OID)
                if irefs:
                    si2 = irefs.Class.Location[irefs.OID]
            if onGetIcon is not None:
                si1, si2 = onGetIcon(aobj)
            if si1 != '' and si2 == '':
                si2 = si1
            elif si2 != '' and si1 == '':
                si1 = si2
            if si1 == '' and si2 == '':
                arefs1 = aclass.WWWMenuImageClosedObject
                if arefs1:
                    si1 = arefs1.Location[arefs1.OID]
                arefs2 = aclass.WWWMenuImageObject
                if arefs2:
                    si2 = arefs2.Location[arefs2.OID]
                if not si2:
                    si2 = si1
                if not si1:
                    si1 = si2

            if si1:
                d['icon'] = si1
                d['openIcon'] = si2
            wr = 0
            if pageevent:
                wr = 1
            if not wr:
                for rfield in rfields:
                    if rfield[aobj.OID]:
                        wr = 1
                        break
            if wr:
                d['src'] = 'icormain.asp?jobtype=menuclassrecur&CID=%d&OID=%d&XMLData=1&brCID=%d&brOID=%d' % (aobj.CID, aobj.OID, brcid, broid)
#         if wcontext:
            d['context'] = 'icormain.asp?jobtype=menuclassrecurcontext&CID=%d&OID=%d&XMLData=1&brCID=%d&brOID=%d' % (aobj.CID, aobj.OID, brcid, broid)
            #            print 'Context 1:',d['context']
            if not aname:
                aname = 'Pozycja ' + str(aobj.OID)
            gname = ''
            sgi1, sgi2 = '', ''
            if gfields and not anogrouping:
                gl = []
                for gfield in gfields:
                    if not sgi1:
                        arefs1 = gfield.WWWMenuImageClosedField
                        if arefs1:
                            sgi1 = arefs1.Location[arefs1.OID]
                        arefs2 = gfield.WWWMenuImageField
                        if arefs2:
                            sgi2 = arefs2.Location[arefs2.OID]
                        if not sgi2:
                            sgi2 = sgi1
                        if not si1:
                            sgi1 = sgi2
                    gl.append(gfield[aobj.OID])
                if reduce(lambda x, y: x + y, gl, ''):
                    #gname=XMLUtil.GetAsXMLStringNoPL(string.join(gl,', ')) #$$UTF
                    gname = string.join(gl, ', ')
                else:
                    gname = ''
            dgimages[gname] = sgi1, sgi2
            lo = dlo.get(gname, [])
            lo.append([lt, aname, d, aobj.OID])
            dlo[gname] = lo
        aobj.Next()
    lok = dlo.keys()
    if not asortdisable:
        lok.sort(cmp=lambda x, y: cmp(ICORUtil.strLowerPL(x), ICORUtil.strLowerPL(y)))
    for agname in lok:
        if agname and not anogrouping:
            d = {'text': XMLUtil.GetAsXMLStringNoPL(agname)}
            sgi1, sgi2 = dgimages.get(agname, ('', ''))
            if sgi1:
                d['icon'] = sgi1
                d['openIcon'] = sgi2
            xmlfile.TagOpen('tree', d)
        lo = dlo[agname]
        if not asortdisable:
            lo.sort()
        for lt, aname, d, aoid in lo:
            if not d.get('text', ''):
                d['text'] = '--=*=--'
            if aprocessevents:
                bobj = aclass[aoid]
                ProcessObjectWWWEvent(bobj, xmlfile, UID)


#         if pageevent is not None:
#            xmlfile.TagOpen('tree',d,aclosetag=0)
#            bobj=aclass[aoid]
#            print 'pageevent 2:',bobj.CID,bobj.OID
#            ret=apply(pageevent,(xmlfile,bobj,UID))
#            xmlfile.TagClose('tree')
#         else:
            xmlfile.TagOpen('tree', d, aclosetag=1)
        if agname and not anogrouping:
            xmlfile.TagClose('tree')


def DoMenuClassRecur(file, acid, afieldname, aoid, UID, brcid, broid, ajson=0):
    bclass = aICORDBEngine.Classes[acid]
    #   print 'domenuclassrecur: cid:',acid,bclass.NameOfClass,'fieldname:',afieldname,'oid:',aoid
    if ajson:
        xmlfile = MenuUtil.JSONMenu(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file, aattrascdata=1)
        xmlfile.Header()
    xmlfile.TagOpen('tree')
    if aoid < 0 and afieldname == '':
        aobj = bclass.GetFirstObject()
        if aobj:
            DoGetObjects(aobj, xmlfile, UID, brcid=brcid, broid=broid)
    elif aoid >= 0 and afieldname == '':
        lfields = bclass.GetFieldsList()
        lfields.sort()
        wcnt = 0
        cfield = None
        for afname in lfields:
            bfield = bclass.FieldsByName(afname)
            if bfield.WWWTreeRecur:
                cfield = bfield
                wcnt = wcnt + 1
                break
#      if wcnt==1:
#         cfield.DeleteRefs(aoid)
#         aobj=cfield.GetRefList(aoid).AsObject()
#         if aobj:
#            DoGetObjects(aobj,xmlfile,UID,aprocessevents=1)
        if wcnt:
            aobj = bclass[aoid]
            ProcessObjectWWWEvent(aobj, xmlfile, UID)
            wcontext = bclass.IsMethodInClass('OnWWWContextMenu')
            for afname in lfields:
                bfield = bclass.FieldsByName(afname)
                if bfield.WWWTreeRecur and bfield[aoid] and bfield.FieldTID > MAX_ICOR_SYSTEM_TYPE:
                    if bfield.WWWTreeRecurObjects:
                        aobj = bfield.GetRefList(aoid).AsObject()
                        #                  print 'wwwtreerecur 1:',aobj.CID,aobj.OID
                        DoGetObjects(aobj, xmlfile, UID, aprocessevents=0, asortdisable=bfield.WWWSortable, brcid=acid, broid=aoid)
                    else:
                        #d={'text':XMLUtil.GetAsXMLStringNoPL(bfield.FieldNameAsDisplayed),'action':'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&brCID=%d&brOID=%d'%(acid,aoid,acid,aoid)} #$$UTF
                        d = {'text': XMLUtil.GetAsXMLStringNoPL(bfield.FieldNameAsDisplayed), 'action': 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&brCID=%d&brOID=%d' % (acid, aoid, acid, aoid)}
                        si1, si2 = '', ''
                        arefs1 = bfield.WWWMenuImageClosedField
                        if arefs1:
                            si1 = arefs1.Location[arefs1.OID]
                        arefs2 = bfield.WWWMenuImageField
                        if arefs2:
                            si2 = arefs2.Location[arefs2.OID]
                        if not si2:
                            si2 = si1
                        if not si1:
                            si2 = si1
                        if not si1:
                            bfclass = bfield.ClassOfType
                            if bfclass is not None:
                                si1, si2 = '', ''
                                arefs1 = bfclass.WWWMenuImageClosedClass
                                if arefs1:
                                    si1 = arefs1.Location[arefs1.OID]
                                arefs2 = bfclass.WWWMenuImageClass
                                if arefs2:
                                    si2 = arefs2.Location[arefs2.OID]
                            if not si2:
                                si2 = si1
                            if not si1:
                                si2 = si1
                        if si1:
                            d['icon'] = si1
                            d['openIcon'] = si2
                        d['src'] = 'icormain.asp?jobtype=menuclassrecur&CID=%d&OID=%d&field=%s&XMLData=1&brCID=%d&brOID=%d' % (acid, aoid, bfield.Name, acid, aoid)
                        #               if wcontext:
                        d['context'] = 'icormain.asp?jobtype=menuclassrecurcontext&CID=%d&OID=%d&field=%s&XMLData=1&brCID=%d&brOID=%d' % (acid, aoid, bfield.Name, acid, aoid)
                        #                  print 'Context 2:',d['context']
                        xmlfile.TagOpen('tree', d, aclosetag=1)
        else:
            aobj = bclass[aoid]
            ProcessObjectWWWEvent(aobj, xmlfile, UID)
    elif aoid >= 0 and afieldname != '':
        bfield = bclass.FieldsByName(afieldname)
        bfield.DeleteRefs(aoid)
        bEvent = None
        if bclass.IsMethodInClass('OnWWWAction'):
            pagemethod = bclass.OnWWWAction.AsModule()
            if pagemethod and hasattr(pagemethod, 'OnWWWGetMenuFieldRecurIteratorEvent'):
                bEvent = getattr(pagemethod, 'OnWWWGetMenuFieldRecurIteratorEvent')
        aobj = None
        if bEvent:
            aobj = bEvent(bfield, aoid)
        if aobj is None:
            aobj = bfield.GetRefList(aoid).AsObject()
        if aobj:
            DoGetObjects(aobj, xmlfile, UID, aprocessevents=0, asortdisable=bfield.WWWSortable, brcid=brcid, broid=broid)
    else:
        print 'bad menuclass recur parameters: acid:', acid, 'afieldname:', afieldname, 'aoid:', aoid, 'UID:', UID


#   print 'aaa 1','c:',bclass.CID,bclass.NameOfClass,'f:',afieldname,'o:',aoid,'u:',UID
    emethod = bclass.MethodsByName('OnWWWAction')
    if emethod is not None:
        try:
            mname = emethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            if hasattr(pagemethod, 'OnWWWMenuClassRecur'):
                pageevent = getattr(pagemethod, 'OnWWWMenuClassRecur')
                if pageevent is not None:
                    ret = apply(pageevent, (xmlfile, bclass, afieldname, aoid, UID))
        except:
            print 'Error during default menu class recur:', emethod.MethodPath
            import traceback
            traceback.print_exc()
    xmlfile.TagClose('tree')
    xmlfile.close()


def DoMenuClassRecurAction(file, acid, aoid, avalue, UID, brcid=-1, broid=-1, ajson=0):
    if ajson:
        xmlfile = MenuUtil.JSONMenu(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file, aattrascdata=1)
        xmlfile.Header()
    xmlfile.TagOpen('tree')
    atype, aparam, acontext = avalue
    aclass = aICORDBEngine.Classes[acid]
    if aclass is not None and aoid >= 0:
        pageevent = None
        emethod = aclass.MethodsByName('OnWWWAction')
        if emethod is not None:
            try:
                mname = emethod.MethodPath
                mname = mname.replace('\\', '_')
                mname = mname.replace('/', '_')
                pagemethod = __import__(mname)
                if hasattr(pagemethod, 'OnWWWMenuClassRecurAction'):
                    pageevent = getattr(pagemethod, 'OnWWWMenuClassRecurAction')
                    if pageevent is not None:
                        bobj = aclass[aoid]
                        brobj = None
                        brclass = aICORDBEngine.Classes[brcid]
                        if brclass is not None and broid >= 0:
                            brobj = brclass[broid]
                        ret = apply(pageevent, (xmlfile, bobj, brobj, atype, aparam, acontext, UID))
            except:
                print 'Error during default menu class recur action:', emethod.MethodPath
                import traceback
                traceback.print_exc()
    xmlfile.TagClose('tree')
    xmlfile.close()


def DoMenuClassRecurContext(file, acid, afieldname, aoid, UID, brcid=-1, broid=-1, ajson=0):
    bclass = aICORDBEngine.Classes[acid]
    if ajson:
        xmlfile = MenuUtil.JSONContext(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file)
        xmlfile.Header()
    axmldata = '1'
    if ajson:
        axmldata = 'json'
    xmlfile.TagOpen('menu')
    try:
        if bclass is not None:
            amethod = bclass.MethodsByName('OnWWWContextMenu')
            l = None
            if amethod is not None:
                if ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, UID):
                    mname = amethod.MethodPath
                    mname = mname.replace('\\', '_')
                    mname = mname.replace('/', '_')
                    pagemethod = __import__(mname)
                    pageevent = getattr(pagemethod, 'OnWWWContextMenu')
                    if pageevent is not None:
                        l = apply(pageevent, (bclass, afieldname, aoid, UID, brcid, broid))
            if l is None:
                #            print 'DoMenuClassRecurContext(file,',acid,afieldname,aoid,UID,brcid,broid
                l = ICORWWWLib.GetClassContextMenu(bclass, aoid, UID, brcid=brcid, broid=broid)
            if type(l) == type([]):
                for d in l:
                    if type(d) == type({}):
                        aid = d.get('id', '-1')
                        d['action'] = 'icormain.asp?jobtype=menuclassrecurcontextsubmit&CID=%d&OID=%d&field=%s&id=%s&XMLData=%s&brCID=%d&brOID=%d' % (acid, aoid, afieldname, aid, axmldata, brcid, broid)
                        xmlfile.TagOpen('menuitem', d, aclosetag=1)
    except:
        print 'Error during default context menu action:', acid, afieldname, aoid, UID
        raise
    xmlfile.TagClose('menu')
    xmlfile.close()


def DoMenuClassRecurContextSubmit(file, acid, afieldname, aoid, aid, UID, brcid=-1, broid=-1, ajson=0):
    bclass = aICORDBEngine.Classes[acid]
    if ajson:
        xmlfile = MenuUtil.JSONContext(file)
    else:
        xmlfile = XMLUtil.MXMLFile(file)
        xmlfile.Header()
    xmlfile.TagOpen('result')
    try:
        if bclass is not None:
            amethod = bclass.MethodsByName('OnWWWContextMenu')
            l = None
            if amethod is not None:
                if ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, UID):
                    mname = amethod.MethodPath
                    mname = mname.replace('\\', '_')
                    mname = mname.replace('/', '_')
                    pagemethod = __import__(mname)
                    pageevent = getattr(pagemethod, 'OnWWWContextMenuSubmit')
                    if pageevent is not None:
                        l = apply(pageevent, (bclass, afieldname, aoid, aid, UID, brcid, broid))
            if l is None:
                l = ICORWWWLib.GetClassContextMenuSubmit(bclass, aoid, aid, UID, brcid=brcid, broid=broid)
            if type(l) == type([]):
                for d in l:
                    if type(d) == type({}):
                        xmlfile.TagOpen('item', d, aclosetag=1)
    except:
        print 'Error during default context menu submit action:', acid, afieldname, aoid, aid, UID
        raise
    xmlfile.TagClose('result')
    xmlfile.close()


def DoMenuObjRecurAction(file, acid, aoid, avalue, UID):
    atype, aparam = avalue
    aclass = aICORDBEngine.Classes[acid]
    if aclass is None or aoid < 0:
        return
    pageevent = None
    emethod = aclass.MethodsByName('OnWWWAction')
    if emethod is not None:
        try:
            mname = emethod.MethodPath
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            if hasattr(pagemethod, 'OnWWWMenuObjRecurAction'):
                pageevent = getattr(pagemethod, 'OnWWWMenuObjRecurAction')
                if pageevent is not None:
                    bobj = aclass[aoid]
                    ret = apply(pageevent, (file, bobj, atype, aparam, UID))
        except:
            print 'Error during default menu object recur action:', emethod.MethodPath
            import traceback
            traceback.print_exc()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
