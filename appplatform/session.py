# -*- coding: utf-8 -*-
import re

import cherrypy

import appplatform.storageutil as storageutil


class Session(object):

    def __init__(self, aappdb, asessiontoken='', atimer=None):
        self.db = aappdb
        self._SessionToken = asessiontoken
        self.timer = atimer

    def SetResponse(self, isid=None):
        if isid is None:
            isid = self._SessionToken
        if isid:
            cherrypy.response.headers['Authorization'] = 'Bearer ' + isid
        else:
            cherrypy.response.headers['Authorization'] = ''
        cookie = cherrypy.response.cookie
        cookie['_isid'] = isid
        cookie['_isid']['path'] = '/'
        if not isid:
            cookie['_isid']['expires'] = 0
        #cookie['_isid']['httponly']=1
        ## Response.AddHeader "Set-Cookie","_isid=; HttpOnly;"
    def getSessionID(self, anew=0):
        if not anew:
            if self._SessionToken:
                if self.CheckValidSession(self._SessionToken):
                    self.SetResponse()
                    return self._SessionToken
                self._SessionToken = ''
            isid = ''
            abearer = cherrypy.request.headers.get('Authorization', '')
            if abearer:
                lb = abearer.split()
                if len(lb) == 2:
                    if lb[0] == 'Bearer':
                        isid = lb[1]
            if not isid:
                cv = cherrypy.request.cookie.get('_isid', None)
                if cv is not None:
                    isid = cv.value
            if isid:
                if self.CheckValidSession(isid):
                    self._SessionToken = isid
                else:
                    isid = ''
            self.SetResponse(isid)
            return isid
        self.SetTokenLogout()
        self._SessionToken = self.db.dbsession.getSessionNewToken()
        self.SetResponse(self._SessionToken)
        return self._SessionToken

    def CheckValidSession(self, isid=''):
        if not isid:
            isid = self._SessionToken
        isid = storageutil.getStrAsOID(isid)
        if not isid:
            return False
        return self.db.dbsession.checkValidSessionToken(isid)

    def SetTokenLogout(self, isid=''):
        if not isid:
            isid = self._SessionToken
        if not isid:
            return False
        ret = self.db.dbsession.setTokenStatus(isid, 'L')
        if ret:
            self._SessionToken = ''
        return ret

    def get(self, aname, adefault='', ifexists=0):
        if self.timer:
            self.timer.Info('Session get 01')
        stoken = self.getSessionID()
        if self.timer:
            self.timer.Info('Session get 02')
        if not stoken:
            return adefault
        if self.timer:
            self.timer.Info('Session get 03')
        ret = self.db.dbsession.getSessionValue(stoken, aname, adefault=adefault)
        if self.timer:
            self.timer.Info('Session get 04')
        if ifexists and ret == '':
            return adefault
        return ret

    def set(self, aname, avalue, ifexists=0):
        if self.timer:
            self.timer.Info('Session set 01')
        stoken = self.getSessionID()
        if self.timer:
            self.timer.Info('Session set 02')
        if stoken == '':
            return ''
        if ifexists:
            v = self.get(aname, '')
            if v == '':
                return ''
        if self.timer:
            self.timer.Info('Session set 03')
        ret = self.db.dbsession.setSessionValue(stoken, aname, avalue, atimer=self.timer)
        if self.timer:
            self.timer.Info('Session set 04')
        return ret
