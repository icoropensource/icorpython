# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from CLASSES_Library_ICORBase_Interface_ICORSummary import ICORSummary, SummarySpace2HTML, GenerateAsHTML, SummaryConditionsAsStringWWW, scEqual, scExisting, scNonExisting
from icorlib.icormdspace import ICORMDSpace
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
import icorlib.icorsecurity as ICORSecurity
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string


def GenerateSummaryParameters(file, OID):
    aspace = ICORMDSpace()
    asummary = ICORSummary(OID, aspace)

    script = """
<SCRIPT LANGUAGE=javascript>

var dselectedelement=0;

function condselect_onchange(aelement,aelement2) {
   if (aelement.selectedIndex==0) {
      document.getElementById(aelement2).style.visibility="visible";
      } else {
      document.getElementById(aelement2).style.visibility="hidden";
      }
}                                                  

var drPopup = null;
if (isIE()) {
   drPopup = window.createPopup();
}

function showPopupDR(asrc,aelement)
{
   dselectedelement=asrc;
   if (isIE()) {
      drPopup.document.body.innerHTML = oContextHTML.innerHTML;
      drPopup.show(0, 0, 300, 200, aelement);
   }
}

function showPopupPR(asrc,aelement,asrcelement,dh)
{
   dselectedelement=asrc;
   if (isIE()) {
      drPopup.document.body.innerHTML = asrcelement.innerHTML;
      drPopup.show(0, 0, 300, dh, aelement);
   }
}

</SCRIPT>

<DIV ID="oContextHTML" STYLE="display:none;">
<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:200px; border-bottom:2px solid black;" >
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;">dzisiaj</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">wczoraj</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">jutro</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">od początku tygodnia</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ten tydzień</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ostatni tydzień</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">następny tydzień</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">od początku miesiąca</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ten miesiąc</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ostatni miesiąc</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">następny miesiąc</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">od początku roku</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ten rok</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">ostatni rok</DIV>
    <DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background='#ffffff'" onmouseout="this.style.background='%(background)s'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">następny rok</DIV>
</div>
</DIV>
""" % {
        'fontsize': '8pt',
        'rowheight': '20px',
        'background': 'wheat'}
    file.write(script)
    if asummary.Description:
        s = string.replace(asummary.Description, '\n', '<br>')
        file.write('<p class=description>%s</p>\n' % (s))
    file.write('<form name=summForm id=summForm METHOD="post" ACTION="icormain.asp?jobtype=summaryexecute&OID=%d">\n' % (OID))
    file.write('<table class=objectsviewtable>\n')
    file.write('<caption class=objectsviewcaption>%s</caption>\n' % (asummary.Name))
    i = 0
    scnl = SummaryConditionsAsStringWWW.keys()
    scnl.sort()
    for arule in asummary.RulesList:
        file.write('<tr><td class=objectsviewheader>\n')
        file.write('<img valign="center" alt="ukryj/schowaj parametry reguły" style="cursor:pointer;" src="images/tree/menu_minus.png" onclick="if(rulesection%d.style.display==\'none\'){rulesection%d.style.display=\'inline\';this.src=\'images/tree/menu_minus.png\';}else{rulesection%d.style.display=\'none\';this.src=\'images/tree/menu_plus.png\';};">\n' % (i, i, i, ))
        file.write('<b>%s</b>\n' % (arule.RuleFieldPath, ))
        file.write('<img valign="center" alt="ignoruj regułę podczas generowania zestawienia" style="cursor:pointer;" src="images/tree/document_ok.png" onclick="if(rulehidden%d.value==\'1\'){this.src=\'images/tree/document_ok.png\';rulehidden%d.value=\'0\';}else{this.src=\'images/tree/document_cancel.png\';rulehidden%d.value=\'1\';};">\n' % (i, i, i, ))
        if arule.Condition in [scExisting, scNonExisting]:
            bclass = arule.Field.ClassOfType
            if bclass is None:
                file.write('</td></tr>\n')
                i = i + 1
                continue
            aobj = bclass.GetFirstObject()
            olist = []
            wsc = 0
            while aobj.Exists():
                if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView'):
                    s = string.join(aobj.AsColumnValues(), ', ')
                    if arule.ExistingRefs.RefExists(aobj.OID, aobj.CID):
                        sc = ' CHECKED'
                    else:
                        sc = ''
                    olist.append((s, sc, str(aobj.OID) + ':' + str(aobj.CID) + ':'))
                else:
                    wsc = 1
                aobj.Next()
            olist.sort()
            file.write('<img valign="center" alt="zaznacz/odznacz pozycje" style="cursor:pointer;" src="images/icon_toggle_on.png" onclick="if(this.src.indexOf(\'icon_toggle_off\')<0){this.src=\'images/icon_toggle_off.png\';}else{this.src=\'images/icon_toggle_on.png\';};for(i=0;i<%d;i++){document.getElementById(\'rulevalue%d_\'+i.toString()).checked=!document.getElementById(\'rulevalue%d_\'+i.toString()).checked;};">\n' % (len(olist), i, i))
            file.write('</td></tr>\n')
            file.write('<tr><td class=objectsviewdata><span style="display:inline;" id=rulesection%d>\n' % i)
            file.write('<input type="hidden" id=rulehidden%d name=rulehidden%d value="0">\n' % (i, i, ))

            file.write('<INPUT id=condselect%d name=condselect%d TYPE=hidden VALUE="%d">\n' % (i, i, arule.Condition))
            file.write('<INPUT id=rulevalue%d_max name=rulevalue%d_max TYPE=hidden VALUE="%d">\n' % (i, i, len(olist)))
            j = 0
            for s, sc, bref in olist:
                if wsc:
                    sc = ' CHECKED'
                file.write('<INPUT id=rulevalue%d_%d name=rulevalue%d_%d class=checkradio TYPE=CHECKBOX VALUE="%s" %s>%s<BR>\n' % (i, j, i, j, bref, sc, s))
                j = j + 1
        else:
            file.write('</td></tr>\n')
            file.write('<tr><td class=objectsviewdata><span style="display:inline;" id=rulesection%d>\n' % i)
            file.write('<input type="hidden" id=rulehidden%d name=rulehidden%d value="0">\n' % (i, i, ))
            if arule.Field.FieldTID == mt_DateTime:
                s = ' language=javascript onchange="return condselect_onchange(this,\'dropdowno%d\')"' % (i, )
            else:
                s = ''
            file.write('<SELECT id=condselect%d name=condselect%d %s>\n' % (i, i, s))
            for acondid in scnl:
                if acondid == arule.Condition:
                    s1 = 'SELECTED '
                else:
                    s1 = ''
                s = '<OPTION %svalue="%d">%s</OPTION>\n' % (s1, acondid, SummaryConditionsAsStringWWW[acondid])
                file.write(s)
            file.write('</SELECT>\n')
            file.write('<INPUT type="text" class=datepicker id=rulevalue%d name=rulevalue%d size="24" value="%s">\n' % (i, i, arule.RuleValue))
            #         if arule.Field.FieldTID==mt_DateTime:
            #            file.write('<IMG alt="wybór daty" id=dateselectiondiv2%d src="images/icon_calendar2.png" style="cursor:pointer;" onclick="showPopupDT(rulevalue%d,dateselectiondiv2%d);">\n'%(i,i,i))
            #            if arule.Condition==scEqual:
            #               sv='visible'
            #            else:
            #               sv='hidden'
            #            file.write('<IMG alt="wybór zakresu dat" id="dropdowno%d" src="images/icon_selectitem.png" style="cursor:pointer;visibility:%s" onmousedown="showPopupDR(rulevalue%d,dropdowno%d)">\n'%(i,sv,i,i))
            if not arule.Field.FieldTID in [mt_Boolean, mt_Memo]:
                foid = arule.Field.GetFirstValueID()
                l, lv, w = [], '', 1
                while foid >= 0:
                    s = arule.Field[foid]
                    if s and s != lv:
                        l.append(s)
                        if len(l) > 500:
                            w = 0
                            break
                        lv = s
                    foid = arule.Field.GetNextValueID(foid)
                if w and l:
                    if len(l) < 10:
                        dh = len(l) * 20
                    else:
                        dh = 200
                    file.write('<IMG alt="podgląd wartości" id="previewrule%d" src="images/icon_preview.png" style="cursor:pointer;" onmousedown="showPopupPR(rulevalue%d,previewrule%d,previewrulecontent%d,%d)">\n' % (i, i, i, i, dh))
                    file.write('<DIV ID="previewrulecontent%d" STYLE="display:none;">\n' % i)
                    file.write('<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:%dpx; border-bottom:2px solid black;" >\n' % dh)
                    dd = {'fontsize': '8pt', 'rowheight': '20px', 'background': 'wheat', 'value': l[0]}
                    file.write('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;">%(value)s</DIV>' % dd)
                    for li in range(1, len(l)):
                        dd['value'] = l[li]
                        file.write('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">%(value)s</DIV>' % dd)
                    file.write('</div></DIV>\n')
            file.write('<BR>\n')
        file.write('</span></td></tr>\n')
        i = i + 1


#   i=0
#   for arule in asummary.RulesList:
#      if not arule.Condition in [scExisting,scNonExisting]:
#      i=i+1

#   fname=FilePathAsSystemPath(aICORWWWServerInterface.OutputPath+'SE_'+str(OID)+'.html')
#   if ICORUtil.FileExists(fname):
#      s='Zaznaczając to pole, zamiast tworzyć zestawienie od początku, system szybko wyświetli ostatnio wygenerowane zestawienie'
#      adate=asummary.LastCreated
#      if adate[0]>1990:
#         s=s+' (%s)'%(ICORUtil.tdatetime2fmtstr(adate))
#      s=s+'<BR><FONT COLOR="red">UWAGA! Jeśli od czasu ostatniej generacji, dane zostały zmienione, to nie będą one uzwględnione w zapamiętanym zestawieniu.</FONT>'
#      file.write('<BR><INPUT class=checkradio TYPE=CHECKBOX NAME=UseCached ID=UseCached VALUE="1">%s<BR>'%(s))
#      file.write('<SCRIPT LANGUAGE="JavaScript">document.getElementById("UseCached").checked=1;</SCRIPT>\n')
#   else:
#      file.write('<INPUT TYPE=HIDDEN NAME=UseCached ID=UseCached VALUE="0">%s<BR>'%(s))
#   file.write('Możesz wykorzystać <A target="other" href="office/ArkuszDoZestawien2.xls">ten arkusz</A>. ')
#   file.write('Jest w nim zawarte makro o nazwie GrupujWiersze, które automatycznie formatuje dane pochodzące z ICOR\'a<BR>')
    file.write('</table></br>\n')

    file.write('<INPUT TYPE=HIDDEN NAME=MIMEContentFileName ID=MIMEContentFileName VALUE="zestawienie.xls">')
    #   file.write('<INPUT TYPE=HIDDEN NAME=noscripttags ID=noscripttags VALUE="1">')
    #   file.write('<INPUT TYPE=HIDDEN NAME=nobodytags ID=nobodytags VALUE="1">')
    file.write('<INPUT TYPE=HIDDEN NAME=nodownloadtags ID=nodownloadtags VALUE="0">')
    file.write('<INPUT class=checkradio TYPE=CHECKBOX NAME=SimpleSummary ID=SimpleSummary VALUE="1">Pokaż zestawienie w formacie do wydruku.<BR>')
    #   file.write('<INPUT class=checkradio onclick="javascript:document.getElementById(\'nodownloadtags\').value=this.value;" TYPE=CHECKBOX NAME=MIMEExcel ID=MIMEExcel VALUE="1">Nagraj zestawienie na swój dysk w formacie Excel.<BR>')
    file.write('<br>')
    file.write('<BUTTON class="fg-button-single ui-state-default ui-corner-all uihover" language=javascript onclick="document.getElementById(\'summForm\').submit();">Pokaż zestawienie</BUTTON>\n')    #this.disabled=\'TRUE\'; #if (document.getElementById(\'MIMESave\').checked){window.location.reload();};
    file.write('</FORM>')
    return
