# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil


class WWWMenuContext:

    def __init__(self, astruct):
        self.WWWMenuStruct = astruct
        self.Response = None
        if self.WWWMenuStruct.repldict.has_key('Response'):
            self.Response = self.WWWMenuStruct.repldict['Response']
        self.ChapterGroup = ''
        self.Mode = 'chapter'    # chapter, full, submenu, navigator, chapterpeer
        self.ProcessLevels = 1
        self.ProcessLevelsMulti = 0
        self.ChapterCnt = 0
        self.ChapterLevel = 0
        self.marked_chapters = {}
        self.SubChaptersCheck = 0
        self.IsIgnoreChapterGroupsIterate = 0
        self.IsFullChaptersIterate = 0
        self.ChaptersOIDPath = []
        self.text = []
        self.IgnoreResponse = 0

    def Init(self, achapter=None):
        pass

    def CheckChapterVisibility(self, achapter):
        if achapter.ChapterParams.get('aHideSubChapters', ''):
            return 1
        if achapter.GetRecursiveParameter('aHideSubChapters', ''):
            return 0
        return 1

    def OnGetMenuClass(self):
        return ''

    def OnGetLevelClass(self, achapter):
        return ''

    def OnGetCurrentLevelClass(self, achapter):
        return ''

    def OnGetChapterClass(self, achapter):
        return ''

    def OnGetCurrentChapterClass(self, achapter):
        return ''

    def OnGetLinkClass(self, achapter):
        return ''

    def OnGetCurrentLinkClass(self, achapter):
        return ''

    def OnGetCaption(self, achapter):
        return achapter.CaptionMenu

    def OnGetTitle(self, achapter):
        return achapter.Caption

    def OnGetMenuTag(self):
        return 'ul'

    def OnGetLevelTag(self, achapter):
        return 'ul'

    def OnGetChapterTag(self, achapter):
        return 'li'

    def OnGetLinkTag(self, achapter):
        return 'a'

    def OnGetLinkHRef(self, achapter):
        return achapter.GetHRef()

    def OnGetMenuID(self):
        return ''

    def OnGetLevelID(self, achapter):
        return ''

    def OnGetChapterID(self, achapter):
        return ''

    def OnGetLinkID(self, achapter):
        return ''

    def OnMenuBeforePre(self):
        return ''

    def OnMenuBeforePost(self):
        return ''

    def OnMenuBefore(self):
        atag = self.OnGetMenuTag()
        if atag:
            aclass = self.OnGetMenuClass()
            if aclass:
                aclass = ' class="%s"' % (aclass, )
            aid = self.OnGetMenuID()
            if aid:
                aid = ' id="%s"' % (aid, )
            apre = self.OnMenuBeforePre()
            apost = self.OnMenuBeforePost()
            sh = '%s%s<%s%s%s>%s\n' % (' ' * self.ChapterLevel, apre, atag, aid, aclass, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuAfterPre(self):
        return ''

    def OnMenuAfterPost(self):
        return ''

    def OnMenuAfter(self):
        atag = self.OnGetMenuTag()
        if atag:
            apre = self.OnMenuAfterPre()
            apost = self.OnMenuAfterPost()
            sh = '%s%s</%s>%s\n' % (' ' * self.ChapterLevel, apre, atag, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuLevelBeforePre(self, achapter):
        return ''

    def OnMenuLevelBeforePost(self, achapter):
        return ''

    def OnMenuLevelBefore(self, achapter):
        atag = self.OnGetLevelTag(achapter)
        if atag:
            aclass = self.OnGetLevelClass(achapter)
            if achapter.OID in self.ChaptersOIDPath:
                bclass = self.OnGetCurrentLevelClass(achapter)
                if aclass and bclass:
                    aclass = aclass + ' '
                aclass = aclass + bclass
            if aclass:
                aclass = ' class="%s"' % (aclass, )
            aid = self.OnGetLevelID(achapter)
            if aid:
                aid = ' id="%s"' % (aid, )
            apre = self.OnMenuLevelBeforePre(achapter)
            apost = self.OnMenuLevelBeforePost(achapter)
            sh = '%s%s<%s%s%s>%s\n' % (' ' * self.ChapterLevel, apre, atag, aid, aclass, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuLevelAfterPre(self, achapter):
        return ''

    def OnMenuLevelAfterPost(self, achapter):
        return ''

    def OnMenuLevelAfter(self, achapter):
        atag = self.OnGetLevelTag(achapter)
        if atag:
            apre = self.OnMenuLevelAfterPre(achapter)
            apost = self.OnMenuLevelAfterPost(achapter)
            sh = '%s%s</%s>%s\n' % (' ' * self.ChapterLevel, apre, atag, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuChapterBeforePre(self, achapter):
        return ''

    def OnMenuChapterBeforePost(self, achapter):
        return ''

    def OnMenuChapterBefore(self, achapter):
        atag = self.OnGetChapterTag(achapter)
        if atag:
            achapterclass = self.OnGetChapterClass(achapter)
            if achapter.OID in self.ChaptersOIDPath:
                bclass = self.OnGetCurrentChapterClass(achapter)
                if achapterclass and bclass:
                    achapterclass = achapterclass + ' '
                achapterclass = achapterclass + bclass
            if achapterclass:
                achapterclass = ' class="%s"' % (achapterclass, )
            aid = self.OnGetChapterID(achapter)
            if aid:
                aid = ' id="%s"' % (aid, )
            apre = self.OnMenuChapterBeforePre(achapter)
            apost = self.OnMenuChapterBeforePost(achapter)
            sh = """%s%s<%s%s%s>%s""" % (' ' * self.ChapterLevel, apre, atag, aid, achapterclass, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuChapterAfterPre(self, achapter):
        return ''

    def OnMenuChapterAfterPost(self, achapter):
        return ''

    def OnMenuChapterAfter(self, achapter):
        atag = self.OnGetChapterTag(achapter)
        if atag:
            apre = self.OnMenuChapterAfterPre(achapter)
            apost = self.OnMenuChapterAfterPost(achapter)
            sh = '%s%s</%s>%s\n' % (' ' * self.ChapterLevel, apre, atag, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnMenuChapterPre(self, achapter):
        return ''

    def OnMenuChapterPost(self, achapter):
        return ''

    def OnMenuChapter(self, achapter):
        if not self.CheckChapterVisibility(achapter):
            return
        atag = self.OnGetLinkTag(achapter)
        if atag:
            ahref = self.OnGetLinkHRef(achapter)
            atarget = achapter.Target
            if atarget:
                atarget = 'target="%s" ' % atarget
            alinkclass = self.OnGetLinkClass(achapter)
            if achapter.OID in self.ChaptersOIDPath:
                bclass = self.OnGetCurrentLinkClass(achapter)
                if alinkclass and bclass:
                    alinkclass = alinkclass + ' '
                alinkclass = alinkclass + bclass
            if alinkclass:
                alinkclass = ' class="%s"' % (alinkclass, )
            aid = self.OnGetLinkID(achapter)
            if aid:
                aid = ' id="%s"' % (aid, )
            acaption = self.OnGetCaption(achapter)
            if not acaption:
                acaption = '***'
            atitle = self.OnGetTitle(achapter)
            if atitle:
                if acaption.lower() == atitle.lower():
                    atitle = ''
                else:
                    atitle = ' title="%s"' % (XMLUtil.GetAsXMLStringNoPL(atitle), )
            apre = self.OnMenuChapterPre(achapter)
            apost = self.OnMenuChapterPost(achapter)
            sh = """%s<%s %shref="%s"%s%s%s>%s</%s>%s\n""" % (apre, atag, atarget, ahref, aid, alinkclass, atitle, acaption, atag, apost)
            self.text.append(sh)
            if not self.IgnoreResponse:
                self.Response.write(sh)

    def OnGetNavigatorTextBefore(self, lchapters):
        return ':.&nbsp;'

    def OnGetNavigatorTextAfter(self):
        return '\n'

    def OnGetNavigatorLinkClass(self, achapter):
        return ''

    def OnGetNavigatorLinkHRef(self, achapter):
        return achapter.GetHRef()

    def OnGetNavigatorCaption(self, achapter):
        acaption = achapter.CaptionMenu
        if len(acaption) > 30:
            acaption = acaption[:30] + '..'
        return acaption

    def OnGetNavigatorTitle(self, achapter):
        return achapter.Caption

    def OnGetNavigatorSeparator(self, achapter):
        return '<b> &raquo; </b>'

    def OnGetNavigatorTagBefore(self, achapter):
        return ''

    def OnGetNavigatorTagAfter(self, achapter):
        return ''

    def OnMenuNavigator(self, lchapters):
        atext = self.OnGetNavigatorTextBefore(lchapters)
        if atext:
            self.text.append(atext)
            if not self.IgnoreResponse:
                self.Response.write(atext)
        w = 0
        alen = len(lchapters)
        for i in range(alen):
            self.ChapterPositionCnt = i
            self.ChapterPositionRel = []
            if not i:
                self.ChapterPositionRel.append('first')
            if i == alen - 1:
                self.ChapterPositionRel.append('last')
            if i and i < (alen - 1):
                self.ChapterPositionRel.append('middle')
            achapter = lchapters[i]
            ahref = self.OnGetNavigatorLinkHRef(achapter)
            atarget = achapter.Target
            if atarget:
                atarget = 'target="%s" ' % atarget
            alinkclass = self.OnGetNavigatorLinkClass(achapter)
            if alinkclass:
                alinkclass = ' class="%s"' % (alinkclass, )
            acaption = self.OnGetNavigatorCaption(achapter)
            if not acaption:
                acaption = '***'
            atitle = self.OnGetNavigatorTitle(achapter)
            if atitle:
                if acaption.lower() == atitle.lower():
                    atitle = ''
                else:
                    atitle = ' title="%s"' % (XMLUtil.GetAsXMLStringNoPL(atitle), )
            aseparator = ''
            if w:
                aseparator = self.OnGetNavigatorSeparator(achapter)
            atag = self.OnGetLinkTag(achapter)
            if atag:
                stagbefore = self.OnGetNavigatorTagBefore(achapter)
                stagafter = self.OnGetNavigatorTagAfter(achapter)
                sh = """%s%s<%s %shref="%s"%s%s>%s</%s>%s""" % (aseparator, stagbefore, atag, atarget, ahref, alinkclass, atitle, acaption, atag, stagafter)
                self.text.append(sh)
                if not self.IgnoreResponse:
                    self.Response.write(sh)
            w = 1
        atext = self.OnGetNavigatorTextAfter()
        if atext:
            self.text.append(atext)
            if not self.IgnoreResponse:
                self.Response.write(atext)

    def Iterate(self, aoid=None):
        if aoid is None:
            aoid = self.WWWMenuStruct.ThisChapter.OID
        self.ChapterOID = aoid
        achapter = self.WWWMenuStruct.chapters_byid[aoid]
        self.ChaptersOIDPath = [aoid, ]
        bchapter = achapter.Parent
        while bchapter is not None:
            self.ChaptersOIDPath.append(bchapter.OID)
            bchapter = bchapter.Parent
        self.ChaptersOIDPath.reverse()
        self.Init(achapter)
        if self.Mode == 'chapter':
            self.IterateChapter(achapter)
        elif self.Mode == 'chapterpeer':
            self.IterateChapterPeer(achapter)
        elif self.Mode == 'chapterpeerparents':
            self.IterateChapterPeer(achapter, aparents=1)
        elif self.Mode == 'chapterpeerparentsroot':
            self.IterateChapterPeer(achapter, aparents=1, aparentsroot=1)
        elif self.Mode == 'navigator':
            self.IterateNavigator(achapter)
        elif self.Mode == 'submenu':
            self.IterateSubMenu(achapter)
        elif self.Mode == 'full':
            self.IterateFull()

    def MarkChapterList(self, alist):
        for achapter in alist:
            if not achapter.IsMenuDisabled and (achapter.Grupa == self.ChapterGroup or self.IsIgnoreChapterGroupsIterate):
                self.marked_chapters[achapter.OID] = 1

    def IterateChapter(self, achapter):
        self.marked_chapters = {}
        self.MarkChapterList(achapter.SubChapters)
        if self.ChapterGroup and not self.IsIgnoreChapterGroupsIterate:
            if self.WWWMenuStruct.chaptersgroups.has_key(self.ChapterGroup):
                lchapters = self.WWWMenuStruct.chaptersgroups[self.ChapterGroup]
            else:
                lchapters = []
                print '*** Nieznana GRUPA ROZDZIALOW: %s ***' % self.ChapterGroup
        else:
            lchapters = self.WWWMenuStruct.chapters
        while achapter is not None:
            if achapter.Parent is not None:
                self.MarkChapterList(achapter.Parent.SubChapters)
            else:
                self.MarkChapterList(lchapters)
                if self.ProcessLevelsMulti:
                    for bchapter in lchapters:
                        self.MarkChapterList(bchapter.SubChapters)
            achapter = achapter.Parent
        self.ChapterCnt = 0
        self.ChapterLevel = 0
        if self.ProcessLevels:
            self.OnMenuBefore()
        self.IterateChapterList(lchapters, acheck=1)
        if self.ProcessLevels:
            self.OnMenuAfter()

    def IterateChapterPeer(self, achapter, aparents=0, aparentsroot=0):
        self.marked_chapters = {}
        self.MarkChapterList(achapter.SubChapters)
        lchapters = achapter.SubChapters
        if not aparents:
            if achapter.Parent is not None:
                self.MarkChapterList(achapter.Parent.SubChapters)
                lchapters = achapter.Parent.SubChapters
        else:
            bchapter = achapter.Parent
            bbchapter = achapter
            while bchapter is not None:
                self.MarkChapterList(bchapter.SubChapters)
                lchapters = bchapter.SubChapters
                bbchapter = bchapter
                bchapter = bchapter.Parent
            if aparentsroot:
                if bbchapter.Grupa:
                    if self.WWWMenuStruct.chaptersgroups.has_key(bbchapter.Grupa):
                        lchapters = self.WWWMenuStruct.chaptersgroups[bbchapter.Grupa]
                    else:
                        lchapters = []
                        print '*** Nieznana GRUPA ROZDZIALOW: %s ***' % bbchapter.Grupa
                else:
                    lchapters = self.WWWMenuStruct.chapters
                self.MarkChapterList(lchapters)

        self.ChapterCnt = 0
        self.ChapterLevel = 0
        if self.ProcessLevels:
            self.OnMenuBefore()
        self.IterateChapterList(lchapters, acheck=1)
        if self.ProcessLevels:
            self.OnMenuAfter()

    def IterateNavigator(self, achapter):
        lchapters = [achapter, ]
        bchapter = achapter.Parent
        while bchapter is not None:
            lchapters.insert(0, bchapter)
            bchapter = bchapter.Parent
        self.OnMenuNavigator(lchapters)

    def IterateFull(self):
        self.marked_chapters = {}
        self.ChapterCnt = 0
        self.ChapterLevel = 0
        if self.ProcessLevels:
            self.OnMenuBefore()
        if self.ChapterGroup and not self.IsIgnoreChapterGroupsIterate:
            if self.WWWMenuStruct.chaptersgroups.has_key(self.ChapterGroup):
                lchapters = self.WWWMenuStruct.chaptersgroups[self.ChapterGroup]
            else:
                lchapters = []
                print '*** Nieznana GRUPA ROZDZIALOW: %s ***' % self.ChapterGroup
        else:
            lchapters = self.WWWMenuStruct.chapters
        self.IterateChapterList(lchapters, acheck=0)
        if self.ProcessLevels:
            self.OnMenuAfter()

    def IterateSubMenu(self, achapter):
        #      if not achapter.RodzajZaglebienia in [1,2]:
        #         return
        self.marked_chapters = {}
        self.ChapterCnt = 0
        self.ChapterLevel = 0
        if self.ProcessLevels:
            self.SubChaptersCheck = 1
            self.OnMenuBefore()
        self.IterateChapterList(achapter.SubChapters, acheck=0)    #acheck=1
        if self.ProcessLevels:
            self.OnMenuAfter()
            self.SubChaptersCheck = 0

    def IterateChapterList(self, lchapters, acheck=0):
        alen = len(lchapters)
        for i in range(alen):
            self.ChapterPositionCnt = i
            self.ChapterPositionRel = []
            if not i:
                self.ChapterPositionRel.append('first')
            if i == alen - 1:
                self.ChapterPositionRel.append('last')
            if i and i < (alen - 1):
                self.ChapterPositionRel.append('middle')
            achapter = lchapters[i]
            self.IterateChapterMenuCall(achapter, acheck=acheck)

    def IterateChapterMenuCall(self, achapter, acheck=0):
        w = 1 - acheck
        if self.marked_chapters.has_key(achapter.OID):
            w = 1
        w1, w2 = 0, 0
        if not achapter.IsMenuDisabled and (achapter.Grupa == self.ChapterGroup or self.IsIgnoreChapterGroupsIterate):
            w1 = 1 - acheck
            if self.ProcessLevels:
                if not w1:
                    for bchapter in achapter.SubChapters:
                        if self.marked_chapters.has_key(bchapter.OID):
                            w1 = 1
                            break
                elif not achapter.SubChapters:
                    w1 = 0
            w2 = 1
            if not self.IsFullChaptersIterate:
                if achapter.RodzajZaglebienia in [1, 2]:
                    w2 = 0
                if self.SubChaptersCheck:
                    w2 = 1
                    if achapter.RodzajZaglebienia == 2 and self.ChapterLevel > 0:
                        w2 = 0

            self.ChapterLevel = self.ChapterLevel + 1
            if w:
                self.WWWMenuStruct.ProcessEventsInternal('OnCMSChapterMenuBefore', dd={'thisWWWMenuContext': self, 'MenuChapterOID': achapter.OID, 'thisChapter': achapter}, aeventschapter=achapter)
                self.OnMenuChapterBefore(achapter)
                self.OnMenuChapter(achapter)
                self.ChapterCnt = self.ChapterCnt + 1
            if w1 and w2 and achapter.SubChapters:
                if self.ProcessLevels:
                    self.OnMenuLevelBefore(achapter)
                self.IterateChapterList(achapter.SubChapters, acheck=acheck)
                if self.ProcessLevels:
                    self.OnMenuLevelAfter(achapter)
            if w:
                self.OnMenuChapterAfter(achapter)
                self.WWWMenuStruct.ProcessEventsInternal('OnCMSChapterMenuAfter', dd={'thisWWWMenuContext': self, 'MenuChapterOID': achapter.OID, 'thisChapter': achapter}, aeventschapter=achapter)
            self.ChapterLevel = self.ChapterLevel - 1
