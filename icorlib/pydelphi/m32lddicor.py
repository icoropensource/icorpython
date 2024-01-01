import sys
import string
import ICORDelphi

magic       = '\\x04\\x17\\x0d\\x0a'

def find_in_locals(aname,adefault):
        f=sys._getframe().f_back
        while f is not None:
                if f.f_locals.has_key(aname):
                        return f.f_locals[aname]
                f=f.f_back
        return adefault

def string_find(where,ch):
        i=0
        j=len(where)
        while i<j:
                if where[i]==ch:
                        return i
                i=i+1
        return -1

def string_rfind(where,ch):
        i=len(where)-1
        while i>=0:
                if where[i]==ch:
                        return i
                i=i-1
        return -1

def uid():
        ret=find_in_locals('UID',None)
        if ret is None:
                return -1
        return ret

class sysoutWrapper:
    def __init__(self,asstdout):
        self.softspace   = 0
        self.asstdout = asstdout
        if self.asstdout:
           self.sysout = sys.stdout
           sys.stdout = self
        else:
           self.sysout = sys.stderr
           sys.stderr = self
    def __del__(self):
        if self.asstdout:
           sys.stdout = self.sysout
        else:
           sys.stderr = self.sysout
    def write(self,s):
        if self.asstdout:
           ICORDelphi.OnStdOutPrint(uid(),s,0)
        else:
           ICORDelphi.OnStdErrPrint(uid(),s,0)

class ICORLoader:
    def __str__(self):
        return 'ICORLoader'
    __repr__=__str__
    def find_module_in_dir(self, loader, name, dirname, allow_packages,loaderid):
        if dirname is None:# and name[:4]=='ICOR':
#           print 'py find_module:',name, dirname
            try:
                code = self.ICORLoadFromStream(name)
                return None, name, (code, None, loaderid)
            except ImportError:
                pass
        return None
    def load_module(self, loader, name, stuff):
        file, filename, info = stuff
        (code, mode, loaderid) = info
#       print 'py load_module:',name, stuff
        m = loader.hooks.add_module(name)
        m.__file__ = name
        exec code in m.__dict__
        return m
    def ICORLoadFromStream(self, iName):
        iExpression = ICORDelphi.ImportModuleAsString(uid(),iName)
        iLen = len(iExpression)
        if iLen==0:
            raise ImportError,"No module named \"%s\" " %iName
        needCompiler=1
        if iLen >= 4:
            needCompiler = (iExpression[0:4] != magic)
        if needCompiler:
            code = compile(iExpression+ "\n", iName, "exec")
        else:
            raise ImportError,"No module named \"%s\" " %iName
        return code
