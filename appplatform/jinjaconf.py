# -*- coding: utf-8 -*-
import sys
import os
import codecs

import jinja2

import appplatform.startutil as startutil
import appplatform.storageutil as storageutil


class ICORJinjaConfGenerator(object):

    def __init__(self, outputdir, templatedir, tvars=None, libdirs=None, block_start_string='{%', block_end_string='%}', variable_start_string='{{', variable_end_string='}}'):
        self.dir = outputdir
        self.templatedir = templatedir
        if libdirs is None:
            libdirs = []
        libdirs.insert(0, templatedir)
        if tvars is None:
            tvars = {}
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(libdirs), block_start_string=block_start_string, block_end_string=block_end_string, variable_start_string=variable_start_string, variable_end_string=variable_end_string)
        self.jinja_env.filters['asPath'] = self.FilterAsPath
        if startutil.appconfig:
            self.jinja_env.globals.update(startutil.appconfig)
        self.jinja_env.globals.update(tvars)

    def FilterAsPath(self, value):
        return value.replace('\\', '/')

    def Process(self):
        for dirpath, _dirnames, filenames in os.walk(self.templatedir):
            #print dirpath,'-',dirnames,'-',filenames
            for afilename in filenames:
                if afilename[-6:] != '.jinja':
                    bfilename = afilename.replace('.remove.', '.')
                    print 'IN:', dirpath, '-', bfilename
                    afilepath = dirpath[len(self.templatedir) + 1:].replace('\\', '/') + '/' + afilename
                    #print '  PATH:',afilepath
                    atemplate = self.jinja_env.get_template(afilepath)
                    atext = atemplate.render()
                    aoutdir = os.path.join(self.dir, dirpath[len(self.templatedir) + 1:])
                    #print '  OUT:',aoutdir
                    if not os.path.exists(aoutdir):
                        os.makedirs(aoutdir)
                    fout = storageutil.OpenText(aoutdir + '/' + bfilename, 'w')
                    fout.write(atext)
                    fout.close()
