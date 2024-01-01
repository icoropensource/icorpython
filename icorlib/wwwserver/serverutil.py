# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
from CLASSES_Library_NetBase_Utils_XMLUtil import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import string

SPLIT_CHAR_PARAM = "$*$!"    #255
SPLIT_CHAR_VALUE = "$*!$"    #254
SPLIT_CHAR_SEPTR = "$*$@"    #253


class ICORReport:

    def __init__(self, reportstring='', adefPost=0, azope=0, aresponse=None, asession=None, arequest=None, autfsplit=0):
        self.formdict = {}
        self.formlist = []
        self.IsZOPE = 0
        self.RESPONSE = aresponse
        self.SESSION = asession
        self.REQUEST = arequest
        if type(reportstring) == type({}):
            self.formdict = reportstring
            for k in reportstring.keys():
                self.formlist.append(k)
        elif type(reportstring) == type([]):
            for k, v in reportstring:
                if not self.formdict.has_key(k):
                    self.formlist.append(k)
                self.formdict[k] = v
        else:
            self.Set(reportstring, adefPost, autfsplit)

    def Set(self, reportstring, adefPost=0, autfsplit=0):
        if reportstring == '':
            return
        cp, cv = chr(255), chr(254)
        if autfsplit:
            cp, cv = SPLIT_CHAR_PARAM, SPLIT_CHAR_VALUE
        reportstring = XMLUtil.UTF2Win(reportstring)
        if adefPost:
            sl = string.split(reportstring, '&')
            for v in sl:
                i = string.find(v, '=')
                if i >= 0:
                    sk, sv = v[:i], URLString2NormalString(v[i + 1:])
                    self.formdict[sk] = sv
                    self.formlist.append(sk)
        else:
            sl = string.split(reportstring, cp)
            for fv in sl:
                fl = string.split(fv, cv)
                if len(fl) != 2:
                    continue
                s = string.replace(fl[1], '&#13;', chr(13))
                s = string.replace(s, '&#10;', chr(10))
                s = string.replace(s, '&#' + str(ord('"')) + ';', '"')
                s = string.replace(s, '&#' + str(ord("'")) + ';', "'")
                s = string.replace(s, '&sup1;', 'ą')
                s = string.replace(s, '&aelig;', 'ć')
                s = string.replace(s, '&ecirc;', 'ę')
                s = string.replace(s, '&sup3;', 'ł')
                s = string.replace(s, '&ntilde;', 'ń')
                s = string.replace(s, '&#339;', 'ś')
                s = string.replace(s, '&#376;', 'ź')
                s = string.replace(s, '&iquest;', 'ż')
                s = string.replace(s, '&yen;', 'Ą')
                s = string.replace(s, '&AElig;', 'Ć')
                s = string.replace(s, '&Ecirc;', 'Ę')
                s = string.replace(s, '&pound;', 'Ł')
                s = string.replace(s, '&Ntilde;', 'Ń')
                s = string.replace(s, '&#338;', 'Ś')
                s = string.replace(s, '&#143;', 'Ź')
                s = string.replace(s, '&macr;', 'Ż')
                self.formdict[fl[0]] = s
                self.formlist.append(fl[0])

    def __repr__(self):
        return str(self.formdict)

    def __str__(self):
        return str(self.formdict)

    def __getattr__(self, name):
        if name == 'reportoid':
            if self.formdict.has_key('reportoid'):
                return int(self.formdict.get('reportoid', -1))
            return -1
        return self.get(name, None)

    def __getitem__(self, name):
        if name == 'reportoid':
            if self.formdict.has_key('reportoid'):
                return int(self.formdict.get('reportoid', -1))
            return -1
        elif type(name) == type(()):
            key, defvalue = name
            if self.formdict.has_key(key):
                return self.formdict.get(key, defvalue)
            return defvalue
        elif self.formdict.has_key(name):
            return self.formdict[name]

    def __setitem__(self, name, value):
        self.SetValue(name, value)

    def get(self, key, defvalue=''):
        if self.formdict.has_key(key):
            return self.formdict.get(key, defvalue)
        return defvalue

    def has_key(self, name):
        if self.formdict.has_key(name):
            return 1
        return 0

    def keys(self):
        return self.formlist

    def items(self):
        return self.formdict.items()

    def SetValue(self, name, value):
        self.formdict[name] = value
        self.formlist.append(name)

    def AsString(self, adefpost=0):
        if adefpost:
            sep1, sep2 = '=', '&'
        else:
            sep1, sep2 = SPLIT_CHAR_VALUE, SPLIT_CHAR_PARAM
        alist = []
        for key in self.formlist:
            value = self.formdict[key]
            alist.append(key + sep1 + value)
        return string.join(alist, sep2)

    def AsListFromField(self, afield, asint=0):
        alist = []
        for key in self.formlist:
            if key.find(afield + '_') == 0:
                value = self.formdict[key]
                if asint:
                    value = int(value)
                alist.append(value)
        return alist

    def Dump(self):
        for akey in self.formlist:
            print akey, '=', self.formdict[akey]


def GenerateHeaderHTML(file, afname):
    sheader = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<HTML>
<HEAD>
<meta http-equiv="X-UA-Compatible" content="IE=8">
<META http-equiv="Content-Type" content="text/html; charset=utf-8">
</HEAD>
<BODY>
<H1>Displaying Hierarchical Data Using the XML DSO</H1>
<applet code=com.ms.xml.dso.XMLDSO.class width=0 height=0 id=xmldso mayscript=true>
   <PARAM NAME="url" VALUE="%s">
</applet>
''' % (afname)
    file.write(sheader)


def GenerateFooterHTML(file):
    sfooter = '''
</BODY>
</HTML>
'''
    file.write(sfooter)


def GenerateHeader(file, aclass):
    file.write('<?xml version="1.0" encoding="utf-8" RMD="NONE"?>\n')
    file.write('\n')
    sheader = '<%s>\n\n' % (aclass.NameOfClass)
    file.write(sheader)


def GenerateFooter(file, aclass):
    sfooter = '\n</%s>\n\n' % (aclass.NameOfClass)
    file.write(sfooter)


def DumpObjectAsXML(aclass, aoid, file, afirst=1, aspaces=0):
    import string
    if afirst:
        file.write('<OBJECT>\n')
    flist = aclass.GetFieldsList()
    for afname in flist:
        afield = aclass.FieldsByName(afname)
        if afield.IsInteractive == '1' and afield.AllowRead == '1' and afield.IsVirtual != '1':
            ismemo = afield.IsContainer == '1' and afield.FieldTypeID == str(mt_String)
            if int(afield.FieldTypeID) > MAX_ICOR_SYSTEM_TYPE:
                s = '%s<%s>\n' % (' ' * (aspaces + 3), afname)
                file.write(s)
                afield.ForEachRefObject(DumpObjectAsXML, aoid, file, 0, aspaces + 3)
                s = '%s</%s>\n' % (' ' * (aspaces + 3), afname)
                file.write(s)
            else:
                s = '%s<%s>' % (' ' * (aspaces + 3), afname)
                file.write(s)
                if ismemo:
                    sv = afield.ValuesAsString(aoid)
                    svl = ''
                    for c in sv:
                        if c != '\015':
                            svl = svl + c
                    slist = string.split(svl, '\n')
                    for sv in slist:
                        file.write(GetAsXMLString(sv) + '\n')
                else:
                    file.write(GetAsXMLString(afield.ValuesAsString(aoid)))
                s = '</%s>\n' % (afname)
                file.write(s)
    if afirst:
        file.write('</OBJECT>\n\n')


def DumpObjectsAsXML(afname, aclass, afoid=-1, acount=-1):
    f = open(afname, 'wb')
    try:
        GenerateHeader(f, aclass)
        if afoid < 0:
            afoid = aclass.FirstObject()
        i = 0
        while afoid >= 0:
            if i == acount:
                break
            i = i + 1
            DumpObjectAsXML(aclass, afoid, f)
            afoid = aclass.NextObject(afoid)
        GenerateFooter(f, aclass)
    finally:
        f.close()
        InfoStatus('')
    return


def DumpClassAsXML(file, aclass, creclist, adatafld='', aspaces=0):
    if aclass.CID in creclist:
        return
    creclist.append(aclass.CID)
    if adatafld != '':
        s = ' datafld=%s' % (adatafld)
    else:
        s = ''
    s1 = '%s<table datasrc=#xmldso border=2 width=100%s cellpadding=3%s>\n' % (' ' * aspaces, '%', s)
    file.write(s1)

    def afieldheadfunc(aclass, afield, file, aspaces):
        s = '%s<th>%s</th>\n' % (' ' * (aspaces + 3), afield.Name)
        file.write(s)

    def afieldfunc(aclass, afield, file, creclist, adatafld, aspaces):
        bcid = int(afield.FieldTypeID)
        if bcid in creclist:
            return
        if bcid > MAX_ICOR_SYSTEM_TYPE:
            file.write('%s<td valign=top>\n' % (' ' * (aspaces + 3)))
            if adatafld != '':
                s = adatafld + '.' + afield.Name
            else:
                s = afield.Name
            bclass = aICORDBEngine.Classes[bcid]
            DumpClassAsXML(file, bclass, creclist, s, aspaces + 6)
            file.write('%s</td>\n' % (' ' * (aspaces + 3)))
        else:
            s = '%s<td valign=top><div datafld=%s dataformatas=HTML></div></td>\n' % (' ' * (aspaces + 3), afield.Name)
            file.write(s)


#   file.write('%s<thead>\n'%(' '*(aspaces+3)))
#   aclass.ForEachField(afieldheadfunc,file,aspaces)
#   file.write('%s</thead>\n'%(' '*(aspaces+3)))

    file.write('%s<tr>\n' % (' ' * (aspaces + 3)))
    aclass.ForEachField(afieldfunc, file, creclist, adatafld, aspaces)
    file.write('%s</tr>\n' % (' ' * (aspaces + 3)))
    file.write('%s</table>\n' % (' ' * (aspaces)))


def CreateHTMLFile(afname, afile, aclass):
    f = open(afname, 'wb')
    try:
        afl = string.split(afile, '/')
        fxn = afl[len(afl) - 1]
        GenerateHeaderHTML(f, fxn)
        DumpClassAsXML(f, aclass, [])
        GenerateFooterHTML(f)
    finally:
        f.close()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    import string
    ClearStdOut()
    afile = InputFile()
    if afile == '':
        return
    afile = FilePathAsSystemPath(afile)
    afileh = FilePathAsSystemPath(afile)
    if afile[-4:] != '.xml':
        afile = afile + '.xml'
    if afileh[-4:] != '.htm':
        afileh = afileh + '.htm'
    adialog = InputElementDialog('Wybierz klasę bazową dla paczki', 0, 0)
    if not adialog.Show():
        return
    aclass = aICORDBEngine.Classes[adialog.ClassPath]
    DumpObjectsAsXML(afile, aclass, -1, -1)
    CreateHTMLFile(afileh, afile, aclass)
    return
