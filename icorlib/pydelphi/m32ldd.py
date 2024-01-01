import ihooks

magic       = ihooks.imp.get_magic()
stringtr    = map(lambda x:chr(x),range(256))
stringtr    = reduce(lambda x, y: x+y, stringtr, '')
stringtr    = stringtr[:0x0d]+chr(0x0a)+stringtr[0x0e:]

LOADER_MODULE = 128
class m32Loader(ihooks.ModuleLoader):
	def __init__(self, verbose=0):
		ihooks.ModuleLoader.__init__(self,None,verbose)
		self.loaders={}
		self.loaderID=LOADER_MODULE
	def registerLoader(self, loader):
		self.loaders[self.loaderID]=loader
                self.loaderID=self.loaderID+1
	def find_module_in_dir(self, name, dirname, allow_packages=1):
		loaders=self.loaders.keys()
		loaders.sort()
#		print 'find_module_in_dir=',name,dirname
		for loader in loaders:
#			print 'loader:',self.loaders[loader],name,dirname
			result=self.loaders[loader].find_module_in_dir(self, name, dirname, allow_packages, loader)
			if result is not None:
				return result
#		print '\tdefault'
		return ihooks.ModuleLoader.find_module_in_dir(self, name, dirname, allow_packages)
	def load_module(self, name, stuff):
#		print 'load_module=',name,stuff
		file, filename, info = stuff
		(suff, mode, loaderid) = info
		if self.loaders.has_key(loaderid):
			return self.loaders[loaderid].load_module(self, name, stuff)
		return ihooks.ModuleLoader.load_module(self, name, stuff)
def install(loader = None):
	if loader is None:
		ihooks.current_importer = ihooks.ModuleImporter(m32Loader())
		ihooks.current_importer.install()
	else:
        	ihooks.current_importer.loader.registerLoader(loader)
