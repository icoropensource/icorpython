# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class FieldRefIterator:

    def __init__(self, arefstr=''):
        self.oids = set()
        self.refs = []
        try:
            l1 = [int(x) for x in arefstr.split(':') if x != '']
            for i in range(0, len(l1), 2):
                self.refs.append([l1[i], l1[i + 1]])
                self.oids.add(l1[i])
        except:
            pass
            raise
        self.len = len(self.refs)
        self._Class = None
        self._CID = -1
        self.First()

    def __getattr__(self, name):
        apos = self.__dict__['position']
        alen = self.__dict__['len']
        if apos >= alen or apos < 0:
            return -1
        if name == 'OID':
            return self.refs[apos][0]
        elif name == 'CID':
            return self.refs[apos][1]
        return getattr(self, name)

    def __getitem__(self, key):
        if key >= 0 and key < self.len:
            return self.refs[key][0], self.refs[key][1]
        raise IndexError

    def __setitem__(self, key, value):
        if key >= 0 and key < self.len:
            self.refs[key][0] = value[0]
            self.refs[key][1] = value[1]

    def __len__(self):
        return self.len

    def __nonzero__(self):
        return self.position >= 0

    def __repr__(self):
        return self.AsString()

    def __str__(self):
        return self.AsString()

    def reverse(self):
        self.refs.reverse()

    def clear(self):
        self.refs = []
        self.len = 0
        self.First()

    def First(self):
        self.position = 0
        if self.position >= self.len:
            self.position = -1
        return self.position

    def Last(self):
        self.position = self.len - 1
        return self.position

    def Next(self):
        self.position = self.position + 1
        if self.position >= self.len:
            self.position = -1
        return self.position

    def Prev(self):
        if self.position >= 0:
            self.position = self.position - 1
        return self.position

    def SetByPosition(self, apos):
        if apos >= self.len or apos < 0:
            self.position = -1
        else:
            self.position = apos
        return self.position

    def ActualRef(self):
        return str(self.OID) + ':' + str(self.CID) + ':'

    def IsEmpty(self):
        return self.len == 0

    def InsertRef(self, pos, aoid, acid):
        if pos < 0:
            pos = 0
        elif pos >= self.len:
            return self.AddRef(aoid, acid)
        self.refs.insert(pos, [aoid, acid])
        self.len = len(self.refs)
        if self.position < 0:
            self.position = 0
        return pos

    def FindRef(self, aoid, acid):    # zwraca: (apos, afind) !!!
        lref = [aoid, acid]
        for i in range(len(self.refs)):
            if self.refs[i] == lref:
                return i, 1
        return -1, 0

    def AddRef(self, aoid, acid):
        self.refs.append([aoid, acid])
        self.len = len(self.refs)
        if self.position < 0:
            self.position = 0
        return self.len - 1

    def AddRefs(self, arefs):
        lpos = arefs.position
        arefs.First()
        while arefs.position >= 0:
            if not self.RefExists(arefs.OID, arefs.CID):
                self.AddRef(arefs.OID, arefs.CID)
            arefs.Next()
        arefs.position = lpos
        return -1

    def DelRef(self, aoid, acid=-1):
        aid = 0
        s = ''
        ret = 0
        while aid < self.len:
            if aoid == self.refs[aid][0]:
                if (acid < 0) or (self.refs[aid][1] == acid):
                    del self.refs[aid]
                    self.len = len(self.refs)
                    if self.position >= self.len:
                        self.position = self.position - 1
                    ret = 1
            aid = aid + 1
        return ret

    def DelRefsInRange(self, aidmin, aidmax, acid=-1):
        aid = 0
        s = ''
        ret = 0
        while aid < self.len:
            boid = self.refs[aid][0]
            if boid >= aidmin and boid < aidmax:
                if (acid < 0) or (self.refs[aid][1] == acid):
                    del self.refs[aid]
                    self.len = len(self.refs)
                    if self.position >= self.len:
                        self.position = self.position - 1
                    ret = 1
            aid = aid + 1
        return ret

    def DelRefByID(self, aid=-1):
        if aid < 0:
            aid = self.position
        if (aid < self.len) and (aid >= 0):
            del self.refs[aid]
            self.len = len(self.refs)
            if self.position >= self.len:
                self.position = self.position - 1
        return -1

    def RefExists(self, aoid, acid=-1):
        if acid < 0:
            for boid, bcid in self.refs:
                if aoid == boid:
                    return 1
        else:
            for boid, bcid in self.refs:
                if aoid == boid and acid == bcid:
                    return 1
        return 0

    def RefsExists(self, arefs):
        arefs.First()
        while arefs.position >= 0:
            if [arefs.OID, arefs.CID] in self.refs:
                #         if self.RefExists(arefs.OID,arefs.CID):
                return 1
            arefs.Next()
        return 0

    def RefsExistsAll(self, arefs):
        if type(arefs) == type([]):
            for aoid, acid in arefs:
                if not self.RefExists(aoid, acid):
                    return 0
        else:
            while arefs.position >= 0:
                if not self.RefExists(arefs.OID, arefs.CID):
                    return 0
                arefs.Next()
        return 1

    def AsString(self, i=0, j=-1):
        if j < 0 or j == sys.maxint:
            j = self.len
        s = ''
        while i < j:
            s = s + str(self.refs[i][0]) + ':' + str(self.refs[i][1]) + ':'
            i = i + 1
        return s

    def AsStringOID(self):
        aid = 0
        s = ''
        while aid < self.len:
            s = s + str(self.refs[aid][0]) + ':'
            aid = aid + 1
        return s

    def AsStringCID(self):
        aid = 0
        s = ''
        while aid < self.len:
            s = s + str(self.refs[aid][1]) + ':'
            aid = aid + 1
        return s

    def AsListOID(self):
        aid = 0
        l = []
        while aid < self.len:
            l.append(self.refs[aid][0])
            aid = aid + 1
        return l

    def AsListCID(self):
        aid = 0
        l = []
        while aid < self.len:
            l.append(self.refs[aid][1])
            aid = aid + 1
        return l


class ICORDBFieldItem(object):

    def __init__(self, aclass, afid, aname=''):
        self.classitem = aclass
        self.fid = afid
        self.name = aname


class ICORDBClassItem(object):

    def __init__(self, aclasses, acid, abasepath='', aname='', abasecid=0):
        self.classes = aclasses
        self.cid = acid
        self.basepath = abasepath
        self.name = aname
        self.basecid = abasecid
        self.derivedclasses = []
        self.fields = []
        self.fieldsbyname = {}

    def AddField(self, afid, aname):
        afield = ICORDBFieldItem(self, afid, aname)
        self.fields.append(afield)
        self.fieldsbyname[aname] = afield
        self.classes.fieldsbyid[afid] = afield
        return afield

    def RefreshObjects(self, aclear=0):
        if aclear:
            self.classes.struct.ClearClassObjects(self.cid)
        d = {}
        for afield in self.fields:
            l = self.classes.struct.GetFieldOIDsAsList(afield.fid)
            if l is None:
                continue
            for aoid, adt, auid in l:
                v = d.get(aoid, None)
                if v is None:
                    d[aoid] = (adt, auid)
                else:
                    bdt, buid = v
                    if adt > bdt:
                        d[aoid] = (adt, auid)
        for aoid, v in d.items():
            adt, auid = v
            self.classes.struct.UpdateClassOID(self.cid, aoid, auid, adt)


class ICORDBClasses(object):

    def __init__(self, astruct, aschema=''):
        self.struct = astruct
        self.schema = aschema
        self.classesbyid = {}
        self.fieldsbyid = {}
        self.baseclasses = []

    def AddClass(self, acid, abasepath='', aname='', abasecid=0):
        aclass = ICORDBClassItem(self, acid, abasepath, aname, abasecid)
        self.classesbyid[acid] = aclass
        return aclass

    def RefreshObjects(self, aclear=0):
        for acid, aclass in self.classesbyid.items():
            aclass.RefreshObjects(aclear=aclear)

    def RefreshObjectsTest(self, rcid):
        for acid, aclass in self.classesbyid.items():
            if acid != rcid:
                continue
            aclass.RefreshObjectsTest()

    def CheckOtherCID(self, this, other, sthis, sother):
        for acid in sorted(this.classesbyid.keys()):
            if not other.classesbyid.has_key(acid):
                aclass = this.classesbyid[acid]
                print '%s.CID=%d (%s\\%s), %s.CID=None' % (sthis, acid, aclass.basepath, aclass.name, sother)

    def CheckOtherFID(self, this, other, sthis, sother):
        for afid in sorted(this.fieldsbyid.keys()):
            wgood = 1
            afield = this.fieldsbyid[afid]
            if not other.fieldsbyid.has_key(afid):
                print '%s.FID=%d (%s\\%s)%s, %s.FID=None' % (sthis, afid, afield.classitem.basepath, afield.classitem.name, afield.name, sother)
            else:
                dthiskv = this.struct.GetFieldValuesAsDict(afid, aschema=this.schema)
                dotherkv = other.struct.GetFieldValuesAsDict(afid, aschema=other.schema)
                athislen, aotherlen = 0, 0
                if dthiskv is not None:
                    athislen = len(dthiskv.keys())
                if dotherkv is not None:
                    aotherlen = len(dotherkv.keys())
                if (dthiskv is None) and (athislen != aotherlen):
                    print '%s.FID=%d (%s\\%s)%s, no table: %s.FID <%d / %d>' % (sthis, afid, afield.classitem.basepath, afield.classitem.name, afield.name, sthis, athislen, aotherlen)
                if (dotherkv is None) and (athislen != aotherlen):
                    print '%s.FID=%d (%s\\%s)%s, no table: %s.FID <%d / %d>' % (sthis, afid, afield.classitem.basepath, afield.classitem.name, afield.name, sother, athislen, aotherlen)
                if (dthiskv is None) or (dotherkv is None):
                    continue
                for athisoid in sorted(dthiskv.keys()):
                    if not dotherkv.has_key(athisoid):
                        print '  %s.FID=%d (%s\\%s)%s, %s missing OID: %d' % (sthis, afid, afield.classitem.basepath, afield.classitem.name, afield.name, sother, athisoid)
                        wgood = 0
                    elif dthiskv[athisoid] != dotherkv[athisoid]:
                        print '  %s.FID=%d (%s\\%s)%s, %s diff OID: %d [%s]:[%s]' % (sthis, afid, afield.classitem.basepath, afield.classitem.name, afield.name, sother, athisoid, str(dthiskv[athisoid])[:100], str(dotherkv[athisoid])[:100])
                        wgood = 0
                #if wgood:
                #print 'OK! %s.FID=%d (%s\\%s)%s, %s.FID - LEN: %d'%(sthis,afid,afield.classitem.basepath,afield.classitem.name,afield.name,sother,icnt)
    def CheckOther(self, bclasses, sthis='this', sother='other'):
        print 'Len(classesbyid) - this: %d, other: %d' % (len(self.classesbyid.keys()), len(bclasses.classesbyid.keys()))
        print 'Len(fieldsbyid) - this: %d, other: %d' % (len(self.fieldsbyid.keys()), len(bclasses.fieldsbyid.keys()))
        self.CheckOtherCID(self, bclasses, sthis, sother)
        self.CheckOtherCID(bclasses, self, sother, sthis)
        self.CheckOtherFID(self, bclasses, sthis, sother)
        self.CheckOtherFID(bclasses, self, sother, sthis)
