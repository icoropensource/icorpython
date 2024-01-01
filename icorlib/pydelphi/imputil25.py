# Greg Stein should proclaim his authorship here!

# note: avoid importing non-builtin modules
import imp
import sys
import string
import __builtin__	### why this instead of just using __builtins__ ??

# for the DirectoryImporter
import struct
import marshal

class Importer:
  "Base class for replacing standard import functions."

  def install(self):
    self.__chain_import = __builtin__.__import__
    self.__chain_reload = __builtin__.reload
    __builtin__.__import__ = self._import_hook
    __builtin__.reload = self._reload_hook

  ######################################################################
  #
  # PRIVATE METHODS
  #
  def _import_hook(self, name, globals=None, locals=None, fromlist=None):
    "Locates and imports a module."

    # determine the context of this import
    parent = self._determine_import_context(globals)

    # import the module within the context, or from the default context
    top, tail = self._import_top_module(parent, name)
    if top is None:
      return self.__chain_import(name, globals, locals, fromlist)

    # if "a.b.c" was provided, then load the ".b.c" portion down from
    # below the top-level module.
    bottom = self._load_tail(top, tail)

    # if the form is "import a.b.c", then return "a"
    if not fromlist:
      # no fromlist: return the top of the import tree
      return top

    # if the bottom node is a package, then import some modules.
    #
    # note: if it is not a package, then "fromlist" refers to names in
    #       the bottom module rather than modules.
    # note: for a mix of names, modules within a package, then we will
    #       import all modules and insert those into the namespace of
    #       the package module. Python will pick up all fromlist names
    #       from the bottom (package) module; some will be modules that
    #       we imported and stored in the namespace, others are expected
    #       to be present already.
    if self._is_package(vars(bottom)):
      self._import_fromlist(bottom, fromlist)

    # if the form is "from a.b import c, d" then return "b"
    return bottom

  def _reload_hook(self, module):
    # gmcm - Hmmm, reloading of a module may or may not be impossible,
    # (depending on the importer),  but at least we can
    # look to see if it's ours to reload:
    if hasattr(module, '__importer__'):
      if getattr(module, '__importer__') == self:
        raise SystemError, "reload not yet implemented"
    return self.__chain_reload(module)

  def _determine_import_context(self, globals):
    'Determine the "location" for a relative import.'
    if not globals or \
       globals.get('__importer__', None) is not self:
      # globals does not refer to one of our modules or packages.
      # That implies there is no relative import context, and it
      # should just pick it off the standard path.
      return None

    # The globals refer to a module or package of ours. It will define
    # the context of the new import. Get the module/package fqname.
    parent_fqname = globals['__name__']

    # for a package, return itself (imports refer to pkg contents)
    if self._is_package(globals):
      parent = sys.modules[parent_fqname]
      assert globals is parent.__dict__
      return parent

    i = string.rfind(parent_fqname, '.')

    # a module outside of a package has no particular import context
    if i == -1:
      return None

    # for a module in a package, return the package (imports refer to siblings)
    parent_fqname = parent_fqname[:i]
    parent = sys.modules[parent_fqname]
    assert parent.__name__ == parent_fqname
    return parent

  def _import_top_module(self, parent, name):
    "Locate the top of the import tree (relative or absolute)."
    i = string.find(name, '.')
    if i == -1:
      head = name
      tail = ""
    else:
      head = name[:i]
      tail = name[i+1:]
    if parent:
      fqname = "%s.%s" % (parent.__name__, head)
    else:
      fqname = head
    module = self._import_one(parent, head, fqname)
    if module:
      # the module was relative, or no context existed (the module was
      # simply found on the path).
      return module, tail
    if parent:
      # we tried relative, now try an absolute import (from the path)
      module = self._import_one(None, head, head)
      if module:
        return module, tail

    # the module wasn't found
    return None, None

  def _import_one(self, parent, modname, fqname):
    "Import a single module."

    # has the module already been imported?
    try:
      return sys.modules[fqname]
    except KeyError:
      pass

    result = self.get_code(parent, modname, fqname)
    if result is None:
      return None

    module = imp.new_module(fqname)
    sys.modules[fqname] = module

    ### record packages a bit differently??
    module.__importer__ = self
    module.__ispkg__ = result[0]

    # if present, the third item is a set of values to insert into the module
    if len(result) > 2:
      vars(module).update(result[2])

    # execute the code within the module's namespace
    exec result[1] in vars(module)

    # insert the module into its parent
    if parent:
      setattr(parent, modname, module)
    return module

  def _load_tail(self, m, tail):
    "Import the rest of the tree, down from the top-level module."
    if tail:
      for part in string.splitfields(tail, '.'):
        fqname = "%s.%s" % (m.__name__, part)
        m = self._import_one(m, part, fqname)
        if not m:
          raise ImportError, "No module named " + fqname
    return m

  def _import_fromlist(self, m, fromlist):
    'Import any sub-modules in the "from" list.'

    # if '*' is present in the fromlist, then look for the '__all__' variable
    # to find additional items (modules) to import.
    if '*' in fromlist:
      fromlist = list(fromlist) + list(vars(m).get('__all__', []))

    for sub in fromlist:
      # if the name is already present, then don't try to import it (it
      # might not be a module!).
      if sub != '*' and not hasattr(m, sub):
        subname = "%s.%s" % (m.__name__, sub)
        submod = self._import_one(m, sub, subname)
        if not submod:
          raise ImportError, "cannot import name " + subname

  def _is_package(self, module_dict):
    return module_dict.get('__importer__', None) is self and \
           module_dict['__ispkg__']

  ######################################################################
  #
  # METHODS TO OVERRIDE
  #
  def get_code(self, parent, modname, fqname):
    """Find and retrieve the code for the given module.

    parent specifies a parent module to define a context for importing. It
    may be None, indicating no particular context for the search.

    modname specifies a single module (not dotted) within the parent.

    fqname specifies the fully-qualified module name. This is a (potentially)
    dotted name from the "root" of the module namespace down to the modname.
    If there is no parent, then modname==fqname.

    This method should return None, a 2-tuple, or a 3-tuple.

    * If the module was not found, then None should be returned.
    * The first item of the 2- or 3-tuple should be the integer 0 or 1,
      specifying whether the module that was found is a package or not.
    * The second item is the code object for the module (it will be
      executed within the new module's namespace).
    * If present, the third item is a dictionary of name/value pairs that
      will be inserted into new module before the code object is executed.
      This provided in case the module's code expects certain values (such
      as where the module was found).
    """
    raise RuntimeError, "get_code not implemented"


######################################################################
#
# Simple function-based importer
#
class FuncImporter(Importer):
  "Importer subclass to use a supplied function rather than method overrides."
  def __init__(self, func):
    self.func = func
  def get_code(self, parent, modname, fqname):
    return self.func(parent, modname, fqname)

def install_with(func):
  FuncImporter(func).install()


######################################################################
#
# Base class for archive-based importing
#
class PackageArchiveImporter(Importer):
  "Importer subclass to import from (file) archives."

  def get_code(self, parent, modname, fqname):
    if parent:
      # if a parent "package" is provided, then we are importing a sub-file
      # from the archive.
      result = self.get_subfile(parent.__archive__, modname)
      if result is None:
        return None
      if type(result) == type(()):
        return (0,) + result
      return 0, result

    # no parent was provided, so the archive should exist somewhere on the
    # default "path".
    archive = self.get_archive(modname)
    if archive is None:
      return None
    return 1, "", {'__archive__':archive}

  def get_archive(self, modname):
    """Get an archive of modules.

    This method should locate an archive and return a value which can be
    used by get_subfile to load modules from it. The value may be a simple
    pathname, an open file, or a complex object that caches information
    for future imports.

    Return None if the archive was not found.
    """
    raise RuntimeError, "get_archive not implemented"

  def get_subfile(self, archive, modname):
    """Get code from a subfile in the specified archive.

    Given the specified archive (as returned by get_archive()), locate
    and return a code object for the specified module name.

    A 2-tuple may be returned, consisting of a code object and a dict
    of name/values to place into the target module.

    Return None if the subfile was not found.
    """
    raise RuntimeError, "get_subfile not implemented"


class PackageArchive(PackageArchiveImporter):
  "PackageArchiveImporter subclass that refers to a specific archive."

  def __init__(self, modname, archive_pathname):
    self.__modname = modname
    self.__path = archive_pathname

  def get_archive(self, modname):
    if modname == self.__modname:
      return self.__path
    return None

  # get_subfile is passed the full pathname of the archive


######################################################################
#
# Emulate the standard directory-based import mechanism
#

class DirectoryImporter(Importer):
  "Importer subclass to emulate the standard importer."

  def __init__(self, dir):
    self.dir = dir
    self.ext_char = __debug__ and 'c' or 'o'
    self.ext = '.py' + self.ext_char

  def get_code(self, parent, modname, fqname):
    if parent:
      dir = parent.__pkgdir__
    else:
      dir = self.dir

    # pull the os module from our instance data. we don't do this at the
    # top-level, because it isn't a builtin module (and we want to defer
    # loading non-builtins until as late as possible).
    try:
      os = self.os
    except AttributeError:
      import os
      self.os = os

    pathname = os.path.join(dir, modname)
    if os.path.isdir(pathname):
      values = { '__pkgdir__' : pathname }
      ispkg = 1
      pathname = os.path.join(pathname, '__init__')
    else:
      values = { }
      ispkg = 0

    t_py = self._timestamp(pathname + '.py')
    t_pyc = self._timestamp(pathname + self.ext)
    if t_py is None and t_pyc is None:
      return None
    code = None
    if t_py is None or (t_pyc is not None and t_pyc >= t_py):
      f = open(pathname + self.ext, 'rb')
      if f.read(4) == imp.get_magic():
        t = struct.unpack('<I', f.read(4))[0]
        if t == t_py:
          code = marshal.load(f)
      f.close()
    if code is None:
      code = self._compile(pathname + '.py', t_py)
    return ispkg, code, values

  def _timestamp(self, pathname):
    try:
      s = self.os.stat(pathname)
    except OSError:
      return None
    return long(s[8])

  def _compile(self, pathname, timestamp):
    codestring = open(pathname, 'r').read()
    if codestring and codestring[-1] != '\n':
      codestring = codestring + '\n'
    code = __builtin__.compile(codestring, pathname, 'exec')

    # try to cache the compiled code
    try:
      f = open(pathname + self.ext_char, 'wb')
      f.write('\0\0\0\0')
      f.write(struct.pack('<I', timestamp))
      marshal.dump(code, f)
      f.flush()
      f.seek(0, 0)
      f.write(imp.get_magic())
      f.close()
    except OSError:
      pass

    return code

def _test_dir():
  path = sys.path[:]
  path.reverse()
  for d in path:
    DirectoryImporter(d).install()


    # Here I'll explain how get_code operates:
    # "import a.b" and "from a import b" yield:
    #  get_code(None, 'a', 'a')
    # if we return a code object from this, then we get
    #  get_code(<module 'a'>, 'b', 'a.b')
    # A 3-level import would go on to:
    #  get_code(<module 'a.b'>, 'c', 'a.b.c')
    # Of course, there may be intervening calls for other things,
    # depending on imports in any of these modules..
