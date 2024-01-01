# -*- coding: utf-8 -*-
import sys
import os
import time
import logging
import urllib
import traceback
import Queue
import threading
import random
import hashlib
import cStringIO

try:
    import json
except:
    import simplejson as json

import cherrypy
import cherrypy.process as process

import appplatform.storageutil as storageutil
import icordbmain
import appplatform.wserverutil.webutil as webutil

import icorlib.icorinterface as ICORInterface
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import icorlib.icorsecurity as ICORSecurity
import icordbmain.adoutil as ADOLibInit
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from icorlib.wwwserver import icorwwwlib
from icorlib.wwwserver import dodefaultmenuitemsubmit
import icorlib.wwwserver.serverutil as ServerUtil

CP1250_To_UTF8 = storageutil.CP1250_To_UTF8_Unicode    # storageutil.CP1250_To_UTF8


class ICORIDEMain(object):

    def __init__(self, amanager):
        self.manager = amanager

    def GetSheetsFields(self, aclass, afield, sheetsinfo, agetfields=0):
        if afield.WWWDisabled or afield.IsInteractive != '1':
            return
        fsi = int(afield.FieldSheetID)
        fti = int(afield.FieldTabIndex)
        if not sheetsinfo.has_key(fsi):
            fsi = 0
        s1 = storageutil.CP1250_To_UTF8(afield.FieldNameAsDisplayed)
        s2 = storageutil.CP1250_To_UTF8(afield.Name)
        lf = [fti, s1, s2]
        if agetfields:
            lf.append(afield)
        sheetsinfo[fsi]['fields'].append(lf)

    def GetSheetsInfo(self, vclass, agetfields=0):
        srefs = vclass.EditorSheets
        sheetsinfo = {}
        i = 0
        while srefs.position >= 0:
            d={
               'name':storageutil.CP1250_To_UTF8(srefs.Name[srefs.OID]),
               'fields': [],
               'wwwdisabled': srefs.WWWDisabled.ValuesAsInt(srefs.OID),
            } # yapf: disable
            sheetsinfo[i] = d
            i = i + 1
            srefs.Next()
        if sheetsinfo == {}:
            d={
               'name':storageutil.CP1250_To_UTF8(vclass.NameOfClass),
               'fields': [],
               'wwwdisabled': 0,
            } # yapf: disable
            sheetsinfo[0] = d
        vclass.ForEachField(self.GetSheetsFields, sheetsinfo, agetfields)
        for akey in sheetsinfo.keys():
            afields = sheetsinfo[akey]['fields']
            afields.sort()
            sheetsinfo[akey]['fields'] = afields
        return sheetsinfo

    def FieldFunc(self, init, aclass, afield, aoid, fieldvalue, acntid=0, alevel=0):
        if alevel > 3:
            return None
        UID = init.UID
        ftid = int(afield.FieldTypeID)
        fieldvalue['FieldOID'] = afield.FOID
        fieldvalue['FieldTypeID'] = ftid
        fieldvalue['FieldType'] = afield.FieldType
        fieldvalue['FieldEditor'] = afield.FieldEditor
        fieldvalue['IsMemo'] = afield.IsMemo
        istable = 0
        if ftid > ICORInterface.MAX_ICOR_SYSTEM_TYPE:
            if not afield.WWWSingleValue and not (afield.FieldEditor == 'ObjectsList'):
                istable = 1
        fieldvalue['IsTable'] = istable
        fieldvalue['WWWSingleValue'] = afield.WWWSingleValue
        fieldvalue['FieldDescription'] = CP1250_To_UTF8(afield.FieldDescription)
        if ftid <= ICORInterface.MAX_ICOR_SYSTEM_TYPE:
            if afield.FieldEditor == 'Worksheet':
                fieldvalue['ValueURL'] = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s' % (aclass.CID, aoid, afield.Name)
            elif afield.FieldEditor == 'XML':
                fieldvalue['ValueURL'] = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s&XMLData=1' % (aclass.CID, aoid, afield.Name)
            v = afield.ValuesAsComp(aoid)
            if isinstance(v, basestring):
                v = CP1250_To_UTF8(v)
            fieldvalue['Value'] = v
        else:
            fv = afield[aoid]
            fieldvalue['ValueRef'] = fv
            aobj = afield.GetRefObject(aoid)
            fieldvalue['ValueLen'] = len(aobj)
            if afield.WWWSingleValue or afield.FieldEditor == 'ObjectsList':
                if afield.WWWBackRefField:
                    l = []
                    cnt = 10
                    while aobj and cnt:
                        if aobj.Class.ObjectExists(aobj.OID) and ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', UID):
                            d = {}
                            lv = aobj.AsColumnValues()
                            d['Value'] = CP1250_To_UTF8(', '.join(lv))
                            d['_CID'] = aobj.CID
                            d['_OID'] = aobj.OID
                            d['ValueLink'] = 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d' % (aobj.CID, aobj.OID, random.randint(1, 10000000), )
                            l.append(d)
                        bfields = aobj.Class.GetFieldsList()
                        cfield = None
                        for bfname in bfields:
                            bfield = aobj.Class.FieldsByName(bfname)
                            if bfield.WWWBackRefField:
                                cfield = bfield
                                break
                        if cfield:
                            aobj = cfield.GetRefObject(aobj.OID)
                        else:
                            aobj = None
                        cnt = cnt - 1
                    fieldvalue['Value'] = l
                else:
                    l = []
                    while aobj:
                        if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', UID):
                            d = {}
                            lv = aobj.AsColumnValues()
                            d['Value'] = CP1250_To_UTF8(', '.join(lv))
                            d['_CID'] = aobj.CID
                            d['_OID'] = aobj.OID
                            d['ValueLink'] = 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d' % (aobj.CID, aobj.OID, random.randint(1, 10000000), )
                            l.append(d)
                        aobj.Next()
                    fieldvalue['Value'] = l
            else:
                rclass = afield.ClassOfType
                rfields = rclass.GetFieldsList()
                lheader=[{
                   'label': 'lp',
                   'field': '_cnt',
                   'name': '_cnt',
                   'align': 'right',
                   'sortable': True,
                   'FieldTypeID': 0x20,
                }] # yapf: disable
                lvfields = []
                rcntid = 0
                for rfname in rfields:
                    rfield = rclass.FieldsByName(rfname)
                    if rfield.WWWDisabled or rfield.IsInteractive != '1' or rfield.IsAliased != '1':
                        continue
                    rtid = int(rfield.FieldTypeID)
                    if (rtid > ICORInterface.MAX_ICOR_SYSTEM_TYPE) and (afield.WWWSingleValue or afield.FieldEditor == 'ObjectsList'):
                        continue
                    alg = rfield.AlignmentStd
                    if alg == 0:
                        align = 'left'
                    elif alg == 1:
                        align = 'right'
                    elif alg == 2:
                        align = 'center'
                    else:
                        align = 'left'
                    rh={
                       'label': CP1250_To_UTF8(rfield.FieldNameAsDisplayed),
                       'field': rfname,
                       'name': rfname,
                       'align': align,
                       'sortable': True,
                       'FieldTypeID': rtid,
                    } # yapf: disable
                    lheader.append(rh)
                    lvfields.append([rfield, rfname, rtid])
                    rcntid = rcntid + 1
                fieldvalue['columns'] = lheader
                fieldvalue['tableFilter'] = ''
                fieldvalue['pagination']={
                   'sortBy': '_cnt',
                   'descending': False,
                   'page': 1,
                   'rowsPerPage': 10,
                } # yapf: disable
                fvalues = []
                dgroups = {}
                rcntid = 1
                while aobj:
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', UID):
                        dvalues={
                           '_CID':aobj.CID,
                           '_OID':aobj.OID,
                           '_Link':'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d'%(aobj.CID,aobj.OID,random.randint(1,10000000),),
                           '_cnt':rcntid,
                        } # yapf: disable
                        for rfield, rfname, rtid in lvfields:
                            if rtid <= ICORInterface.MAX_ICOR_SYSTEM_TYPE:
                                v = storageutil.CP1250_To_UTF8_Unicode(rfield[aobj.OID])
                                dvalues[rfname] = v
                                if rfname == 'Grupa':
                                    dgroups[v] = {'label': v, 'value': v}
                            else:
                                robj = aobj[rfname]
                                l = []
                                while robj:
                                    if ICORSecurity.CheckRecursiveAccessLevelForUser(robj, 'AccessLevelView', UID):
                                        d = {}
                                        lv = robj.AsColumnValues()
                                        d['Value'] = CP1250_To_UTF8(', '.join(lv))
                                        d['_CID'] = robj.CID
                                        d['_OID'] = robj.OID
                                        d['ValueLink'] = 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d' % (robj.CID, robj.OID, random.randint(1, 10000000), )
                                        l.append(d)
                                    robj.Next()
                                dvalues[rfname] = l
                        fvalues.append(dvalues)
                        rcntid = rcntid + 1
                    aobj.Next()
                fieldvalue['Values'] = fvalues
                lg = dgroups.values()
                lg.sort()
                fieldvalue['Groups'] = lg
                fieldvalue['GroupSel'] = []
                fieldvalue['ValueURL'] = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s&XMLData=1' % (aclass.CID, aoid, afield.Name)
        return fieldvalue

    def WriteFieldSheet(self, init, asheetname, afields, asheetid, aclass, aoid, brcid=-1, broid=-1):
        UID = init.UID
        sheet = {}
        fieldvalues = []
        if not aclass.WWWDisableDescription:
            sheet['WWWDescription'] = storageutil.CP1250_To_UTF8(aclass.WWWDescription)
        lWWWEditPageTopHTML = []
        hobj = aclass.WWWEditPageTopHTML
        while hobj:
            lWWWEditPageTopHTML.append(storageutil.CP1250_To_UTF8(hobj.HTMLText))
            hobj.Next()
        sheet['WWWEditPageTopHTML'] = lWWWEditPageTopHTML
        acntid = 0
        for afitem in afields:
            ftid, fnameasdisplayed, fname, afield = afitem
            fieldvalue={
               'tabid': ftid,
               'FieldNameAsDisplayed':fnameasdisplayed,
               'Name':fname,
               'cnt':acntid,
            } # yapf: disable
            self.FieldFunc(init, aclass, afield, aoid, fieldvalue, acntid)
            fieldvalues.append(fieldvalue)
            acntid = acntid + 1
        lWWWEditPageBottomHTML = []
        hobj = aclass.WWWEditPageBottomHTML
        while hobj:
            lWWWEditPageBottomHTML.append(storageutil.CP1250_To_UTF8(hobj.HTMLText))
            hobj.Next()
        sheet['WWWEditPageBottomHTML'] = lWWWEditPageBottomHTML
        return sheet, fieldvalues

    def WriteClassMenu(self, menus, eclass, amenu, OID, alevel):
        sisrc = ''
        slineseparator = '<br>'
        if amenu.Action == 'ObjectApplyMethods':
            amlist = eclass.GetMethodsList()
            mobj = eclass[OID]
            for amname in amlist:
                amethod = eclass.MethodsByName(amname)
                if amethod is None:
                    continue
                if not amethod.WWWMethod:
                    continue
                if not ICORSecurity.CheckAccessLevelForUser(amethod.AllowReadGroups, amenu.uid):
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
                            f2 = cStringIO.StringIO()
                            try:
                                res = apply(pageevent, (mobj, amenu, f2))
                                #stext=f2.getvalue()
                            finally:
                                f2.close()
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
                dmenu = {}
                alink = 'icormain.asp?jobtype=menuitem&OID=' + str(amenu.oid) + '&param=' + str(eclass.CID) + '_' + str(OID) + '_' + amethod.Name + blink
                alink = alink + '&brCID=' + str(amenu.BackRefCID) + '&brOID=' + str(amenu.BackRefOID)
                smname = amethod.WWWDescription
                if not smname:
                    smname = amethod.Name
                if amethod.WWWConfirmExecute:
                    dmenu['confirm'] = 1
                else:
                    dmenu['confirm'] = 0
                dmenu['level'] = alevel
                dmenu['link'] = alink
                irefs = amethod.WWWMenuImageLink
                wi = 0
                if irefs:
                    dmenu['image'] = irefs.Location[irefs.OID]
                    wi = 1
                if not wi:
                    dmenu['image'] = '/icormanager/images/icons/silk/icons/page_forward.png'
                    wi = 1
                dmenu['label'] = storageutil.CP1250_To_UTF8(smname)
                dmenu['MenuOID'] = str(amenu.oid)
                menus.append(dmenu)
        else:
            wmenushow = 1
            if amenu.Action in ['ObjectAdd', ]:
                mobj = eclass[OID]
                pclass = ICORInterface.aICORDBEngine.Classes[amenu.ParamItem]
                aseclev = 0
                if pclass is not None:
                    aseclev = pclass.CID == eclass.CID
                    sisrc = icorwwwlib.GetClassImageSrc(pclass)
                wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelEdit', amenu.uid, aseclev)
            elif amenu.Action in ['ObjectEdit', ]:
                mobj = eclass[OID]
                #         print '*** Object Edit ACL Check:',mobj,'***'
                wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelEdit', amenu.uid)
                sisrc = icorwwwlib.GetClassImageSrc(eclass)

    #         print 'wmenushow=',wmenushow
            elif amenu.Action in ['ObjectDelete', ]:
                mobj = eclass[OID]
                wmenushow = ICORSecurity.CheckRecursiveAccessLevelForUser(mobj, 'AccessLevelDelete', amenu.uid)
                sisrc = icorwwwlib.GetClassImageSrc(eclass)
            emethod = eclass.MethodsByName('OnWWWAction')
            if wmenushow and emethod is not None:
                try:
                    mname = emethod.MethodPath
                    mname = mname.replace('\\', '_')
                    mname = mname.replace('/', '_')
                    pagemethod = __import__(mname)
                    if hasattr(pagemethod, 'OnBeforeWWWAction'):
                        pageevent = getattr(pagemethod, 'OnBeforeWWWAction')
                        if pageevent is not None:
                            mobj = eclass[OID]
                            f2 = cStringIO.StringIO()
                            try:
                                wmenushow = apply(pageevent, (mobj, amenu, f2))
                                #stext=f2.getvalue()
                            finally:
                                f2.close()
                except:
                    print 'Error during default menu class link action:', amenu.Action, ' - ', emethod.MethodPath
                    raise
            if wmenushow:
                dmenu = {}
                scaption = amenu.AsPageCaption + ' ' + amenu.AsPageSubCaption
                alink = 'icormain.asp?jobtype=menuitem&OID=' + str(amenu.oid) + '&param=' + str(eclass.CID) + '_' + str(OID) + '_'    #+fieldname
                alink = alink + '&brCID=' + str(amenu.BackRefCID) + '&brOID=' + str(amenu.BackRefOID)
                if amenu.ConfirmHRef:
                    dmenu['confirm'] = 1
                else:
                    dmenu['confirm'] = 0
                dmenu['level'] = alevel
                dmenu['link'] = alink
                wi = 0
                if amenu.ImageLocation:
                    dmenu['image'] = amenu.ImageLocation
                    wi = 1
                if not wi and sisrc:
                    dmenu['image'] = sisrc
                    wi = 1
                if not wi:
                    dmenu['image'] = '/icormanager/images/icons/silk/icons/page_go.png'
                    wi = 1
                dmenu['label'] = storageutil.CP1250_To_UTF8(scaption)
                dmenu['MenuOID'] = str(amenu.oid)
                menus.append(dmenu)
        for smenu in amenu.SubMenus:
            if smenu.IsVisibleByProfile(amenu.uid):
                self.WriteClassMenu(menus, eclass, smenu, OID, alevel + 1)

    def GetClassWWWMenu(self, init, aclass, aoid, acid, broid, brcid):
        menus = []
        mrefs = aclass.GetWWWMenuRefs()
        while mrefs:
            amenu = ICORWWWMenuItem(init.UID, mrefs.OID, brcid=brcid, broid=broid)
            if amenu.IsVisibleByProfile(init.UID):
                self.WriteClassMenu(menus, aclass, amenu, aoid, 0)
            mrefs.Next()
        i = 0
        for menu in menus:
            menu['cnt'] = i
            i += 1
        return menus

    def GetObjectEdit(self, init, oid, cid, broid, brcid):
        UID = init.UID
        ret = {}
        status = 0
        info = None
        aclass = ICORInterface.aICORDBEngine.Classes[cid]
        if aclass is None:
            return ret, 1, 'brak dostępu'
        w = aclass.ObjectExists(oid)
        aobj = aclass[oid]
        if w and not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', init.UID):
            w = 0
        if not w:
            return ret, 1, 'brak danych'
        sheetsinfo = self.GetSheetsInfo(aclass)
        sheetids = sheetsinfo.keys()
        sheetids.sort()
        menus = self.GetClassWWWMenu(init, aclass, oid, cid, broid, brcid)
        aWWWDescription = ''
        if not aclass.WWWDisableDescription:
            aWWWDescription = storageutil.CP1250_To_UTF8(aclass.WWWDescription)
        if not aWWWDescription and sheetsinfo:
            aWWWDescription = sheetsinfo[0].name
        if not aWWWDescription:
            aWWWDescription = aclass.NameOfClass
        aimgsrc = icorwwwlib.GetClassImageSrc(aclass)
        ret={
           'sheets':sheetsinfo,
           'sheetids':sheetids,
           'menus':menus,
           'wwwdescription':aWWWDescription,
           'imgsrc':aimgsrc,
        } # yapf: disable
        return ret, status, info

    def GetObjectEditSheet(self, init, oid, cid, broid, brcid, sheetid):
        UID = init.UID
        ret = {}
        status = 0
        info = None
        aclass = ICORInterface.aICORDBEngine.Classes[cid]
        if aclass is None:
            return ret, 1, 'brak dostępu'
        w = aclass.ObjectExists(oid)
        aobj = aclass[oid]
        if w and not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', init.UID):
            w = 0
        if not w:
            return ret, 1, 'brak danych'
        sheetsinfo = self.GetSheetsInfo(aclass, agetfields=1)
        sheetids = sheetsinfo.keys()
        sheetids.sort()
        sheet, fields = self.WriteFieldSheet(init, sheetsinfo[sheetid]['name'], sheetsinfo[sheetid]['fields'], sheetid, aclass, oid, brcid=brcid, broid=broid)
        ret={
           'sheet':sheet,
           'fields':fields,
        } # yapf: disable
        return ret, status, info

    def GetObjectEditFormSubmit(self, init, menuoid, oid, cid, broid, brcid, data):
        UID = init.UID
        ret = {}
        aclass = ICORInterface.aICORDBEngine.Classes[cid]
        if aclass is None:
            return ret, 1, 'brak dostępu'
        w = aclass.ObjectExists(oid)
        aobj = aclass[oid]
        if w and not ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', init.UID):
            w = 0
        if not w:
            return ret, 1, 'brak danych'
        ajsonres = {'status': 0, 'info': '', 'data': data}
        aparms = ServerUtil.ICORReport(data.get('values', {}))
        dodefaultmenuitemsubmit.DoDefaultMenuItemSubmitJSON(menuoid, oid, cid, broid, brcid, aparms, init.UID, ajsonres)
        return ajsonres['data'], ajsonres['status'], ajsonres['info']
