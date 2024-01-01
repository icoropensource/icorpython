# -*- coding: utf-8 -*-
from icorlib.icorinterface import *


class WWWMenuChapterView:

    def __init__(self, apresentation, vobj, akind=None, atype=None):
        self.Presentation = apresentation
        self.OID = vobj.OID
        self.Obj = vobj.AsObject()
        self._kind = akind
        self._type = atype
        self._text = None
        self._iscustom = None
        self._key = None
        self._description = None

    def __getattr__(self, name):
        if name == 'Kind':
            if self._kind is None:
                kobj = self.Obj.Kind
                if kobj:
                    self._kind = kobj.Kind
                else:
                    self._kind = ''
            return self._kind
        if name == 'ViewType':
            if self._type is None:
                tobj = self.Obj.ViewType
                if tobj:
                    self._type = tobj.ViewType
                else:
                    self._type = ''
            return self._type
        if name == 'ViewText':
            if self._text is None:
                self._text = self.Obj.ViewText
            return self._text
        if name == 'IsCustom':
            if self._iscustom is None:
                self._iscustom = self.Obj['IsCustom']
            return self._iscustom
        if name == 'ViewKey':
            if self._key is None:
                self._key = self.Obj.ViewKey
            return self._key
        if name == 'Description':
            if self._description is None:
                self._description = self.Obj.Description
            return self._description

    def __setattr__(self, name, value):
        if name == 'ViewText':
            self.Obj.ViewText = value
        else:
            self.__dict__[name] = value


class WWWMenuChapterPresentation:

    def __init__(self, robj):
        self.OID = robj.OID
        self.Obj = robj.AsObject()

    def Exists(self):
        return self.Obj.ChapterView.Exists()

    def CreateViewByData(self, akind, atype, aiscustom, atext, aupdate=0):
        btext = atext.replace(chr(10), '')
        btext = atext.replace(chr(13), '')
        btext = atext.replace(chr(32), '')
        if not btext:
            return
        dkind_oid = {'dane': 1, 'tabela': 2, 'lista': 3}
        dtype_oid = {'xsl': 1, 'quasar': 2}
        aview = self.GetView(akind, atype)
        if aview is None:
            vclass = self.Obj.Class.ChapterView.ClassOfType
            void = vclass.AddObject(arefobject=self.Obj)
            if void < 0:
                print 'brak zakresu OID dla ChapterID:', self.OID
                return None
            vclass.IsCustom[void] = aiscustom
            vclass.Kind[void] = [dkind_oid[akind], vclass.Kind.ClassOfType.CID]
            vclass.ViewType[void] = [dtype_oid[atype], vclass.ViewType.ClassOfType.CID]
            vclass.ViewText[void] = atext
            self.Obj.Class.ChapterView.AddRefs(self.OID, [void, vclass.CID])
        elif aupdate:
            if not aview.IsCustom:
                aview.ViewText = atext
        return

    def GetView(self, akind, atype=''):
        # Kind: dane, tabela, lista
        # Type: xsl, quasar
        vobj = self.Obj.ChapterView
        while vobj:
            kobj = vobj.Kind
            if kobj and kobj.Kind == akind:
                if atype:
                    tobj = vobj.ViewType
                    if tobj and tobj.ViewType == atype:
                        return WWWMenuChapterView(self, vobj, akind, atype)
                else:
                    return WWWMenuChapterView(self, vobj, akind)
            vobj.Next()
        return None


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
