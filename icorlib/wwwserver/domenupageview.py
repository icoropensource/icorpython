# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.wwwmenu.menuutil import ICORWWWMenuItem
from CLASSES_Library_NetBase_WWW_Server_DoContentsView import *
from icorlib.wwwserver.icorwwwinterface import aICORWWWServerInterface
from CLASSES_Library_NetBase_WWW_Server_DoSummaryParameters import GenerateSummaryParameters
from CLASSES_Library_NetBase_WWW_Server_DoSummaryExecute import GenerateSummaryExecute
from CLASSES_Library_NetBase_WWW_Server_DoSiteMap import DoSiteMapReportNonVisibleMenus
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import cStringIO


def GenerateMenuAsPage(file, aoid, uid=0):
    amenu = ICORWWWMenuItem(0, aoid)
    if not amenu.IsVisibleByProfile(uid):
        return

    if amenu.ViewAs == 'MSWord-MenuTree':
        file.write("""
<SCRIPT LANGUAGE="JScript">
<!--
function doSubmit() {
   document.getElementById('raportform').submit()
   }
function treeNodeClick0() {
   var aelement=window.event.srcElement;
   var sdiv=aelement.getAttribute("mDIVID");
   var adiv=document.getElementById(sdiv);
   if (adiv.style.display=='none') {
      adiv.style.display='';
   } else {
      adiv.style.display='none'; 
   }
}
function firstTOCNumberSelect_onchange() {
   var si=document.getElementById('firstTOCNumber').selectedIndex;
   if (document.getElementById('firstTOCNumber').options(si).value=="-2") {
      document.getElementById('firstTOCValueBlock').style.display='';
   } else {
      document.getElementById('firstTOCValueBlock').style.display='none';
   }
}
-->
</SCRIPT>
""")
        file.write('<h2><img src="images/BS00877A.gif" alt="" valign="center"> Generowanie raportu</h2>')
        file.write('<h1><font color="navy">%s</font></h1>' % (amenu.Caption))
        file.write('<font color="green">UWAGA! Tworzenie raportu moze byc operacją czasochłonną.</font><br>')
        file.write('<form id=raportform METHOD="post" ACTION="icormain.asp?jobtype=reportsubmit&OID=%d&ReportOID=%d">\n' % (amenu.oid, -1))
        file.write('<INPUT TYPE=HIDDEN NAME=MIMEContentFileName ID=MIMEContentFileName VALUE="%s.doc">' % (amenu.Caption, ))
        file.write('<INPUT TYPE=HIDDEN NAME=noscripttags ID=noscripttags VALUE="1">')
        file.write("""
<INPUT class=checkradio TYPE=CHECKBOX NAME=MIMEWord ID=MIMEWord VALUE=1>Pokaż raport w formacie MS Word.<i><font color="blue" style="cursor:pointer;" onclick="treeNodeClick0();" mDIVID="div_0_1">&nbsp;&nbsp;Informacje...</font></i>
<div id="div_0_1" style="display:none;"><i>
W przypadku wykorzystywania Worda w wersji 2000 żadne dodatkowe operacje nie są potrzebne.
Jeśli korzystasz z Worda w wersji niższej upewnij się, że są zainstalowane tzw. Rozszerzenia WWW.
Można to łatwo sprawdzić: uruchom aplikację MS Word, a następnie spróbuj nagrać aktualnie edytowany
dokument jako stronę HTML. Jeśli możesz to zrobić, oznacza to, że w/w rozszerzenia są zainstalowane.
Druga uwaga odnosi się do treści dokumentów zapisanych w ICOR'ze. Jeśli podczas wprowadzania danych
był wykorzystywany MS Word w wersji 2000, a raport będzie generowany na komputerze z MS Word'em w wersji
niższej, wtedy generacja poprawnego raportu nie będzie możliwa. W takim przypadku raport należy wygenerować
na komputerze z zainstalowanym programem MS Word w wersji 2000.<BR>
Po zaznaczeniu tej opcji w oknie ICOR'a zostanie osadzony dokument Word'a. Aby pracować lokalnie z wygenerowanym
dokumentem należy przenieść go do programu MS Word poprzez schowek. Naciśnięcie klawiszy Ctrl+A zaznaczy
treść całego dokumentu, następnie wciśnięcie klawiszy Ctrl+C przekopiuje zawartość dokumentu do schowka.<BR>
Pamiętaj, aby nagrywając raport w formacie MS Word na swój dysk, na końcu nazwy pliku znajdowało się rozszerzenie .DOC - tylko wtedy dwukrotne kliknięcie na nagranym lokalnie
zestawieniu spowoduje otwarcie MS Word'a.<BR>
Uwaga! Jeśli korzystasz z Internet Explorera 5.5 koniecznie zainstaluj poprawki znajdujące się <a href="http://www.microsoft.com/windows/ie/download/ie55sp1.htm">na tej stronie</a>.
Bez tych poprawek IE 5.5 może mieć kłopoty z nagrywaniem raportów na dysk.
</i></div>
""")

        #      file.write("""<br><INPUT class=checkradio TYPE=CHECKBOX NAME=OpenInNewWindow ID=OpenInNewWindow VALUE=1><b>Pokaż zestawienie w nowym oknie.</b>
        #Po wybraniu tej opcji system otworzy nowe okno i skieruje wyniki raportu do tego okna. Wszystkie okienka są dostępne poprzez
        #przyciski na pasku zadań u dołu ekranu. UWAGA! Czasami zamiast raportu możesz zobaczyć dialog logowania - w takim przypadku oznacza to,
        #że ustawienia bezpieczeństwa Twojej przeglądarki nie są prawidłowo skonfigurowane - skontaktuj się z Administratorem.
        #<BR>""")

        file.write("""<br><INPUT class=checkradio TYPE=CHECKBOX NAME=showInfoPages ID=showInfoPages VALUE=1>Pokaż tylko opisy i komentarze.<i><font color="blue" style="cursor:pointer;" onclick="treeNodeClick0();" mDIVID="div_0_2">&nbsp;&nbsp;Informacje...</font></i>
<div id="div_0_2" style="display:none;"><i>
Jeśli zaznaczysz ten przełącznik w raporcie znajdą się jedynie opisy i komentarze, które zwykle mówią co na danej stronie/rozdziale ma się
znaleźć i w jakiej formie.<BR>
</i></div>

<BR><BR>
<SELECT ID=firstTOCNumber NAME=firstTOCNumber  onchange="return firstTOCNumberSelect_onchange()">
<OPTION VALUE="0" SELECTED>automatycznie</OPTION>
<OPTION VALUE="1">1</OPTION>
<OPTION VALUE="2">2</OPTION>
<OPTION VALUE="3">3</OPTION>
<OPTION VALUE="4">4</OPTION>
<OPTION VALUE="5">5</OPTION>
<OPTION VALUE="6">6</OPTION>
<OPTION VALUE="7">7</OPTION>
<OPTION VALUE="8">8</OPTION>
<OPTION VALUE="9">9</OPTION>
<OPTION VALUE="10">10</OPTION>
<OPTION VALUE="11">11</OPTION>
<OPTION VALUE="12">12</OPTION>
<OPTION VALUE="13">13</OPTION>
<OPTION VALUE="14">14</OPTION>
<OPTION VALUE="15">15</OPTION>
<OPTION VALUE="16">16</OPTION>
<OPTION VALUE="17">17</OPTION>
<OPTION VALUE="18">18</OPTION>
<OPTION VALUE="19">19</OPTION>
<OPTION VALUE="20">20</OPTION>
<OPTION VALUE="21">21</OPTION>
<OPTION VALUE="22">22</OPTION>
<OPTION VALUE="23">23</OPTION>
<OPTION VALUE="24">24</OPTION>
<OPTION VALUE="25">25</OPTION>
<OPTION VALUE="26">26</OPTION>
<OPTION VALUE="27">27</OPTION>
<OPTION VALUE="28">28</OPTION>
<OPTION VALUE="29">29</OPTION>
<OPTION VALUE="30">30</OPTION>
<OPTION VALUE="31">31</OPTION>
<OPTION VALUE="32">32</OPTION>
<OPTION VALUE="33">33</OPTION>
<OPTION VALUE="-1">bez automatycznej numeracji</OPTION>
<OPTION VALUE="-2">własny numer</OPTION>
</SELECT> Numer pierwszego rozdziału
<BR>
<DIV id="firstTOCValueBlock" style="display:none;">
<input type="edit" name="firstTOCValue" id="firstTOCValue" value="1.1">
</DIV>
""")
        file.write('<br><input TYPE="button" onclick="document.getElementById(\'MIMEClass\').value=\'\';doSubmit();" VALUE="  Generuj  " tabIndex=1>')
        file.write("""
<INPUT TYPE=HIDDEN NAME=MIMEClass ID=MIMEClass VALUE="">
&nbsp;&nbsp;&nbsp;&nbsp;
""")
        file.write('<input TYPE="button" onclick="document.getElementById(\'MIMEWord\').checked=true;document.getElementById(\'MIMEClass\').value=\'application/save\';doSubmit();" VALUE="  Generuj do pliku " tabIndex=2>')
        file.write('</form>\n')

        file.write("""
<br>
<b>Lista rozdziałów w raporcie:</b><i><font color="blue" style="cursor:pointer;" onclick="treeNodeClick0();" mDIVID="div_0_3">&nbsp;&nbsp;Informacje...</font></i><BR>
<div id="div_0_3" style="display:none;"><i>
Poniżej znajduje się lista rozdziałów zawartych w generowanym raporcie. Pozycje wyróżnione
oznaczają, że dany podrozdział może zawierać treści, które mogą nie zostać prawidłowo
rozpoznane podczas konwersji do formatu MS Word. W takim przypadku należy wybrać wyróżniony
podrozdział, a następnie przenieść jego zawartość poprzez schowek (ang. clipboard) do uprzednio
wygenerowanego raportu. Treścią nierozpoznawalną dla konwertera w MS Word mogą być np. wykresy.
W szczególności wykresy można kopiować do dokumentu w MS Word za pomocą instrukcji 'Wklej specjalnie'.
W takim przypadku mamy możliwość wstawienia wykresu w postaci obrazka lub w formacie wektorowym.
Format wektorowy jest formatem preferowanym, ze względu na możliwość dowolnego powiększania/pomniejszania
bez utraty jakości. Przed skopiowaniem wykresu do schowka, należy się upewnić, czy wszystkie istotne
elementy wykresu są widoczne (legenda, opisy kolumn bądź kategorii). Czasami, gdy w wykresie
występują długie opisy, część elementów może być ukryta. Rozwiązaniem jest powiększenie wykresu
za pomocą strzałek znajdujących się w lewym górnym rogu wykresu.<BR>
</i></div>
<br>
""")
        for rmenu in amenu.ReferredMenu:
            DoSiteMapReportNonVisibleMenus(rmenu, file)

        return

    file.write('<center><P class=menuaspagecaption>%s</P>\n' % amenu.AsPageCaption)
    file.write('<P class=menuaspagesubcaption>%s</P></center>\n' % amenu.AsPageSubCaption)
    s = amenu.AsPageDescription
    if s != '':
        file.write('<p>%s</p>\n' % s)
    if amenu.SubMenus != []:
        file.write('<hr>\n')
        file.write('<table>\n')
        i = 1
        for smenu in amenu.SubMenus:
            if not smenu.IsVisibleByProfile(uid):
                continue
            file.write('<tr><td><a class="fg-button-single ui-state-default ui-corner-all uihover" ')
            file.write(' HREF="%s" ' % smenu.GetMenuRef())
            s = smenu.AsPageSubCaption
            if s != '':
                s = smenu.AsPageCaption + ' ' + s
            else:
                s = smenu.AsPageCaption
            file.write('>%d. %s</a></td>\n' % (i, s))
            file.write('<td>%s</td></tr>\n' % smenu.AsPageShortDescription)
            i = i + 1
        file.write('</table>\n')

    if amenu.Action in ['ObjectAdd', 'ObjectEdit', 'ObjectDelete']:
        mname = amenu.ParamItem
        mname = mname.replace('\\', '_')
        mname = mname.replace('/', '_')
        mclass = aICORDBEngine.Classes[mname]
        try:
            pagemethod = __import__(mname + '_OnWWWAction')
            pageevent = getattr(pagemethod, 'OnWWWAction')
            if pageevent is not None:
                apply(pageevent, (mclass, amenu, file))
        except:
            print 'Error during default menu action:', amenu.Action, ' - ', mname + '_OnWWWAction'
            raise

    s = amenu.PageHTMLInfo
    if s != '':
        file.write(s)
    s = amenu.PageHTML
    if s != '':
        file.write('<hr>' + ICORUtil.GetTextAsHTMLText(s, aengine=aICORDBEngine))

    sref = amenu.Summaries
    while sref:
        file.write('<hr>')
        #      file.write('<h1>'+sref.Name[sref.OID]+'</h1>\n')
        soid = sref.Summary[sref.OID]
        try:
            soid = int(soid)
        except:
            soid = -1
        fname = FilePathAsSystemPath(aICORWWWServerInterface.OutputPath + 'SE_' + str(soid) + '.html')
        if 1 or not ICORUtil.FileExists(fname):
            bfile = open(fname, 'w')
            try:
                if soid >= 0:
                    if sref.ShowParameters.ValuesAsInt(sref.OID):
                        GenerateSummaryParameters(bfile, soid)
                    else:
                        GenerateSummaryExecute(bfile, soid)
            finally:
                bfile.close()
        bfile = open(fname, 'r')
        try:
            file.write(bfile.read())
        finally:
            bfile.close()

        wref = sref.WorksheetQueries.GetRefList(sref.OID)
        while wref:
            file.write(wref.Class.TextAsHTML[wref.OID])
            wref.Next()

        mname = sref.CustomPageByMethod[sref.OID]
        if mname != '':
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            pagemethod = __import__(mname)
            pageevent = getattr(pagemethod, 'DoCustomPageByMethod')
            aparam = sref.Parameter[sref.OID]
            if pageevent is not None:
                apply(pageevent, (file, amenu, uid, aparam))
        sref.Next()

    if amenu.IsVisibleForEdit(uid):
        #      eref=amenu.GetMenuRef(aedit=1,amode='',nobodytags=1,noscripttags=1)
        #      if eref!='':
        #        file.write('<hr><a class=reflistoutnavy ')
        #         file.write(' HREF="%s">Edycja</a> ' % eref)
        #
        #         fref='icormain.asp?jobtype=objectedit&CID=%d&OID=%d'%(amenu.MenuClass.CID,amenu.oid)
        #         file.write(' | <a class=reflistoutnavy ')
        #         file.write(' HREF="%s">Edycja HTML (1)</a> ' % fref)
        ameoid = -1
        mobj = amenu.MenuClass.GetWWWMenuRefs().AsObject()
        while mobj:
            if mobj.Action.Name == 'ObjectEdit':
                ameoid = mobj.OID
            mobj.Next()
        if ameoid >= 0:
            fref = 'icormain.asp?jobtype=menuitem&OID=%d&param=%d_%d_' % (ameoid, amenu.MenuClass.CID, amenu.oid)
            file.write('<hr><a class="fg-button-single ui-state-default ui-corner-all uihover" href="%s">Edycja strony</a> ' % fref)


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    if OID < 0:
        return


#   fname=FilePathAsSystemPath(aICORWWWServerInterface.OutputPath+'MPV_'+str(OID)+'.html')
#   file=open(fname,'wb')
    file = cStringIO.StringIO()
    GenerateMenuAsPage(file, OID, UID)
    return file.getvalue()
