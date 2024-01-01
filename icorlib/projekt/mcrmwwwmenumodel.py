# -*- coding: utf-8 -*-
from icorlib.icorinterface import *


class WWWMenuChapterModel:

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
        if name == 'ModelType':
            if self._type is None:
                tobj = self.Obj.ModelType
                if tobj:
                    self._type = tobj.ModelType
                else:
                    self._type = ''
            return self._type
        if name == 'ModelText':
            if self._text is None:
                self._text = self.Obj.ModelText
            return self._text
        if name == 'IsCustom':
            if self._iscustom is None:
                self._iscustom = self.Obj['IsCustom']
            return self._iscustom
        if name == 'ModelKey':
            if self._key is None:
                self._key = self.Obj.ModelKey
            return self._key
        if name == 'Description':
            if self._description is None:
                self._description = self.Obj.Description
            return self._description

    def __setattr__(self, name, value):
        if name == 'ModelText':
            self.Obj.ModelText = value
        else:
            self.__dict__[name] = value


class WWWMenuChapterModels:

    def __init__(self, robj):
        self.OID = robj.OID
        self.Obj = robj.AsObject()

    def Exists(self):
        return self.Obj.Models.Exists()

    def CreateModelByData(self, akind, atype, aiscustom, atext, aupdate=0):
        btext = atext.replace(chr(10), '')
        btext = atext.replace(chr(13), '')
        btext = atext.replace(chr(32), '')
        if not btext:
            return
        dkind_oid = {'struktura': 1}
        dtype_oid = {'sqlshape': 1, 'sqlxml': 2}
        amodel = self.GetModel(akind, atype)
        if amodel is None:
            mclass = self.Obj.Class.Models.ClassOfType
            moid = mclass.AddObject(arefobject=self.Obj)
            if moid < 0:
                print 'brak zakresu OID dla ChapterID:', self.OID
                return None
            mclass.IsCustom[moid] = aiscustom
            mclass.Kind[moid] = [dkind_oid[akind], mclass.Kind.ClassOfType.CID]
            mclass.ModelType[moid] = [dtype_oid[atype], mclass.ModelType.ClassOfType.CID]
            mclass.ModelText[moid] = atext
            self.Obj.Class.Models.AddRefs(self.OID, [moid, mclass.CID])
        elif aupdate:
            if not amodel.IsCustom:
                amodel.ModelText = atext
        return

    def GetModel(self, akind, atype):
        # Kind: struktura
        # Type: sqlshape, sqlxml
        mobj = self.Obj.Models
        while mobj:
            kobj = mobj.Kind
            if kobj and kobj.Kind == akind:
                if atype:
                    tobj = mobj.ModelType
                    if tobj and tobj.ModelType == atype:
                        return WWWMenuChapterModel(self, mobj, akind, atype)
                else:
                    return WWWMenuChapterModel(self, mobj, akind)
            mobj.Next()
        return None


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    aclass = aICORDBEngine.Classes[CID]
    return
