# -*- coding: utf-8 -*-
import sys
import struct
import string
import os
import time
import thread
import mmap
import cStringIO
import hashlib

import CLASSES_Library_ICORBase_Interface_FTHRQueue as FTHRQueue

HEADER_FORMAT = '4s4siiiiiiiiidB'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
HEADER_GAP_SIZE = 252

REC_FORMAT = '=iiiiiiidiBBB'
REC_SIZE = struct.calcsize(REC_FORMAT)

mt_Integer, mt_Double, mt_DateTime, mt_Boolean, mt_String = 0x20, 0x40, 0x60, 0x70, 0x90
mt_Bool, mt_Date, mt_Time = 0x70, 0x60, 0x60
mt_Memo = 0x91


def PasReal2Double(six):
    Q = 1.0 / 256.0
    A = map(ord, six)
    if A[0] == 0:
        return 0.0
    S = 1.0 + 2.0 * ((((A[1] * Q + A[2]) * Q + A[3]) * Q + A[4]) * Q + (A[5] & 0x7F)) * Q
    if A[5] > 127:
        S = -S
    P = A[0] - 129
    S1 = 1.0
    for J in range(abs(P)):
        S1 = 2.0 * S1
    if P < 0:
        S1 = 1.0 / S1
    return S * S1


ZERO_DATE_T = (0, 0, 0, 0)
ZERO_DATE_Z = (0, 0, 0)
ZERO_DATE_TZ = ZERO_DATE_T + ZERO_DATE_Z


def GetDateTime(bdt):
    #   adt=PasReal2Double(adt)
    adt = (bdt - 25569.0) * 86400.0
    try:
        adt = time.gmtime(adt)
    except:
        adt = time.gmtime(0)
    return adt


def tdatetime2fmtstr(value, adelimiter='-', atimedelimiter=':', apartdelimiter=' '):
    if len(value) == 7:
        y, m, d, h, mm, s, ms = value
    else:
        y, m, d, h, mm, s, v1, v2, v3 = value
    return '%04d%s%02d%s%02d%s%02d%s%02d%s%02d' % (y, adelimiter, m, adelimiter, d, apartdelimiter, h, atimedelimiter, mm, atimedelimiter, s)


def CP1250_To_UTF8(s, amode='xmlcharrefreplace'):
    return unicode(s, 'cp1250', 'ignore').encode('utf-8', amode)


def str2PGImport(s, aquote=0):
    s = s.replace('\\', r'\\')
    s = s.replace('\b', r'\b')
    s = s.replace('\f', r'\f')
    s = s.replace('\n', r'\n')
    s = s.replace('\r', r'\r')
    s = s.replace('\t', r'\t')
    s = s.replace('\0', '')
    if aquote:
        s = s.replace("'", r"\\'")
    return s


def GetAsOneLineString(data):
    data = string.replace(data, "&", "&amp;")
    data = string.replace(data, "\\", "&bslash;")
    data = string.replace(data, "\"", "&quot;")    #"
    data = string.replace(data, chr(9), "&#9;")
    data = string.replace(data, chr(10), "&#10;")
    data = string.replace(data, chr(13), "&#13;")
    return data


def GetOneLineStringAsString(data):

    def dorepl(amatch):
        s = amatch.group(amatch.lastindex)
        if s == 'amp':
            return '&'
        elif s == 'quot':
            return '"'
        elif s == 'bslash':
            return '\\'
        i = int(s)
        if i in [9, 10, 13]:
            return chr(i)
        return '&#' + s + ';'

    data = re.sub('\&\#(\d+)\;|\&(amp)\;|\&(bslash)\;|\&(quot)\;', dorepl, data)
    return data


def LogException(s='', fname='', amode='a+', aconsole=1):
    import traceback
    try:
        f = open(fname, amode)
        if aconsole:
            traceback.print_exc()
        f.write(s + ': Exception!\n')
        traceback.print_exc(file=f)
        f.close()
    except:
        traceback.print_exc()


class MFDFile:

    def __init__(self, afname, asort=1, anodeleted=1, arecordsonly=1):
        self.FileName = afname
        self._Header = None
        self._Data = None
        self._Records = {}
        self._datasort = asort
        self._nodeleted = anodeleted
        self.recordsonly = arecordsonly

    def __getattr__(self, name):
        if name == 'Header':
            if self._Header is None:
                self.ReadHeader()
            return self._Header
        if name == 'Data':
            if self._Data is None:
                self.ReadData()
            return self._Data

    def ReadHeader(self):
        fin = open(self.FileName, 'rb')
        try:
            aheader = fin.read(HEADER_SIZE)
        finally:
            fin.close()
        self._Header, self.Recogn, self.Version, self.RecordCount, self.DeletedCount, self.SizeOfFile, self.Level, self.PropertiesOffset, self.DeletedOffset, self.DefaultTypeID, self.OwnerClassID, self.LastBackup, self.DefaultTypeModifier = struct.unpack(HEADER_FORMAT, aheader)

    def ReadData(self, fout=None):
        if self.Header != 'MARS' or self.Recogn != 'MODB':
            print '*** Unknown file header!!! ***'
            return
        self._Data = []
        self.RecordsDeleted = 0
        self.RecordsZero = 0
        self.RecSig = 0

        if fout:
            fout.write('DATA=[\n')
        if 1:
            f = open(self.FileName, 'rb')
            fin = cStringIO.StringIO(f.read())
        else:
            f = open(self.FileName, 'r+b')
            fin = mmap.mmap(f.fileno(), 0)
        try:
            fin.seek(0, 2)
            afilesize = fin.tell()
            aposition = HEADER_SIZE + HEADER_GAP_SIZE
            while aposition < (afilesize - 4):
                fin.seek(aposition)
                aoffset = struct.unpack('i', fin.read(4))[0]
                if aoffset == (aposition - 4):
                    fin.seek(aposition - 4)
                    self.RecSig = self.RecSig + 1
                    srec = fin.read(REC_SIZE)
                    akeyid, aoffset, avaluesize, atypeid, arecsize, anextdeletedoffset, apropertyoffset, alastmodification, aownerid, alevel, atypemodifier, aisdeleted = struct.unpack(REC_FORMAT, srec)
                    #print akeyid,aoffset,avaluesize,atypeid,arecsize,anextdeletedoffset,apropertyoffset,alastmodification,alevel,aownerid,atypemodifier,aisdeleted
                    if avaluesize > 0:
                        isbad = 0
                        try:
                            fin.seek(aoffset + arecsize)
                        except:
                            isbad = 1
                        if (akeyid < 0) or (akeyid > 400000000):
                            isbad = 1
                        if avaluesize > 160000:
                            isbad = 1
                        if isbad:
                            self.RecordsZero = self.RecordsZero + 1
                            aposition = aposition + 1
                            continue
                        avalue = fin.read(avaluesize)
                        #print akeyid,aoffset,avaluesize,arecsize,aisdeleted,avalue
                        aownerid = (akeyid & 0xff000000) >> 24
                        if aisdeleted:
                            self.RecordsDeleted = self.RecordsDeleted + 1
                        try:
                            blastmodification = GetDateTime(alastmodification)
                            alastmodification = blastmodification
                        except:
                            alastmodification = ZERO_DATE_TZ
                        arecord = (akeyid, aownerid, alastmodification, aisdeleted, avalue)
                        if not (self._nodeleted and aisdeleted):
                            if not self.recordsonly:
                                self._Data.append(arecord)
                            rv = self._Records.get(akeyid, None)
                            if rv is None:
                                self._Records[akeyid] = arecord
                            else:
                                if alastmodification > rv[2]:
                                    self._Records[akeyid] = arecord
                        if fout:
                            svalue, cvalue, adt, cadt = self.GetRecValues(arecord, aasutf=0)
                            fout.write('[%d,%d,"%s",%d,"%s"],\n' % (akeyid, aownerid, cadt, aisdeleted, GetAsOneLineString(cvalue)))
                            if 0:
                                #fout.write('%d,%d,%s,%d,%s\n'%(akeyid,aownerid,str(GetDateTime(alastmodification)),aisdeleted,avalue.replace(chr(10),' ').replace(chr(13),'')[:100]))
                                if self.DefaultTypeID == mt_DateTime:
                                    avalue = struct.unpack('d', avalue)[0]
                                    avalue = str(GetDateTime(avalue))
                                else:
                                    avalue.replace(chr(10), ' ').replace(chr(13), '')[:100]
                                fout.write('%d | %d | %s | %d | %s\n' % (akeyid, aownerid, str(alastmodification), aisdeleted, avalue))
                            if 0:
                                aname, aext = os.path.splitext(self.FileName)
                                fout2 = open('outid/%s_%06d %02d-%02d-%02d %02d-%02d-%02d.txt' % (aname, akeyid, alastmodification[0], alastmodification[1], alastmodification[2], alastmodification[3], alastmodification[4], alastmodification[5]), 'w')
                                fout2.write(avalue)
                                fout2.close()
                                fout2 = open('outdt/%s %02d-%02d-%02d %02d-%02d-%02d %06d.txt' % (aname, alastmodification[0], alastmodification[1], alastmodification[2], alastmodification[3], alastmodification[4], alastmodification[5], akeyid), 'w')
                                fout2.write(avalue)
                                fout2.close()
                    else:
                        self.RecordsZero = self.RecordsZero + 1
                    if 0:
                        aposition = aoffset + REC_SIZE + avaluesize
                    else:
                        aposition = aoffset + REC_SIZE    #aposition=aoffset+arecsize+avaluesize
                else:
                    aposition = aposition + 1
        finally:
            fin.close()
            f.close()
        if fout:
            fout.write(']\n')
        if self._datasort:
            self._Data.sort()

    def Write(self, fout, avalue, asbyte=0, asstring=0):
        if asbyte:
            fout.write(struct.pack('b', avalue))
            return
        if asstring:
            fout.write(struct.pack('i', len(avalue)))
            fout.write(avalue)
            return
        if type(avalue) == type(1):
            fout.write(struct.pack('i', avalue))
        elif type(avalue) == type(0.0):
            fout.write(struct.pack('d', avalue))
        elif type(avalue) == type(''):
            fout.write(avalue)
        elif type(avalue) in (time.struct_time, type(())):
            fout.write(tdatetime2fmtstr(avalue))
        else:
            print 'nieznany typ dla wartosci:', avalue, type(avalue)

    def GetRecValues(self, arecord, aasutf=1):
        avalue = arecord[4]
        if self.DefaultTypeID == mt_Integer:
            try:
                svalue = struct.unpack('i', avalue)[0]
            except:
                svalue = 0
                print 'BAD INT:', len(avalue), avalue[:500]
            cvalue = str(svalue)
        elif self.DefaultTypeID == mt_Double:
            svalue = struct.unpack('d', avalue)[0]
            cvalue = str(svalue)
        elif self.DefaultTypeID == mt_DateTime:
            x = GetDateTime(struct.unpack('d', avalue)[0])    # Except - avalue - length==0
            if x[0] == 0:
                svalue = '1900-01-01'
                cvalue = '1900-01-01 00:00:00'
            else:
                svalue = tdatetime2fmtstr((x[0], x[1], x[2], x[3], x[4], x[5], 0))
                cvalue = svalue
        elif self.DefaultTypeID == mt_Boolean:
            try:
                svalue = struct.unpack('b', avalue)[0]
            except:
                svalue = 0
                print 'BAD BOOL:', len(avalue), avalue[:500]
            if svalue:
                svalue = True
                cvalue = 't'
            else:
                svalue = False
                cvalue = 'f'
        else:
            if aasutf:
                svalue = CP1250_To_UTF8(avalue)
            else:
                svalue = avalue
            cvalue = svalue
        #print '  ',arecord[0],arecord[3],svalue,type(svalue)
        if arecord[2][0] == 0:
            adt = '1900-01-01'
            cadt = '1900-01-01 00:00:00'
        else:
            adt = tdatetime2fmtstr(arecord[2])
            cadt = adt
        return svalue, cvalue, adt, cadt

    def Backup(self):
        fout = open(self.FileName + '.dmp', 'wb')
        try:
            self.Write(fout, self.Header)
            self.Write(fout, self.DefaultTypeID)
            self.Write(fout, self.DefaultTypeModifier)
            for akeyid, aownerid, alastmodification, aisdeleted, avalue in self.Data:
                self.Write(fout, akeyid)
                self.Write(fout, aownerid, asbyte=1)
                self.Write(fout, alastmodification)
                self.Write(fout, avalue, asstring=1)
        finally:
            fout.close()

    def ReadDataDMP(self):
        self._DMPData = {}
        print 'read: %s' % self.FileName
        fin = open(self.FileName, 'rb')
        try:
            dmpHEADER_FORMAT = '4sii'
            dmpHEADER_SIZE = struct.calcsize(dmpHEADER_FORMAT)
            dmpREC_FORMAT = '=iB19si'
            dmpREC_SIZE = struct.calcsize(dmpREC_FORMAT)
            aheader = fin.read(dmpHEADER_SIZE)
            self._Header, self.DefaultTypeID, self.DefaultTypeModifier = struct.unpack(dmpHEADER_FORMAT, aheader)
            fin.seek(0, 2)
            afilesize = fin.tell()
            aposition = dmpHEADER_SIZE
            fin.seek(aposition)
            while aposition < (afilesize - 4):    # and aposition<1000:
                arec = fin.read(dmpREC_SIZE)
                aoid, aownerid, alastmodification, alen = struct.unpack(dmpREC_FORMAT, arec)
                #print self.FileName,aoid,aownerid,alastmodification,alen
                avalue = fin.read(alen)
                aposition = aposition + dmpREC_SIZE + alen
                self._DMPData[aoid] = avalue
        finally:
            fin.close()

    def CompareDMP(self, amdffile, adirout):
        print 'compare: %s' % self.FileName
        fname = os.path.split(self.FileName)[1]
        lk = self._DMPData.keys()
        lk.sort()
        o1cnt, o2cnt = 0, 0
        fout = None
        for aoid in lk:
            if not amdffile._DMPData.has_key(aoid):
                if not fout:
                    fout = open(adirout + '/' + fname, 'w')
                fout.write('!!!-N,%d, %s\n' % (aoid, self._DMPData[aoid]))
                o1cnt = o1cnt + 1
                continue
            if self._DMPData[aoid] != amdffile._DMPData[aoid]:
                if not fout:
                    fout = open(adirout + '/' + fname, 'w')
                fout.write('!!!-D,%d, %s\n' % (aoid, self._DMPData[aoid]))
                o2cnt = o2cnt + 1
        if fout:
            fout.close()
        ret = ''
        if (o1cnt > 0) or (o2cnt > 0):
            ret = '%s - n: %d, d: %d' % (self.FileName, o1cnt, o2cnt)
        return ret

    def DumpHeader(self):
        l = []
        l.append('*** %s ***' % self.FileName)
        l.append('Header: %s' % self.Header)
        l.append('Recogn: %s' % self.Recogn)
        l.append('Version: %s' % self.Version)
        l.append('RecordCount: %d' % self.RecordCount)
        l.append('DeletedCount: %d' % self.DeletedCount)
        l.append('SizeOfFile: %d' % self.SizeOfFile)
        l.append('Level: %d' % self.Level)
        l.append('PropertiesOffset: %d' % self.PropertiesOffset)
        l.append('DefaultTypeID: %d' % self.DefaultTypeID)
        l.append('DefaultTypeModifier: %d' % self.DefaultTypeModifier)
        #l.append('LastBackup: %s'%str(GetDateTime(self.LastBackup)))
        l.append('DeletedOffset: %d' % self.DeletedOffset)
        l.append('RecordCount+DeletedCount: %d' % (self.RecordCount + self.DeletedCount, ))
        l.append('Rozpoznano rekordow: %d' % self.RecSig)
        l.append('Odczytano rekordow: %d' % len(self.Data))
        l.append('RecordsZero: %d' % self.RecordsZero)
        l.append('Skasowanych rekordow: %d' % self.RecordsDeleted)
        areclost = self.RecordCount + self.DeletedCount - len(self.Data) - self.RecordsZero
        l.append('Utracono rekordow: %d' % areclost)
        s = '\n'.join(l)
        print s

    def DumpData(self, fout=None):
        lkeyid = -1
        lv = []
        for akeyid, aownerid, alastmodification, aisdeleted, avalue in self.Data:
            if aisdeleted:
                s = '#'
            elif lkeyid == akeyid:
                s = '*'
            else:
                s = ' '
            if self.DefaultTypeID == mt_Integer:
                svalue = struct.unpack('i', avalue)[0]
            elif self.DefaultTypeID == mt_Double:
                svalue = struct.unpack('d', avalue)[0]
            elif self.DefaultTypeID == mt_DateTime:
                svalue = struct.unpack('d', avalue)[0]
            elif self.DefaultTypeID == mt_Boolean:
                svalue = struct.unpack('b', avalue)[0]
            else:
                svalue = avalue
            if fout:
                if avalue != ',' * len(avalue):
                    lv.append([akeyid, avalue])
            else:
                print s, akeyid, len(avalue), svalue
            lkeyid = akeyid
        if fout:
            lv.reverse()
            d = {}
            for akeyid, avalue in lv:
                if not d.has_key(akeyid):
                    #fout.write('%08d,%d,%06d,%s,%d,"%s"\n'%(akeyid,aisdeleted,aownerid,alastmodification,avalue))
                    fout.write('[%d,"%s"],\n' % (akeyid, avalue))
                    d[akeyid] = 1


def ProcessSingleFile(afname, queue):
    fout = open(afname + '.dat', 'w')
    amfdfile = MFDFile(afname)
    fout2 = open(afname + '.txt', 'w')
    amfdfile.ReadData(fout2)
    fout2.close()
    amfdfile.DumpHeader()
    amfdfile.DumpData(fout)
    fout.close()
    amfdfile.Backup()
    s = '%16s type: %4d reccnt: %7d, recread: %7d, reclost: %7d, reczero: %7d' % (afname, amfdfile.DefaultTypeID, amfdfile.RecordCount, len(amfdfile.Data), amfdfile.RecordCount - len(amfdfile.Data) - amfdfile.RecordsZero, amfdfile.RecordsZero)
    print s
    queue.STATUS.append(s)
    del amfdfile


def ProcessSingleFileDMP(afnameold, afnamenew, adirout, queue):
    amfdfileold = MFDFile(afnameold)
    amfdfileold.ReadDataDMP()
    amfdfilenew = MFDFile(afnamenew)
    amfdfilenew.ReadDataDMP()
    s = amfdfilenew.CompareDMP(amfdfileold, adirout)
    #s='%16s type: %4d reccnt: %7d, recread: %7d, reclost: %7d, reczero: %7d'%(afname,amfdfile.DefaultTypeID,amfdfile.RecordCount,len(amfdfile.Data),amfdfile.RecordCount-len(amfdfile.Data)-amfdfile.RecordsZero,amfdfile.RecordsZero)
    #print s
    if s:
        queue.STATUS.append(s)
    del amfdfileold
    del amfdfilenew


def ProcessFile(queue, d, files):
    if d == '.':
        d = ''
    else:
        d = d + '\\'
    for afname in files:
        if os.path.isdir(d + afname):
            continue
        if afname[-4:] != '.mfd':
            continue
        print 'append:', afname
        queue.append(ProcessSingleFile, (d + afname, queue))


def ProcessFileDMP(adirold, adirnew, adirout, queue):
    files = os.listdir(adirnew)
    for afname in files:
        if os.path.isdir(adirnew + '/' + afname):
            continue
        if afname[-4:] != '.dmp':
            continue
        if not os.path.exists(adirold + '/' + afname):
            queue.STATUS.append('new file: %s' % afname)
            continue
        print 'append:', afname
        queue.append(ProcessSingleFileDMP, (adirold + '/' + afname, adirnew + '/' + afname, adirout, queue))


def ImportFile(aimportdir, afilepath, aICORDB, afid, acopydir, asqldir, queue):
    adtstart = time.clock()
    try:
        amfdfile = MFDFile(afilepath, asort=0)
        amfdfile.ReadHeader()
        #print afid,amfdfile.DefaultTypeID,amfdfile.DefaultTypeModifier
        adtstart1 = time.clock()
        amfdfile.ReadData()
        adtstart2 = time.clock()
        # dane dostepne
        if amfdfile._Records.keys():
            if asqldir:
                asql = aICORDB.struct.CreateField(afid, amfdfile.DefaultTypeID, amfdfile.DefaultTypeModifier, asqlonly=1)
                asqlpath = os.path.join(asqldir, afid + '.sql')
                fsql = open(asqlpath, 'w')
                fsql.write(asql)
                fsql.close()
            if acopydir:
                acopypath = os.path.join(acopydir, afid + '.txt')
                fcopy = open(acopypath, 'w')
                #aICORDB.dbimpex.ExportFieldData(int(afid),os.path.join(acopydir,afid+'.csv'))
            if afid == '4101':    # aClassName Field
                if asqldir:
                    asqlpath2 = os.path.join(asqldir, '_classes.sql')
                    fsql2 = open(asqlpath2, 'w')
                    asql = aICORDB.struct.DeleteSchemaTables()
                    fsql2.write(asql)
                    for akeyid, arecord in amfdfile._Records.items():
                        aisdeleted = arecord[3]
                        if aisdeleted:
                            continue
                        acid = arecord[0]
                        asql = aICORDB.struct.CreateClass(acid, asqlonly=1)
                        fsql2.write(asql)
                    fsql2.close()
            for akeyid, arecord in amfdfile._Records.items():
                aisdeleted = arecord[3]
                if aisdeleted:
                    continue
                try:
                    svalue, cvalue, adt, cadt = amfdfile.GetRecValues(arecord)
                except:
                    LogException('BAD VALUE - %d - (%d) : [%s] ' % (arecord[0], len(arecord[4]), arecord[4]), os.path.join(aimportdir, afid + '.log'))
                    continue
                if not acopydir:
                    aICORDB.struct.UpdateFieldValue(afid, arecord[0], arecord[1], adt, svalue)
                else:
                    fcopy.write('%d\t%d\t%s\t%s\n' % (arecord[0], arecord[1], cadt, str2PGImport(cvalue)))
            if acopydir:
                fcopy.close()
    except:
        LogException(afilepath, os.path.join(aimportdir, afid + '.log'))
    adtfinish = time.clock()
    #print '%s - %0.6f - %0.6f - %0.6f - %0.6f'%(afilepath,adtfinish-adtstart,adtstart1-adtstart,adtstart2-adtstart1,adtfinish-adtstart2)

def HistoryFile(aimportdir, afilepath, aICORDB, afid, acopydir, asqldir, queue):
    adtstart = time.clock()
    try:
        amfdfile = MFDFile(afilepath, asort=0, anodeleted=0, arecordsonly=0)
        amfdfile.ReadHeader()
        print 'DATA: %s'%(afid,)
        adtstart1 = time.clock()
        amfdfile.ReadData()
        adtstart2 = time.clock()
        print 'TIME: %s - %0.4f'%(afid,adtstart2-adtstart1)
        if amfdfile._Data:
            acopypath = os.path.join(acopydir, afid + '.txt')
            fcopy = open(acopypath, 'w')
            for arecord in amfdfile._Data:
                try:
                    svalue, cvalue, adt, cadt = amfdfile.GetRecValues(arecord)
                except:
                    LogException('BAD VALUE - %d - (%d) : [%s] ' % (arecord[0], len(arecord[4]), arecord[4]), os.path.join(aimportdir, afid + '.log'))
                    continue
                #arecord = (akeyid, aownerid, alastmodification, aisdeleted, avalue)
                astatus=''
                if '\0' in cvalue:
                    astatus='B0'
                vpg=str2PGImport(cvalue)
                h = hashlib.sha256()
                h.update(vpg)
                fcopy.write('%s\t%d\t%d\t%s\t%d\t%s\t%s\t%d\t%s\n' % (afid, arecord[0], arecord[1], cadt, arecord[3], astatus, vpg, len(vpg), h.hexdigest()))
            fcopy.close()
    except:
        LogException(afilepath, os.path.join(aimportdir, afid + '.log'))
    adtfinish = time.clock()
    #print '%s - %0.6f - %0.6f - %0.6f - %0.6f'%(afilepath,adtfinish-adtstart,adtstart1-adtstart,adtstart2-adtstart1,adtfinish-adtstart2)


def ImportDir(aICORDB, aimportdir, acopy=1, asql=1, ahistory=0):
    start = time.time()
    adatadir = os.path.join(aimportdir, 'MIDD')
    acopydir = ''
    if acopy:
        acopydir = os.path.join(aimportdir, 'COPY')
        if not os.path.exists(acopydir):
            os.makedirs(acopydir)
    asqldir = ''
    if asql:
        asqldir = os.path.join(aimportdir, 'COPYSQL')
        if not os.path.exists(asqldir):
            os.makedirs(asqldir)
    #S-6501
    #I-6502
    #F-6503
    #B-6504
    #D-6505
    #M-6506
    #C-6507
    queue = FTHRQueue.THRQueue(20)
    queue.STATUS = []
    for afilename in os.listdir(adatadir):
        afid, aext = os.path.splitext(afilename)
        afilepath = os.path.join(adatadir, afilename)
        if os.path.isdir(afilepath):
            continue
        if afilename[-4:] != '.mfd':
            continue
        if afid in ['9471','4147','9496',
            '6734', # HTTPLog - Cookie
            '6733', # HTTPLog - UserAgent
        ]:
            continue
        if ahistory:
            queue.append(HistoryFile, (aimportdir, afilepath, aICORDB, afid, acopydir, asqldir, queue))
        else:
            queue.append(ImportFile, (aimportdir, afilepath, aICORDB, afid, acopydir, asqldir, queue))
    queue.waittilfinished()
    finish = time.time()
    print 'Processed in: %s' % (str(finish - start), )


def LoadDBFile(aimportdir, aICORDB, afid, acopydir, asqldir, queue):
    print afid
    try:
        asqlpath = os.path.join(asqldir, afid + '.sql')
        if os.path.exists(asqlpath):
            aICORDB.ExecuteSQLFile(asqlpath)
        acopypath = os.path.join(acopydir, afid + '.txt')
        if os.path.exists(acopypath):
            print 'Import Table Data'
            #aICORDB.dbimpex.ImportTableData(afid,acopypath)
    except:
        LogException('ERROR in: ' + afid, os.path.join(aimportdir, afid + '.log'))

def LoadDBFileHistory(aimportdir, aICORDB, afid, acopydir, asqldir, atablename, queue):
    try:
        acopypath = os.path.join(acopydir, afid + '.txt')
        if os.path.exists(acopypath):
            print 'IMPORT: %s'%afid
            aICORDB.struct.LoadHistoryTableTemp(atablename, acopypath)
            os.rename(acopypath,acopypath+'.ok')
    except:
        LogException('ERROR in: ' + afid, os.path.join(aimportdir, afid + '.log'))

def LoadDBDir(aICORDB, aimportdir, aclasses=0, ahistory=0, atablename='', apoolsize=10):
    start = time.time()
    try:
        acopydir = os.path.join(aimportdir, 'COPY')
        asqldir = os.path.join(aimportdir, 'COPYSQL')
        if aclasses:
            asqlpath2 = os.path.join(asqldir, '_classes.sql')
            if os.path.exists(asqlpath2):
                print 'execute:', asqlpath2
                aICORDB.ExecuteSQLFile(asqlpath2)
            else:
                print '_classes.sql doesnt exists'
        queue = FTHRQueue.THRQueue(apoolsize)
        queue.STATUS = []
        for afilename in os.listdir(acopydir):
            afid, aext = os.path.splitext(afilename)
            afilepath = os.path.join(acopydir, afilename)
            if os.path.isdir(afilepath):
                continue
            if afilename[-4:] != '.txt':
                continue
            try:
                ifid = int(afid)
            except:
                ifid = -1
            if ifid >= 0:
                if ahistory:
                    queue.append(LoadDBFileHistory, (aimportdir, aICORDB, afid, acopydir, asqldir, atablename, queue))
                else:
                    queue.append(LoadDBFile, (aimportdir, aICORDB, afid, acopydir, asqldir, queue))
        queue.waittilfinished()
    except:
        LogException('ERROR in loaddir:' + aimportdir, os.path.join(aimportdir, 'loaddir.log'))
    finish = time.time()
    print 'Processed in: %s' % (str(finish - start), )


def GetFIDListByDir(bbasedir, bdir, bext):
    lfn = GetDirFilenameByExtension
    adatadir = os.path.join(bbasedir, bdir)
    for afilename in os.listdir(adatadir):
        afid, aext = os.path.splitext(afilename)
        afilepath = os.path.join(adatadir, afilename)
        if os.path.isdir(afilepath):
            continue
        if afilename[-4:] != bext:
            continue
        lfn.append(int(afid))
    return lfn


def CheckDir(aICORDB, aimportdir):
    lft = aICORDB.struct.GetFieldTablesList()
    print 'Field tables:', len(lft)
    lfn = GetFIDListByDir(aimportdir, 'MIDD', '.mfd')
    print 'Field files:', len(lfn)
    lfmove = []
    for afilename in lfn:
        if afilename in lft:
            print 'move %d.mfd ..' % (afilename, )
            lfmove.append(afilename)
    print 'Field to move:', len(lfmove)


def CheckFieldFiles(aICORDB, aimportdir):
    lft = aICORDB.struct.GetFieldIDList()
    print 'Field tables:', len(lft)
    lfn = GetFIDListByDir(aimportdir, 'MIDD', '.mfd')
    print 'Field files:', len(lfn)
    lfmove = []
    for afilename in lfn:
        if afilename not in lft:
            print 'move %d.mfd ..' % (afilename, )
            lfmove.append(afilename)
    print 'Field to move:', len(lfmove)


if __name__ == '__main__':

    if options.importdir or options.loaddir:    # $$TODO off
        import mfdimport
        import icordbmain
        aICORDB = icordbmain.ICORDBData()
        if options.importdir:
            print 'import dir:', options.importdir
            mfdimport.ImportDir(aICORDB, options.importdir)
        if options.loaddir:
            print 'load dir:', options.loaddir
            mfdimport.LoadDBDir(aICORDB, options.loaddir, aclasses=1, apoolsize=startutil.appconfig.PGMaxConnectionQueue)
        #mfdimport.CheckDir(aICORDB,options.importdir)
        #mfdimport.CheckFieldFiles(aICORDB,options.importdir)
        #aICORDB.CheckFieldTables()
    elif options.classrefresh:    # $$TODO off
        import icordbmain
        aICORDB = icordbmain.ICORDBData()
        aclasses = aICORDB.struct.GetRepositoryStruct()
        aclasses.RefreshObjects()

    if 1:
        adir = sys.argv[1]
        aout = sys.argv[2]

        queue = FTHRQueue.THRQueue(10)
        queue.STATUS = []
        start = time.time()
        os.path.walk(adir, ProcessFile, queue)
        queue.waittilfinished()
        finish = time.time()
        print 'Processed in:', finish - start
        fout = open('log_%s.txt' % aout, 'w')
        fout.write(string.join(queue.STATUS, '\n'))
        fout.close()

    if 0:
        adirold = sys.argv[1]
        adirnew = sys.argv[2]
        adirout = sys.argv[3]

        queue = FTHRQueue.THRQueue(10)
        queue.STATUS = []
        start = time.time()
        ProcessFileDMP(adirold, adirnew, adirout, queue)
        queue.waittilfinished()
        finish = time.time()
        print 'Processed in:', finish - start
        fout = open('log_dmp.txt', 'w')
        fout.write(string.join(queue.STATUS, '\n'))
        fout.close()
