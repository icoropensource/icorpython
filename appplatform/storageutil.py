# -*- coding: utf-8 -*-
import sys
import os
import re
import decimal
import time
import datetime
import uuid
import codecs
import hashlib
import random
import traceback
import types
try:
    import json
except:
    import simplejson as json

PATT_OID = re.compile('^[0-9a-f]{32}$', re.I)
SPLIT_CHAR_PARAM = "$*$!"    #255
SPLIT_CHAR_VALUE = "$*!$"    #254
SPLIT_CHAR_SEPTR = "$*$@"    #253
PATT_CLEANPATH = re.compile(r'[/\\]')


class SafeStreamReaderWriter(codecs.StreamReaderWriter):

    def write(self, atext):
        if isinstance(atext, str):
            atext = unicode(atext, 'cp1250', 'ignore')
        try:
            codecs.StreamReaderWriter.write(self, atext)
        except:
            traceback.print_exc()


def OpenText(afilename, amode='rb', aencoding='utf-8', aerrors='xmlcharrefreplace', abuffering=1):
    if aencoding is not None and 'b' not in amode:
        amode = amode + 'b'
    if (aencoding == 'utf-8') and 'r' in amode:
        aencoding = 'utf-8-sig'
    acnt = 5
    atime = 0.2
    while acnt:
        try:
            acnt = acnt - 1
            afile = open(afilename, amode, abuffering)
            break
        except IOError, e:
            if e.errno == 13:    #Permission denied
                time.sleep(atime)
                atime = atime + atime
            else:
                raise
    if aencoding is None:
        return afile
    ainfo = codecs.lookup(aencoding)
    asrw = SafeStreamReaderWriter(afile, ainfo.streamreader, ainfo.streamwriter, aerrors)
    asrw.encoding = aencoding
    return asrw


def CleanPath(afilepath, aslash='/', aremovelast=True, aensurelast=False, anormalize=True):
    if anormalize:
        afilepath = os.path.normpath(afilepath)
    afilepath = PATT_CLEANPATH.sub(aslash, afilepath)
    if aremovelast and afilepath[-1:] == aslash:
        afilepath = afilepath[:-1]
    if aensurelast and afilepath[-1:] != aslash:
        afilepath = afilepath + aslash
    return afilepath


def SplitFilePath(afilepath, aclean=True):
    if aclean:
        afilepath = CleanPath(afilepath)
    l = []
    while afilepath:
        afilepath, s = os.path.split(afilepath)
        l.append(s)
    l.reverse()
    return l


def IsUTF8String(s):
    s1 = s.encode('unicode-internal')
    isinternal = 0
    if len(s1) > len(s):
        isinternal = 1
    if s1.find('\x00') >= 0:
        return 1, isinternal
    if s1.find('\xc3') >= 0:
        return 1, isinternal
    if s1.find('\xc4') >= 0:
        return 1, isinternal
    if s1.find('\xc5') >= 0:
        return 1, isinternal
    if s1.find('\xe3') >= 0:
        return 1, isinternal
    if s1.find('\xe4') >= 0:
        return 1, isinternal
    if s1.find('\xe5') >= 0:
        return 1, isinternal
    return 0, 0


def UTF8_To_CP1250(s, amode='xmlcharrefreplace', aencoding='utf-8'):
    if not s:
        return ''.encode('cp1250', amode)
    isutf8, isinternal = IsUTF8String(s)
    if not isutf8:
        return s
    if type(s) == type(''):
        s = unicode(s, aencoding, 'ignore')
    return s.encode('cp1250', amode)


def CP1250_To_UTF8_Unicode(s, amode='xmlcharrefreplace'):
    if not s:
        return ''.encode('utf-8', amode)
    isutf8, isinternal = IsUTF8String(s)
    if not isutf8:
        try:
            return unicode(s, 'cp1250', 'ignore').encode('utf-8', amode)
        except:
            return CP1250_To_UTF8(s, amode)
    try:
        return s.encode('utf-8', amode)
    except:
        return unicode(s, 'utf-8', 'ignore').encode('utf-8', amode)


d_CP1250_To_UTF8 = {
    chr(0xb9): chr(0xc4) + chr(0x85),    # a
    chr(0xe6): chr(0xc4) + chr(0x87),    # c
    chr(0xea): chr(0xc4) + chr(0x99),    # e
    chr(0xb3): chr(0xc5) + chr(0x82),    # l
    chr(0xf1): chr(0xc5) + chr(0x84),    # n
    chr(0xf3): chr(0xc3) + chr(0xb3),    # o
    chr(0x9c): chr(0xc5) + chr(0x9b),    # s
    chr(0x9f): chr(0xc5) + chr(0xba),    # x
    chr(0xbf): chr(0xc5) + chr(0xbc),    # z
    chr(0xa5): chr(0xc4) + chr(0x84),    # A
    chr(0xc6): chr(0xc4) + chr(0x86),    # C
    chr(0xca): chr(0xc4) + chr(0x98),    # E
    chr(0xa3): chr(0xc5) + chr(0x81),    # L
    chr(0xd1): chr(0xc5) + chr(0x83),    # N
    chr(0xd3): chr(0xc3) + chr(0x93),    # O
    chr(0x8c): chr(0xc5) + chr(0x9a),    # S
    chr(0x8f): chr(0xc5) + chr(0xb9),    # X
    chr(0xaf): chr(0xc5) + chr(0xbb),    # Z
    chr(0x96): '',    # Start Of Guarded Area
}

spatt_CP1250_To_UTF8=\
   '(?<!%s)%s|'%(chr(0xc5),chr(0xb9),)+\
   '%s|'%(chr(0xe6))+\
   '%s|'%(chr(0xea))+\
   '(?<!%s)%s|'%(chr(0xc3),chr(0xb3),)+\
   '%s|'%(chr(0xf1))+\
   '%s|'%(chr(0xf3))+\
   '%s|'%(chr(0x9c))+\
   '%s|'%(chr(0x9f))+\
   '%s|'%(chr(0xbf))+\
   '%s|'%(chr(0xa5))+\
   '%s|'%(chr(0xc6))+\
   '%s|'%(chr(0xca))+\
   '%s|'%(chr(0xa3))+\
   '%s|'%(chr(0xd1))+\
   '%s|'%(chr(0xd3))+\
   '%s|'%(chr(0x8c))+\
   '%s|'%(chr(0x8f))+\
   '%s|'%(chr(0xaf))+\
   '%s'%(chr(0x96))
patt_CP1250_To_UTF8 = re.compile(spatt_CP1250_To_UTF8, re.M + re.S)


def Char2UTF(m):
    ret = d_CP1250_To_UTF8.get(m.group(0), '')
    return ret


def CP1250_To_UTF8(s, amode='replace'):
    if not s:
        return ''.encode('utf-8', amode)
    if not isinstance(s, types.StringTypes):
        s = str(s)
    atext = patt_CP1250_To_UTF8.sub(Char2UTF, s)
    return atext


d_UTF8_To_CP1250 = {
    chr(0xc4) + chr(0x85): chr(0xb9),    # a
    chr(0xc4) + chr(0x87): chr(0xe6),    # c
    chr(0xc4) + chr(0x99): chr(0xea),    # e
    chr(0xc5) + chr(0x82): chr(0xb3),    # l
    chr(0xc5) + chr(0x84): chr(0xf1),    # n
    chr(0xc3) + chr(0xb3): chr(0xf3),    # o
    chr(0xc5) + chr(0x9b): chr(0x9c),    # s
    chr(0xc5) + chr(0xba): chr(0x9f),    # x
    chr(0xc5) + chr(0xbc): chr(0xbf),    # z
    chr(0xc4) + chr(0x84): chr(0xa5),    # A
    chr(0xc4) + chr(0x86): chr(0xc6),    # C
    chr(0xc4) + chr(0x98): chr(0xca),    # E
    chr(0xc5) + chr(0x81): chr(0xa3),    # L
    chr(0xc5) + chr(0x83): chr(0xd1),    # N
    chr(0xc3) + chr(0x93): chr(0xd3),    # O
    chr(0xc5) + chr(0x9a): chr(0x8c),    # S
    chr(0xc5) + chr(0xb9): chr(0x8f),    # X
    chr(0xc5) + chr(0xbb): chr(0xaf),    # Z
}


def UTF8_To_CP1250_Replace(s, amode='replace'):
    for k, v in d_UTF8_To_CP1250.items():
        s = s.replace(k, v)
    return s


def ASCII_CP1250_To_UTF8(s, amode='xmlcharrefreplace'):
    if s is None:
        return ''.encode('utf-8', amode)
    return unicode(s, 'cp1250', 'ignore').encode('utf-8', amode)


def CP1250_To_ASCII_Default(s, encoding='cp1250'):
    import unicodedata
    if not isinstance(s, unicode):
        s = unicode(s, encoding)
    s = s.replace(u'ł', u'l')
    s = s.replace(u'Ł', u'L')
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')


def UTF8_CleanConsole(s, amode='replace'):
    if type(s) == type(u''):
        return s.encode('cp852', amode)
    return CP1250_To_UTF8(s)


patt1_UTF8_To_ASCII = re.compile(r'(\&\#\d+\;)', re.M + re.S + re.U)
patt2_UTF8_To_ASCII = re.compile(r'\&\#(\d+)\;', re.M + re.S + re.U)


def UTF8_To_ASCII(s):
    import unidecode
    s = s.replace(u'ł', u'l')
    s = s.replace(u'Ł', u'L')
    l = patt1_UTF8_To_ASCII.split(s)
    l2 = []
    for s2 in l:
        m = patt2_UTF8_To_ASCII.match(s2)
        if m:
            l2.append(unidecode.unidecode(unichr(int(m.group(1)))).encode('ASCII', 'ignore'))
        elif s2:
            if type(s2) == type(''):
                l2.append(unidecode.unidecode(unicode(s2, 'utf-8')).encode('ASCII', 'ignore'))
            else:
                l2.append(unidecode.unidecode(s2).encode('ASCII', 'ignore'))
    return ''.join(l2)


def URI2UTF8(s):
    return s.encode('latin-1').decode('utf-8')


_slugify_strip_re = re.compile(r'[^\w\s\-\(\)\,\.\{\}\[\]]', re.M + re.S + re.U)
_slugify_hyphenate_re = re.compile(r'[\-\s]+', re.M + re.S + re.U)


def UTF8_slugify(value, alower=0, maxlen=210):
    if type(value) == type(''):
        value = unicode(value, 'utf-8')
    #if type(value)!=type(unicode):
    #value=CP1250_To_UTF8(value)
    value = UTF8_To_ASCII(value)
    value = _slugify_strip_re.sub('-', value).strip()
    if alower:
        value = value.lower()
    value = _slugify_hyphenate_re.sub('_', value)[:maxlen]
    return value


_filename_ascii_strip_re = re.compile('[^A-Za-z0-9_\\.\\-\\(\\)\\{\\}\\[\\]]')
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')


def Secure_Filename(filename, alower=0, maxlen=210, encoding='utf-8'):
    if not isinstance(filename, unicode):
        filename = unicode(filename, encoding)
    ofilename = filename
    filename = CP1250_To_ASCII_Default(filename, 'utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(filename.split()))).strip('._')
    if filename and filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename
    if alower:
        filename = filename.lower()
    filename = filename[:maxlen]
    return ofilename.lower() != filename.lower(), filename


def IterableUTF2CP1250(o):
    if type(o) == type({}):
        ret = {}
        for k, v in o.items():
            ret[UTF8_To_CP1250(k)] = IterableUTF2CP1250(v)
    elif type(o) == type([]):
        ret = []
        for v in o:
            ret.append(IterableUTF2CP1250(v))
    elif isinstance(o, types.StringTypes):
        ret = UTF8_To_CP1250(o)
    else:
        ret = o
    return ret


def IterableCP1250ToUTF(o):
    if type(o) == type({}):
        ret = {}
        for k, v in o.items():
            ret[CP1250_To_UTF8(k)] = IterableCP1250ToUTF(v)
    elif type(o) == type([]):
        ret = []
        for v in o:
            ret.append(IterableCP1250ToUTF(v))
    elif isinstance(o, types.StringTypes):
        ret = CP1250_To_UTF8(o)
    else:
        ret = o
    return ret


def JSONLoad(afilepath, aconvert=1):
    fin = OpenText(afilepath)
    try:
        dd = json.load(fin)
    finally:
        fin.close()
    if aconvert:
        dd = IterableUTF2CP1250(dd)
    return dd


def str2bool(s):
    if isinstance(s, types.StringTypes):
        if s.lower() in ['true', '1', 'on', 'yes', 'prawda', 'tak', 't', 'y']:
            return 1
    try:
        i = int(s)
        if i > 0:
            return 1
    except:
        return 0
    return 0


ZERO_DATE_T = (0, 0, 0, 0)
ZERO_DATE_Z = (0, 0, 0)
ZERO_DATE_TZ = ZERO_DATE_T + ZERO_DATE_Z
ZERO_DATE_T_L = [0, 0, 0, 0]
ZERO_DATE_Z_L = [0, 0, 0]
ZERO_DATE_TZ_L = ZERO_DATE_T_L + ZERO_DATE_Z_L


def IsLeapYear(year):
    if year % 4 != 0:
        return 0
    elif year % 100 != 0:
        return 1
    elif year % 400 == 0:
        return 1
    else:
        return 0


def DaysInMonth(year, month):
    monthlist = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2:
        if IsLeapYear(year):
            return 29
        else:
            return 28
    return monthlist[month - 1]


def normalizeDate(y, m, d, adumb=0):
    if d > 31:
        y, m, d = d, m, y
    if not y and not m and not d:
        y, m, d = 1900, 1, 1
    if y < 0:
        y = 1900
    if m <= 0:
        m = 1
    if d <= 0:
        d = 1
    if y < 30:
        y = y + 2000
    elif y >= 30 and y < 100:
        y = y + 1900
    elif y < 1900:
        y = 1900
    if m < 1 or m > 12:
        m = 1
    if d < 1 or d > 31:
        d = 1
    if adumb:
        while y >= 3000:
            y = y - 1000
        while y >= 2030:
            y = y - 100
    return y, m, d


def getStrAsDate(s):
    s = s.strip()
    patt = re.compile(r'(\d+)\D(\d+)\D(\d+)', re.I)
    m = patt.search(s)
    if m:
        y, m, d = normalizeDate(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        alastday = DaysInMonth(y, m)
        if d < 1 or d > alastday:
            return ZERO_DATE_Z
        return (y, m, d)
    return ZERO_DATE_Z


def getStrAsTime(s):
    s = s.strip()
    patt = re.compile(r'(\d+)\D(\d+)\D(\d+)', re.I)
    m = patt.search(s)
    if m:
        h, m, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (h, m, s, 0)
    return ZERO_DATE_T


patt_nums = re.compile('\d+')


def getStrAsTimeL(s):
    l = [int(x) for x in patt_nums.findall(s)]
    ret = ZERO_DATE_T_L
    i = len(l)
    if i == 2:
        ret = l + [0, 0]
    elif i == 3:
        ret = l + [0, ]
    elif i == 4:
        ret = l
    elif i > 4 and i <= 6:
        ret = l[3:] + [0, ]
    elif i >= 7:
        ret = l[3:7]
    return ret


def getStrAsDateTime(s):
    if type(s) in [type(()), type([])]:
        return s
    s = s.strip()
    ld = map(int, re.findall(r'(\d+)', s))
    if len(ld) == 3 and ':' in s:
        return (0, 0, 0) + getStrAsTime(s)
    if len(ld) >= 3:
        y, mt, d = normalizeDate(ld[0], ld[1], ld[2])
        alastday = DaysInMonth(y, mt)
        if d < 1 or d > alastday:
            return getStrAsDate(s) + (0, 0, 0, 0)
        h, mm, ss = 0, 0, 0
        if len(ld) >= 5:
            h, mm = ld[3], ld[4]
        if len(ld) >= 6:
            ss = ld[5]
        return (y, mt, d, h, mm, ss, 0)
    return getStrAsDate(s) + (0, 0, 0, 0)


def tdate(adate=None):
    if adate is None:
        x = time.localtime(time.time())
    else:
        x = time.localtime(adate)
    return (x[0], x[1], x[2])


def tdatetime(atime=None):
    if atime is None:
        x = time.localtime(time.time())
    else:
        x = time.localtime(atime)
    return (x[0], x[1], x[2], x[3], x[4], x[5], 0)


def tdatetime2fmtstr(value=None, noms=1, longfmt=1, adelimiter='-', asmart=0, atimedelimiter=':', apartdelimiter=' ', amsdelimiter='.'):
    if not value:
        value = tdatetime()
    if value == ():
        return ''
    if len(value) == 7:
        y, m, d, h, mm, s, ms = value
        if asmart and value[3:] == ZERO_DATE_T:
            return tdate2fmtstr((y, m, d), adelimiter, longfmt)
    if len(value) == 3:
        if asmart:
            return tdate2fmtstr(value, adelimiter, longfmt)
        y, m, d = value
        h, mm, s, ms = 0, 0, 0, 0
    if len(value) == 4:
        y, m, d = 1899, 12, 30
        h, mm, s, ms = value
    if h == 0 and mm == 0 and s == 0 and ms == 0:
        if longfmt:
            if noms:
                return '%04d%s%02d%s%02d' % (y, adelimiter, m, adelimiter, d)
            else:
                return '%04d%s%02d%s%02d' % (y, adelimiter, m, adelimiter, d)
        elif noms:
            return '%d%s%d%s%d' % (y, adelimiter, m, adelimiter, d)
        else:
            return '%d%s%d%s%d' % (y, adelimiter, m, adelimiter, d)
    else:
        if longfmt:
            if noms:
                return '%04d%s%02d%s%02d%s%02d%s%02d%s%02d' % (y, adelimiter, m, adelimiter, d, apartdelimiter, h, atimedelimiter, mm, atimedelimiter, s)
            else:
                return '%04d%s%02d%s%02d%s%02d%s%02d%s%02d%s%03d' % (y, adelimiter, m, adelimiter, d, apartdelimiter, h, atimedelimiter, mm, atimedelimiter, s, amsdelimiter, ms)
        elif noms:
            return '%d%s%d%s%d%s%d%s%d%s%d' % (y, adelimiter, m, adelimiter, d, apartdelimiter, h, atimedelimiter, mm, atimedelimiter, s)
        else:
            return '%d%s%d%s%d%s%d%s%d%s%d%s%d' % (y, adelimiter, m, adelimiter, d, apartdelimiter, h, atimedelimiter, mm, atimedelimiter, s, amsdelimiter, ms)


def tdate2fmtstr(value=None, delimiter='-', longfmt=1):
    if not value:
        value = tdatetime()
    if value == ():
        return ''
    if len(value) == 3:
        y, m, d = value
    else:
        y, m, d, _h, _mm, _s, _ms = value
    if longfmt:
        return '%04d%s%02d%s%02d' % (y, delimiter, m, delimiter, d)
    return '%d%s%d%s%d' % (y, delimiter, m, delimiter, d)


def GetDateTime(adt):
    adt = (adt - 25569.0) * 86400.0
    x = time.gmtime(adt)
    return (x[0], x[1], x[2], x[3], x[4], x[5], 0)


def GetLastWeekday(adate=None, aweekday=5):
    if adate is None:
        adate = datetime.datetime.now()
    adiff = datetime.timedelta(days=1)
    while adate.weekday() != aweekday:
        adate = adate - adiff
    return adate.year, adate.month, adate.day


def ISODateTime2SQLDateTime(value):
    value = value.replace('T', ' ')
    ipos = value.find('.')
    if ipos > 0:
        value = value[:ipos]
    return value


def getStrAsSQLDate(value):
    adt = ISODateTime2SQLDateTime(value)
    adt = getStrAsDate(adt)
    if adt == ZERO_DATE_Z:
        adt = None
    return tdate2fmtstr(adt)


def getStrAsInt(s, adefault=-1):
    try:
        ret = int(s)
    except:
        return adefault
    return ret


def getStrAsFloat(s, adefault=0.0):
    try:
        ret = float(s)
    except:
        return adefault
    return ret


def getStrAsDecimal(s, adefault=0.0):
    try:
        ret = decimal.Decimal(s)
    except:
        return decimal.Decimal(adefault)
    return ret


def getStrAsOID(s, adefault=''):
    s = s.lower()
    if PATT_OID.match(s):
        return s
    return adefault


def replaceIllegalCharsLev0Text(s):
    s = s.replace("'", '"')
    s = s.lower()
    lr = ["select", "drop", "--", "insert", "delete", "xp_", "truncate", "update", "#", "%", "<", ">"]
    for sr in lr:
        s = s.replace(sr, '')
    return s


patt1_EmptyString = re.compile(r'([\n\t ]+)', re.M + re.S + re.U)


def isEmptyString(s):
    s1 = patt1_EmptyString.sub('', s)
    if not s1:
        return True
    return False


def GetTimeToken():
    adt = time.time()
    h = hashlib.sha256()
    h.update(str(adt) + '_' + os.urandom(64))
    return adt, h.hexdigest()


def GetNumToken(alength=6):
    ret = str(random.randint(1, 9))
    while len(ret) < alength:
        ret += str(random.randint(0, 9))
    return ret


_password_chars = []
_password_chars.extend(range(ord('0'), ord('9') + 1))
_password_chars.extend(range(ord('a'), ord('z') + 1))
_password_chars.extend(range(ord('A'), ord('Z') + 1))


def GetRandomPassword(alen=10):
    while 1:
        res = []
        ws = 0
        for _i in range(alen):
            c = chr(random.choice(_password_chars))
            if c >= 'a' and c <= 'z':
                ws = ws | 1
            if c >= 'A' and c <= 'Z':
                ws = ws | 2
            if c >= '0' and c <= '9':
                ws = ws | 4
            res.append(c)
        if ws == 7:
            break
    return ''.join(res)


def GetReadablePassword():
    l1 = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'w', 'z']    #'q','v','x','y',
    l2 = ['a', 'e', 'i', 'o', 'u', 'y']
    ret = ''
    for _i in range(3):
        ret = ret + random.choice(l1) + random.choice(l2) + random.choice(l1)
    return ret


def MakeIdentifier(avalue, adefaultprefix='a', alower=1, acapitalize=0, aproper=1):
    apatt = re.compile(' +')
    ret = apatt.sub('_', avalue)
    apatt = re.compile('[^A-Za-z_0-9]')
    ret = apatt.sub('', ret)
    if not ret:
        return ''
    c = ret[:1]
    if aproper and not ((c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z')):
        if not adefaultprefix:
            adefaultprefix = 'a'
        ret = adefaultprefix + ret
        c = ret[:1]
    if alower:
        ret = ret.lower()
    if acapitalize and c >= 'a' and c <= 'z':
        ret = c.upper() + ret[1:]
    return ret


class VarDict(dict):

    def __getitem__(self, key):
        if key not in self:
            raise AttributeError(key)
        v = dict.get(self, key, None)
        if type(v) == type({}):
            v = VarDict(v)
            self[key] = v
        return v

    def __getattr__(self, key):
        if key not in self:
            raise AttributeError(key)
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def getint(self, akey, adefault=0):
        v = self.get(akey, adefault)
        if type(v) != type(1):
            if v == '':
                v = adefault
            else:
                v = int(v)
        return v

    def getlist(self, akey, asplit=','):
        s = self.get(akey, '')
        ret = [x.strip() for x in s.split(asplit) if x]
        return ret

    def getlistint(self, akey, asplit=','):
        s = self.get(akey, '')
        ret = [int(x.strip()) for x in s.split(asplit) if x]
        return ret

    def getlistintpairs(self, akey, asplit=','):
        ret = self.getlistint(akey, asplit)
        return zip(ret[0::2], ret[1::2])


def ExtendClass(acls, *bclss):
    for bcls in bclss:
        for k, v in bcls.__dict__.items():
            if k in ['__module__', '__dict__', '__doc__', '__weakref__']:
                continue
            #print 'k:',k,type(k)
            setattr(acls, k, v)
            #acls.__dict__[k]=v


def DictFromModule(module, allowfunctions=0, allowclasses=0, allowmodules=0, printunknown=1):
    d = {}
    for k in dir(module):
        v = getattr(module, k)
        if isinstance(v, str):
            d[k] = v
        elif isinstance(v, basestring):
            d[k] = v
        elif isinstance(v, (int, long, float, complex)):
            d[k] = v
        elif isinstance(v, (tuple, list, dict, set)):
            d[k] = v
        elif isinstance(v, (types.TypeType, types.ClassType)):
            if allowclasses:
                d[k] = v
        elif isinstance(v, (types.FunctionType, )):
            if allowfunctions:
                d[k] = v
        elif isinstance(v, (types.NoneType, )):
            if not k.startswith('__') and not k.endswith('__'):
                d[k] = v
        elif isinstance(v, (types.ModuleType, )):
            if allowmodules:
                d[k] = v
        else:
            if printunknown:
                print 'Nieznany typ wartosci: ', k, type(v), 'w module:', module
    return d


MAX_ICOR_SYSTEM_TYPE = 255

#stale dla typow podstawowych
mt_Integer, mt_Double, mt_DateTime, mt_Boolean, mt_String = 0x20, 0x40, 0x60, 0x70, 0x90
mt_Bool, mt_Date, mt_Time = 0x70, 0x60, 0x60
mt_Memo = 0x91
mt_Any = -1


def GetLastExceptionInfo(asstring=0):
    import cStringIO
    import string
    f = cStringIO.StringIO()
    traceback.print_exc(file=f)
    ret = f.getvalue()
    f.close()
    if asstring:
        return ret
    return ret.split('\n')


def trace_string(tb=None, skip=0):
    return " <- ".join("%s() (%s:%s)" % (m, os.path.split(f)[1], n) for f, n, m, u in reversed(tb or traceback.extract_stack()[:-1 - skip]))


def exc_string():
    import win32api
    t, v, tb = sys.exc_info()
    if t is None:
        return ""
    try:
        v = str(v)
    except:
        v = ""
    return "[%d] {%s} [%s] %s(\"%s\") in %s" % (os.getpid(), win32api.GetUserName(), tdatetime2fmtstr(tdatetime()), t.__name__, v, trace_string(tb=traceback.extract_tb(tb)))


def dumpstack(aslist=0):
    l = traceback.format_stack()[:-2]
    if aslist:
        return l
    for s in l:
        print s[:-1]


def GetUUID(aprefix='', asufix=''):
    return aprefix + uuid.uuid4().hex + asufix


def JSONEncoder_newdefault(kind=['uuid', 'datetime', 'date', 'time', 'decimalasfloat', 'decimal']):
    '''
   JSON Encoder newdefault is a wrapper capable of encoding several kinds
   Use it anywhere on your code to make the full system to work with this defaults:
      JSONEncoder_newdefault()  # for everything
      JSONEncoder_newdefault(['decimal'])  # only for Decimal
   '''
    JSONEncoder_olddefault = json.JSONEncoder.default

    def JSONEncoder_wrapped(self, o):
        '''
      json.JSONEncoder.default = JSONEncoder_newdefault
      '''
        if ('decimalasfloat' in kind) and isinstance(o, decimal.Decimal):
            return float(o)
        if ('decimal' in kind) and isinstance(o, decimal.Decimal):
            return str(o)
        if ('datetime' in kind) and isinstance(o, datetime.datetime):
            return str(o)
        if ('date' in kind) and isinstance(o, datetime.date):
            return str(o)
        if ('time' in kind) and isinstance(o, time.struct_time):
            return datetime.datetime.fromtimestamp(time.mktime(o))
        if ('uuid' in kind) and isinstance(o, uuid.UUID):
            return str(o)
        return JSONEncoder_olddefault(self, o)

    json.JSONEncoder.default = JSONEncoder_wrapped


JSONEncoder_newdefault()


def SafeSplit(s, sc=','):
    l = filter(lambda x: len(x), map(lambda x: x.strip(), s.split(sc)))
    return l


def SafeSplitInt(s, sc=','):
    l = map(int, SafeSplit(s, sc))
    return l


def TextReplaceByMarkup(stext, dd, sm1='{{', sm2='}}'):
    patt = re.compile(re.escape(sm1) + '.*?' + re.escape(sm2), re.M + re.S)
    l = patt.findall(stext)
    for sp in l:
        sk = sp[len(sm1):-len(sm2)]
        sv = dd.get(sk, '')
        if not isinstance(sv, basestring):
            sv = ''
        stext = stext.replace(sp, sv)
    return stext
