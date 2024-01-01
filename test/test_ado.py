# -*- coding: utf-8 -*-
import sys
import time

try:
    import json
except:
    import simplejson as json

import icorapi

import appplatform.storageutil as storageutil
import icordbmain.adoutil as ADOLibInit
from icordbmain import dbado


def GetADOContext(kwargs, UID):
    ioid = storageutil.getStrAsOID(kwargs.get('ioid', ''))
    tid = storageutil.getStrAsInt(kwargs.get('tid', '-1'))
    poid = storageutil.getStrAsInt(kwargs.get('poid', '-1'))
    chapterid = storageutil.getStrAsInt(kwargs.get('chapterid', '-1'))
    if not ioid or (tid < 0) or (poid < 0):
        return None
    storeado = dbado.ICORDBADO()
    acontext = storeado.GetConnectionByProject(poid)
    acontext.SetContextVars(uid=UID, poid=None, cmsid=None, toid=tid, coid=chapterid, ioid=ioid, basenamemodifier=None, infotablessufix=None)
    return acontext


if __name__ == '__main__':
    filename = u'aąćęłńóśźżz-AĆĘŁŃÓŚŹŻZ.txt'
    filename = "a\xc4\x85\xc4\x87\xc4\x99\xc5\x82\xc5\x84\xc3\xb3\xc5\x9b\xc5\xba\xc5\xbcYYY.txt".decode('utf-8')

    #if type(filename)==type(''):
    #filename=unicode(filename,'utf-8')
    kwargs = {'ioid': 'F2B958156424426A88B227C8F8EA6153', 'tid': '200048', 'poid': '200000', 'chapterid': '202025', 'uid': 200000}
    adocontext = GetADOContext(kwargs, kwargs['uid'])
    asql = '''
SELECT 
  _OID, Name, Path, FileSize, LastModification, Description, 
  InformacjaPodmiotUdostepniajacy, InformacjaOsobaOdpowiedzialna, InformacjaDataWytworzenia, InformacjaOpisCzynnosci, 
  RefTable, RefOID, _datetime, _UID, _UserName, 
  Category, Kind, ItemKey, ItemRel, ItemTitle, ItemType, ItemWidth, ItemHeight, Status, ItemStatus, ItemPosition
from %sFILEUPLOADS_0 
WHERE 
_OID='-1'
''' % (adocontext.basenamemodifier, )
    rs = adocontext.GetRS(asql)
    if rs.EOF or not rs.BOF:
        rs.AddNew()
        #rs.Fields.Item('Name').Value=storageutil.UTF8_To_ASCII(filename)
        rs.Fields.Item('Name').Value = storageutil.UTF8_slugify(filename)
        rs.Update()
        aoid = ADOLibInit.GetRSValueAsStr(rs, '_OID')
        print 'NEW FILE:', aoid
    rs = adocontext.CloseRS(rs)
    adocontext.Close()

    print u'ąćęłńóśźż'.encode('utf-8')
    print u'form-data; name="file"; filename="a\xc4\x85\xc4\x87\xc4\x99\xc5\x82\xc5\x84\xc3\xb3\xc5\x9b\xc5\xba\xc5\xbc.txt"'.encode('utf-8')
