import string
import zlib
import struct
import marshal
import m32ldd

_MAGIC0 = 'PYLB\0\0\0\0' # python library not compressed
_MAGIC1 = 'PYLB\0\1\0\0' # python library compressed

def writez(output,data,pack):
        if pack:
                data = zlib.compress(data, 9)
                crc32= zlib.adler32(data)
        else:
                crc32=0
        pdata=struct.pack('<ii',len(data),crc32)
        output.write(pdata)
        output.write(data)

def readz(input,pack):
        ldata,lcrc32=struct.unpack('<ii',input.read(8))
        data=input.read(ldata)
        if pack:
                crc32= zlib.adler32(data)
                ok=lcrc32==crc32
                data = zlib.decompress(data)
        else:
                ok=lcrc32==0
        if ok:
                data=marshal.loads(data)
        else:
                data=''
        return ok,data

class PYLLoader:
	def __str__(self):
		return 'PYLLoader(%s)' %self.archive_pathname
	__repr__=__str__
        def __init__(self, archive_pathname):
        	self.archive_pathname = archive_pathname
                self.library = open(archive_pathname, 'rb')
                magik = self.library.read(len(_MAGIC0))
                if magik==_MAGIC0:
	                self.packed=0
		elif magik==_MAGIC1:
	                self.packed=1
		else:
			raise NameError,archive_pathname
                offset = struct.unpack('=i', self.library.read(4))[0]
                self.library.seek(offset)
                self.toc = readz(self.library,self.packed)[1]
	def find_module_in_dir(self, loader, name, dirname, allow_packages,loaderid):
		if dirname is None:
			data=self.toc.get(name,None)
		else:
			name=string.join([dirname,name],'.')
			data=self.toc.get(name,None)
		if not data:
			return None
#		print 'pyl find_module:',name, dirname
		pos, ispkg = data
#		print '\t',pos, ispkg
                self.library.seek(pos)
                code=readz(self.library,self.packed)[1]
		return None, name, ((code, ispkg,{'__path__':name}), None, loaderid)
	def load_module(self, loader, name, stuff):
#		print 'py load_module:',name, stuff
		code,ispkg,dict = stuff[2][0]
		m = loader.hooks.add_module(name)
		m.__file__ = name
		if ispkg:
			m.__path__ = [name,]
#		print dir(m)
		exec code in m.__dict__
		return m
