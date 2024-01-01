import Queue
import threading
import types

try:
    import json
except:
    import simplejson as json

import cherrypy
import cherrypy.process as process


def CORS():
    sorigin = cherrypy.request.headers.get('Origin', '*')
    cherrypy.response.headers["Access-Control-Allow-Origin"] = sorigin
    cherrypy.response.headers['Access-Control-Allow-Credentials'] = 'true'
    if cherrypy.request.method == 'OPTIONS':
        # preflight request
        # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With, Accept-Language, Content-Language, client-security-token'
        cherrypy.response.headers['Access-Control-Max-Age'] = '1728000'
        cherrypy.response.headers['Content-Type'] = ''
        cherrypy.response.headers['Content-Length'] = '0'
        # tell CherryPy to avoid normal handler
        return True
    #else:
    #cherrypy.response.headers['Access-Control-Allow-Origin'] = sorigin


def InitCORS():
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)


class BackgroundTaskQueue(process.plugins.SimplePlugin):
    thread = None

    def __init__(self, bus, qsize=100, qwait=2):
        super(BackgroundTaskQueue, self).__init__(bus)
        self.q = Queue.Queue(qsize)
        self.qwait = qwait

    def start(self):
        self.running = True
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        if hasattr(self.q, 'join'):
            self.q.join()

    def run(self):
        while self.running:
            try:
                try:
                    func, args, kwargs = self.q.get(block=True, timeout=self.qwait)
                except Queue.Empty:
                    continue
                else:
                    func(*args, **kwargs)
                    if hasattr(self.q, 'task_done'):
                        self.q.task_done()
            except:
                self.bus.log("Error in BackgroundTaskQueue %r." % self, level=40, traceback=True)

    def put(self, func, *args, **kwargs):
        """Schedule the given func to be run."""
        self.q.put((func, args, kwargs))


def isClientConnected(asock=None):
    if asock is None:
        asock = cherrypy.request.rfile.rfile._sock
    ret = 0
    atimeout = asock.gettimeout()
    try:
        asock.settimeout(0.001)
        try:
            adata = asock.recv(0)
        except:
            ret = 1
    finally:
        asock.settimeout(atimeout)
    return ret


def noBodyProcess():
    cherrypy.request.process_request_body = False
    if 0:
        cherrypy.request.show_tracebacks = False
    if cherrypy.request.method != 'POST':
        raise cherrypy.HTTPError(405, "405 Method Not Allowed\n\nrequest must use 'POST' method.")


def GetJSONErrorResult(id='', code=None, title='', status='', info='', asstring=0):
    d = {}
    if status:
        d['status'] = status
        d['info'] = info
        if id:
            d['id'] = id
        if code is not None:
            d['code'] = code
        if title:
            d['title'] = title
    else:
        if code is None:
            code = -1
        d['id'] = id
        d['code'] = "%d" % code
        d['title'] = title
    ret = {"errors": [d]}
    if asstring:
        return json.dumps(ret)
    return ret


def GetJSONResult(ret=None, status=None, info=None, adatakey='data', items=None, aitemskey='items', asjsontext=0):
    if isinstance(ret, types.StringTypes) and not asjsontext:
        return ret
    dret = {}
    if type(ret) == type([]):
        dret[adatakey] = ret
    if type(ret) == type({}):
        if not ret.has_key('errors'):
            dret[adatakey] = ret
        else:
            dret.update(ret)
    if items is not None:
        dret[aitemskey] = items
    if status is not None:
        dret['status'] = status
    if info is not None:
        dret['info'] = info
    if isinstance(ret, types.StringTypes) and asjsontext:
        dret[adatakey] = '$!$!$!$!$!$!$'
        sret = json.dumps(dret)
        sret = sret.replace('"$!$!$!$!$!$!$"', ret)
        return sret
    return json.dumps(dret)
