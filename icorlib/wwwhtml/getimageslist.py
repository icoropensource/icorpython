# -*- coding: utf-8 -*-
from icorlib.icorinterface import *

IMAGES_LIST_AS_FIELD_EDITOR=''

def GetImagesListAsFieldEditor():
   global IMAGES_LIST_AS_FIELD_EDITOR
   if IMAGES_LIST_AS_FIELD_EDITOR:
      return IMAGES_LIST_AS_FIELD_EDITOR
   aclass=aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Dictionary_Named_ImageInfo']
   aoid=aclass.FirstObject()
   l=[]
   while aoid>=0:
      aname=aclass.Name[aoid]
      alocation=aclass.Location[aoid]
      l.append([aname,aoid,alocation])
      aoid=aclass.NextObject(aoid)
   l.sort()
   ls=[]
   for aname,aoid,alocation in l:
      ls.append('<img src="%s"><br>'%(alocation,))
   IMAGES_LIST_AS_FIELD_EDITOR='\n'.join(ls)
   return IMAGES_LIST_AS_FIELD_EDITOR
