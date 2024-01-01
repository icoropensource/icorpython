import sys
import os
import m32ldd
import m32lddicor
import m32lddpyl
import m32lddfunc
import m32ldddir

def installone(name):
   try:
      if type(name)==type(''):
         if os.path.isdir(name):
            m32ldd.install(m32ldddir.DIRLoader(name))
         else:
            m32ldd.install(m32lddpyl.PYLLoader(name))
      else:
         m32ldd.install(m32lddfunc.FUNCLoader(name))
   except:
      pass

def installall(syspath,top,modules):
#   sys.path=[]
   for i in modules:
                installone('%s/%s' %(top,i))
   for i in syspath:
                installone(i)

m32ldd.install()
m32stdout=m32lddicor.sysoutWrapper(0)
m32stderr=m32lddicor.sysoutWrapper(1)
m32ldd.install(m32lddicor.ICORLoader())
