import appplatform.startutil as startutil

__connectionscache = {}


def GetConnectionString(dobj, agetifdeactivated=0, aconnectiontimeout=0, adatabase=''):
    global __connectionscache
    if dobj is None:
        return ''
    if not agetifdeactivated and dobj['SGIsInactive']:
        return ''
    hobj = dobj.DBHost
    if not hobj:
        return ''
    if hobj['SGIsDisabled']:
        return ''
    if not agetifdeactivated and hobj['SGIsInactive']:
        return ''
    sconn = __connectionscache.get(dobj.OID, None)
    if sconn is not None:
        return sconn
    l = []
    robj = dobj.DBProvider
    if robj:
        s = robj.Nazwa
        if s:
            l.append('provider=%s' % startutil.GetStrEnv(s))
    iobj = dobj.DBDriver
    if iobj:
        s = iobj.Nazwa
        if s:
            l.append('driver=%s' % startutil.GetStrEnv(s))
    s = hobj.DataBaseHost
    if not s:
        return ''
    l.append('server=%s' % startutil.GetStrEnv(s))
    s = hobj.DataBaseFailoverPartner
    if s:
        l.append('failover partner=%s' % startutil.GetStrEnv(s))
    s = hobj.DataBaseUser
    if s:
        l.append('uid=%s' % startutil.GetStrEnv(s))
    s = hobj.DataBasePassword
    if s:
        l.append('pwd=%s' % startutil.GetStrEnv(s))
    s = dobj.DataBaseName
    if adatabase:
        s = adatabase
    if s:
        l.append('database=%s' % startutil.GetStrEnv(s))
    if aconnectiontimeout == 0:
        aconnectiontimeout = dobj['ConnectionTimeout']
    if aconnectiontimeout > 0:
        l.append('connection timeout=%d' % min(aconnectiontimeout, 15))
    s = hobj.ConnectionStringExtra
    if s:
        l.append(startutil.GetStrEnv(s))
    s = dobj.ConnectionStringExtra
    if s:
        l.append(startutil.GetStrEnv(s))
    sconn = ';'.join(l)
    if not agetifdeactivated:
        __connectionscache[dobj.OID] = sconn
    return sconn


def RegisterConnectionError(dobj, aforce=0):
    global __connectionscache
    if not dobj:
        return
    cnt = dobj['InactiveCounter']
    cnt = cnt + 1
    dobj['InactiveCounter'] = cnt
    if cnt > 3:
        if aforce:
            dobj['SGIsInactive'] = 1
        if __connectionscache.has_key(dobj.OID):
            del __connectionscache[dobj.OID]


def RegisterConnectionOK(dobj):
    global __connectionscache
    if not dobj:
        return
    dobj['InactiveCounter'] = 0
    dobj['SGIsInactive'] = 0
    if __connectionscache.has_key(dobj.OID):
        del __connectionscache[dobj.OID]


def GetConnectionName(aobj):
    l = [str(aobj.OID), aobj.Nazwa, startutil.GetStrEnv(aobj.DataBaseName)]
    if aobj.DBProvider:
        l.append(aobj.DBProvider.Nazwa)
    if aobj.DBDriver:
        l.append(aobj.DBDriver.Nazwa)
    if aobj.DBHost:
        l.append(startutil.GetStrEnv(aobj.DBHost.DataBaseHost))
        l.append(startutil.GetStrEnv(aobj.DBHost.DataBaseUser))
    ret = ', '.join([x for x in l if x])
    return 'DBAccess: [' + ret + ']'
