# -*- coding: utf-8 -*-
from icorinterface import *
from icormdspace import *
from CLASSES_Library_NetBase_Utils_MDSpaceUtil import *
from CLASSES_Library_NetBase_Utils_XMLUtil import GetAsXMLString, GetAsXMLStringNoPL
import string
import random


class ObjectDataValue:

    def __init__(self, afield=None, aoid=-1, acid=-1, arefcid=-1, arefoid=-1):
        self.Field = afield
        self.OID = aoid
        self.CID = acid
        self.RefCID = arefcid
        self.RefOID = arefoid
        self.StringValue = ''

    def AsString(self):
        if self.OID >= 0:
            if self.Field.FieldTID == mt_Bool:
                if self.Field.ValuesAsInt(self.OID):
                    return 'Tak'
                else:
                    return 'Nie'
            else:
                return self.Field.ValuesFmt(self.OID)
        else:
            return self.StringValue

    def AlignmentStd(self):
        if self.Field is None:
            return -1
        else:
            return self.Field.AlignmentStd


class ICORClassObjectsViewer:

    def __init__(self, acid, aspace, afield=None, aoid=-1):
        self.space = aspace
        self.Class = aICORDBEngine.Classes[acid]
        self.CID = self.Class.CID
        self.Field = afield
        self.LOID = aoid
        self.OnIsObjectValid = None
        self.ValueCheck = ''
        self.ObjectsCount = 0

    def Process(self, afoid=-1, acount=0):
        self.acol = 0
        self.header = self.PrepareHeader(self.Class, [])
        self.acol = 0
        self.header = self.ProcessHeader(self.header)
        self.ObjectsCount = 0
        if self.Field is None:
            return self.ProcessByClass(afoid, acount)
        else:
            return self.ProcessByField(afoid, acount)

    def ProcessByField(self, afoid=-1, acount=0):
        arefs = self.Field.GetRefList(self.LOID)
        arow = 0
        while arefs.position >= 0:
            self.RefOID = arefs.OID
            self.RefCID = arefs.CID
            if self.IsObjectValid(arefs.Class, arefs.OID, arow):
                self.ObjectsCount = self.ObjectsCount + 1
                self.ProcessObject(arefs.Class, arefs.OID, arow, self.header)
            arow = arow + 1
            arefs.Next()
        return 'OV_' + str(self.CID) + '_' + self.Field.Name + '_' + str(self.LOID) + '_' + str(afoid) + '_' + str(acount)

    def ProcessByClass(self, afoid=-1, acount=0):
        if afoid < 0:
            afoid = self.Class.FirstObject()
        if acount >= 0:
            arow = 0
            self.RefCID = self.Class.CID
            while afoid >= 0:
                self.RefOID = afoid
                if self.IsObjectValid(self.Class, afoid, arow):
                    self.ObjectsCount = self.ObjectsCount + 1
                    self.ProcessObject(self.Class, afoid, arow, self.header)
                arow = arow + 1
                if arow == acount:
                    break
                afoid = self.Class.NextObject(afoid)
        elif acount < 0:
            arow = -acount
            self.RefCID = self.Class.CID
            while afoid >= 0:
                if arow == 0:
                    break
                self.RefOID = afoid
                if self.IsObjectValid(self.Class, afoid, arow):
                    self.ObjectsCount = self.ObjectsCount + 1
                    self.ProcessObject(self.Class, afoid, arow, self.header)
                arow = arow - 1
                afoid = self.Class.PrevObject(afoid)
        return 'OV_' + str(self.CID) + '_' + str(afoid) + '_' + str(acount)

    def ProcessObject(self, aclass, afoid, arow, header):
        for x in range(len(header)):
            v = header.values[x]
            afield = v[0]
            acolid = v[1]
            slist = v[2:][0]
            if slist is None:
                odv = ObjectDataValue(afield, afoid, self.CID, self.RefCID, self.RefOID)
                self.space[arow, acolid] = odv
            else:
                arefs = afield.GetRefList(afoid)
                if arefs.position >= 0:
                    self.ProcessObject(afield.ClassOfType, arefs.OID, arow, slist)

    def ProcessHeader(self, header):
        for x in range(len(header)):
            v = header.values[x]
            afield = v[0]
            slist = v[2:][0]
            if slist is None:
                self.space.header.Append(afield.FieldNameAsDisplayed)
                v = afield, self.acol, None
                header.values[x] = v
                self.acol = self.acol + 1
            else:
                slist = self.ProcessHeader(slist)
                v = afield, -1, slist
                header.values[x] = v
        return header

    def PrepareHeader(self, aclass, reclist):
        if aclass is None:
            return None
        if aclass.CID in reclist:
            return None
        reclist.append(aclass.CID)
        flist = aclass.GetFieldsList()
        fplist = ICORSortedDictionary()
        for afname in flist:
            afield = aclass.FieldsByName(afname)
            if afield.IsAliased != '1' or afield.IsInteractive != '1':
                continue
            apos = int(afield.FieldPosition)
            fclass = afield.ClassOfType
            if fclass is None:
                li = afield, self.acol, None
                self.acol = self.acol + 1
                fplist.Add(apos, li)
            else:
                sflist = self.PrepareHeader(fclass, reclist)
                li = afield, -1, sflist
                if sflist is not None:
                    fplist.Add(apos, li)
        del reclist[len(reclist) - 1]
        return fplist

    def IsObjectValid(self, aclass, aoid, arow):
        if self.OnIsObjectValid is not None:
            return self.OnIsObjectValid(self, aclass, aoid, arow)
        return 1


class ICORClassObjects2HTML(ICORMDSpace2HTML):

    def OnData(self, arow, acol):
        if self.Value is None:
            s = '<DIV align=Center><A CLASS="objectitemasanchor">&nbsp;-&nbsp;</A></DIV>'
            self.file.write(s)
        else:
            alg = self.Value.AlignmentStd()
            if alg == '0':
                align = 'Left'
            elif alg == '1':
                align = 'Right'
            elif alg == '2':
                align = 'Center'
            else:
                align = 'Left'


#         s=string.replace(self.Value.AsString(),' ','&nbsp;')
            s = self.Value.AsString()
            if s == '':
                align = 'Center'
                s = '&nbsp;-&nbsp;'
            s = '<DIV align=%s><A CLASS="objectitemasanchor" href="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d">%s</A></DIV>' % (align, self.Value.RefCID, self.Value.RefOID, random.randint(1, 10000000), s)
            self.file.write(s)


class ICORClassObjects2HTMLSorted(ICORMDSpace2HTMLSimple):

    def OnData(self, arow, acol):
        if self.Value is None:
            s = '<DIV align=Center><A CLASS="objectitemasanchor">&nbsp;-&nbsp;</A></DIV>'
            self.file.write(s)
        else:
            alg = self.Value.AlignmentStd()
            if alg == '0':
                align = 'Left'
            elif alg == '1':
                align = 'Right'
            elif alg == '2':
                align = 'Center'
            else:
                align = 'Left'


#         s=string.replace(self.Value.AsString(),' ','&nbsp;')
            s = self.Value.AsString()
            if s == '':
                align = 'Center'
                s = '&nbsp;-&nbsp;'
            s = '<DIV align=%s><A CLASS="objectitemasanchor" href="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d">%s</A></DIV>' % (align, self.Value.RefCID, self.Value.RefOID, random.randint(1, 10000000), s)
            self.file.write(s)


class ICORClassObjects2HTMLLinks(ICORMDSpace2HTMLLinks):

    def OnStartRow(self, arow):
        self.CurrentValue = []

    def OnData(self, arow, acol):
        if self.Value is not None:
            self.CurrentCID = self.Value.RefCID
            self.CurrentOID = self.Value.RefOID
            s = self.Value.AsString()
            if s:
                self.CurrentValue.append(s)

    def OnEndRow(self, arow):
        s = string.join(self.CurrentValue, ', ')
        s = '<A class="reflistoutnavy objectitemasanchor" href="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d">%s</A>' % (self.CurrentCID, self.CurrentOID, random.randint(1, 10000000), s)
        self.Links.append(s)


class ICORClassObjects2HTMLLinksNoRefs(ICORMDSpace2HTMLLinks):

    def OnStartRow(self, arow):
        self.CurrentValue = []

    def OnData(self, arow, acol):
        if self.Value is not None:
            self.CurrentCID = self.Value.RefCID
            self.CurrentOID = self.Value.RefOID
            s = self.Value.AsString()
            if s:
                self.CurrentValue.append(s)

    def OnEndRow(self, arow):
        s = string.join(self.CurrentValue, ', ')
        s = '<A  class=reflistoutnavy>%s</A>' % (s, )
        self.Links.append(s)


class ICORClassObjects2HTMLNoRefs(ICORMDSpace2HTML):

    def OnData(self, arow, acol):
        if self.Value is None:
            s = '<DIV align=Center><A CLASS="objectitemasanchor">&nbsp;-&nbsp;</A></DIV>'
            self.file.write(s)
        else:
            alg = self.Value.AlignmentStd()
            if alg == '0':
                align = 'Left'
            elif alg == '1':
                align = 'Right'
            elif alg == '2':
                align = 'Center'
            else:
                align = 'Left'


#         s=string.replace(self.Value.AsString(),' ','&nbsp;')
            s = self.Value.AsString()
            if s == '':
                align = 'Center'
                s = '&nbsp;-&nbsp;'
            s = '<DIV align=%s><A CLASS="objectitemasanchor">%s</A></DIV>' % (align, s)
            self.file.write(s)


class ICORClassObjects2XMLDSO(ICORMDSpace2XMLDSO):

    def OnData(self, arow, acol):
        #      if self.Value is None:
        #         self.file.write('-')
        #      else:
        #         self.file.write(self.Value.AsString())
        #      return
        if self.Value is None:
            s = '<DIV align="Center"><A CLASS="objectitemasanchor">&nbsp;-&nbsp;</A></DIV>'
            self.file.write(GetAsXMLString(s))
        else:
            alg = self.Value.AlignmentStd()
            if alg == '0':
                align = 'Left'
            elif alg == '1':
                align = 'Right'
            elif alg == '2':
                align = 'Center'
            else:
                align = 'Left'


#         s=string.replace(self.Value.AsString(),' ','&nbsp;')
            s = self.Value.AsString()
            if s == '':
                align = 'Center'
                s = '&nbsp;-&nbsp;'
            s1 = '<DIV align="%s"><A CLASS="objectitemasanchor" href="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&RandomValue=%d">' % (align, self.Value.RefCID, self.Value.RefOID, random.randint(1, 10000000))
            s1 = GetAsXMLString(s1)
            s2 = GetAsXMLString('</A></DIV>')
            self.file.write('%s%s%s' % (s1, GetAsXMLStringNoPL(s), s2))
