import os
import sys
import marshal
import m32ldd

class DIRLoader:
	def __str__(self):
		return 'DIRLoader(%s)' %self.dirname
	__repr__=__str__
	def __init__(self,dirname):
		self.dirname = dirname
	def find_module_in_dir(self, loader, name, dirname, allow_packages,loaderid):
		if dirname is not None:
			return None
		return m32ldd.ihooks.ModuleLoader.find_module_in_dir(loader, name, self.dirname, allow_packages)
