import sys
import marshal
import string

magic       = '\\x04\\x17\\x0d\\x0a'
stringtr    = map(lambda x:chr(x),range(256))
stringtr    = reduce(lambda x, y: x+y, stringtr, '')
stringtr    = stringtr[:0x0d]+chr(0x0a)+stringtr[0x0e:]

class FUNCLoader:
	def __str__(self):
		return 'FUNCLoader(%s)' %self.func
	__repr__=__str__
	def __init__(self,func):
		self.func = func
	def find_module_in_dir(self, loader, name, dirname, allow_packages,loaderid):
		try:
			code = self.LoadFromFunction(name, dirname)
			return None, name, (code, None, loaderid)
		except ImportError:
			pass
		return None
	def load_module(self, loader, name, stuff):
        	file, filename, info = stuff
		(code, mode, loaderid) = info
		m = loader.hooks.add_module(name)
		m.__file__ = name
		exec code in m.__dict__
		return m
	def LoadFromFuncion(self, iName, dirName):
		data=self.func(iName,dirName)
		iLen = len(data)
		if iLen==0:
			raise ImportError,"No module named \"%s\" " %iName
		needCompiler=1
		if iLen >= 4:
			needCompiler = (data[0:4] != magic)
		if needCompiler:
			data=string.translate(data,stringtr)
			code = compile(data+ "\n", iName, "exec")
#			codes= marshal.dumps(code)
#			ICORDelphi.ExportModuleAsString(uid(),iName,codes)
		else:
			code = marshal.loads(data[8:])
		return code
