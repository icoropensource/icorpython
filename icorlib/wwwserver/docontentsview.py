# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem, JSONMenu
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
from icorlib.icorsecurity import *
from CLASSES_Library_NetBase_WWW_HTML_Tree_SimpleLinks_Main import SimpleLinksHTMLTree
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_NetBase_WWW_Server_DoMenuWorkflowRecur as DoMenuWorkflowRecur
import string
import cStringIO


class ICORWWWServer:

    def __init__(self, aname='Default'):
        self.srvclass = aICORDBEngine.Classes['CLASSES\Library\NetBase\WWW\Server']
        self.OID = self.srvclass.Name.Identifiers(aname)
        if self.OID < 0:
            raise exception, 'Bad server name!'
        self.UID = 0
        self.file = None
        self.group = ''

    def Generate(self, fname, avalue, auid, amenuoid, aparam='', ajson=0, agroup=''):
        self.UID = auid
        self.MenuOID = amenuoid
        #      self.file=open(fname,'wb')
        if agroup == 'conf':    # conf,main
            mclass = self.srvclass.Menu.ClassOfType
            self.MenuOID = mclass.Name.Identifiers('Konfiguracja projektu')
        if agroup == 'system':    # conf,main
            mclass = self.srvclass.Menu.ClassOfType
            self.MenuOID = mclass.Name.Identifiers('System')
        self.group = agroup
        self.cntWWWMenuClassRecur = 0
        self.file = cStringIO.StringIO()
        try:
            if avalue == 'Introduction':
                self.Generate1()
            elif avalue == 'Contents':
                #            self.Generate2()
                self.Generate2B()
            elif avalue == 'MenuXML':
                if ajson:
                    self.jsonmenu = JSONMenu(self.file)
                    self.GenerateMenuXML(self.jsonmenu)
                else:
                    self.GenerateMenuXML()
            elif avalue == 'MenuFavGet':
                self.GenerateMenuFav()
            elif avalue == 'MenuFavSet':
                self.SetMenuFav(aparam)
            elif avalue == 'NavigationBar':
                self.Generate3()
            elif avalue == 'NavigationButtons':
                self.file.write('<HTML><HEAD><TITLE>ICOR Button Bar</TITLE></HEAD><BODY BGCOLOR="#000000">')
                self.Generate4()
                self.file.write('</BODY></HTML>')
            #self.file.write('<br>')
        finally:
            pass
        s = self.file.getvalue()
        #      f=open('c:/icor/'+avalue+'.xml','w')
        #      f.write(s)
        #      f.close()
        return s
#         self.file.close()

    def Generate4(self):
        self.file.write('<FONT FACE="VERDANA,ARIAL,HELVETICA" SIZE="2"><P ALIGN=RIGHT>\n')
        self.file.write('<A STYLE="color:#FFFFFF"><IMG SRC="art/d_prev.gif" BORDER=0 ALT="Poprzedni temat"></A>\n')
        self.file.write('<A STYLE="color:#FFFFFF"><IMG SRC="art/d_home.gif" BORDER=0 ALT="Strona główna"></A>\n')
        sde, sref, sc = 'd', '', ''
        if self.MenuOID >= 0:
            amenu = ICORWWWMenuItem(self.UID, self.MenuOID)
            if amenu.ParentMenu is not None:
                sde = 'u'
                sref = 'href="' + amenu.ParentMenu.GetMenuRef() + '"'
                sc = ' - ' + amenu.ParentMenu.Caption
        self.file.write('<A STYLE="color:#FFFFFF" %s ><IMG SRC="art/%s_local.gif" BORDER=0 ALT="Poziom wyżej%s"></A>\n' % (sref, sde, sc))

        self.file.write('<A STYLE="color:#FFFFFF" ><IMG SRC="art/d_index.gif" BORDER=0 ALT="Index"></A>\n')
        self.file.write('<A STYLE="color:#FFFFFF" ><IMG SRC="art/d_next.gif" BORDER=0 ALT="Następny temat"></A>\n')
        self.file.write('</P></FONT>\n')

    def Generate1(self):
        self.first = 1
        self.fontcolor = 'navy'
        self.srvclass.Introduction.ForEachRefObject(self.GenerateIntroItem, self.OID)

    def GetFontColor(self, amenu):
        acolor = amenu.FontColor
        if acolor != '':
            self.fontcolor = acolor
        return self.fontcolor

    def GenerateIntroItem(self, aclass, aoid):
        amenu = ICORWWWMenuItem(self.UID, aoid)
        if not amenu.IsVisibleByProfile(self.UID):
            return
#      if not self.first:
#         self.file.write('<BR>')
#      else:
#         self.first=0
        self.GetFontColor(amenu)
        if 0:
            self.file.write('<tr><td align="left" width="100%">\n')
            self.file.write('  <a href="%s"><font color="black" face="Arial"><b>&nbsp;%s</b></font></a>\n' % (amenu.GetMenuRef(), amenu.Caption))
            self.file.write('</td></tr>\n')
        else:
            self.file.write('<tr><td align="left" width="100%">\n')
            self.file.write('<font face="wingdings" color="red">v</font><a CLASS="BOLD" HREF="%s">' % amenu.GetMenuRef())
            self.file.write('<span style="color: %s"><font color="%s" face="Arial" onmouseover="this.style.color=\'blue\'" onmouseout="this.style.color=\'%s\'" size="-1">' % (self.fontcolor, self.fontcolor, self.fontcolor))
            self.file.write('<b>&nbsp;%s</b></font></span></a>\n' % amenu.Caption)
            self.file.write('</td></tr>\n')

    def Generate3(self):
        #      self.srvclass.NavigationItems.ForEachRefObject(self.GenerateNavigationItem,self.OID)
        self.file.write('<ul class="sf-menu sf-navbar">\n')
        self.srvclass.NavigationItems.ForEachRefObject(self.GenerateDropDownMenu, self.OID)
        self.file.write('</ul>\n')

    def GenerateDropDownMenu(self, aclass, aoid):
        arefs = aclass.Profile.GetRefList(aoid)
        if not arefs.IsEmpty():
            if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
                return
        arefs = aclass.AccessLevel.GetRefList(aoid)
        ret = CheckAccessLevelForUser(arefs, self.UID)
        if not ret:
            return
        if aclass.IsDisabled.ValuesAsInt(aoid) > 0:
            return
        aobj = aclass[aoid]
        mobj = aobj.MenuItem
        if mobj:
            self.file.write('<li><a href="#mymenu" target="_self">%s</a><ul>\n' % (aobj.Name, ))
            while mobj:
                amenu = ICORWWWMenuItem(self.UID, mobj.OID)
                if amenu.IsVisibleByProfile(self.UID):
                    if amenu.ParamValue3 != '':
                        ahref = amenu.ParamValue3
                    else:
                        ahref = amenu.GetMenuRef()
                    self.file.write('  <li><a href="%s">%s</a></li>\n' % (ahref, amenu.Caption))
                mobj.Next()
        self.file.write('</ul></li>\n')

    def GenerateDropDownMenu_Old(self, aclass, aoid):
        arefs = aclass.Profile.GetRefList(aoid)
        if not arefs.IsEmpty():
            if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
                return
        arefs = aclass.AccessLevel.GetRefList(aoid)
        ret = CheckAccessLevelForUser(arefs, self.UID)
        if not ret:
            return
        if aclass.IsDisabled.ValuesAsInt(aoid) > 0:
            return
        aobj = aclass[aoid]
        mobj = aobj.MenuItem
        if mobj:
            #f6f6f6
            #6699CC
            self.file.write('<mymenu:menu id="menu_p_%d" backcolor="#f6f6f6" onsubmenu_click="javascript:CallMenuFunction();">%s\n' % (aoid, aobj.Name))
            while mobj:
                amenu = ICORWWWMenuItem(self.UID, mobj.OID)
                if amenu.IsVisibleByProfile(self.UID):
                    if amenu.ParamValue3 != '':
                        ahref = amenu.ParamValue3
                    else:
                        ahref = amenu.GetMenuRef()
                    self.file.write('  <mymenu:menu id="menu_s_%d" menuhref="%s" backcolor="#f6f6f6">%s</mymenu:menu>\n' % (mobj.OID, ahref, amenu.Caption))
                mobj.Next()
            self.file.write('</mymenu:menu>\n')

    def GenerateNavigationItem(self, aclass, aoid):
        arefs = aclass.Profile.GetRefList(aoid)
        if not arefs.IsEmpty():
            if not arefs.RefsExists(aICORDBEngine.ProfileGroupRefs):
                return
        arefs = aclass.AccessLevel.GetRefList(aoid)
        ret = CheckAccessLevelForUser(arefs, self.UID)
        if not ret:
            return
        if aclass.IsDisabled.ValuesAsInt(aoid) > 0:
            return
        aobj = aclass[aoid]
        ahref = aobj.HRef
        if not ahref:
            mobj = aobj.MenuItem
            if mobj:
                amenu = ICORWWWMenuItem(self.UID, mobj.OID)
                ahref = amenu.GetMenuRef()
        if ahref != '':
            atarget = aobj.Target
            if atarget != '':
                atarget = ' TARGET ="%s"' % atarget
            self.file.write('&nbsp;&nbsp;|&nbsp;&nbsp;<a href="%s"%s>' % (ahref, atarget))
        if 1:
            self.file.write(aobj.Name)
        else:
            iobj = aobj.Image
            if iobj:
                aloc = iobj.Location
                aheight = iobj.Class.Height.ValuesAsInt(iobj.OID)
                if aheight > 0:
                    aheight = ' HEIGHT="%d"' % aheight
                else:
                    aheight = ''
                awidth = iobj.Class.Width.ValuesAsInt(iobj.OID)
                if awidth > 0:
                    awidth = ' WIDTH="%d"' % awidth
                else:
                    awidth = ''
                aalt = iobj.Alt
                self.file.write('<img SRC="%s"%s%s BORDER="0" ALT="%s">' % (aloc, aheight, awidth, aalt))
        if ahref != '':
            self.file.write('</a>')
        self.file.write('\n')

    def Generate2(self):
        self.first = 1
        self.fontcolor = 'FFFFFF'
        self.srvclass.Menu.ForEachRefObject(self.GenerateMenuItem, self.OID, 0)

    def Generate2B(self):
        self.first = 1
        self.fontcolor = 'FFFFFF'
        atree = SimpleLinksHTMLTree()
        self.srvclass.Menu.ForEachRefObject(self.GenerateMenuItemB, self.OID, atree.RootNode)
        self.file.write('<font FACE="Arial">\n')
        atree.Write(self.file)
        self.file.write('</font>\n')

    def GenerateMenuItem(self, aclass, aoid, alevel):
        amenu = ICORWWWMenuItem(self.UID, aoid)
        if not amenu.IsVisibleByProfile(self.UID):
            return
        if alevel == 0:
            if not self.first:
                self.file.write('<BR>')
            else:
                self.first = 0
        self.GetFontColor(amenu)
        if alevel == 0:
            self.file.write('<font SIZE="1" FACE="Arial,Verdana,Helvetica" COLOR="#%s">\n' % self.fontcolor)
            self.file.write('<table BORDER="0" CELLPADDING="0" CELLSPACING="0" WIDTH="195"><tr><td ALIGN="RIGHT"\n>')
            self.file.write('<a onmouseover="DoOver(\'#%s\')" onmouseout="DoOut()" CLASS="BOLD"' % self.fontcolor)
            self.file.write(' HREF="%s" onclick="ExpandCollapse();"' % amenu.GetMenuRef())
            self.file.write('>%s</a></td>\n' % amenu.Caption)
            self.file.write('<td width="9" align="right" VALIGN="BOTTOM"><img SRC="art/dnarr.gif" ALT="*" WIDTH="7" HEIGHT="4"></td>\n')
            self.file.write('</tr></table>\n\n')
        else:
            self.file.write('<li><a onmouseover="DoOver(\'#%s\')" onmouseout="DoOut()"' % self.fontcolor)
            self.file.write(' HREF="%s" onclick="ExpandCollapse();"' % amenu.GetMenuRef())
            self.file.write('>%s</a></li>\n' % amenu.Caption)
        if aclass.SubMenu[aoid] != '':
            self.file.write('<div class="Outline" style="DISPLAY: none"><ul>\n')
            afontcolor = self.fontcolor
            aclass.SubMenu.ForEachRefObject(self.GenerateMenuItem, aoid, 1)
            self.fontcolor = afontcolor
            self.file.write('</ul></div>\n')
        if alevel == 0:
            self.file.write('</font>')

    def GenerateMenuItemB(self, aclass, aoid, anode):
        amenu = ICORWWWMenuItem(self.UID, aoid)
        if not amenu.IsVisibleByProfile(self.UID):
            return
        bnode = anode.AddNode(amenu.Caption, amenu.GetMenuRef())
        if aclass.SubMenu[aoid] != '':
            aclass.SubMenu.ForEachRefObject(self.GenerateMenuItemB, aoid, bnode)

    def GenerateMenuFav(self):
        auser = ICORSecurityUser(self.UID)
        atext = auser.MenuFavorites
        self.file.write(atext)

    def SetMenuFav(self, aparam):
        auser = ICORSecurityUser(self.UID)
        auser.MenuFavorites = aparam

    def GenerateMenuXML(self, axmlfile=None):
        if axmlfile is None:
            self.xmlfile = XMLUtil.MXMLFile(self.file, aattrascdata=1)
            self.xmlfile.Header()
        else:
            self.xmlfile = axmlfile
        self.xmlfile.TagOpen('tree')
        if self.MenuOID < 0:
            if self.group == 'main':
                wmenu = []
                pclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
                pobj = pclass.GetFirstObject()
                while pobj:
                    if not pobj['SGIsDisabled']:
                        wobj = pobj.WWWMenuStruct
                        while wobj:
                            if not wobj['SGIsDisabled'] and CheckRecursiveAccessLevelForUser(wobj, 'AccessLevelView', self.UID):
                                wobj2 = wobj.AsObject()
                                ws = wobj2.Title
                                if not ws:
                                    ws = wobj2.Nazwa
                                if ws:
                                    wmenu.append([ws, wobj2.OID, wobj2])
                            wobj.Next()
                    pobj.Next()
                if wmenu:
                    wmenu.sort()
                    for acaption, woid, wobj in wmenu:
                        d = {'text': XMLUtil.GetAsXMLStringNoPL(acaption)}
                        if len(wmenu) > 1:
                            d['src'] = 'icormain.asp?jobtype=workflowmenustruct&OID=%d&coid=-1&XMLData=1' % (woid, )
                            d['rel'] = 'menustruct'
                            d['coid'] = str(woid)
                            self.xmlfile.TagOpen('tree', d, aclosetag=1)
                        else:
                            DoMenuWorkflowRecur.DoMenuWorkflowRecur(None, woid, -1, '', self.UID, self.xmlfile)

            lmenu = []
            arefs = self.srvclass.Menu.GetRefList(self.OID)
            self.cntWWWMenuClassRecur = 0
            while arefs:
                mname = arefs.Name[arefs.OID]
                mnum = 0
                if self.group == 'main' and mname in ['Konfiguracja projektu', 'System']:
                    arefs.Next()
                    continue
                if self.group == 'conf' and mname in ['System']:
                    arefs.Next()
                    continue
                if self.group == 'system' and mname in ['Konfiguracja projektu']:
                    arefs.Next()
                    continue
                if mname in ['Konfiguracja projektu', 'System', 'Dokumentacja']:
                    mnum = 99
                amenu = ICORWWWMenuItem(self.UID, arefs.OID)
                if (amenu.Action != 'Workflow Project') and amenu.IsVisibleByProfile(self.UID):    #$$ workflow project exclude!
                    lmenu.append([mnum, mname, amenu])
                    if amenu.Action == 'Workflow Project':
                        self.cntWWWMenuClassRecur = self.cntWWWMenuClassRecur + 1
                arefs.Next()
            lmenu.sort()
            for mnum, mname, amenu in lmenu:
                self.DoGenerateMenuItemXML(amenu)


#         self.srvclass.Menu.ForEachRefObject(self.GenerateMenuItemXML,self.OID)
        else:
            amenu = ICORWWWMenuItem(self.UID, self.MenuOID)
            if amenu.IsVisibleByProfile(self.UID):
                self.srvclass.Menu.ClassOfType.SubMenu.ForEachRefObject(self.GenerateMenuItemXML, self.MenuOID)
        self.xmlfile.TagClose('tree')
        self.xmlfile.close()

    def GenerateMenuItemXML(self, aclass, aoid):
        amenu = ICORWWWMenuItem(self.UID, aoid)
        #      if amenu.Caption=='BIP':
        #         __import__('CLASSES_Library_ICORBase_Debugger_ICORDebugger').set_trace()
        if not amenu.IsVisibleByProfile(self.UID):
            return
        self.DoGenerateMenuItemXML(amenu)

    def DoGenerateMenuItemXML(self, amenu):
        aclass = amenu.MenuClass
        aoid = amenu.oid
        if self.group == 'conf' and aclass.Name[aoid] in ['System']:
            return
        d = {'text': XMLUtil.GetAsXMLStringNoPL(amenu.Caption), 'action': amenu.GetMenuRef()}
        if aclass.SubMenu[aoid] != '':
            d['src'] = 'icormain.asp?jobtype=menuxml&OID=%d&XMLData=1' % aoid
        aobj = aclass[aoid]
        if aobj.Action.Name == 'MenuClassRecur':
            bclass = aICORDBEngine.Classes[aclass.ParamItem[aoid]]
            if bclass is not None:
                si1, si2 = '', ''
                arefs1 = bclass.WWWMenuImageClosedClass
                if arefs1:
                    si1 = arefs1.Location[arefs1.OID]
                arefs2 = bclass.WWWMenuImageClass
                if arefs2:
                    si2 = arefs2.Location[arefs2.OID]
                if not si2:
                    si2 = si1
                if si1:
                    d['icon'] = si1
                    d['openIcon'] = si2
                d['src'] = 'icormain.asp?jobtype=menuclassrecur&CID=%d&OID=%d&XMLData=1' % (bclass.CID, -1)
            self.xmlfile.TagOpen('tree', d, aclosetag=1)
        elif aobj.Action.Name == 'Workflow Project':
            arefs = aclass.WorkflowMenuStruct.GetRefList(aoid)
            while arefs:
                if amenu.WorkflowNoRecur or self.cntWWWMenuClassRecur > 1:
                    d['src'] = 'icormain.asp?jobtype=workflowmenustruct&OID=%d&coid=-1&XMLData=1' % (arefs.OID, )
                    d['rel'] = 'menustruct'
                    d['coid'] = str(arefs.OID)
                    self.xmlfile.TagOpen('tree', d, aclosetag=1)
                else:
                    DoMenuWorkflowRecur.DoMenuWorkflowRecur(None, arefs.OID, -1, '', self.UID, self.xmlfile)
                arefs.Next()
        else:
            self.xmlfile.TagOpen('tree', d, aclosetag=1)


def ProcessContents(avalue, auid, aoid, aparam, ajson=0, agroup=''):
    fname = FilePathAsSystemPath(aICORWWWServerInterface.OutputPath + '_' + avalue + '_' + str(aoid) + '_' + str(auid) + '.html')
    aserver = ICORWWWServer()
    return aserver.Generate(fname, avalue, auid, aoid, aparam, ajson=ajson, agroup=agroup)


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    #   Value='Contents'
    #   Value='Introduction'
    #   Value='NavigationBar'
    #   Value='NavigationButtons'
    if Value == '':
        print 'Error! - Value is Empty!'
        return
    return ProcessContents(Value, UID, OID, FieldName)
