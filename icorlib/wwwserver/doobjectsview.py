# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.icorobjectsviewer import *
from icorlib.icormdspace import ICORMDSpace
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import string
import cStringIO


def DoObjectsView(file, aclass, fobj=-1, objc=0):
    apage = 0
    aspace = ICORMDSpace()
    aspace.Caption = aclass.WWWDescription
    cov = ICORClassObjectsViewer(aclass, aspace)
    sfname = cov.Process(fobj, objc)
    if 0:
        titerator = ICORClassObjects2HTML(cov.space, file, apage, 'ObjectsView')
    else:
        titerator = ICORClassObjects2XMLDSO(cov.space, file, apage, 'ObjectsView')
    titerator.ForEachNotEmptyRow()
