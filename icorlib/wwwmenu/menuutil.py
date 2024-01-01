from icorlib.icorinterface import *
from icorlib.icoriterators import *
from icorlib.icorsecurity import *
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
from CLASSES_Library_ICORBase_Interface_ICORSummary import DoSummaryLoad, DoSummarySave
from icorlib.wwwmenu.xmlmenuutil import XMLMenuExporter, XMLMenuImporter
import string
import re
import random
import urlparse
import types

try:
    import json
except:
    import simplejson as json

import appplatform.storageutil as storageutil

_jsonEncode = json.JSONEncoder(ensure_ascii=True, check_circular=False, encoding='utf-8').encode


def jsonEncode(s):
    ret = ''
    try:
        s = storageutil.CP1250_To_UTF8_Unicode(s)
        ret = _jsonEncode(s)
    except:
        print '$$ error jsonencode'
        raise
    return ret


class SystemMenuIterator(ICORObjectIterator):

    def __init__(self, afield, oid, uid):
        self.field = afield
        self.oid = oid
        self.uid = uid
        self.result = []
        ICORObjectIterator.__init__(self)
        self.Process()

    def Process(self):
        self.ForEachRefObject(self.field, self.oid)

    def OnObject(self, aclass, aoid):
        aitem = ICORWWWMenuItem(self.uid, aoid)
        if aitem.Accepted:
            self.result.append(aitem)


class JSONMenu:

    def __init__(self, file):
        self.outputfile = file
        self.file = ['[']
        self.stack = []

    def close(self):
        self.file.append(']')
        self.outputfile.write(self.AsString())

    def TagOpen(self, atag, d=None, aindent='', aclosetag=0, ainsertemptyattributes=0, anoattributeconversion=0, anl='\n', asortattrnames=None, avalue='', avalueascdata=1, aproperxmlattrs=None):
        if not self.stack:
            self.stack.append(1)
            return
        aindent = '  ' * len(self.stack)
        afirst = self.stack.pop()
        if not afirst:
            self.file.append(aindent + ',')
        afirst = 0
        #d.allowmove
        #d.context
        for akey, avalue in d.items():
            d[akey] = avalue.replace(chr(92), chr(92) + chr(92))
        acontext = d.get('context', '').replace('XMLData=1', 'XMLData=json')
        asrc = d.get('src', '').replace('XMLData=1', 'XMLData=json')
        astate = ''
        arel = d.get('rel', 'section')
        if asrc:
            astate = ',"state":"closed"'
        aicon = d.get('icon', '')
        if not aicon:
            if asrc:
                aicon = '/icorimg/silk/folder.png'
            else:
                aicon = '/icorimg/silk/page.png'
        atext = aindent + '{"attributes":{"rel":%s},"data":{"title":%s,"icon":%s,"attributes":{"href":%s,"openicon":%s,"coid":%s,"roid":%s,"context":%s,"submenu":%s}}%s,"children":[' % (jsonEncode(arel), jsonEncode(d.get('text', '')), jsonEncode(aicon), jsonEncode(d.get('action', '')), jsonEncode(d.get('openIcon', '')), jsonEncode(d.get('coid', '')), jsonEncode(d.get('roid', '')), jsonEncode(acontext), jsonEncode(asrc), astate)
        self.file.append(atext)

        self.stack.append(0)
        if aclosetag:
            self.file.append(aindent + ']}')
        else:
            self.stack.append(1)

    def TagClose(self, atag='', aindent=''):
        aindent = '  ' * len(self.stack)
        self.stack.pop()
        if self.stack:
            self.file.append(aindent + ']}')

    def AsString(self):
        return '\n'.join(self.file)


class JSONContext:

    def __init__(self, file):
        self.outputfile = file
        self.file = ['[']
        self.comma = ''

    def close(self):
        self.file.append(']')
        self.outputfile.write(self.AsString())

    def TagOpen(self, atag, d=None, aindent='', aclosetag=0, ainsertemptyattributes=0, anoattributeconversion=0, anl='\n', asortattrnames=None, avalue='', avalueascdata=1, aproperxmlattrs=None):
        if atag in ['menu', ]:
            return
        if d is None:
            d = {}
        l = d.keys()
        l.sort()
        ltext = []
        for akey in l:
            ltext.append('%s:%s' % (jsonEncode(akey), jsonEncode(d[akey])))
        atext = aindent + self.comma + '{' + ','.join(ltext) + '}'
        self.file.append(atext)
        self.comma = ','

    def TagClose(self, atag='', aindent=''):
        pass

    def AsString(self):
        return '\n'.join(self.file)


class JSONContextSubmit:

    def __init__(self, file):
        self.outputfile = file
        self.file = ['[']
        self.comma = ''

    def close(self):
        self.file.append(']')
        self.outputfile.write(self.AsString())

    def TagOpen(self, atag, d=None, aindent='', aclosetag=0, ainsertemptyattributes=0, anoattributeconversion=0, anl='\n', asortattrnames=None, avalue='', avalueascdata=1, aproperxmlattrs=None):
        if atag in ['result', ]:
            return
        if d is None:
            d = {}
        l = d.keys()
        l.sort()
        ltext = []
        for akey in l:
            ltext.append('%s:%s' % (jsonEncode(akey), jsonEncode(d[akey])))
        atext = aindent + self.comma + '{' + ','.join(ltext) + '}'
        self.file.append(atext)
        self.comma = ','

    def TagClose(self, atag='', aindent=''):
        pass

    def AsString(self):
        return '\n'.join(self.file)


class ICORWWWMenuItem:

    def __init__(self, uid, oid, awwwparam='', brcid=-1, broid=-1, jsonres=None):
        self.uid = uid
        self.oid = oid
        self.jsonres = jsonres
        self.asJSON = 1
        if jsonres is None:
            self.asJSON = 0
        self.Accepted = 1
        self.MenuClass = aICORDBEngine.Classes['CLASSES\Library\NetBase\WWW\Dictionary\Menu']
        self.Attrs = {}
        self.Reports_ = None
        self.Summaries_ = None
        self.ParentMenu_, self.PrevSiblingMenu_, self.NextSiblingMenu_ = -1, -1, -1
        self.BackRefCID = brcid
        self.BackRefOID = broid
        if awwwparam is None:
            awwwparam = ''
        slp = string.split(awwwparam, '_')
        self.WWWParam = ()
        for sp in slp:
            try:
                self.WWWParam = self.WWWParam + (int(sp), )
            except:
                self.WWWParam = self.WWWParam + (sp, )

    def __setattr__(self, name, value):
        attrs = ('Caption', 'AsPageCaption', 'AsPageSubCaption', 'AsPageDescription', 'AsPageShortDescription', 'PageHTML', 'PageHTMLInfo', 'WorkSheetQueriesIDs', 'ParamSubItem')
        if name in attrs:
            #         self.Attrs[name]=value
            afield = self.MenuClass.FieldsByName(name)
            afield[self.oid] = value
            return
        if name == 'AccessLevel':
            if not isinstance(value, types.StringTypes):
                value = value.AsString()
            self.MenuClass.AccessLevel[self.oid] = value
            return
        if name == 'AccessLevelEdit':
            if not isinstance(value, types.StringTypes):
                value = value.AsString()
            self.MenuClass.AccessLevelEdit[self.oid] = value
            return
        if name == 'AccessLevelStored':
            if not isinstance(value, types.StringTypes):
                value = value.AsString()
            self.MenuClass.AccessLevelStored[self.oid] = value
            return
        self.__dict__[name] = value

    def __getattr__(self, name):
        attrs=('Caption','ParamItem','ParamSubItem','ParamValue1','ParamValue2','ParamValue3',\
           'AsPageSubCaption','AsPageDescription','AsPageShortDescription','WorkSheetQueriesIDs')
        if name in attrs:
            afield = self.MenuClass.FieldsByName(name)
            value = afield[self.oid]
            #         if not self.Attrs.has_key(name):
            #            afield=self.MenuClass.FieldsByName(name)
            #            value=afield[self.oid]
            #            self.Attrs[name]=value
            #         else:
            #            value=self.Attrs[name]
            return value
        if name == 'AsPageCaption':
            s = self.MenuClass.AsPageCaption[self.oid]
            if s == '':
                s = self.MenuClass.Caption[self.oid]
            return s
        if name == 'ConfirmHRef':
            if self.ConfirmHRef_ is None:
                self.ConfirmHRef_ = self.MenuClass.ConfirmHRef.ValuesAsInt(self.oid)
            return self.ConfirmHRef_
        if name == 'DisableInReport':
            if self.DisableInReport_ is None:
                self.DisableInReport_ = self.MenuClass.DisableInReport.ValuesAsInt(self.oid)
            return self.DisableInReport_
        if name == 'WorkflowNoRecur':
            if self.WorkflowNoRecur_ is None:
                self.WorkflowNoRecur_ = self.MenuClass.WorkflowNoRecur.ValuesAsInt(self.oid)
            return self.WorkflowNoRecur_
        if name in ['PageHTML', 'PageHTMLInfo']:
            afield = self.MenuClass.FieldsByName(name)
            value = afield[self.oid]
            if value == '<P>&nbsp;</P>':
                value = ''
            value = string.replace(value, chr(13), '')
            return re.sub('file\:\/+', '', value)
        if name == 'FontColor':
            if self.FontColor_ is None:
                arefs = self.MenuClass.DisplayAttributes.GetRefList(self.oid)
                if arefs.position >= 0:
                    brefs = arefs.FontColor.GetRefList(arefs.OID)
                    if brefs.position >= 0:
                        self.FontColor_ = brefs.AsRGB[brefs.OID]
                    else:
                        self.FontColor_ = ''
                else:
                    self.FontColor_ = ''
            return self.FontColor_
        if name == 'Action':
            if self.Action_ is None:
                arefs = self.MenuClass.Action.GetRefList(self.oid)
                if arefs.position >= 0:
                    self.Action_ = arefs.Name[arefs.OID]
                else:
                    self.Action_ = ''
            return self.Action_
        if name == 'ViewAs':
            if self.ViewAs_ is None:
                arefs = self.MenuClass.ViewAs.GetRefList(self.oid)
                if arefs.position >= 0:
                    self.ViewAs_ = arefs.Name[arefs.OID]
                else:
                    self.ViewAs_ = ''
            return self.ViewAs_
        if name == 'Reports':
            if self.Reports_ is None:
                self.Reports_ = self.MenuClass.Report.GetRefList(self.oid)
            return self.Reports_
        if name == 'Summaries':
            if self.Summaries_ is None:
                self.Summaries_ = self.MenuClass.Summaries.GetRefList(self.oid)
            return self.Summaries_
        if name == 'ImageName':
            if self.ImageName_ is None:
                arefs = self.MenuClass.Image.GetRefList(self.oid)
                if arefs.position >= 0:
                    self.ImageName_ = arefs.Name[arefs.OID]
                else:
                    self.ImageName_ = ''
            return self.ImageName_
        if name == 'ImageLocation':
            if self.ImageLocation_ is None:
                arefs = self.MenuClass.Image.GetRefList(self.oid)
                if arefs.position >= 0:
                    self.ImageLocation_ = arefs.Location[arefs.OID]
                else:
                    self.ImageLocation_ = ''
            return self.ImageLocation_
        if name == 'ImageAlt':
            if self.ImageAlt_ is None:
                arefs = self.MenuClass.Image.GetRefList(self.oid)
                if arefs.position >= 0:
                    self.ImageAlt_ = arefs.Alt[arefs.OID]
                else:
                    self.ImageAlt_ = ''
            return self.ImageAlt_
        if name == 'SubMenus':
            if self.SubMenus_ is None:
                miterator = SystemMenuIterator(self.MenuClass.SubMenu, self.oid, self.uid)
                self.SubMenus_ = miterator.result
            return self.SubMenus_
        if name == 'ReferredMenu':
            if self.ReferredMenu_ is None:
                miterator = SystemMenuIterator(self.MenuClass.ReferredMenu, self.oid, self.uid)
                self.ReferredMenu_ = miterator.result
            return self.ReferredMenu_
        if name == 'ParentMenu':
            if type(self.ParentMenu_) == type(-1):
                self.ParentMenu_ = None
                arefs = self.MenuClass.ParentMenu.GetRefList(self.oid)
                if arefs:
                    self.ParentMenu_ = ICORWWWMenuItem(self.uid, arefs.OID)
            return self.ParentMenu_
        if name == 'PrevSiblingMenu':
            if type(self.PrevSiblingMenu_) == type(-1):
                self.PrevSiblingMenu_ = None
                pmenu = self.ParentMenu
                if pmenu is None:
                    return
                lmenu = None
                for amenu in pmenu.SubMenus:
                    if amenu.oid == self.oid:
                        self.PrevSiblingMenu_ = lmenu
                        return lmenu
                    lmenu = amenu
            return self.PrevSiblingMenu_
        if name == 'NextSiblingMenu':
            if type(self.NextSiblingMenu_) == type(-1):
                self.NextSiblingMenu_ = None
                pmenu = self.ParentMenu
                if pmenu is None:
                    return
                w = 0
                for amenu in pmenu.SubMenus:
                    if w:
                        self.PrevSiblingMenu_ = amenu
                        return amenu
                    if amenu.oid == self.oid:
                        w = 1
            return self.NextSiblingMenu_
        if name == 'AccessLevel':
            return self.MenuClass.AccessLevel.GetRefList(self.oid)
        if name == 'AccessLevelEdit':
            return self.MenuClass.AccessLevelEdit.GetRefList(self.oid)
        if name == 'AccessLevelStored':
            return self.MenuClass.AccessLevelStored.GetRefList(self.oid)

    def NewMenu(self, aname='', acaption='', aaction=''):
        moid = self.MenuClass.AddObject()
        if aname:
            self.MenuClass.Name[moid] = aname
        if acaption:
            self.MenuClass.Caption[moid] = acaption
        if not aaction:
            aaction = 'MenuAsPage'
        self.MenuClass.Profile[moid] = self.MenuClass.Profile[self.oid]
        toid = self.MenuClass.Action.ClassOfType.Name.Identifiers(aaction)
        if toid >= 0:
            self.MenuClass.Action[moid] = [toid, self.MenuClass.Action.ClassOfType.CID]
        bmenu = ICORWWWMenuItem(self.uid, moid)
        return bmenu

    def RemoveMenuRefFromParentMenu(self, adelete=0):
        if self.ParentMenu is None:
            aICORWWWServerInterface.ServerClass.Menu.DeleteRefs(aICORWWWServerInterface.OID, [[self.oid, self.MenuClass.CID], ])
            aICORWWWServerInterface.ServerClass.Introduction.DeleteRefs(aICORWWWServerInterface.OID, [[self.oid, self.MenuClass.CID], ])
        else:
            self.MenuClass.SubMenu.DeleteRefs(self.ParentMenu.oid, [[self.oid, self.MenuClass.CID], ])
        self.ParentMenu = -1
        aICORDBEngine.RepositoryChange('WWWMenuDelete', self.oid)
        if adelete:
            self.MenuClass.DeleteObject(self.oid)

    def IsInServerMenu(self):
        arefs = aICORWWWServerInterface.ServerClass.Menu.GetRefList(aICORWWWServerInterface.OID)
        return arefs.RefExists(self.oid, self.MenuClass.CID)

    def IsInServerIntroduction(self):
        arefs = aICORWWWServerInterface.ServerClass.Introduction.GetRefList(aICORWWWServerInterface.OID)
        return arefs.RefExists(self.oid, self.MenuClass.CID)

    def InsertMenuBefore(self, bmenu):
        bmenu.RemoveMenuRefFromParentMenu()
        if self.ParentMenu is None:
            if self.IsInServerMenu():
                aICORWWWServerInterface.ServerClass.Menu.AddRefs(aICORWWWServerInterface.OID, [[bmenu.oid, self.MenuClass.CID], ], ainsertbefore=[self.oid, self.MenuClass.CID])
            elif self.IsInServerIntroduction():
                aICORWWWServerInterface.ServerClass.Introduction.AddRefs(aICORWWWServerInterface.OID, [[bmenu.oid, self.MenuClass.CID], ], ainsertbefore=[self.oid, self.MenuClass.CID])
            else:
                print 'Menu:', self.Caption, 'nie posiada menu nadrzednego'
                return
        else:
            self.MenuClass.SubMenu.AddRefs(self.ParentMenu.oid, [[bmenu.oid, self.MenuClass.CID], ], ainsertbefore=[self.oid, self.MenuClass.CID])
        self.SubMenus_ = None
        aICORDBEngine.RepositoryChange('WWWMenuInsertBefore', self.oid, bmenu.oid)

    def AddChildMenu(self, bmenu):
        bmenu.RemoveMenuRefFromParentMenu()
        self.MenuClass.SubMenu.AddRefs(self.oid, [[bmenu.oid, self.MenuClass.CID], ])
        self.SubMenus_ = None
        aICORDBEngine.RepositoryChange('WWWMenuAddChild', self.oid, bmenu.oid)

    def AddSummary(self, asummoid, asumminfo=0, ainsertbefore=None, adeletesummoidfromownermenu=0, anocreatesummaryitem=0):
        summclass = aICORDBEngine.Classes['CLASSES_System_SummaryItem']
        self.Summaries_ = None
        sclass = self.MenuClass.Summaries.ClassOfType
        if not asumminfo:
            soid = sclass.AddObject()
            sclass.Summary[soid] = str(asummoid)
            sclass.ParentMenu[soid] = [self.oid, self.MenuClass.CID]
            sclass.Name[soid] = summclass.Name[asummoid]
        else:
            if adeletesummoidfromownermenu:
                sobj = sclass[asummoid]
                bmenu = ICORWWWMenuItem(self.uid, sobj.ParentMenu.OID)
                if bmenu is not None:
                    bmenu.DeleteSummary(asummoid)
                soid = asummoid
            elif anocreatesummaryitem:
                soid = asummoid
            else:
                soid = sclass.AddObject()
                sclass.ParentMenu[soid] = [self.oid, self.MenuClass.CID]
                sclass.Name[soid] = sclass.Name[asummoid]
                sclass.CustomPageByMethod[soid] = sclass.CustomPageByMethod[asummoid]
                sclass.DisableInHTMLReport[soid] = sclass.DisableInHTMLReport[asummoid]
                sclass.Parameter[soid] = sclass.Parameter[asummoid]
                sclass.WorksheetQueries[soid] = sclass.WorksheetQueries[asummoid]
                sclass.GeoProject[soid] = sclass.GeoProject[asummoid]
                s = sclass.Summary[asummoid]
                if s:
                    try:
                        bsummoid = int(s)
                    except:
                        print 'niepoprawny numer zestawienia', s
                        bsummoid = -1
                    if bsummoid >= 0:
                        atext = DoSummarySave(bsummoid)
                        bsummoid = DoSummaryLoad(atext, ainteractive=0)
                        if bsummoid >= 0:
                            sclass.Summary[soid] = str(bsummoid)
        self.MenuClass.Summaries.AddRefs(self.oid, [soid, sclass.CID], ainsertbefore=ainsertbefore)
        self.RefreshSummaries()

    def DeleteSummary(self, asummoid, adelete=0):
        self.Summaries_ = None
        self.MenuClass.Summaries.DeleteRefs(self.oid, [asummoid, self.MenuClass.Summaries.ClassOfType.CID])
        if adelete:
            self.MenuClass.Summaries.ClassOfType.DeleteObject(asummoid)
        aICORDBEngine.RepositoryChange('WWWMenuSummaryDelete', asummoid)

    def AddReport(self, arepoid):
        self.Reports_ = None
        sclass = self.MenuClass.Report.ClassOfType
        self.MenuClass.Report.AddRefs(self.oid, [arepoid, sclass.CID])
        self.RefreshReports()

    def DeleteReport(self, arepoid, adelete=0):
        self.Reports_ = None
        self.MenuClass.Report.DeleteRefs(self.oid, [[arepoid, self.MenuClass.Report.ClassOfType.CID], ])
        if adelete:
            self.MenuClass.Report.ClassOfType.DeleteObject(arepoid)
        aICORDBEngine.RepositoryChange('WWWMenuReportDelete', arepoid)

    def GetPageHTML(self, akind='Text'):
        mobj = self.MenuClass[self.oid]
        hobj = mobj.PageHTMLItems
        while hobj.Exists():
            if hobj.PageName.Name == akind:
                return hobj.TextValue
            hobj.Next()

    def IsVisibleByProfile(self, auid=0):
        #print 'IsVisibleByProfile:',self.oid,auid,self.AsPageCaption
        arefs = self.MenuClass.Profile.GetRefList(self.oid)
        if not arefs.IsEmpty():
            if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
                #print '    $$ not arefs.RefsExists'
                return 0
        arefs = self.MenuClass.AccessLevel.GetRefList(self.oid)
        ret = CheckAccessLevelForUser(arefs, auid)
        #if not ret:
        #print '    $$ not ret'
        return ret

    def IsVisibleForEdit(self, auid=0):
        arefs = self.MenuClass.Profile.GetRefList(self.oid)
        if not arefs.IsEmpty():
            if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
                return 0
        amenu = self
        brefs = None
        while amenu is not None:
            arefs = self.MenuClass.AccessLevelEdit.GetRefList(amenu.oid)
            if arefs:
                brefs = arefs
                break
            amenu = amenu.ParentMenu
        if brefs:
            return CheckAccessLevelForUser(arefs, auid)
        return 0

    def StoreAccessLevel(self, adisabled=0):
        acoid = self.MenuClass.AccessLevel.ClassOfType.Name.Identifiers('Disabled')
        sdref = str(acoid) + ':' + str(self.MenuClass.AccessLevel.ClassOfType.CID) + ':'
        if self.MenuClass.AccessLevel[self.oid] == sdref:
            return
        self.MenuClass.AccessLevelStored[self.oid] = self.MenuClass.AccessLevel[self.oid]
        if adisabled and acoid >= 0:
            self.MenuClass.AccessLevel[self.oid] = sdref
        self.Refresh()

    def RestoreAccessLevel(self):
        self.MenuClass.AccessLevel[self.oid] = self.MenuClass.AccessLevelStored[self.oid]
        self.Refresh()

    def SetEditMode(self, adisable=1):
        if adisable:
            sclass = self.MenuClass.AccessLevelEdit.ClassOfType
            soid = sclass.Name.Identifiers('Disabled')
            sref = str(soid) + ':' + str(sclass.CID) + ':'
        else:
            sref = ''
        self.MenuClass.AccessLevelEdit[self.oid] = sref
        for amenu in self.SubMenus:
            amenu.SetEditMode(adisable=adisable)

    def GetMenuRef(self, aedit=0, amode='', nobodytags=0, noscripttags=0, asubmit=0, aparms=None):
        saddparams = urlparse.urlparse(self.ParamValue1)[4]
        if saddparams:
            saddparams = '&' + saddparams
        retvalue = ''
        if self.Action == 'HTML Redirect':
            s = self.ParamValue1
            if '?' in s:
                s = s + '&MenuOID=' + str(self.oid)
            else:
                s = s + '?MenuOID=' + str(self.oid)
            retvalue = s
        elif self.Action == 'ObjectsView':
            pclass = aICORDBEngine.Classes[self.ParamItem]
            if pclass is None:
                retvalue = ''
            else:
                retvalue = 'icormain.asp?jobtype=objectsview&CID=' + str(pclass.CID) + '&OID=-1' + '&MenuOID=' + str(self.oid) + saddparams
        elif self.Action == 'MenuAsPage':
            if aedit:
                if amode:
                    amode = "&passthrupagevalue=" + amode
                retvalue = 'icormain.asp?jobtype=menuitemedit&OID=' + str(self.oid) + '&nobodytags=' + str(nobodytags) + '&noscripttags=' + str(noscripttags) + amode + '&MenuOID=' + str(self.oid) + saddparams
            else:
                retvalue = 'icormain.asp?jobtype=menuaspage&OID=' + str(self.oid) + '&MenuOID=' + str(self.oid) + saddparams
        elif self.Action == 'CustomPageByMethod':
            if asubmit:
                sp = ''
                if aparms is not None:
                    sl = ['', ]
                    for akey, avalue in aparms.items():
                        sl.append(akey + '=' + avalue)
                    if len(sl) > 1:
                        sp = string.join(sl, '&')
                retvalue = 'icormain.asp?jobtype=reportsubmit&OID=%d&ReportOID=%d&RandomValue=%d%s' % (self.oid, self.Reports.OID, random.randint(1, 10000000), sp) + saddparams
            else:
                retvalue = 'icormain.asp?jobtype=custompagebymethod&OID=' + str(self.oid) + '&MenuOID=' + str(self.oid) + saddparams
        elif self.Action == 'SummaryList':
            retvalue = 'icormain.asp?jobtype=summarylist&OID=' + str(self.oid) + '&MenuOID=' + str(self.oid) + saddparams
        else:
            if aedit:
                if amode:
                    amode = "&passthrupagevalue=" + amode
                retvalue = 'icormain.asp?jobtype=menuitemedit&OID=' + str(self.oid) + '&nobodytags=' + str(nobodytags) + '&noscripttags=' + str(noscripttags) + amode + '&MenuOID=' + str(self.oid) + saddparams
            else:
                retvalue = 'icormain.asp?jobtype=menuitem&OID=' + str(self.oid) + '&MenuOID=' + str(self.oid) + saddparams
        if self.BackRefCID > 0:
            retvalue = retvalue + '&brCID=' + str(self.BackRefCID) + '&brOID=' + str(self.BackRefOID)
        return retvalue

    def Refresh(self):
        aICORDBEngine.RepositoryChange('WWWMenuRefresh', -1, self.oid)

    def RefreshSummaries(self):
        aICORDBEngine.RepositoryChange('WWWMenuRefreshSummaries', -1, self.oid)

    def RefreshReports(self):
        aICORDBEngine.RepositoryChange('WWWMenuRefreshReports', -1, self.oid)

    def XMLExportSubItems(self, afile, aheader=1):
        aexporter = XMLMenuExporter()
        aexporter.XMLExportSubItems(self, afile, aheader)

    def XMLImportSubItems(self, afname):
        aparser = XMLMenuImporter()
        aparser.Parse(self, afname)

    def SetWorksheetQueries(self):
        aobj = self.MenuClass[self.oid]
        sobj = aobj.Summaries
        while sobj:
            qobj = sobj.WorksheetQueries
            while qobj:
                qobj.Status = 'Menu'
                qobj.Next()
            sobj.Next()
        for amenu in self.SubMenus:
            amenu.SetWorksheetQueries()

    def ShowParentRefs(self, afile, astart=''):
        l = []
        bmenu = self.ParentMenu
        while bmenu is not None:
            l.insert(0, '<a href="%s">%s</a>' % (bmenu.GetMenuRef(), bmenu.AsPageCaption))
            bmenu = bmenu.ParentMenu
        if astart:
            l.insert(0, '<a href="%s">Start</a>' % astart)
        l.append('<a href="%s">%s</a>' % (self.GetMenuRef(), self.AsPageCaption))    #l.append('...')
        afile.write('<font size="-2">%s</font><hr size=1>' % (string.join(l, ' / '), ))

    def Przenies(self, fout):
        fout.write('\n\n\n<!--%s-->\n\n\n' % self.Caption)
        fout.write(self.PageHTML)
        for amenu in self.SubMenus:
            amenu.Przenies(fout)

    def SprawdzTresc(self):
        fout = open('c:/icor/html/output.html', 'w')
        fout.write('<HTML>\n')
        fout.write('<HEAD>\n')
        fout.write('<link rel=STYLESHEET type="text/css" href="icor.css" title="SOI">\n')
        fout.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=windows-1250">\n')
        fout.write('<TITLE>Tabela</TITLE>\n')
        fout.write('</HEAD><BODY>\n\n')
        try:
            self.Przenies(fout)
            fout.write('</BODY></HTML>\n')
        finally:
            fout.close()
        return
        apatt = re.compile('\Wbody|html', re.I)
        s = self.PageHTML
        if apatt.search(s):
            print self.Caption
        for amenu in self.SubMenus:
            amenu.SprawdzTresc()

    def SetAction(self, aaction):
        self.Action__ = self.Action_
        self.Action_ = aaction

    def RestoreAction(self):
        self.Action_ = self.Action__
