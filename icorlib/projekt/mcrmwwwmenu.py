# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import os
import sys
import string
import cStringIO

ICOR_TYPES=[
   "Adres",
   "Auto PIN",
   "Auto increment",
   "CPV",
   "Ciąg znaków - 1 długa linia",
   "Ciąg znaków - 1 linia - duże litery",
   "Ciąg znaków - 1 linia",
   "Ciąg znaków - identyfikator",
   "Data - dzisiejsza lub przyszła",
   "Data i czas - dzisiejsza lub przyszła",
   "Data i czas kwadrans",
   "Data i czas",
   "Data",
   "EMail",
   "GUID",
   "HTML",
   "Kod pocztowy",
   "Kod, Identyfikator",
   "Kolor",
   "Liczba całkowita",
   "Liczba zmiennoprzecinkowa",
   "Liczba",
   "NIP",
   "Nr rachunku bankowego",
   "OID",
   "Obrazek",
   "Opis",
   "Pesel",
   "Pieniądze (0.01 - 999 999 999)",
   "Pieniądze - EUR - (0.01 - 999 999 999)",
   "Pieniądze",
   "REGON",
   "Słownik użytkownika - liczba całkowita",
   "Słownik użytkownika",
   "Tak/Nie",
   "Telefon",
   "URL",
   "Współrzędne geograficzne",
] # yapf: disable

class ICORBIPField:

    def __init__(self, atable, atabid, attrs, acomment=''):
        self.Table = atable
        self.TabID = atabid
        self.OID = int(attrs.get('oid', '-1'))
        self.Name = attrs.get('name', '')
        self.Type = attrs.get('type', '')
        self.IsSearch = int(attrs.get('issearch', '1'))
        self.IsAliased = int(attrs.get('isaliased', '1'))
        self.IsObligatory = int(attrs.get('isobligatory', '0'))
        self.IsDictViewHidden = int(attrs.get('isdictviewhidden', '0'))
        self.IsDictViewHidden = int(attrs.get('isdictviewhidden', '0'))
        self.IsSingleViewHidden = int(attrs.get('issingleviewhidden', '0'))
        self.NameVisible = attrs.get('namevisible', '')
        self.DefaultValue = attrs.get('defaultvalue', '')
        if self.Type == 'Obrazek':
            self.IsSearch = 0
        elif self.Type in ['HTML', ]:
            self.IsAliased = 0
        self.Dictionary = attrs.get('dictionary', '')
        self.IsTableView = int(attrs.get('istableview', '1'))
        self.XMLComment = acomment
        self.FieldValues = []
        self.FieldDictValues = []
        self.IsNew = 0
        if self.OID < 0:
            self.IsNew = 1
            self.Table.IsModified = 1
        self.IsModified = 0

    def CheckModified(self, fout, fclass, lclass):
        if self.IsNew:
            return
        if self.OID >= 0:
            if not fclass.ObjectExists(self.OID):
                self.OID = -1
                self.IsNew = 1
                self.Table.IsModified = 1
                return
            else:
                fobj = fclass[self.OID]
                if fobj.Dotyczy.OID != self.Table.OID:
                    self.OID = -1
                    self.IsNew = 1
                    self.Table.IsModified = 1
                    return
        if self.Type == 'Słownik zewnętrzny - wiele wartości':
            lobj = lclass[self.OID]
            if lobj.DestinationTable.Nazwa != self.Dictionary:
                self.IsModified = 1
        else:
            fobj = fclass[self.OID]
            if fobj.Nazwa != self.Name:
                self.IsModified = 1
            if fobj.TypPolaDotyczy.Opis != self.Type:
                if fout:
                    fout.write('*** Niekompatybilny typ pola "%s" dla pola "%s" ***\n' % (self.Type, self.Name))
            if fobj.SGTabIndex != str(self.TabID):
                self.IsModified = 1

    def Store(self, tobj, fout, fsql, llinkfields, lextdictfields):
        if not self.IsNew and not self.IsModified:
            return self.OID
        aclass = tobj.Class.Pola.ClassOfType
        if self.Type == 'Słownik zewnętrzny - wiele wartości':
            llinkfields.append(self)
        else:
            if self.IsNew:
                aoid = aclass.AddObject(arefobject=tobj)
                self.OID = aoid
            else:
                aoid = self.OID
            aclass.Nazwa[aoid] = self.Name
            aclass.NazwaWidoczna[aoid] = self.NameVisible
            aclass.SGIsAliased[aoid] = self.IsAliased
            aclass.SGIsObligatory[aoid] = self.IsObligatory

            if self.IsNew:
                if not self.Type in ['Opis', 'HTML']:
                    aclass.SGIsIndexed[aoid] = 1
                aclass.SGIsInteractive[aoid] = 1
            aclass.SGIsSearch[aoid] = self.IsSearch
            aclass.SGIsDictViewHidden[aoid] = self.IsDictViewHidden
            aclass.SGIsSingleViewHidden[aoid] = self.IsSingleViewHidden
            aclass.SGTabIndex[aoid] = self.TabID
            aclass.Komentarz[aoid] = self.XMLComment
            tclass = aclass.TypPolaDotyczy.ClassOfType
            toid = tclass.Opis.Identifiers(self.Type)
            if toid >= 0:
                aclass.TypPolaDotyczy[aoid] = [toid, tclass.CID]
            else:
                if fout:
                    fout.write('Nieznany typ pola "%s" dla pola "%s"\n' % (self.Type, self.Name))
            if self.Type == 'OID':
                aclass.SGIsDictViewHidden[aoid] = 0
                aclass.SGIsSingleViewHidden[aoid] = 1
            elif self.Type == 'Słownik zewnętrzny':
                aclass.SGIsObligatory[aoid] = 1
                lextdictfields.append(self)
            if self.FieldValues:
                aclass.WartosciPola[aoid] = string.join(self.FieldValues, '\n')
            if self.FieldDictValues:
                ls = []
                for bid, bvalue in self.FieldDictValues:
                    ls.append('"%s","%s"' % (bid, bvalue))
                aclass.WartosciSlownika[aoid] = string.join(ls, '\n')
            aclass.DomyslnaWartosc[aoid] = self.DefaultValue
        return self.OID

    def StoreLink(self, aobj, atables, aexttables):
        tclass = aobj.Class.TabeleZrodlowe.ClassOfType
        lclass = tclass.PolaczeniaDoTabel.ClassOfType
        if self.IsNew:
            loid = lclass.AddObject(arefobject=aobj)
            self.OID = loid
        else:
            loid = self.OID
        boid = -1
        if atables.has_key(self.Dictionary):
            btable = atables[self.Dictionary]
            boid = btable.OID
        elif aexttables.has_key(self.Dictionary):
            boid = aexttables[self.Dictionary]
        lclass.LinkName[loid] = self.Name
        if boid >= 0:
            lclass.DestinationTable[loid] = [boid, tclass.CID]
        lclass.SourceField[loid] = '_OID'
        lclass.LinkTabID[loid] = '10'
        lclass.LinkTabOrder[loid] = self.TabID
        lclass.DestinationField[loid] = '_OIDDictRef'
        lclass.IsTableView[loid] = self.IsTableView
        tclass.PolaczeniaDoTabel.AddRefs(self.Table.OID, [loid, lclass.CID], ainsertifnotexists=1)

    def StoreExtDict(self, aobj, atables, aexttables):
        tclass = aobj.Class.TabeleZrodlowe.ClassOfType
        pclass = tclass.Pola.ClassOfType
        boid = -1
        if atables.has_key(self.Dictionary):
            btable = atables[self.Dictionary]
            boid = btable.OID
        elif aexttables.has_key(self.Dictionary):
            boid = aexttables[self.Dictionary]
        if boid >= 0:
            pclass.ZrodloDanychSlownika[self.OID] = [boid, tclass.CID]


class ICORBIPTable:

    def __init__(self, atables, attrs, acomment=''):
        self.Tables = atables
        self.OID = int(attrs.get('oid', '-1'))
        self.Name = attrs['name']
        self.Group = attrs.get('group', '')
        self.NameTable = attrs.get('nametable', '')
        self.NameObject = attrs.get('nameobject', '')
        self.TabID = 10
        self.Fields = {}
        self.FieldsList = []
        self.XMLComment = acomment
        self.IsNew = self.OID < 0
        self.IsModified = 0

    def Store(self, aclass, fout, fsql, llinkfields, lextdictfields):
        if not self.IsNew and not self.IsModified:
            return self.OID
        if self.IsNew:
            self.OID = aclass.AddObject()
            if fout:
                fout.write('Nowa tabela: [%d] %s\n' % (self.OID, self.Name))
        aobj = aclass[self.OID]
        aclass.Nazwa[self.OID] = self.Name
        aclass.Grupa[self.OID] = self.Group
        aclass.NazwaTabeli[self.OID] = self.NameTable
        aclass.NazwaObiektu[self.OID] = self.NameObject

        #      aclass.Grupa[self.OID]='WWW Menu Struct'
        aclass.Komentarz[self.OID] = self.XMLComment
        aclass.IsVersionControl[self.OID] = 1
        if not self.Fields.has_key('Informacja podmiot udostępniający'):
            d={
            'name':'Informacja podmiot udostępniający',
            'type':'Ciąg znaków - 1 linia',
            'issearch':'1',
            'isaliased':'1',
            'isdictviewhidden':'1',
            } # yapf: disable
            self.AddField(d)
        if not self.Fields.has_key('Informacja osoba odpowiedzialna'):
            d={
            'name':'Informacja osoba odpowiedzialna',
            'type':'Ciąg znaków - 1 linia',
            'issearch':'1',
            'isaliased':'1',
            'isdictviewhidden':'1',
            } # yapf: disable
            self.AddField(d)
        if not self.Fields.has_key('Informacja data wytworzenia'):
            d={
            'name':'Informacja data wytworzenia',
            'type':'Data',
            'issearch':'1',
            'isaliased':'1',
            'isdictviewhidden':'1',
            } # yapf: disable
            self.AddField(d)
        if not self.Fields.has_key('Informacja opis czynności'):
            d={
            'name':'Informacja opis czynności',
            'type':'Ciąg znaków - 1 linia',
            'issearch':'1',
            'isaliased':'1',
            'isdictviewhidden':'1',
            } # yapf: disable
            self.AddField(d)
        if self.IsNew:
            d={
            'name':'_OIDDictRef',
            'type':'OID',
            'issearch':'0',
            'isaliased':'0',
            } # yapf: disable
            self.AddField(d)
        if self.IsNew:
            d={
            'name':'_ChapterID',
            'type':'Liczba całkowita',
            'issearch':'0',
            'isaliased':'0',
            'isdictviewhidden':'1',
            } # yapf: disable
            self.AddField(d)
        arefs = []
        fclass = aclass.Pola.ClassOfType
        for afield in self.FieldsList:
            afield.CheckModified(fout, aclass.Pola.ClassOfType, aclass.PolaczeniaDoTabel.ClassOfType)
            if afield.IsNew:
                boid = afield.Store(aobj, fout, fsql, llinkfields, lextdictfields)
                if boid >= 0:
                    arefs.extend([boid, fclass.CID])
            elif afield.IsModified:
                afield.Store(aobj, fout, fsql, llinkfields, lextdictfields)
                if fout:
                    fout.write('*** zmodyfikowane pole [%d] "%s" w tabeli [%d] "%s" ***\n' % (afield.OID, afield.Name, self.OID, self.Name, ))
            else:
                if fout:
                    fout.write('stare pole [%d] "%s" w tabeli [%d] "%s"\n' % (afield.OID, afield.Name, self.OID, self.Name, ))


#sprawdzic kolejnosc pol przed zapamietaniem
        aclass.Pola.AddRefs(self.OID, arefs, dosort=1, asortedreffield=aclass.Pola.ClassOfType.SGTabIndex, ainsertifnotexists=1)
        return self.OID

    def AddField(self, attrs, acomment=''):
        afield = ICORBIPField(self, self.TabID, attrs, acomment=acomment)
        self.Fields[afield.Name] = afield
        self.FieldsList.append(afield)
        self.TabID = self.TabID + 10
        return afield

    def Check(self, astatus, aclass=None):
        if aclass is not None and self.OID >= 0:
            if not aclass.ObjectExists(self.OID):
                self.IsNew = 1
                self.OID = -1
        for afield in self.Fields.values():
            if afield.Type in ['Słownik zewnętrzny', 'Słownik zewnętrzny - wiele wartości', ]:
                if not self.Tables.has_key(afield.Dictionary):
                    astatus.append('tabela "%s", pole "%s" odnosi sie do nieistniejacego slownika: "%s"' % (self.Name, afield.Name, afield.Dictionary))


class ICORBIPChapter:

    def __init__(self, aparent, attrs, acomment='', group=''):
        self.Parent = aparent
        self.OID = int(attrs.get('oid', '-1'))
        self.StoreDisabled = int(attrs.get('storedisabled', '0'))
        self.TableID = int(attrs.get('tableid', '-1'))
        self.Title = attrs.get('title', '')
        self.TitleMenu = attrs.get('titlemenu', '')
        self.TableName = attrs.get('table', '')
        self.IsTableView = int(attrs.get('istableview', '0'))
        self.IsSearch = int(attrs.get('issearch', '0'))
        self.IsMenuDisabled = int(attrs.get('ismenudisabled', '0'))
        self.ShowAsTable = int(attrs.get('showastable', '0'))
        self.HRef = attrs.get('href', '')
        self.HRefApp = attrs.get('hrefapp', '')
        self.HRefParams = attrs.get('hrefparams', '')
        self.Target = attrs.get('target', '')
        self.Comment = attrs.get('comment', '')
        self.IsAutoGenerate = int(attrs.get('isautogenerate', '0'))
        self.IsGenerateDisabled = int(attrs.get('isgeneratedisabled', '0'))
        self.XMLComment = acomment
        self.Group = group
        self.SubChapters = []
        if self.Parent is not None:
            self.Parent.SubChapters.append(self)

    def Store(self, aclass=None, atabid=-1, atables=None, aexttables=None):
        if aclass is None:
            aclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial']
        if self.OID < 0:
            self.OID = aclass.AddObject()
        aoid = self.OID
        if not self.StoreDisabled:
            aclass.Naglowek[aoid] = self.Title
            aclass.NaglowekMenu[aoid] = self.TitleMenu
            aclass.NazwaTabeli[aoid] = self.TableName
            aclass.Komentarz[aoid] = self.Comment
            aclass.XMLComment[aoid] = self.XMLComment
            aclass.SGIsTableView[aoid] = self.IsTableView
            aclass.SGShowAsTable[aoid] = self.ShowAsTable
            aclass.SGIsSearch[aoid] = self.IsSearch
            aclass.SGIsMenuDisabled[aoid] = self.IsMenuDisabled
            aclass.IsAutoGenerate[aoid] = self.IsAutoGenerate
            aclass.IsGenerateDisabled[aoid] = self.IsGenerateDisabled
            aclass.SGHref[aoid] = self.HRef
            aclass.SGHrefApp[aoid] = self.HRefApp
            aclass.SGHrefParams[aoid] = self.HRefParams
            aclass.SGTarget[aoid] = self.Target
            aclass.SGTabID[aoid] = atabid
            if self.TableName:
                boid = -1
                if atables.has_key(self.TableName):
                    btable = atables[self.TableName]
                    boid = btable.OID
                elif aexttables.has_key(self.TableName):
                    boid = aexttables[self.TableName]
                if boid >= 0:
                    aclass.TabelaZrodlowa[aoid] = [boid, aclass.TabelaZrodlowa.ClassOfType.CID]
            #if self.Parent is None:
            #   aclass.GrupaRozdzialow[aoid]=self.Group
        if self.TableID >= 0:
            aclass.TabelaZrodlowa[aoid] = [self.TableID, aclass.TabelaZrodlowa.ClassOfType.CID]
        arefs = []
        btabid = 10
        for achapter in self.SubChapters:
            boid = achapter.Store(aclass, btabid, atables, aexttables)
            arefs.extend([boid, aclass.CID])
            btabid = btabid + 10
        aclass.PodRozdzialy.AddRefs(aoid, arefs, ainsertifnotexists=1, asortedreffield=aclass.SGTabID, dosort=1)
        robj = aclass[aoid]
        btabid = 10
        r2obj = robj.PodRozdzialy
        while r2obj:
            r2obj.SGTabID = btabid
            btabid = btabid + 10
            r2obj.Next()
        return aoid


class ICORBIPStructXMLParser(XMLUtil.ICORBaseXMLParser):

    def Parse(self, atext, atabele, aexttables):
        self.Tables = atabele
        self.ExtTables = aexttables
        self.ThisChapter = None
        self.Chapters = []
        self.IsGood = 1
        self.Group = ''
        XMLUtil.ICORBaseXMLParser.Parse(self, atext)

    def Store(self, aobj, fout, fsql):
        #      aobj.Class.Rozdzialy.DeleteReferencedObjects(aobj.OID)
        robj = aobj.Rozdzialy
        atabid = 0
        while robj:
            btabid = robj['SGTabID', mt_Integer]
            if btabid > atabid:
                atabid = btabid
            robj.Next()
        atabid = atabid + 10
        drefs = {}
        for achapter in self.Chapters:
            aoid = achapter.Store(aobj.Class.Rozdzialy.ClassOfType, atabid, self.Tables, self.ExtTables)
            arefs = drefs.get(achapter.Group, [])
            arefs.extend([aoid, aobj.Class.Rozdzialy.ClassOfType.CID])
            drefs[achapter.Group] = arefs
            atabid = atabid + 10
        dgroups = {}
        for agroup, arefs in drefs.items():
            gobj = dgroups.get(agroup, None)
            if gobj is None:
                if agroup == '':
                    gobj = aobj
                else:
                    w = 0
                    gobj = aobj.GrupyRozdzialow
                    while gobj:
                        if gobj.Nazwa == agroup:
                            w = 1
                            break
                        gobj.Next()
                    if not w:
                        gclass = aobj.Class.GrupyRozdzialow.ClassOfType
                        goid = gclass.AddObject()
                        gobj = gclass[goid]
                        gobj.Nazwa = agroup
                        aobj.Class.GrupyRozdzialow.AddRefs(aobj.OID, [goid, gclass.CID])
                dgroups[agroup] = gobj
            gobj.Class.Rozdzialy.AddRefs(aobj.OID, arefs)
        return 1

    def StoreXMLSourceChapter(self, robj, axml):
        d = {}
        d['oid'] = robj.OID
        d['title'] = robj.Naglowek
        d['titlemenu'] = robj.NaglowekMenu
        d['table'] = robj.TabelaZrodlowa.Nazwa
        d['istableview'] = robj.Class.SGIsTableView.ValuesAsInt(robj.OID)
        d['issearch'] = robj.Class.SGIsSearch.ValuesAsInt(robj.OID)
        d['ismenudisabled'] = robj.Class.SGIsMenuDisabled.ValuesAsInt(robj.OID)
        d['isautogenerate'] = robj.Class.IsAutoGenerate.ValuesAsInt(robj.OID)
        d['isgeneratedisabled'] = robj.Class.IsGenerateDisabled.ValuesAsInt(robj.OID)
        d['href'] = robj.SGHref
        d['hrefapp'] = robj.SGHrefApp
        d['hrefparams'] = robj.SGHrefParams
        d['target'] = robj.SGTarget
        d['comment'] = robj.Komentarz
        sobj = robj.PodRozdzialy
        w = 1
        if sobj:
            w = 0
        axml.Comment(robj.XMLComment)
        axml.TagOpen('rozdzial', d, aclosetag=w, asortattrnames=['oid', 'title', 'table'])
        while sobj:
            self.StoreXMLSourceChapter(sobj, axml)
            sobj.Next()
        if not w:
            axml.TagClose()

    def StoreXMLSource(self, aobj, asave=0):
        fout = cStringIO.StringIO()
        axml = XMLUtil.MXMLFile(fout, anopl=1)
        axml.Header()
        axml.TagOpen('struktura')
        robj = aobj.Rozdzialy
        while robj:
            self.StoreXMLSourceChapter(robj, axml)
            robj.Next()
        axml.TagClose('struktura')
        axml.close()
        ret = fout.getvalue()
        if asave:
            aobj.WWWMenuStructXML2 = ret
        fout.close()
        return ret

    def start_struktura(self, attrs):
        l = self.CheckAttrs(attrs, ['version'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {struktura}: %s' % str(l))

    start_bipstruktura = start_struktura

    def end_struktura(self):
        pass

    def start_grupa(self, attrs):
        l = self.CheckAttrs(attrs, ['name'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {grupa}: %s' % str(l))
        #self.Group=attrs['name']
    def end_grupa(self):
        self.Group = ''

    end_bipstruktura = end_struktura

    def start_rozdzial(self, attrs):
        l = self.CheckAttrs(attrs, ['oid', 'title', 'titlemenu', 'table', 'istableview', 'issearch', 'ismenudisabled', 'href', 'hrefapp', 'target', 'comment', 'showastable', 'isautogenerate', 'isgeneratedisabled'])
        #accessleveledit
        #accessleveltableedit
        #accesslevelview
        #gallery,isautogenerate,isgeneratedisabled,menutitle,hrefparams,showallrecords,
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {rozdzial}: %s' % str(l) + ' ' + str(attrs))
        if attrs.has_key('table'):
            wtables = self.Tables.has_key(attrs['table'])
            if not wtables:
                wtables = self.ExtTables.has_key(attrs['table'])
            if not wtables:
                self.IsGood = 0
                self.status.append('nieznana nazwa tabeli w tagu {rozdzial}: ' + str(attrs))
        acomment = self.GetComments()
        self.ThisChapter = ICORBIPChapter(self.ThisChapter, attrs, acomment=acomment, group=self.Group)
        if self.ThisChapter.Parent is None:
            self.Chapters.append(self.ThisChapter)

    def end_rozdzial(self):
        self.ThisChapter = self.ThisChapter.Parent


class ICORBIPTablesXMLParser(XMLUtil.ICORBaseXMLParser):

    def Parse(self, atext='', astructobj=None, aallowduptablenames=0):
        self.Tables = {}
        self.TablesOIDs = []
        self.IsGood = 1
        self.AllowDupTableNames = aallowduptablenames
        self.ThisTable = None
        self.ThisField = None
        self.InTable = 0
        self.StructObj = astructobj
        self.ExistingTables = {}
        self.ExistingTablesOIDs = {}
        self.status = []
        if self.StructObj:
            bobj = self.StructObj.Projekt.BazyZrodlowe
            while bobj:
                self.ExistingTables[bobj.Nazwa] = bobj.OID
                self.ExistingTablesOIDs[str(bobj.OID)] = bobj.Nazwa
                bobj.Next()
            bobj = self.StructObj.TabeleZrodlowe
            while bobj:
                self.ExistingTables[bobj.Nazwa] = bobj.OID
                self.ExistingTablesOIDs[str(bobj.OID)] = bobj.Nazwa
                bobj.Next()
        XMLUtil.ICORBaseXMLParser.Parse(self, atext)
        tclass = None
        if self.StructObj:
            tclass = self.StructObj.Class.TabeleZrodlowe.ClassOfType
        for atable in self.Tables.values():
            atable.Check(self.status, tclass)

    def ClearTables(self, aobj):
        trefs = aobj.Class.TabeleZrodlowe.GetRefList(aobj.OID)
        try:
            aobj.Projekt.Class.BazyZrodlowe.DeleteRefs(aobj.Projekt.OID, trefs.refs)
        except:
            print 'exception!!!', trefs.refs
            raise
        aobj.Class.TabeleZrodlowe.DeleteReferencedObjects(aobj.OID)

    def Store(self, aobj=None, fout=None, fsql=None):
        if aobj is None:
            aobj = self.StructObj
        tclass = aobj.Class.TabeleZrodlowe.ClassOfType
        for atable in self.Tables.values():
            atable.Check(self.status, tclass)
        arefs = []
        llinkfields, lextdictfields = [], []
        for atable in self.Tables.values():
            if atable.IsNew:
                aoid = atable.Store(tclass, fout, fsql, llinkfields, lextdictfields)
                self.TablesOIDs.append(aoid)
                arefs.extend([aoid, tclass.CID])
            elif atable.IsModified:
                if fout:
                    fout.write('*** tabela zmodyfikowana [%d] %s ***\n' % (atable.OID, atable.Name))
            else:
                if fout:
                    fout.write('tabela bez zmian [%d] %s\n' % (atable.OID, atable.Name))
        aobj.Class.TabeleZrodlowe.DeleteRefs(aobj.OID, arefs)
        aobj.Class.TabeleZrodlowe.AddRefs(aobj.OID, arefs, dosort=1, asortedreffield=aobj.Class.TabeleZrodlowe.ClassOfType.Nazwa, ainsertifnotexists=1)
        aobj.Projekt.Class.BazyZrodlowe.DeleteRefs(aobj.Projekt.OID, arefs)
        aobj.Projekt.Class.BazyZrodlowe.AddRefs(aobj.Projekt.OID, arefs, dosort=1, asortedreffield=aobj.Class.TabeleZrodlowe.ClassOfType.Nazwa, ainsertifnotexists=1)
        #$$
        for alinkfield in llinkfields:
            alinkfield.StoreLink(aobj, self.Tables, self.ExistingTables)
        for aextdictfield in lextdictfields:
            aextdictfield.StoreExtDict(aobj, self.Tables, self.ExistingTables)
        return 1

    def StoreXMLSource(self, aobj):
        fout = cStringIO.StringIO()
        axml = XMLUtil.MXMLFile(fout, anopl=1)
        axml.Header()
        axml.TagOpen('tabele')
        tobj = aobj.TabeleZrodlowe
        while tobj:
            axml.Comment(tobj.Komentarz)
            d = {}
            d['oid'] = tobj.OID
            d['name'] = tobj.Nazwa
            d['group'] = tobj.Group
            d['nametable'] = tobj.NazwaTabeli
            d['nameobject'] = tobj.NazwaObiektu
            axml.TagOpen('tabela', d, asortattrnames=['oid', 'name'])
            lfields = []
            pobj = tobj.Pola
            while pobj:
                anazwa = pobj.Nazwa
                if anazwa[:1] != '_':
                    d = {}
                    atabid = pobj.Class.SGTabIndex.ValuesAsInt(pobj.OID)
                    d['oid'] = pobj.OID
                    d['name'] = pobj.Nazwa
                    d['type'] = pobj.TypPolaDotyczy.Opis
                    d['issearch'] = pobj.Class.SGIsSearch.ValuesAsInt(pobj.OID)
                    d['isaliased'] = pobj.Class.SGIsAliased.ValuesAsInt(pobj.OID)
                    d['isobligatory'] = pobj.Class.SGIsObligatory.ValuesAsInt(pobj.OID)
                    dobj = pobj.ZrodloDanychSlownika
                    if dobj:
                        d['dictionary'] = dobj.Nazwa
                    lfw = []
                    s = pobj.WartosciSlownika
                    if s:
                        lfw = string.split(s, '\n')
                    lfields.append([atabid, d, pobj.Komentarz, lfw])
                pobj.Next()
            lobj = tobj.PolaczeniaDoTabel
            while lobj:
                alinkname = lobj.LinkName
                if alinkname:
                    d = {}
                    atabid = lobj.Class.LinkTabOrder.ValuesAsInt(lobj.OID)
                    d['oid'] = lobj.OID
                    d['name'] = alinkname
                    d['type'] = 'Słownik zewnętrzny - wiele wartości'
                    d['istableview'] = lobj.Class.IsTableView.ValuesAsInt(lobj.OID)
                    d['dictionary'] = lobj.DestinationTable.Nazwa
                    lfields.append([atabid, d, '', []])
                lobj.Next()
            lfields.sort()
            for atabid, d, acomment, lfw in lfields:
                axml.Comment(acomment)
                w = 1
                if lfw:
                    w = 0
                axml.TagOpen('pole', d, aclosetag=w, asortattrnames=['oid', 'name', 'type', 'issearch', 'isaliased', 'dictionary', 'istableview'])
                if not w:
                    d = {}
                    for avalue in lfw:
                        d['value'] = avalue
                        axml.TagOpen('wartoscpola', d, aclosetag=1)
                    axml.TagClose()
            axml.TagClose('tabela')
            axml.write('\n')
            tobj.Next()
        axml.TagClose('tabele')
        axml.close()
        aobj.WWWMenuDataXML2 = fout.getvalue()
        fout.close()

    def start_tabele(self, attrs):
        l = self.CheckAttrs(attrs, ['version'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {tabele}: %s' % str(l))

    start_biptabele = start_tabele

    def start_tabela(self, attrs):
        if self.InTable:
            self.IsGood = 0
            self.status.append('tag <tabela> nie moze wystepowac jak podtag tagu {tabela}: ' + str(attrs))
        self.InTable = 1
        l = self.CheckAttrs(attrs, ['oid', 'name', 'group', 'nametable', 'nameobject'])
        #group,
        #accessleveldelete
        #accessleveledit
        #accesslevelfilesupload
        #accesslevelview
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {tabela}: %s' % str(l) + ' ' + str(attrs))
        if self.Tables.has_key(attrs['name']):
            self.IsGood = 0
            self.status.append('powtorzona nazwa tabeli w tagu {tabela}: ' + str(attrs))
        self.ignoreTable = 0
        if not self.AllowDupTableNames and self.ExistingTables.has_key(attrs['name']):
            self.ignoreTable = 1
            if attrs.has_key('oid'):
                if attrs['oid'] != str(self.ExistingTables[attrs['name']]):
                    self.IsGood = 0
                    self.status.append('powtorzona nazwa tabeli w tagu {tabela}, tabela juz istnieje i ma inny OID: ' + str(attrs))
            else:
                #            self.IsGood=0
                attrs['oid'] = self.ExistingTables[attrs['name']]
                attrs['exists'] = '1'
                self.status.append('info: tabela juz istnieje: ' + str(attrs))


#      elif attrs.has_key('oid'):
#         if self.ExistingTablesOIDs[attrs['oid']]!=attrs['name']:
#            self.IsGood=0
#            self.status.append('tabela o juz istniejacym OID ma inna nazwe: '+str(attrs))
        if not self.ignoreTable:
            acomment = self.GetComments()
            self.ThisTable = ICORBIPTable(self.Tables, attrs, acomment=acomment)
            self.Tables[self.ThisTable.Name] = self.ThisTable

    def start_pole(self, attrs):
        if self.ignoreTable:
            return
        l = self.CheckAttrs(attrs, ['oid', 'name', 'type', 'issearch', 'isaliased', 'dictionary', 'istableview', 'namevisible', 'issingleviewhidden', 'isdictviewhidden', 'isobligatory', 'defaultvalue'])
        #isobligatory,isunique,sortstyle,isdictviewhidden,issingleviewhidden
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {pole}: %s' % str(l))
        if not attrs['type'] in ICOR_TYPES:
            self.IsGood = 0
            self.status.append('nieznany typ pola w tagu {pole}: ' + str(attrs))
        acomment = self.GetComments()
        self.ThisField = self.ThisTable.AddField(attrs, acomment=acomment)
        self.FieldValues = []
        self.FieldDictValues = []

    def start_wartoscpola(self, attrs):
        if self.ignoreTable:
            return
        l = self.CheckAttrs(attrs, ['value'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {wartoscpola}: %s' % str(l))
        self.FieldValues.append(attrs.get('value', ''))

    def start_wartoscslownika(self, attrs):
        if self.ignoreTable:
            return
        l = self.CheckAttrs(attrs, ['value', 'id'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {wartoscslownika}: %s' % str(l))
        avalue = attrs.get('value', '')
        aid = attrs.get('id', avalue)
        self.FieldDictValues.append([aid, avalue])

    def end_tabele(self):
        pass

    end_biptabele = end_tabele

    def end_tabela(self):
        self.InTable = 0

    def end_pole(self):
        if self.ignoreTable:
            return
        self.ThisField.FieldValues = self.FieldValues
        self.ThisField.FieldDictValues = self.FieldDictValues

    def end_wartoscpola(self):
        pass

    def end_wartoscslownika(self):
        pass


class ICORBIPTemplateParser(XMLUtil.ICORBaseXMLParser):

    def Parse(self, amenustruct, atext):
        self.MenuStruct = amenustruct
        self.Variables = {}
        XMLUtil.ICORBaseXMLParser.Parse(self, atext)

    def get(self, name, default=''):
        return self.Variables.get(name, '')

    def __getitem__(self, name):
        return self.Variables.get(name, '')

    def __setitem__(self, name, value):
        self.Variables[name] = value

    def start_TEMPLATE(self, attrs):
        pass

    def start_VARIABLES(self, attrs):
        pass

    def start_VAR(self, attrs):
        l = self.CheckAttrs(attrs, ['name'])
        if l:
            self.IsGood = 0
            self.status.append('nieznane atrybuty w tagu {struktura}: %s' % str(l))
        self.ThisVarName = attrs.get('name', '')
        self.TagData = ''

    def end_TEMPLATE(self):
        pass

    def end_VARIABLES(self):
        pass

    def end_VAR(self):
        self.Variables[self.ThisVarName] = self.TagData

    def start_OUTPUT(self, attrs):
        self.output_folder = attrs.get('folder', '')
        self.output_filename = attrs.get('filename', '')
        self.output_extension = attrs.get('extension', 'asp')
        self.output_scope = attrs.get('scope', 'chapter')
        self.output_filename = attrs.get('filename', '')
        self.output_var = attrs.get('var', '')
        self.output_text = []

    def end_OUTPUT(self):
        pass

    def start_FILEITEM(self, attrs):
        aname = attrs.get('name', '')
        if 0:
            atext = self.MenuStruct.GetTemplateFileItem(aname)
            btext = ICORUtil.GetTextAsHTMLText(atext, repldict=self.MenuStruct.repldict, aengine=aICORDBEngine, aashtmlstring=0)
            self.output_text.append(btext)

    def end_FILEITEM(self):
        pass

    def Dump(self):
        print '*** variables ***'
        l = self.Variables.keys()
        l.sort()
        for s in l:
            print '  %s="%s"' % (s, self.Variables[s])


def Main():
    if len(sys.argv) != 3:
        print 'usage:'
        print '  %s <struct.xml> <tables.xml>' % sys.argv[0]
        return
    fin = open(sys.argv[1], 'r')
    sstruct = fin.read()
    fin.close()
    fin = open(sys.argv[2], 'r')
    stables = fin.read()
    fin.close()

    fout = open('out', 'w')
    fout.write('*** TABELE ***\n')
    bparser = ICORBIPTablesXMLParser()
    bparser.Parse(stables)
    bparser.Dump(fout)
    fout.write('\n\n*** STRUKTURA ***\n')
    aparser = ICORBIPStructXMLParser()
    aparser.Parse(sstruct, bparser.Tables)
    aparser.Dump(fout)
    fout.close()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    axml = """<?xml version="1.0" encoding="utf-8"?>
<TEMPLATE>
  <VARIABLES>
    <VAR name="type_Telefon_xsl_BeforeFieldValue"><![CDATA[<img border="0" src="img/telefon.gif"/>&#160;]]></VAR>
    <VAR name="type_EMail_xsl_BeforeFieldValue"><![CDATA[<img border="0" src="img/email.gif"/>&#160;]]></VAR>
  </VARIABLES>
</TEMPLATE>
"""
    aparser = ICORBIPTemplateParser()
    aparser.Parse(axml)
    aparser.Dump()
