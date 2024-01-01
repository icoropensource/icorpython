from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil


def main(aint, astr1, astr2):
    aclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_Projekt']
    aobj = aclass.GetFirstObject()
    while aobj:
        print aobj.OID, aobj['Nazwa']
        aobj.Next()
    return 'Abab'


def OnRepositoryChanged(acategory, amode, aid, aoid, atype, avalue):    #   CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    return
    #print 'cat:',acategory,'mod:',amode,'aid:',aid,'oid:',aoid,'typ:',atype
    #print 'val:',avalue
    if acategory == 'FIELD':
        if amode == 'UPDATE':
            aICORDBEngine.SysBase.SetLastFieldValueModificationID(aid, aoid)
            #print 'RU: id:%d oid:%d type:%d v:%s tv: %s'%(aid,aoid,atype,avalue,type(avalue))
            aICORDBEngine.CacheBase.SetFieldValue(aid, aoid, atype, avalue)
            #print '  GU: v:%s'%aICORDBEngine.CacheBase.GetFieldValue(aid,aoid,atype,1)
        elif amode == 'DELETE':
            aICORDBEngine.SysBase.SetLastFieldValueModificationID(aid, aoid)
            aICORDBEngine.CacheBase.DelFieldValue(aid, aoid)
        else:
            print 'unknown FIELD RepositoryChanged mode: %s' % amode
    elif acategory == 'CLASS':
        if amode == 'UPDATE':
            aICORDBEngine.SysBase.SetLastClassModificationID(aid)
        elif amode == 'DELETE':
            aICORDBEngine.SysBase.SetLastClassModificationID(aid)
        else:
            print 'unknown CLASS RepositoryChanged mode: %s' % amode
    return
