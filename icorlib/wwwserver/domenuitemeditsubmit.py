# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
import CLASSES_Library_NetBase_WWW_Server_DoMenuPageView


def DoMenuItemEditSubmit(file, aoid, areport, UID):
    amenu = ICORWWWMenuItem(0, aoid)
    amenu.Caption = areport.me_caption
    amenu.AsPageCaption = areport.me_aspagecaption
    amenu.AsPageSubCaption = areport.me_aspagesubcaption
    amenu.AsPageDescription = areport.me_aspagedescription
    amenu.AsPageShortDescription = areport.me_aspageshortdescription
    amenu.PageHTML = areport.me_pagehtml
    amenu.PageHTMLInfo = areport.me_pagehtmlinfo
    CLASSES_Library_NetBase_WWW_Server_DoMenuPageView.GenerateMenuAsPage(file, aoid, UID)
