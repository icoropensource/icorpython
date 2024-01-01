# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import appplatform.startutil as startutil
import icorlib.icorsecurity as ICORSecurity
import string
import re

import appplatform.storageutil as storageutil

DEFAULTS = {'UI_SKIN': 'redmond', }


def GetScriptCSS():
    atext = '''<link rel=STYLESHEET type="text/css" href="/icormanager/icor.css" title="SOI">
<!--[if IE]>
<link rel=STYLESHEET type="text/css" href="/icormanager/icor_ie.css" title="SOI">
<![endif]-->
'''
    return atext


def GetScriptHeader(aheadertext='', asasp=1):
    if asasp:
        auiskin = '<%=Dession("UI_SKIN")%>'
    else:
        auiskin = DEFAULTS['UI_SKIN']
        auid = GetUID()
        if auid >= 0:
            aprofile = ICORSecurity.ICORSecurityProfile()
            aprofile.SetByUser(auid)
            auiskin = aprofile.GetParam('UI_SKIN', auiskin)
    atext = '''<script type="text/javascript">
function isIE(){return false;}
</script>
<!--[if IE]>
<script type="text/javascript">
function isIE(){return true;}
</script>
<![endif]-->
<script type="text/javascript" src="/icorlib/jquery/jquery-latest.min.js"></script>
<link rel="stylesheet" type="text/css" href="/icorlib/jquery/plugins/ui-1.8.14/css/%s/jquery-ui-1.8.14.custom.min.css">
<script type="text/javascript" src="/icorlib/jquery/plugins/ui-1.8.14/js/jquery-ui-1.8.14.custom.js"></script>
<link rel="stylesheet" href="/icorlib/jquery/plugins/ui-1.8.14/css/fixbadstyles.css" type="text/css">
<script type="text/javascript" src="/icorlib/jquery/plugins/metadata/jquery.metadata.js"></script>
<script type="text/javascript" src="/icorlib/jquery/plugins/dataTables/media/js/jquery.dataTables.js"></script>

<script type="text/javascript" src="/icorlib/jquery/plugins/form/jquery.form.js"></script>

<script type="text/javascript" src="/icorlib/jquery/plugins/jqModal/jqModal.js"></script>
<script type="text/javascript" src="/icorlib/jquery/plugins/jqDnR/jqDnR.js"></script>
<script type="text/javascript" src="/icorlib/jquery/plugins/jqGrid371/js/i18n/grid.locale-pl_win.js"></script>
<script type="text/javascript" src="/icorlib/jquery/plugins/jqGrid371/js/jquery.jqGrid.js"></script>
<link rel="stylesheet" href="/icorlib/jquery/plugins/jqModal/jqModal.css" type="text/css" media="screen">
<link rel="stylesheet" href="/icorlib/jquery/plugins/jqGrid371/css/ui.jqgrid.css" type="text/css" media="screen">
<script type="text/javascript" src="/icorlib/jquery/plugins/ajaxManager/jquery.ajaxmanager.js"></script>

<link rel="stylesheet" href="/icorlib/jquery/plugins/auto-complete/jquery.auto-complete.css" type="text/css" media="screen">
<script type="text/javascript" src="/icorlib/jquery/plugins/auto-complete/jquery.auto-complete.js"></script>

<script type="text/javascript" src="/icorlib/jquery/plugins/validate_1.7/jquery.validate.js"></script>

<script type="text/javascript" src="/icormanager/inc/icor_migrate.js"></script>

<style type="text/css">
label { width: 10em; float: left; }
input.error { border: 1px solid red; }

label.error {
   float: none; 
   color: red; 
   vertical-align: top; 
   background: url('/icorlib/jquery/plugins/validate_1.7/demo/images/unchecked.gif') no-repeat;
   padding-left: 16px;
   margin-left: .3em;
}
label.valid {
   float: none; 
   vertical-align: top; 
   background: url('/icorlib/jquery/plugins/validate_1.7/demo/images/checked.gif') no-repeat;
   display: block;
   width: 16px;
   height: 16px;
}
</style>
<script type="text/javascript" src="/icorlib/jquery/plugins/keyfilter/jquery.keyfilter-1.7.js"></script>
<script type="text/javascript" src="/icorlib/validation/email_check.js"></script>
<script type="text/javascript" src="/icorlib/validation/iban_check.js"></script>
<script type="text/javascript">
function IsValidDate(Yr,Mn,Day){
   var dt = new Date(Yr,Mn-1,Day);
   if(dt.getDate()!=Day){
       return(false);
       }
   else if(dt.getMonth()!=Mn-1){
       return(false);
       }
   else if(dt.getFullYear()!=Yr){
       return(false);
       }
   return(true);
}

function checkStrDate(asdate) {
   var re=new RegExp("^(\\\\d{4,4})[\\\\\\\\\\/\\-](\\\\d{1,2})[\\\\\\\\\\/\\-](\\\\d{1,2})$",'gim');
   var arr=re.exec(asdate);
   if (arr==null) {
      return false;
   }
   return IsValidDate(arr[1],arr[2],arr[3]);
}

jQuery(function(){
/*
   jQuery.validator.setDefaults({
      ignore: "[type=file]",
      debug: false
   });
*/
   jQuery.extend(jQuery.validator.messages, {
         required: "To pole jest wymagane.",
         remote: "Proszę o wypełnienie tego pola.",
         email: "Proszę wprowadzić poprawny adres e-mail.",
         url: "Proszę wprowadzić poprawny URL.",
         date: "Proszę wprowadzić poprawną datę.",
         dateISO: "Proszę wprowadzić poprawną datę (ISO).",
         dateDE: "Proszę wprowadzić poprawną datę.",
         number: "Proszę wprowadzić poprawną liczbę.",
         digits: "Proszę o podanie samych cyfr.",
         creditcard: "Proszę o podanie prawidłowej karty kredytowej.",
         numberDE: "Proszę wprowadzić poprawną liczbę.",
         digits: "Proszę wprowadzić tylko cyfry.",
         creditcard: "Proszę wprowadzić poprawny numer karty płatniczej.",
         equalTo: "Proszę wprowadzić ponownie poprawną wartość.",
         accept: "Proszę wprowadzić poprawne rozszerzenie.",
         maxLength: jQuery.validator.format("Proszę wprowadzić wartość, nie dłuższą niż {0} znaków."),
         minLength: jQuery.validator.format("Proszę wprowadzić wartość, nie krótszą niż {0} znaków."),
         rangeLength: jQuery.validator.format("Proszę wprowadzić wartość, o długości pomiędzy {0} a {1} znaków."),
         rangeValue: jQuery.validator.format("Proszę wprowadzić wartość, w zakresie pomiędzy {0} a {1}."),
         range: jQuery.validator.format("Proszę o podanie wartości z przedziału od {0} do {1}."),
         maxValue: jQuery.validator.format("Proszę wprowadzić wartość, mniejszą lub równą {0}."),
         minValue: jQuery.validator.format("Proszę wprowadzić wartość, większą lub równą {0}."),
         max: jQuery.validator.format("Proszę o podanie wartości mniejszej bądź równej {0}."),
         min: jQuery.validator.format("Proszę o podanie wartości większej bądź równej {0}.")
   });

   jQuery.validator.addMethod("iban",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      return checkIBAN(value);
   }, 'Proszę wprowadzić poprawny numer rachunku bankowego (same cyfry, bez kresek).');
   jQuery.validator.addMethod("emailCheck",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      return emailCheck(value);
   }, 'Proszę wprowadzić poprawny adres email.');   
   jQuery.validator.addMethod("myFilter",function(value,element,params) {
      if (this.optional(element)) {
         return true;
      }
      myregexp=new RegExp('^'+params+'*$','gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną wartość.');
   jQuery.validator.addMethod("myRegexp",function(value,element,params) {
      if (this.optional(element)) {
         return true;
      }
      if (params[0]!='^') {
         params='^'+params+'$';
      }
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną wartość.');
   jQuery.validator.addMethod("mySignedInteger",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^(\\\\d|-)?\\\\d*$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną liczbę całkowitą.');
   jQuery.validator.addMethod("myInteger",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^\\\\d*$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną liczbę całkowitą.');
   jQuery.validator.addMethod("mySignedNumeric",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^(\\\\d|-)?\\\\d*[\\\\.\\\\,]?\\\\d*$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną liczbę.');
   jQuery.validator.addMethod("myNumeric",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^\\\\d*[\\\\.\\\\,]?\\\\d*$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną liczbę.');
   jQuery.validator.addMethod("mySignedMoney",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^(\\\\d|-)?\\\\d*[\\\\.\\\\,]?\\\\d{1,2}$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną kwotę.');
   jQuery.validator.addMethod("myMoney",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      params='^\\\\d*[\\\\.\\\\,]?\\\\d{1,2}$'
      myregexp=new RegExp(params,'gim');
      return myregexp.test(value);
   }, 'Proszę wprowadzić poprawną kwotę.');
   jQuery.validator.addMethod("myDate",function(value,element) {
      if (this.optional(element)) {
         return true;
      }
      return checkStrDate(value);
   }, 'Proszę wprowadzić poprawną datę.');
});
</script>

<script type="text/javascript">
ltabscontainer=[];
lEditorsInit=[];
jQuery(function(){
   jQuery.ajaxSetup({
      async:false,
      cache:false
   });
   jQuery.maxZIndex = jQuery.fn.maxZIndex = function(opt) {
    /// <summary>
    /// Returns the max zOrder in the document (no parameter)
    /// Sets max zOrder by passing a non-zero number
    /// which gets added to the highest zOrder.
    /// </summary>
    /// <param name="opt" type="object">
    /// inc: increment value,
    /// group: selector for zIndex elements to find max for
    /// </param>
    /// <returns type="jQuery" />
    var def = { inc: 10, group: "*" };
    jQuery.extend(def, opt);
    var zmax = 0;
    jQuery(def.group).each(function() {
      var cur = parseInt(jQuery(this).css('z-index'));
      zmax = cur > zmax ? cur : zmax;
    });
    if (!this.jquery)
      return zmax;
    return this.each(function() {
      zmax += def.inc;
      jQuery(this).css("z-index", zmax);
    });
   }
   jQuery.datepicker.setDefaults({
      buttonImage: '/icorimg/silk/calendar.png',
      changeMonth: true,
      changeYear: true,
      closeText:'Zamknij',
      constrainInput: true,
      currentText: 'Dziś', 
      dateFormat: 'yy/mm/dd',
      dayNames: ['Niedziela','Poniedziałek','Wtorek','Środa','Czwartek','Piątek','Sobota'],
      dayNamesMin:['Ni','Po','Wt','Śr','Cz','Pi','So'],
      dayNamesShort:['Nie','Pon','Wto','Śro','Czw','Pią','Sob'],
      monthNames:['Styczeń','Luty','Marzec','Kwiecień','Maj','Czerwiec','Lipiec','Sierpień','Wrzesień','Październik','Listopad','Grudzień'],
      monthNamesShort:['Sty','Lut','Mar','Kwi','Maj','Cze','Lip','Sie','Wrz','Paź','Lis','Gru'],
      nextText:'Następny',
      prevText:'Poprzedni',
      duration:'fast',
      firstDay:1,
      gotoCurrent:true,
      showButtonPanel:true,
      yearRange: '-20:+20',
      beforeShow: function() {jQuery('#ui-datepicker-div').maxZIndex();}
   });
});

function makeTable(aid) {
   ret=jQuery(aid).dataTable({
      'bJQueryUI':true,
      'bRetrieve':true,
      'bSort': true,
      'sPaginationType':'full_numbers',
      'iDisplayLength': 25,
      'aLengthMenu': [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "wszystkie"]],
      'oLanguage':{
         'sLengthMenu':'Wyświetl _MENU_ pozycji na stronę',
         'sZeroRecords':'Brak danych..',
         'sInfo':'Pozycje od _START_ do _END_ z _TOTAL_ dostępnych',
         'sInfoEmpty':'Pozycje od 0 do 0 z 0 dostępnych',
         'sInfoFiltered':'(filtr z _MAX_ dostępnych pozycji)',
         'sInfoPostFix':'',
         'sProcessing':'W trakcie obliczeń..',
         'sSearch':'Znajdź w/g filtra:',
         'oPaginate': {
            'sFirst':'Pierwsza',
            'sLast':'Ostatnia',
            'sNext':'Następna',
            'sPrevious':'Poprzednia'
         }
      },
      'asStripClasses':['ui-widget-content','ui-widget-content'],
      'sDom':'<"top"i>rt<"bottom"flp><"clear">'
   });
   return ret;
}

</script>
''' % (auiskin, )
    apatt1 = re.compile('''\<script.*?src\=.(.+?)[\"\']''', re.I)
    apatt2 = re.compile('''\<link.*?href\=.(.+?)[\"\']''', re.I)
    l = aheadertext.split('\n')
    for aline in l:
        m = apatt1.search(aline)
        w = 1
        if m:
            asrc = m.group(1)
            if atext.find(asrc) >= 0:
                w = 0
            if w:
                asrc = asrc[:-2] + 'min.js'
                if atext.find(asrc) >= 0:
                    w = 0
        else:
            m = apatt2.search(aline)
            if m:
                asrc = m.group(1)
                if atext.find(asrc) >= 0:
                    w = 0
                if w:
                    asrc = asrc[:-3] + 'min.css'
                    if atext.find(asrc) >= 0:
                        w = 0
        if w and aline.strip():
            atext = atext + aline + '\n'
    return atext


def GetScriptInit():
    atext = '''<script type="text/javascript">
jQuery(function(){
   jQuery("body").append("<div id='mdiv1' class='ui-widget ui-widget-content'></div>");
   var el=jQuery("#mdiv1");
   var abc=el.css("background-color");
   jQuery("html").css("background-color",abc);
   jQuery("body").css("background-color",abc);
   el.remove();

   jQuery(".objectsviewtable").addClass("ui-widget");
   jQuery(".objectsviewheader").addClass("ui-widget-header");
   jQuery(".objectsviewrow").addClass("ui-state-default");
   //all hover and click logic for buttons
   jQuery(".fg-button:not(.ui-state-disabled)")
   .hover(
      function(){ 
         jQuery(this).addClass("ui-state-hover");
      },
      function(){ 
         jQuery(this).removeClass("ui-state-hover");
      }
   )
   .mousedown(function(){
         jQuery(this).parents('.fg-buttonset-single:first').find(".fg-button.ui-state-active").removeClass("ui-state-active");
         if( jQuery(this).is('.ui-state-active.fg-button-toggleable, .fg-buttonset-multi .ui-state-active') ){ jQuery(this).removeClass("ui-state-active"); }
         else { jQuery(this).addClass("ui-state-active"); }
   })
   .mouseup(function(){
      if(! jQuery(this).is('.fg-button-toggleable, .fg-buttonset-single .fg-button,  .fg-buttonset-multi .fg-button') ){
         jQuery(this).removeClass("ui-state-active");
      }
   });
});
jQuery(function(){
   jQuery('.ui-state-default').hover(
      function(){ jQuery(this).addClass('ui-state-hover'); }, 
      function(){ jQuery(this).removeClass('ui-state-hover'); }
   );
   jQuery('.ui-state-default').click(function(){
      jQuery(this).toggleClass('ui-state-active');
   });
});
jQuery(function(){
   jQuery('.uihover').hover(
      function() { jQuery(this).addClass('ui-state-hover'); },
      function() { jQuery(this).removeClass('ui-state-hover'); }
   );
});
</script>
<script type="text/javascript">
function getBaseURL(aurl) {
  if ((aurl.search('http:') === 0) || (aurl.search('https:') === 0)) {
    return aurl;
  }
  var loc = window.location;
  var baseURL = loc.protocol + "//" + loc.hostname;
  if (typeof loc.port !== "undefined" && loc.port !== "") {
    baseURL += ":" + loc.port;
  }
  var pathname = loc.pathname;
  if (pathname.length > 0 && pathname.substr(0,1) === "/") {
    pathname = pathname.substr(1, pathname.length - 1);
  }
  var pathParts = pathname.split("/");
  if (pathParts.length > 0) {
    for (var i = 0; i < (pathParts.length-1); i++) {
      if (pathParts[i] !== "") {
        baseURL += "/" + pathParts[i];
      }
    }
  }
  if (aurl !== '') {
    baseURL += "/" + aurl;
  }
  return baseURL;
}
jQuery(function(){
   jQuery('.elclickredirect').live('click',function(){
      var aurl=jQuery(this).attr('data-url');
      var ahref=aurl+'&__nt=1'
      var abaseurl=getBaseURL(ahref)
      window.parent.postMessage({
         type: 'setIframeTextSrc',
         ownerTab: window.ownerTab,
         ownerSheet: window.ownerSheet,
         href: abaseurl
      }, '*');
      return false
   });

   jQuery('.objectitemasanchor').live('click',function(){
      var $el=jQuery(this)
      var ahref=$el.attr('href')+'&__nt=1'
      var abaseurl=getBaseURL(ahref)
      window.parent.postMessage({
         type: 'setIframeTextSrc',
         ownerTab: window.ownerTab,
         ownerSheet: window.ownerSheet,
         href: abaseurl
      }, '*');
      return false
   });
});
</script>
<script type="text/javascript">
jQuery(function(){
   jQuery('.datepicker').datepicker({
      buttonImageOnly: true,
      showOn: 'button'
   });
   jQuery("#ui-datepicker-div").css("top","-21474836px");
});
function FCKeditor_OnComplete(editorInstance){
   for (i in lEditorsInit) {
      lEditorsInit[i]();
   }
}
/*
jQuery(function() {
  jQuery(".searchableselect").searchable({
    maxListSize: 500,
    maxMultiMatch: 100,
    exactMatch: false,
    wildcards: true,
    ignoreCase: true,
    latency: 100,
    warnMultiMatch: 'pierwsze {0}...',
    warnNoMatch: 'brak...',
    zIndex: 'auto'
  });
});
*/
</script>
'''
    return atext


def WriteDefIncMeta(file, anocache=1, anodownloadtags=0):
    file.write('<meta http-equiv="X-UA-Compatible" content="IE=8">')
    file.write('<meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8">')
    file.write('<meta http-equiv="Content-Language" content="pl">')
    file.write('<meta name="description" content="Opis strony">')
    if anocache:
        file.write('<META NAME="Pragma" CONTENT="no-cache">')
        file.write('<META NAME="Cache-Content" CONTENT="no-cache">')
        file.write('<META HTTP-EQUIV="Pragma" CONTENT="no-cache">')
        file.write('<META HTTP-EQUIV="Cache-Content" CONTENT="no-cache">')
        file.write('<META HTTP-EQUIV="Expires" CONTENT="-1">')
    file.write('<meta name="keywords" content="ICOR object oriented database WWW information management repository">')
    file.write('<meta name="author" content="%s">'%(startutil.appconfig.IParams['meta_author'],))
    if not anodownloadtags:
        file.write(GetScriptCSS())
        file.write(GetScriptHeader(asasp=0))


#   file.write('<?IMPORT namespace="t" implementation="#default#time2">')


def WriteAlwaysInFrame(file):
    return
    file.write("""
<script language="javascript">
if (parent.frames.length==0)
   window.location.replace("default.asp");
</script>
""")


def DoGetFieldVersions(file, aclass, afield, afieldid, aoid):
    if aoid < 0:
        return
    ret = []
    l, w = [], 1
    amemo = 0
    if afield.IsMemo:
        amemo = 1
    if 1:
        lv = afield.GetFieldVersions(aoid)
        v = lv[3].get('v' + afield.FName, '')
        v = storageutil.UTF8_To_CP1250(v)
        l.append([l[1], v])

    if 0:
        i = 0
        aoff = afield.GetFirstDeletedOffset()
        while aoff >= 0:
            avalue = afield.GetRecValueAsString(aoff)
            boid = afield.GetRecOID(aoff)
            if boid >= 0 and boid == aoid and avalue and avalue != 'Error!':
                if len(l) > 500:
                    break
                adt = afield.GetRecLastModification(aoff)
                alm = ICORUtil.tdate2fmtstr(adt, delimiter='-', longfmt=1) + ' ' + ICORUtil.ttime2fmtstr(adt, longfmt=1, delimiter=':')
                l.append([adt, alm, avalue])
                i = i + 1
            aoff = afield.GetNextDeletedOffset(aoff)
    adt = afield.GetValueLastModified(aoid)
    alm = ICORUtil.tdate2fmtstr(adt, delimiter='-', longfmt=1) + ' ' + ICORUtil.ttime2fmtstr(adt, longfmt=1, delimiter=':')
    avalue = afield[aoid]
    l.insert(0, [alm, avalue])
    if l:
        dd = {'value': '&nbsp;', }
        for adm, avalue in l:
            dd['adm'] = adm
            dd['valuexml'] = XMLUtil.GetAsXMLStringNoPL(avalue)
            if not amemo:
                dd['value'] = avalue
            ret.append('<div class="versionClick" versionValue="%(valuexml)s"><div>%(adm)s</div><div>%(value)s</div></div><hr>' % dd)
    file.write(string.join(ret, ''))
    return


def DoGetFieldValues(file, aclass, afield, afieldid, aoid):
    ret = []
    l, w = [], 1
    foid = afield.GetFirstValueID()
    lv = ''
    while foid >= 0:
        s = afield[foid]
        if s and s != lv:
            l.append(s)
            if len(l) > 500:
                break
            lv = s
        foid = afield.GetNextValueID(foid)
    if w and l:
        if len(l) < 10:
            dh = len(l) * 20 + 4
        else:
            dh = 200
        ret.append('<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; border-bottom:2px solid black; width:300px; height:%dpx; " >\n' % dh)
        dd = {'fontsize': '8pt', 'rowheight': '20px', 'background': 'wheat', 'value': l[0]}
        ret.append('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;">%(value)s</DIV>' % dd)
        for li in range(1, len(l)):
            dd['value'] = l[li]
            ret.append('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">%(value)s</DIV>' % dd)
        ret.append('</div>\n')
    file.write(string.join(ret, ''))
    return


def DoGetFieldValuesAC(file, aclass, afield, afieldid, aoid):
    #   file.write('''[{"value":"absence"},{"value":"abundance"},{"value":"accessible"},{"value":"accidentally"},{"value":"acclaim"},{"value":"accommodate"},{"value":"accomplish"},{"value":"accordion"},{"value":"accumulate"},{"value":"achievement"}]''')
    #   return
    l, w = [], 1
    if aclass.IsMethodInClass('OnWWWAction'):
        mname = aclass.ClassPath + '_OnWWWAction'
        mname = mname.replace('\\', '_')
        mname = mname.replace('/', '_')
        pagemethod = __import__(mname)
        if pagemethod is not None:
            pageevent = getattr(pagemethod, 'OnWWWGetFieldAutoCompleteValues', None)
            if pageevent is not None:
                aobj = aclass[aoid]
                ret = apply(pageevent, (aobj, afield))
                if ret is not None:
                    w = 0
                    if type(ret) == type(1):
                        w = ret
                    else:
                        if isinstance(ret, ICORDBObject):
                            dobj = ret
                            d = {}
                            while dobj:
                                d[afield[dobj.OID]] = 1
                                dobj.Next()
                            ret = d.keys()
                            ret.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
                        l = ['{"value":"%s"}' % (XMLUtil.GetAsXMLStringNoPL(s)) for s in ret]
    if w:
        ret = []
        foid = afield.GetFirstValueID()
        lv = ''
        while foid >= 0:
            s = afield[foid]
            if s and s != lv:
                l.append('{"value":"%s"}' % (XMLUtil.GetAsXMLStringNoPL(s)))
                if len(l) > 500:
                    break
                lv = s
            foid = afield.GetNextValueID(foid)
    file.write('[' + ','.join(l) + ']')
    return


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    ret = []
    if Value == 'FieldPreview':
        aFieldName, aFieldID = string.split(FieldName, ':')
        aclass = aICORDBEngine.Classes[OID]
        afield = aclass.FieldsByName(aFieldName)
        l, w = [], 1
        if afield is not None:
            foid = afield.GetFirstValueID()
            lv = ''
            while foid >= 0:
                s = afield[foid]
                if s and s != lv:
                    l.append(s)
                    if len(l) > 200:
                        break
                    lv = s
                foid = afield.GetNextValueID(foid)
        if w and l:
            if len(l) < 10:
                dh = len(l) * 20 + 4
            else:
                dh = 200
            ret.append('&nbsp;<IMG alt="podgląd wartości" id="previewrule%s" src="images/icon_preview.png" style="cursor:pointer;" onmousedown="showPopupPR(%s,previewrule%s,previewrulecontent%s,%d)">\n' % (aFieldID, aFieldID, aFieldID, aFieldID, dh))
            ret.append('<DIV ID="previewrulecontent%s" STYLE="display:none;">\n' % aFieldID)
            ret.append('<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; border-bottom:2px solid black; width:300px; height:%dpx; " >\n' % dh)
            dd = {'fontsize': '8pt', 'rowheight': '20px', 'background': 'wheat', 'value': l[0]}
            ret.append('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;">%(value)s</DIV>' % dd)
            for li in range(1, len(l)):
                dd['value'] = l[li]
                ret.append('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">%(value)s</DIV>' % dd)
            ret.append('</div></DIV>\n')
    return string.join(ret, '')
