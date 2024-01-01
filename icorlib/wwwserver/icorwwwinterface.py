# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
from icorlib.icoriterators import FieldRefIterator
import appplatform.storageutil as storageutil
from CLASSES_Library_ICORBase_Interface_ICORUtil import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
from icorlib.wwwhtml.main import *
from icorlib.wwwhtml.worksheetmain import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import icorlib.icorsecurity as ICORSecurity
import icorlib.wwwhtml.getimageslist as GetImagesList
import icorwwwinterfaceutil as ICORWWWInterfaceUtil
import string
import types

# UWAGA! Trzeba to dolaczyc!
ifFormDirtyScript = """
function IsDirty(eForm)
{
  var iNumElems = eForm.elements.length;
  for (var i=0; i<iNumElems; i++)
  {
    var eElem = eForm.elements[i];
    if ("text" == eElem.type || "TEXTAREA" == eElem.tagName)
    {
      if (eElem.value != eElem.defaultValue) return true;
    }                               
    else if ("checkbox" == eElem.type || "radio" == eElem.type)
    {
      if (eElem.checked != eElem.defaultChecked) return true;
    }
    else if ("SELECT" == eElem.tagName)
    {
      var cOpts = eElem.options;
      var iNumOpts = cOpts.length;
      for (var j=0; j<iNumOpts; j++)
      {
        var eOpt = cOpts[j];
        if (eOpt.selected != eOpt.defaultSelected) return true;
      }
    }
  }
  return false;
}
"""

PERSISTENT_CLASSES = {'CLASSES\Library\NetBase\WWW\Dictionary\Named\ImageInfo': {'field': 'Location', 'sort': 'Name', 'mode': 'image', 'value': '', 'field64': 'Base64', 'filterlocation': 'silk'}, }


class ICORWWWInputField:

    def __init__(self, aeditor, afile, aclass, afield, adisplayed='', aoid=-1, atype=-1, avalue='', adescription='', acols=-1, arows=-1, aempty='', aactioneditdisable=0, adefaultcheck=0, aupdaterefs=0, aisunique=0, ahidden=0, afieldeditor='', ano_td1=0, ano_tr1=0, ano_td2=0, ano_tr2=0, atag='', adisabledefaultvalue=0, asheetname='', awwwsortable=0):
        self.Editor = aeditor
        self.file = afile
        self.ClassItem = aclass
        self.OID = aoid
        self.Cols = acols
        self.Rows = arows
        self.FieldType = atype
        self.FieldValue = avalue
        self.IfEmptyValue = aempty
        self.DefaultCheck = adefaultcheck
        self.ActionEditDisable = aactioneditdisable
        self.UpdateRefs = aupdaterefs
        self.NoTR1 = ano_tr1
        self.NoTR2 = ano_tr2
        self.NoTD1 = ano_td1
        self.NoTD2 = ano_td2
        self.Tag = atag
        self.DisableDefaultValue = adisabledefaultvalue
        self.SheetName = asheetname
        if self.FieldType < 0:
            if isinstance(afield, types.StringTypes):
                afield = self.ClassItem.FieldsByName(afield)
            self.Field = afield
            self.FieldTID = afield.FieldTID
            self.FieldID = self.Field.Name + '_' + str(self.Field.FOID)
            self.IsMemo = self.Field.IsMemo
            self.FieldNameAsDisplayed = self.Field.FieldNameAsDisplayed
            self.FieldEditor = self.Field.FieldEditor
            self.WWWSortable = self.Field.WWWSortable
            if adescription == '':
                self.Description = self.Field.FieldDescription
            else:
                self.Description = adescription
            self.IsUnique = self.Field.WWWUnique or aisunique
            if not avalue:
                self.FieldValue = self.Field.WWWDefaultValue
            if not self.DefaultCheck:
                self.DefaultCheck = ICORUtil.str2bool(self.Field.IsObligatory) or self.IsUnique
        else:
            self.Field = None
            if adisplayed is None:
                self.FieldNameAsDisplayed = ''
            else:
                self.FieldNameAsDisplayed = afield
            self.FieldTID = self.FieldType
            self.IsMemo = 0
            if self.FieldTID == mt_Memo:
                self.IsMemo = 1
            self.FieldID = afield
            self.Description = adescription
            self.IsUnique = aisunique
            self.FieldEditor = afieldeditor
            self.WWWSortable = awwwsortable
        if adisplayed != '' and adisplayed is not None:
            self.FieldNameAsDisplayed = adisplayed

        self.Report = None
        self.IsHidden = ahidden
        self.AutoHiddenField = 0
        self.OnSubmitFunctions = []

    def AsJSON(self):
        if self.ActionEditDisable:
            return
        ftype = 'text'
        if self.IsMemo:
            ftype = 'textarea'
        df = {
            'field': {
                'name': self.FieldID,
                'type': ftype,
                'icon': 'email',
                'label': storageutil.CP1250_To_UTF8(self.FieldNameAsDisplayed),
                'helper': storageutil.CP1250_To_UTF8(self.Description),
                'FieldTypeID': self.FieldTID,
                'IsMemo': self.IsMemo,
                'FieldEditor': self.FieldEditor,
                'IsHidden': self.IsHidden, },    # yapf: disable
            'validation': {
        #'required': True,
        #'maxLength': 44,
        #'email': True
            }    # yapf: disable
        }
        avalue = ''
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.FieldTID in [mt_Memo, mt_String]:
                if self.OID >= 0:
                    avalue = self.Field[self.OID]
                else:
                    if type(self.FieldValue) == type([]):
                        for aline in self.FieldValue:
                            avalue = avalue + str(aline) + '\n'
                    else:
                        avalue = self.FieldValue
                if self.DisableDefaultValue:
                    avalue = ''
            elif self.FieldTID == mt_Integer:
                if self.OID >= 0:
                    avalue = self.Field[self.OID]
                else:
                    avalue = self.FieldValue
                if self.DisableDefaultValue:
                    avalue = ''
            elif self.FieldTID == mt_Double:
                if self.OID >= 0:
                    avalue = self.Field[self.OID]
                else:
                    avalue = self.FieldValue
                if self.DisableDefaultValue:
                    avalue = ''
            elif self.FieldTID == mt_DateTime:
                if self.OID >= 0:
                    adate = self.Field.ValuesAsDateTime(self.OID)
                    if adate == ZERO_DATE:
                        avalue = tdate2fmtstr(tdatetime())
                    else:
                        avalue = tdate2fmtstr(adate)
                else:
                    if self.FieldValue == '':
                        avalue = tdate2fmtstr(tdatetime())
                    else:
                        if isinstance(self.FieldValue, types.StringTypes):
                            avalue = ICORUtil.getStrAsDate(self.FieldValue)
                            avalue = ICORUtil.tdate2fmtstr(avalue)
                        else:
                            avalue = self.FieldValue
                if self.DisableDefaultValue:
                    avalue = ''
            elif self.FieldTID == mt_Boolean:
                if self.OID >= 0:
                    if self.Field.ValuesAsInt(self.OID) > 0:
                        avalue = True
                    else:
                        avalue = False
                else:
                    if ICORUtil.str2bool(self.FieldValue):
                        avalue = True
                    else:
                        avalue = False
                if self.DisableDefaultValue:
                    avalue = False
        else:
            if self.FieldEditor == 'ObjectsList':
                avalue = self.Field[self.OID]
                #self.DoWriteInputObjectsListField()
            else:
                avalue = self.Field[self.OID]
                #self.DoWriteInputObjectsMultipleField()
        if type(avalue) == type(''):
            avalue = storageutil.CP1250_To_UTF8(avalue)
        return df, avalue

    def Write(self):
        if self.ActionEditDisable:
            return
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.FieldTID == mt_Memo:
                self.DoWriteInputMemoField()
            if self.FieldTID == mt_String:
                aeditor = 'TEXT'
                if self.FieldEditor == 'File':
                    aeditor = 'FILE'
                if self.IsHidden:
                    self.DoWriteInputHiddenField()
                elif self.IsMemo:
                    self.DoWriteInputMemoField()
                else:
                    self.DoWriteInputTextField(aeditor=aeditor)
            elif self.FieldTID == mt_Integer:
                self.DoWriteInputIntegerField()
            elif self.FieldTID == mt_Double:
                self.DoWriteInputFloatField()
            elif self.FieldTID == mt_DateTime:
                self.DoWriteInputDateField()
            elif self.FieldTID == mt_Boolean:
                self.DoWriteInputBoolField()
        else:
            if self.FieldEditor == 'ObjectsList':
                self.DoWriteInputObjectsListField()
            else:
                self.DoWriteInputObjectsMultipleField()

    def GetValue(self):
        s = self.Report.get(self.FieldID, '')
        if self.Editor.Menu.asJSON:    #$$
            if type(s) not in [type(''), type(u'')]:
                s = str(s)
        s = string.replace(s, chr(13), '')
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.IfEmptyValue and not s:
                s = self.IfEmptyValue
            return s
        else:
            if self.Editor.Menu.asJSON:    #$$
                return s
            if self.Field.FieldEditor == 'ObjectsList':
                if s and s != '-1':
                    return s + ':' + str(self.Field.ClassOfType.CID) + ':'
            else:
                l = []
                if 0:
                    aobj = self.Field.ClassOfType.GetFirstObject()
                    while aobj.Exists():
                        s = self.Report.get(self.FieldID + '_' + str(aobj.OID), '')
                        if s and s != '-1':
                            l.append(s + ':' + str(self.Field.ClassOfType.CID) + ':')
                        aobj.Next()
                else:
                    for akey in self.Report.keys():
                        sl = string.split(akey, '_')
                        akeyfield = ''
                        if len(sl) > 2:
                            akeyfield = sl[0] + '_' + sl[1]
                        if akeyfield == self.FieldID:
                            s = self.Report.get(akey, '')
                            if s and s != '-1':
                                l.append(s + ':' + str(self.Field.ClassOfType.CID) + ':')
                return string.join(l, '')
            return ''

    def GetRefList(self):
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            sref = ''
        else:
            sref = self.GetValue()
        return FieldRefIterator(sref)

    def Read(self):
        if self.Report.has_key(self.FieldID):
            self.file.write('<tr><td>' + self.FieldNameAsDisplayed + '</td><td>' + self.Report[self.FieldID] + '</td><td>' + self.Description + '</td></tr>\n')

    def Store(self, aobj, file=None, arefoid=-1, arefcid=-1):
        if self.Field is None:
            return
        if self.ClassItem.CID != aobj.Class.CID:
            print 'CID dla pola', self.Field.Name, 'jest rozny od CID modyfikowanego obiektu'
            return
        if self.FieldTID > MAX_ICOR_SYSTEM_TYPE:
            if not self.CheckAccessLevelView(aobj):
                return
            sv = self.GetValue()
            ov = self.Field[aobj.OID]
            if sv == ov:
                return
            tclass = self.Field.ClassOfType
            asecprofile = ICORSecurity.ICORSecurityProfile()
            if tclass.CID == asecprofile.ProfileClass.ItemGroups.ClassOfType.CID:
                asecprofile.SetByUser(self.Editor.Menu.uid)
                asecprofile.GetItemGroupsByUser()
                orefs = self.Field.GetRefList(aobj.OID)
                nrefs = FieldRefIterator(sv)
                ipos = 0
                for goid in asecprofile.ItemGroupsID.keys():
                    if nrefs.RefExists(goid):
                        if not orefs.RefExists(goid):
                            orefs.InsertRef(ipos, goid, tclass.CID)
                            ipos = ipos + 1
                    else:
                        orefs.DelRef(goid)
                orefs.Store()
            elif tclass.CID == asecprofile.ProfileClass.UserGroups.ClassOfType.CID:
                asecprofile.SetByUser(self.Editor.Menu.uid)
                asecprofile.GetUserGroups(aincludeuser=1)
                orefs = self.Field.GetRefList(aobj.OID)
                nrefs = FieldRefIterator(sv)
                ipos = 0
                for goid in asecprofile.GroupsID.keys():
                    if nrefs.RefExists(goid):
                        if not orefs.RefExists(goid):
                            orefs.InsertRef(ipos, goid, tclass.CID)
                            ipos = ipos + 1
                    else:
                        orefs.DelRef(goid)
                orefs.Store()
            else:
                fbackref, fupdaterefs = '', ''
                for bfname in tclass.GetFieldsList():
                    bfield = tclass.FieldsByName(bfname)
                    if bfield.WWWBackRefField and bfield.ClassOfType.CID == self.Field.CID:
                        fbackref = bfield
                    elif bfield.WWWUpdateRefs and bfield.ClassOfType.CID == self.Field.CID:
                        fupdaterefs = bfield
                if self.Field.WWWBackRefField and fupdaterefs:
                    self.Field.UpdateReferencedObjects(aobj.OID, fupdaterefs, adeleterefs=1, aupdaterefs=1)
                elif self.UpdateRefs and fbackref:
                    self.Field.UpdateReferencedObjects(aobj.OID, fbackref, adeleterefs=1, aupdaterefs=1)
                fclass = self.Field.ClassOfType
                orefs = self.Field.GetRefList(aobj.OID)
                nrefs = FieldRefIterator(sv)
                ret = orefs.AsRefsEmpty()
                fpos = -1
                ipos = 0
                for ooid, ocid in orefs.refs:
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(fclass[ooid], 'AccessLevelView', self.Editor.Menu.uid):
                        if fpos < 0:
                            fpos = ipos
                    else:
                        ret.AddRef(ooid, ocid)
                        ipos = ipos + 1
                if fpos < 0:
                    #fpos=len(ret)
                    fpos = 0    # uwaga - w tym scenariuszu obiekty z uprawnieniami maja priorytet nad juz przypisanymi obiektami bez praw dostepu
                for noid, ncid in nrefs.refs:
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(fclass[noid], 'AccessLevelView', self.Editor.Menu.uid):
                        ret.InsertRef(fpos, noid, ncid)
                        fpos = fpos + 1
                ret.Store()
                if self.Field.WWWBackRefField and fupdaterefs:
                    self.Field.UpdateReferencedObjects(aobj.OID, fupdaterefs, aupdaterefs=1)
                elif self.UpdateRefs and fbackref:
                    self.Field.UpdateReferencedObjects(aobj.OID, fbackref, aupdaterefs=1)
        elif self.FieldTID in [mt_Memo, mt_String, mt_Integer, mt_Double, mt_Boolean]:
            avalue = self.GetValue()
            #print 'STORE:',self.Field.Name,'>',avalue,'<',type(avalue)
            self.Field[aobj.OID] = avalue
        elif self.FieldTID == mt_DateTime:
            self.Field.SetValuesAsDate(aobj.OID, ICORUtil.getStrAsDate(self.GetValue()))
        else:
            print 'Nieznany typ dla pola:', self.Field.Name, self.FieldTID

    def GetFieldValidationText(self, aissearch=0):
        if aissearch:
            return ''
        ret = {'DISPLAY-NAME': ICORUtil.GetStringAsSafeScriptString(self.FieldNameAsDisplayed)}
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.FieldTID in [mt_Memo, mt_String]:
                pass
            elif self.FieldTID in [mt_Double, ]:
                if self.Field is not None and not self.Field.WWWUnsigned:
                    ret['SIGNED'] = '1'
                ret['FILTER'] = '[0-9\\.]'
                ret['FLOAT'] = '1'
            elif self.FieldTID in [mt_DateTime, mt_Date, ] and not aissearch:
                ret['FILTER'] = '[0-9/]'
                ret['DATE'] = 'YYYY/M/D'
            elif self.FieldTID in [mt_Integer, ]:
                if self.Field is not None and not self.Field.WWWUnsigned:
                    ret['SIGNED'] = '1'
                ret['FILTER'] = '[0-9]'
                ret['INTEGER'] = '1'
            else:
                pass
        if not aissearch:
            if self.DefaultCheck:
                ret['REQUIRED'] = '1'
            if self.Field is not None:
                if self.Field.WWWFilter:
                    ret['FILTER'] = self.Field.WWWFilter
                if self.Field.WWWRegex:
                    ret['REGEXP'] = self.Field.WWWRegex
                if self.Field.WWWMinValue:
                    ret['MIN'] = self.Field.WWWMinValue
                if self.Field.WWWMaxValue:
                    ret['MAX'] = self.Field.WWWMaxValue
        s = ''
        for akey in ret.keys():
            sv = ret[akey]
            if sv:
                s = s + akey + "='" + sv + "' "
            else:
                s = s + akey + ' '
        return s

    def DoWriteFieldPreviewValues(self, apreview=1, ahistory=1, afieldsonly=1):
        if type(self.FieldValue) == type([]) and afieldsonly:
            l = self.FieldValue
            if len(l) < 10:
                dh = len(l) * 20 + 4
            else:
                dh = 200
            self.file.write('&nbsp;<IMG alt="podgląd wartości" id="previewrule%s" src="images/icon_preview.png" style="cursor:pointer;" onmousedown="showPopupPR(%s,previewrule%s,previewrulecontent%s,%d)">\n' % (self.FieldID, self.FieldID, self.FieldID, self.FieldID, dh))
            self.file.write('<DIV ID="previewrulecontent%s" STYLE="display:none;">\n' % (self.FieldID, ))
            self.file.write('<div style="position:absolute; top:0; left:0; overflow:scroll; overflow-x:hidden; width:300px; height:%dpx; border-bottom:2px solid black;" >\n' % dh)
            dd = {'fontsize': '8pt', 'rowheight': '20px', 'background': 'wheat', 'value': l[0]}
            self.file.write('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px;  cursor:pointer;">%(value)s</DIV>' % dd)
            for li in range(1, len(l)):
                dd['value'] = l[li]
                self.file.write('<DIV ONCLICK="parent.dselectedelement.value=this.innerText;parent.drPopup.hide();" onmouseover="this.style.background=\'#ffffff\'" onmouseout="this.style.background=\'%(background)s\'" STYLE="font-family:verdana; font-size:%(fontsize)s; height:%(rowheight)s; background:%(background)s; border:1px solid black; padding:3px; padding-left:10px; cursor:pointer; border-top:0px solid black">%(value)s</DIV>' % dd)
            self.file.write('</div></DIV>\n')
        elif self.Field is not None:
            if 0:
                ret = '''
<div id="fb%s" style="height:18px;"></div>
''' % (self.FieldID, )
                self.file.write(ret)
                atext = '''
<script type="text/javascript">
jQuery(function() {
   alert("%s 1");
   jQuery('#fb%s').flexbox('/icormanager/test1.asp');
   alert("%s 2");
});  
</script>
''' % (self.FieldID, self.FieldID, self.FieldID, )
                self.Editor.OnLoad.append(['', '', atext])
            if 0:
                ret = aICORWWWServerInterface.ServerClass.ICORWWWInterfaceUtil(self.Field.Name + ':' + self.FieldID, self.Field.CID, 'FieldPreview', ainternalexecute=1)
                self.file.write(ret)
            if 0 and apreview:
                lret = ['&nbsp;<IMG alt="podgląd wartości" id="previewrule2%s" src="images/icon_preview.png" style="cursor:pointer;">\n' % (self.FieldID, )]
                lret.append('<DIV ID="previewrulecontent2%s" STYLE="display:none;"></div>\n' % (self.FieldID, ))
                self.file.write(''.join(lret))
                lret = []
                dd = {'FieldID': self.FieldID, 'CID': self.Field.CID, 'OID': self.OID, 'FieldName': self.Field.Name, 'dh': 200, }
                lret.append('''
<script type="text/javascript" language="javascript">
jQuery(function(){
   jQuery('#previewrule2%(FieldID)s').click(function(){
      jQuery('#previewrulecontent2%(FieldID)s').load('icormain.asp','jobtype=getfieldvalues&CID=%(CID)d&OID=%(OID)d&FieldName=%(FieldName)s&FieldID=%(FieldID)s&nobodytags=1',function(responseText,textStatus,XMLHttpRequest){
         if (textStatus=='success') {
            if (responseText!='') {
               showPopupPR(jQuery('#%(FieldID)s').get(0),jQuery('#previewrule2%(FieldID)s').get(0),jQuery('#previewrulecontent2%(FieldID)s').get(0),%(dh)d);
            } else {
               alert('Brak poprzednich wersji');
            }
         }
      });
   });
})
</script>
''' % dd)
                self.Editor.OnLoad.append(['', '', ''.join(lret)])
            if 1 and apreview:
                lret = []
                dd={
                   'FieldID':self.FieldID,
                   'CID':self.Field.CID,
                   'OID':self.OID,
                   'FieldName':self.Field.Name,
                   'dh':200,
                } # yapf: disable
                lret.append('''
<script type="text/javascript">
jQuery(function(){            
   linputs=["%(FieldID)s"];
   for (i in linputs) {
      asid=linputs[i];
      jQuery("#"+asid).after("&nbsp;<img alt='podgląd wartości' src='/icorimg/silk/zoom.png' style='cursor:pointer;' id='img"+asid+"'>");
      jQuery("#"+asid).autoComplete({
         ajax:"icormain.asp?mode=ac&jobtype=getfieldvaluesac&CID=%(CID)d&OID=%(OID)d&FieldName=%(FieldName)s&FieldID=%(FieldID)s&nobodytags=1",
         ajaxCache:false,
         useCache:true,
         autoFill:false,
         delay:86400000,
         newList:false,
         onShow:function(e,ui) {
            jQuery(ui.ul).css('width',jQuery(this).outerWidth())
            jQuery(ui.ul).maxZIndex();
         },
         onLoad:function(e,ui) {
            for (i=0; i<ui.list.length; i++) {
               ui.list[i].value=htmlDecode(ui.list[i].value);
            }
            return ui.list;
         }
      });
      jQuery("#img"+asid).click(function(bsid){return function(){
         jQuery("#"+bsid).autoComplete('option','delay',0);
         jQuery("#"+bsid).autoComplete('button-ajax', {}, "cache_"+bsid);
         jQuery("#"+bsid).autoComplete('option','delay',86400000);
      }}(asid));
   }
});
</script>
''' % dd)
                self.Editor.OnLoad.append(['', '', ''.join(lret)])
            if 0:
                lret = []
                dd={
                   'FieldID':self.FieldID,
                   'CID':self.Field.CID,
                   'OID':self.OID,
                   'FieldName':self.Field.Name,
                   'dh':200,
                } # yapf: disable
                lret.append('''
<script type="text/javascript" language="javascript">
jQuery(function(){
   jQuery('#%(FieldID)s').flexbox('test1.asp', {
       resultTemplate: '<div class="col1">{id}</div>   
                        <div class="col2">{name}</div>',   
       watermark: 'Enter account number or name',   
       width: 300,
       onSelect: function() {   
           jQuery('#%(FieldID)s-result')
               .html('You selected "' + this.value + '", ' +
                     'which has a hidden value of ' +   
                     this.getAttribute('hiddenValue'));   
       }   
   });
})
</script>
''' % dd)
                self.Editor.OnLoad.append(['', '', ''.join(lret)])
            if 0 and ahistory:
                lret = ['&nbsp;<IMG alt="poprzednie wersje" id="lastversionrule2%s" src="/icorimg/silk/book_previous.png" style="cursor:pointer;">\n' % (self.FieldID, )]
                lret.append('<DIV ID="lastversionrulecontent2%s" STYLE="display:none;"></div>\n' % (self.FieldID, ))
                self.file.write(''.join(lret))
                lret = []
                dd = {'FieldID': self.FieldID, 'CID': self.Field.CID, 'OID': self.OID, 'FieldName': self.Field.Name, 'dh': 200, }
                lret.append('''
<script type="text/javascript" language="javascript">
jQuery(function(){
   jQuery('#lastversionrule2%(FieldID)s').click(function(){
      jQuery('#lastversionrulecontent2%(FieldID)s').load('icormain.asp','jobtype=getfieldversions&CID=%(CID)d&OID=%(OID)d&FieldName=%(FieldName)s&FieldID=%(FieldID)s&nobodytags=1',function(responseText,textStatus,XMLHttpRequest){
         if (textStatus=='success') {
            if (responseText!='') {
               showPopupPR(jQuery('#%(FieldID)s').get(0),jQuery('#lastversionrule2%(FieldID)s').get(0),jQuery('#lastversionrulecontent2%(FieldID)s').get(0),%(dh)d);
            } else {
               alert('Brak poprzednich wersji');
            }
         }
      });
   });
})
</script>
''' % dd)
                self.Editor.OnLoad.append(['', '', ''.join(lret)])
# dialog UI
            if 1 and ahistory:
                lret = ['&nbsp;<IMG alt="poprzednie wersje" id="gvb_%s" src="/icorimg/silk/book_previous.png" style="cursor:pointer;">\n' % (self.FieldID, )]
                lret.append('<div id="gvd_%s" title="Poprzednie wersje"></div>\n' % (self.FieldID, ))
                self.file.write(''.join(lret))
                lret = []
                dd={
                   'FieldID':self.FieldID,
                   'CID':self.Field.CID,
                   'OID':self.OID,
                   'FieldName':self.Field.Name,
                } # yapf: disable
                lret.append('''
<script type="text/javascript">
$(function() {
   $("#gvd_%(FieldID)s").dialog({
      bgiframe: true,
      autoOpen: false,
      height: 360,
      modal: true,
      buttons: {
/*         'Wybierz wersję': function() {
            $(this).dialog('close');
         },
*/
         'Zamknij': function() {
            $(this).dialog('close');
         }
      },
      close: function() {
         dCurrentFieldID="";
      }
   });
   
   $('#gvb_%(FieldID)s').click(function() {
      jQuery('#gvd_%(FieldID)s').load('icormain.asp','jobtype=getfieldversions&CID=%(CID)d&OID=%(OID)d&FieldName=%(FieldName)s&FieldID=%(FieldID)s&nobodytags=1',function(responseText,textStatus,XMLHttpRequest){
         if (textStatus=='success') {
            if (responseText!='') {
               dCurrentFieldID='%(FieldID)s';
               $('#gvd_%(FieldID)s').dialog('open');
            } else {
               alert('Brak poprzednich wersji');
            }
         }
      });
   });
});
</script>
''' % dd)
                self.Editor.OnLoad.append(['', '', ''.join(lret)])

    def DoWriteInputHiddenField(self):
        if self.OID >= 0:
            avalue = self.Field[self.OID]
        else:
            avalue = self.FieldValue
        avalue = string.replace(avalue, '"', '&quot;')    #"
        self.file.write('<input type=HIDDEN class="fcnt" id=%s name=%s value="%s" %s>' % (self.FieldID, self.FieldID, avalue, self.GetFieldValidationText(), ))

    def DoWriteFieldBegin(self, afieldname=0, astream=None):
        l = []
        if self.Editor.OnFieldRowBeginBefore is not None:
            ret = self.Editor.OnFieldRowBeginBefore(self)
            if type(ret) == type([]):
                l.extend(ret)
            elif isinstance(ret, types.StringTypes):
                l.append(ret)
        if not self.NoTR1:
            l.append('<tr>')
        if self.Editor.OnFieldRowBeginAfter is not None:
            ret = self.Editor.OnFieldRowBeginAfter(self)
            if type(ret) == type([]):
                l.extend(ret)
            elif isinstance(ret, types.StringTypes):
                l.append(ret)
        if afieldname:
            if not self.NoTD1:
                l.append('<td class=objectseditdatafieldname>')
            else:
                l.append('<span class=bold>')
            if self.FieldNameAsDisplayed:
                l.append('%s:&nbsp;' % (self.FieldNameAsDisplayed, ))
            if not self.NoTD1:
                l.append('</td>')
            else:
                l.append('</span>')
        if not self.NoTD1:
            l.append('<td>')
        if astream:
            astream.extend(l)
        else:
            self.file.write(string.join(l, ''))

    def DoWriteFieldEnd(self, afieldpreviewvalues=0, adescription=0, astream=None):
        l = []
        if afieldpreviewvalues:
            self.DoWriteFieldPreviewValues()
        if not self.NoTD2:
            l.append('</td><td>')
        if adescription:
            l.append('<i><font size="-1">%s</font></i>' % (self.Description, ))
        if not self.NoTD2:
            l.append('</td>')
        else:
            l.append('&nbsp;')
        if self.Editor.OnFieldRowEndBefore is not None:
            ret = self.Editor.OnFieldRowEndBefore(self)
            if type(ret) == type([]):
                l.extend(ret)
            elif isinstance(ret, types.StringTypes):
                l.append(ret)
        if not self.NoTR2:
            l.append('</tr>\n')
        if self.Editor.OnFieldRowEndAfter is not None:
            ret = self.Editor.OnFieldRowEndAfter(self)
            if type(ret) == type([]):
                l.extend(ret)
            elif isinstance(ret, types.StringTypes):
                l.append(ret)
        if astream:
            astream.extend(l)
        else:
            self.file.write(string.join(l, ''))

    def DoWriteInputTextField(self, aeditor='TEXT'):
        if self.OID >= 0:
            avalue = self.Field[self.OID]
        else:
            avalue = self.FieldValue
        if type(avalue) == type([]):
            avalue = ''
        if self.DisableDefaultValue:
            avalue = ''
        if self.Cols < 1:
            self.Cols = 36
        avalue = string.replace(avalue, '"', '&quot;')    #"
        self.DoWriteFieldBegin(afieldname=1)
        self.file.write('<input type=%s id=%s name=%s class="autocomplete fcnt" size=%d value="%s" tabindex=%d %s>' % (aeditor, self.FieldID, self.FieldID, self.Cols, avalue, self.Editor.TabIndex, self.GetFieldValidationText(), ))
        self.DoWriteFieldEnd(afieldpreviewvalues=1, adescription=1)

    def DoWriteInputIntegerField(self):
        if self.OID >= 0:
            avalue = self.Field[self.OID]
        else:
            avalue = self.FieldValue
        if self.DisableDefaultValue:
            avalue = ''
        self.DoWriteFieldBegin(afieldname=1)
        self.file.write('<input type=text id=%s name=%s class="autocomplete fcnt" size=12 value="%s" tabindex=%d %s>' % (self.FieldID, self.FieldID, avalue, self.Editor.TabIndex, self.GetFieldValidationText(), ))
        self.DoWriteFieldEnd(afieldpreviewvalues=1, adescription=1)

    def DoWriteInputFloatField(self):
        if self.OID >= 0:
            avalue = self.Field[self.OID]
        else:
            avalue = self.FieldValue
        if self.DisableDefaultValue:
            avalue = ''
        self.DoWriteFieldBegin(afieldname=1)
        self.file.write('<input type=text id=%s name=%s class="autocomplete fcnt" size=14 value="%s" tabindex=%d %s>' % (self.FieldID, self.FieldID, avalue, self.Editor.TabIndex, self.GetFieldValidationText(), ))
        self.DoWriteFieldEnd(afieldpreviewvalues=1, adescription=1)

    def DoWriteInputDateField(self):
        if self.OID >= 0:
            adate = self.Field.ValuesAsDateTime(self.OID)
            if adate == ZERO_DATE:
                avalue = tdate2fmtstr(tdatetime())
            else:
                avalue = tdate2fmtstr(adate)
        else:
            if self.FieldValue == '':
                avalue = tdate2fmtstr(tdatetime())
            else:
                if isinstance(self.FieldValue, types.StringTypes):
                    avalue = ICORUtil.getStrAsDate(self.FieldValue)
                    avalue = ICORUtil.tdate2fmtstr(avalue)
                else:
                    avalue = self.FieldValue
        if self.DisableDefaultValue:
            avalue = ''
        self.DoWriteFieldBegin(afieldname=1)
        self.file.write('<input class="datepicker autocomplete fcnt" type=text size=10 id=%s name=%s value="%s" tabindex=%d %s>' % (self.FieldID, self.FieldID, avalue, self.Editor.TabIndex, self.GetFieldValidationText(), ))
        self.DoWriteFieldEnd(afieldpreviewvalues=1, adescription=1)

    def DoWriteInputBoolField(self):
        if self.OID >= 0:
            if self.Field.ValuesAsInt(self.OID) > 0:
                avalue = 'CHECKED '
            else:
                avalue = ''
        else:
            if ICORUtil.str2bool(self.FieldValue):
                avalue = 'CHECKED '
            else:
                avalue = ''
        if self.DisableDefaultValue:
            avalue = ''
        self.DoWriteFieldBegin(afieldname=1)
        self.file.write('<input class="checkradio fcnt" type=checkbox id=%s name=%s %s tabindex=%d %s>' % (self.FieldID, self.FieldID, avalue, self.Editor.TabIndex, self.GetFieldValidationText()))
        self.DoWriteFieldEnd(afieldpreviewvalues=0, adescription=1)

    def DoWriteInputMemoField(self):
        if False and self.Field is not None and self.Field.FieldEditor == 'HTML':
            if 0:
                if self.OID >= 0:
                    ahref = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s' % (self.Field.ClassItem.CID, self.OID, self.Field.Name)
                else:
                    ahref = ''
                self.Editor.EditorScript = 1
                self.AutoHiddenField = 1
                self.file.write('</table><table width="100%%"><tr><td width="100%%" colspan=3 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>' % (self.FieldNameAsDisplayed, ))
                self.file.write(GetEditorText(aid=self.FieldID, aheight="480px", ahref=ahref))
                self.file.write('<input type=hidden class="fcnt" id=%s name=%s value=""></input>' % (self.FieldID, self.FieldID))
                self.file.write('</td></tr></table><table width="100%">')
            if 1:
                if self.OID >= 0:
                    avalue = self.Field[self.OID]
                else:
                    if type(self.FieldValue) == type([]):
                        avalue = ''
                        for aline in self.FieldValue:
                            avalue = avalue + aline + '\n'
                    else:
                        avalue = self.FieldValue
                if self.DisableDefaultValue:
                    avalue = ''
                self.file.write('</table><table width="100%%"><tr><td width="100%%" colspan=3 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>' % (self.FieldNameAsDisplayed, ))
                avalue = string.join(map(XMLUtil.GetAsXMLStringNoPL, string.split(avalue, '\n')), '\n')
                self.file.write('<textarea id=%s name=%s style="width:100%%" spellcheck="false" rows="25" class="mceEditor fcnt">%s</textarea>' % (self.FieldID, self.FieldID, avalue))
                self.file.write('</td></tr></table><table width="100%">')
#      elif self.Field is not None and self.Field.FieldEditor=='Worksheet':
        elif self.FieldEditor == 'Worksheet':
            if self.OID >= 0:
                ahref = 'icormain.asp?jobtype=gethtmlfieldvalue&CID=%d&OID=%d&FieldName=%s' % (self.Field.ClassItem.CID, self.OID, self.Field.Name)
            else:
                ahref = ''
            self.AutoHiddenField = 1
            self.file.write('</table><table width="100%%"><tr><td width="100%%" colspan=3 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br>' % (self.FieldNameAsDisplayed, ))
            atext, aonloadtext, aOnBeforeLoadText, aOnAfterLoadText = GetWorksheetText(aid=self.FieldID, aheight="480px", ahref=ahref)
            self.Editor.OnLoad.append([aonloadtext, aOnBeforeLoadText, aOnAfterLoadText])
            self.file.write(atext)
            self.file.write('<input type=hidden class="fcnt" id=%s name=%s value=""></input>' % (self.FieldID, self.FieldID))
            self.file.write('</td></tr></table><table width="100%">')
        else:
            if self.OID >= 0:
                avalue = self.Field[self.OID]
            else:
                if type(self.FieldValue) == type([]):
                    avalue = ''
                    for aline in self.FieldValue:
                        avalue = avalue + aline + '\n'
                else:
                    avalue = self.FieldValue
            if self.DisableDefaultValue:
                avalue = ''
            if self.Cols < 1:
                self.Cols = 70
            if self.Rows < 1:
                self.Rows = 26


#         avalue=string.replace(avalue,'"','&quot;') #"
            avalue = string.join(map(XMLUtil.GetAsXMLStringNoPL, string.split(avalue, '\n')), '\n')
            tclass = ' class="fcnt"'
            # class="codepress javascript"
            #            self.file.write('<tr><td colspan=2 class=objectseditdatafieldnameleftalign>%s:&nbsp;<br><textarea id=%s name=%s style="width:800px;" rows=%d wrap=off tabindex=%d>%s</textarea></td><td><i><font size="-1">%s</font></i></td></tr>\n'%(self.FieldNameAsDisplayed,self.FieldID,self.FieldID,self.Rows,self.Editor.TabIndex,avalue,self.Description))
            self.file.write('<tr><td colspan=2 class=objectseditdatafieldnameleftalign>%s:\n' % (self.FieldNameAsDisplayed, ))
            self.DoWriteFieldPreviewValues(apreview=0, ahistory=1, afieldsonly=0)
            self.file.write('<br><textarea id=%s name=%s style="width:640px;font-family:DejaVu Sans Mono, Courier New, Courier, monospaced;" spellcheck="false" rows=%d tabindex=%d%s>%s</textarea>\n' % (self.FieldID, self.FieldID, self.Rows, self.Editor.TabIndex, tclass, avalue, ))
            self.file.write('</td><td><i><font size="-1">%s</font></i></td></tr>\n' % (self.Description, ))
            if (self.FieldEditor in ['SourceCode', 'XML']) or (self.Field is not None and self.Field.FieldEditor == 'HTML'):
                atext = '''
<script language="javascript">
function onsubmit_sourcecode(aid) {
   var s=editAreaLoader.getValue(aid);
   var sl=s.split(String.fromCharCode(13));
   jQuery('#'+aid).text(sl.join(''));
}
jQuery(function(){
   var aid="%s"
//   jQuery('#'+aid).codepress({
//      path: '/icormanager/lib/codepress/'
//   });
   editAreaLoader.init({
      id : aid      // textarea id
      ,display: "later"
      ,language: "pl"
      ,toolbar: "search,go_to_line,|,undo,redo,|,select_font,|,change_smooth_selection,highlight,reset_highlight,syntax_selection,|,help"
      ,font_size: 8
      ,replace_tab_by_spaces: 3
      ,syntax: "python"         // syntax to be uses for highgliting
      ,start_highlight: false      // to display with highlight mode on start-up
      ,allow_toggle: true
      ,browsers: "all" 
   });
});
</script>
''' % (self.FieldID, )
                self.OnSubmitFunctions.append("onsubmit_sourcecode('%s');" % self.FieldID)
                self.Editor.OnLoad.append(['', '', atext])

    def CheckAccessLevelView(self, aobj=None):
        if aobj:
            return ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', self.Editor.Menu.uid)
        else:
            aobj = self.Field.ClassOfType.GetFirstObject()
            while aobj:
                if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', self.Editor.Menu.uid):
                    return 1
                aobj.Next()
        return 0

    def DoWriteInputObjectsListField(self):
        aneweditor = 1
        astream = ['', '', ]
        if self.OID >= 0:
            arefs = self.Field.GetRefList(self.OID)
            if not self.CheckAccessLevelView(arefs.AsObject()):
                return
        else:
            arefs = None
        if self.DisableDefaultValue:
            arefs = None

        apinfo = PERSISTENT_CLASSES.get(self.Field.ClassOfType.ClassPath, None)

        self.DoWriteFieldBegin(afieldname=1, astream=astream)
        if apinfo and apinfo['mode'] == 'image':
            if aneweditor:
                sname, slocation = '', ' style="display:none;"'
                if arefs:
                    sname = arefs.Class.Name[arefs.OID]
                    if self.Editor.User.BrowserVersion >= 8:
                        slocation = 'src="data:image/png;base64,' + arefs.Class.Base64[arefs.OID] + '" '
                    else:
                        slocation = 'src="' + arefs.Class.Location[arefs.OID] + '" '
                astream.append('<br><img id=img_%s width=36 height=36 %salt="%s"><br>' % (self.FieldID, slocation, sname))
            astream.append("<br><div id=div_%s name=div_%s style='background:aliceblue; overflow:scroll; overflow-x:hidden; width:100%%; height:400px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'>" % (self.FieldID, self.FieldID, ))
        else:
            astream.append('<select class="fcnt" id=%s name=%s tabindex=%d>\n' % (self.FieldID, self.FieldID, self.Editor.TabIndex, ))
        if not self.DefaultCheck:
            if apinfo and apinfo['mode'] == 'image':
                if not aneweditor:
                    astream.append('<input type="radio" class="checkradio fcnt" name="%s" id="%s" value="-1">&nbsp;***&nbsp;brak&nbsp;przypisania&nbsp;***<br>' % (self.FieldID, self.FieldID, ))
            else:
                astream.append('<option value="-1">&nbsp;***&nbsp;brak&nbsp;przypisania&nbsp;***\n')
        l = []
        if apinfo:
            if apinfo['mode'] == 'image':
                w64 = 0
                if self.Editor.User.BrowserVersion >= 8:
                    w64 = 1
                pclass = self.Field.ClassOfType
                if apinfo['value']:
                    l2 = apinfo['value']
                else:
                    l2 = []
                    pfield = pclass.FieldsByName(apinfo['field'])
                    pfield64 = pclass.FieldsByName(apinfo['field64'])
                    sfield = pclass.FieldsByName(apinfo['sort'])
                    sfilterlocation = apinfo.get('filterlocation', '')
                    poid = pclass.FirstObject()
                    while poid >= 0:
                        if sfilterlocation:
                            if pfield[poid].find(sfilterlocation) < 0:
                                poid = pclass.NextObject(poid)
                                continue
                        if w64:
                            l2.append([sfield[poid], pfield64[poid], poid])
                        else:
                            l2.append([sfield[poid], pfield[poid], poid])
                        poid = pclass.NextObject(poid)
                    l2.sort()
                apinfo['value'] = l2
                for asort, avalue, poid in l2:
                    aselected = ''
                    if arefs:
                        if arefs.RefExists(poid, pclass.CID):
                            aselected = ' CHECKED'
                    if aneweditor:
                        if w64:
                            astream.append('<img oid="%d" src="data:image/png;base64,%s" alt="%s"> \n' % (poid, avalue, asort))
                        else:
                            astream.append('<img oid="%d" src="%s" alt="%s"> \n' % (poid, avalue, asort))
                    else:
                        astream.append('<input type="radio" class="checkradio fcnt" name="%s" id="%s" value="%d"%s>&nbsp;<img src="%s">&nbsp;%s<br>\n' % (self.FieldID, self.FieldID, poid, aselected, avalue, asort))
            else:
                print 'Unknown editor mode:', apinfo['mode']
        else:
            aobj = None
            ddefaultobjvalues = {}
            if self.Editor.OnWWWGetFieldIteratorEvent:
                aobj = self.Editor.OnWWWGetFieldIteratorEvent(self.Field, self.OID, self.Editor.ParamObj)
                if type(aobj) == type(()):
                    aobj, ddefaultobjvalues = aobj
            if aobj is None:
                aobj = self.Field.ClassOfType.GetFirstObject()
            gfields = []
            for afname in aobj.Class.GetFieldsList():
                bfield = aobj.Class.FieldsByName(afname)
                if bfield.WWWTreeRecur:
                    if bfield.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
                        gfields.append(bfield)
            while aobj:
                if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', self.Editor.Menu.uid):
                    lt = []
                    sl = aobj.AsColumnValues(aretvaluesbytype=lt)
                    s = string.join(sl, ', ')
                    if len(s) > 120:
                        s = s[:120] + '...'
                    aselected = ''
                    if arefs:
                        if arefs.RefExists(aobj.OID, aobj.CID):
                            aselected = ' SELECTED'
                    s = string.replace(s, '"', '&quot;')    #"
                    s1 = '<option value="%d"%s>%s\n' % (aobj.OID, aselected, s)
                    lg = []
                    for gfield in gfields:
                        lg.append(string.replace(gfield[aobj.OID], '"', '&quot;'))
                    sg = string.join(lg, ', ')
                    sgs = strLowerPL(sg)
                    l.append([sgs, lt, s, s1, sg])
                aobj.Next()
            l.sort()
            if l:
                slg = ''
                wlg = 0
                for sgs, lt, s, s1, sg in l:
                    if sg != slg:
                        if wlg:
                            astream.append('</optgroup>')
                        wlg = 1
                        astream.append('<optgroup label="%s">' % (sg))
                        slg = sg
                    astream.append(s1)
                if wlg:
                    astream.append('</optgroup>')
        if apinfo and apinfo['mode'] == 'image':
            astream.append("</div>")
            if aneweditor:
                astream.append('\n<input type="hidden" class="fcnt" name="%s" id="%s" value="%d"><br>\n' % (self.FieldID, self.FieldID, poid, ))
                astream.append('''
<script language=javascript>
jQuery(function(){
   jQuery('#div_%s img').click(function(){
      jQuery("input[name=%s]").val(jQuery(this).attr('oid'))
      jQuery("#img_%s").attr("src",jQuery(this).attr('src'));
      jQuery("#img_%s").attr("alt",jQuery(this).attr('alt'));
      jQuery("#img_%s").show();
      return false;
   });
})
</script>
''' % (self.FieldID, self.FieldID, self.FieldID, self.FieldID, self.FieldID, ))
        else:
            astream.append('</select>')
        self.DoWriteFieldEnd(afieldpreviewvalues=0, adescription=1, astream=astream)
        self.file.write(string.join(astream, ''))

    def DoWriteInputObjectsMultipleField(self):
        jqmultiple = 0
        if self.OID >= 0:
            arefs = self.Field.GetRefList(self.OID)
            acid = self.Field.ClassOfType.CID
        else:
            arefs = None
            acid = -1
        if self.DisableDefaultValue:
            arefs = None
        fieldclass = aICORDBEngine.Classes[self.FieldTID]
        l = []
        sbackground = 'aliceblue'
        sclass = ''
        if self.WWWSortable:
            sbackground = '#AFC0DA'
            sbackground = '#bbccee'
            sclass = ' sortableitem ui-state-default'
        asecprofile = ICORSecurity.ICORSecurityProfile()
        if fieldclass.CID == asecprofile.ProfileClass.ItemGroups.ClassOfType.CID:
            asecprofile.SetByUser(self.Editor.Menu.uid)
            asecprofile.GetItemGroupsByUser()
            agroups = asecprofile.ItemGroups.keys()
            agroups.sort()
            for aname in agroups:
                goid, gname = asecprofile.ItemGroups[aname].OID, asecprofile.ItemGroups[aname].GroupName
                aselected = ''
                if arefs:
                    if arefs.RefExists(goid, arefs.CID):
                        if jqmultiple:
                            aselected = ' selected=selected'
                        else:
                            aselected = ' CHECKED'
                s = string.replace(gname, '"', '&quot;')    #"
                if jqmultiple:
                    s1 = '<option value="%s"%s>%s</option>' % (goid, aselected, s)
                else:
                    s1 = '<li class="checkdescription%s"><input class="checkradio fcnt" type=checkbox id="%s_%d" name="%s_%d" value="%d" %s tabindex=%d >%s</li>\n' % (sclass, self.FieldID, goid, self.FieldID, goid, goid, aselected, self.Editor.TabIndex, s)
                self.Editor.TabIndex = 1 + self.Editor.TabIndex
                l.append([-1, 0, strLowerPL(s), s, s1])
        elif fieldclass.CID == asecprofile.ProfileClass.UserGroups.ClassOfType.CID:
            asecprofile.SetByUser(self.Editor.Menu.uid)
            asecprofile.GetUserGroups(aincludeuser=1)
            agroups = asecprofile.Groups.keys()
            agroups.sort()
            for aname in agroups:
                goid, gname = asecprofile.Groups[aname].OID, asecprofile.Groups[aname].GroupName
                aselected = ''
                if arefs:
                    if arefs.RefExists(goid, arefs.CID):
                        if jqmultiple:
                            aselected = ' selected=selected'
                        else:
                            aselected = ' CHECKED'
                s = string.replace(gname, '"', '&quot;')    #"
                if jqmultiple:
                    s1 = '<option value="%s"%s>%s</option>' % (goid, aselected, s)
                else:
                    s1 = '<li class="checkdescription%s"><input class="checkradio fcnt" type=checkbox id="%s_%d" name="%s_%d" value="%d" %s tabindex=%d >%s</li>\n' % (sclass, self.FieldID, goid, self.FieldID, goid, goid, aselected, self.Editor.TabIndex, s)
                self.Editor.TabIndex = 1 + self.Editor.TabIndex
                l.append([-1, 0, strLowerPL(s), s, s1])
        else:
            aobj = None
            ddefaultobjvalues = {}
            ddefaultobjcompvalues = {}
            if self.Editor.OnWWWGetFieldIteratorEvent:
                aobj = self.Editor.OnWWWGetFieldIteratorEvent(self.Field, self.OID, self.Editor.ParamObj)
                if type(aobj) == type(()):
                    aobj, ddefaultobjvalues, ddefaultobjcompvalues = aobj
            if not (type(aobj) == type(1) and aobj == -1):
                afieldtype = 'checkbox'
                if aobj is None:
                    if self.WWWSortable and self.Field and not self.Field.WWWDefaultInput:
                        if self.OID >= 0:
                            aobj = self.Field.GetRefList(self.OID).AsObject()
                        else:
                            aobj = fieldclass.GetFirstObject()
                            aobj.Prev()
                        afieldtype = 'hidden'
                    else:
                        aobj = fieldclass.GetFirstObject()
                while aobj.Exists():
                    if ICORSecurity.CheckRecursiveAccessLevelForUser(aobj, 'AccessLevelView', self.Editor.Menu.uid):
                        lt = []
                        if ddefaultobjvalues.has_key(aobj.OID):
                            sl = ddefaultobjvalues[aobj.OID]
                            lt = ddefaultobjcompvalues[aobj.OID]
                        else:
                            sl = aobj.AsColumnValues(aretvaluesbytype=lt, anowwwtreerecur=0)
                        lts = []
                        for ss in lt:
                            if isinstance(ss, types.StringTypes):
                                lts.append(strLowerPL(ss))
                            else:
                                lts.append(ss)
                        s = ''
                        lsclass = ['fontcolor_list0', 'fontcolor_list1', 'fontcolor_list2', 'fontcolor_list3', 'fontcolor_list0', 'fontcolor_list1', 'fontcolor_list2', 'fontcolor_list3', 'fontcolor_list0', 'fontcolor_list1', 'fontcolor_list2', 'fontcolor_list3', ]
                        alens = 0
                        ipos = 0
                        for i in range(len(sl)):
                            sa = string.strip(sl[i])
                            if sa:
                                if len(sa) > 96:
                                    sa = sa[:96]
                                alens = alens + len(sa)
                                if alens > 200:
                                    sa = sa[:alens - len(sa)]
                                if sa:
                                    s1c = ''
                                    s2c = ''
                                    if ipos < len(lsclass):
                                        s1c = '<span class="%s">' % (lsclass[ipos], )
                                        s2c = '</span>'
                                        ipos = ipos + 1
                                    if s:
                                        s = s + ', '
                                    s = s + s1c + string.replace(sa, '"', '&quot;') + s2c    #"
                        aselected = ''
                        apos, afind = -1, 0
                        if arefs:
                            apos, afind = arefs.FindRef(aobj.OID, aobj.CID)
                            if afind:
                                if jqmultiple:
                                    aselected = ' selected=selected'
                                else:
                                    aselected = ' CHECKED'
                        if jqmultiple:
                            s1 = '<option value="%s"%s>%s</option>' % (aobj.OID, aselected, s)
                        else:
                            s1 = '<li class="checkdescription%s"><input class="checkradio fcnt" type=%s id="%s_%d" name="%s_%d" value="%d" %s tabindex=%d>%s</li>\n' % (sclass, afieldtype, self.FieldID, aobj.OID, self.FieldID, aobj.OID, aobj.OID, aselected, self.Editor.TabIndex, s)
                        self.Editor.TabIndex = 1 + self.Editor.TabIndex
                        if not self.WWWSortable:
                            apos, afind = -1, 0
                        l.append([1 - afind, apos, lts, s, s1])
                    aobj.Next()
        if l:
            self.file.write('<tr><td colspan=2><b>%s:&nbsp;</b>\n' % (self.FieldNameAsDisplayed, ))
            if jqmultiple:
                self.file.write('<div style="width:80%%; height:280px;">')
                self.file.write('<select class="multiselect fcnt" multiple=multiple id=%s name=%s tabindex=%d>\n' % (self.FieldID, self.FieldID, self.Editor.TabIndex, ))
            else:
                if self.WWWSortable:
                    #               self.file.write("<br><div style='background:%s; overflow:scroll; overflow-x:hidden; width:80%%; height:280px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'><ul id='%s_cont' style='cursor:pointer;float:left;height:280px;width:80%%;'>"%(sbackground,self.FieldID,))
                    self.file.write("<br><div class='ui-widget ui-widget-content' style='overflow:scroll; overflow-x:hidden; width:80%%; height:280px;'><ul class='sortablelist' id='%s_cont' style='cursor:pointer;height:280px;'>" % (self.FieldID, ))
                else:
                    #               self.file.write("<br><div style='background:%s; overflow:scroll; overflow-x:hidden; width:80%%; height:200px; border-left: 1 solid Black; border-top: 1 solid Black; border-bottom: 1 solid Black;'><ul id='%s_cont' style='cursor:pointer;float:left;height:280px;width:80%%;'>"%(sbackground,self.FieldID,))
                    self.file.write("<br><div class='ui-widget ui-widget-content' style='overflow:scroll; overflow-x:hidden; width:80%%; height:200px;'><ul class='sortablelist' id='%s_cont' style='cursor:pointer;height:280px;'>" % (self.FieldID, ))
            l.sort()
            for anfind, apos, lt, s, s1 in l:
                self.file.write(s1)
            if jqmultiple:
                self.file.write('</select></div>\n')
            else:
                if self.WWWSortable:
                    self.file.write('</ul><br style="clear:both;"></div><br></td><td><i><font size="-1">' + self.Description + '</font></i></td></tr>\n')
                else:
                    self.file.write('</ul><br style="clear:both;"></div><br></td><td><i><font size="-1">' + self.Description + '</font></i></td></tr>\n')
            atext = ''
            if self.WWWSortable:
                if jqmultiple:
                    atext = '''
<script type="text/javascript">
jQuery(function(){
  jQuery("#%s").multiselect({sortable: true});
});
</script>
''' % (self.FieldID, )
                else:
                    atext = '''
<script language="javascript">
jQuery(function(){
   jQuery("#%s_cont").sortable({
      items:"li"
   });
   jQuery("#%s_cont").css('position',''); //IE8 bug!
});
</script>
''' % (self.FieldID, self.FieldID, )
            else:
                if jqmultiple:
                    atext = '''
<script type="text/javascript">
jQuery(function(){
  jQuery("#%s").multiselect();
});
</script>
''' % (self.FieldID, )
            if atext:
                self.Editor.OnLoad.append(['', '', atext])

    def CheckField(self, file=None):
        w = 1
        avalue = self.GetValue()
        if self.FieldTID <= MAX_ICOR_SYSTEM_TYPE:
            if self.FieldTID == mt_Memo:
                if avalue == '':
                    w = 0
            elif self.FieldTID == mt_String:
                if avalue == '':
                    w = 0
            elif self.FieldTID == mt_Integer:
                try:
                    x = int(avalue)
                except:
                    w = 0
            elif self.FieldTID == mt_Double:
                try:
                    x = float(avalue)
                except:
                    w = 0
            elif self.FieldTID == mt_DateTime:
                try:
                    y, m, d = ICORUtil.getStrAsDate(avalue)
                    if y == 0 or m == 0 or d == 0:
                        w = 0
                except:
                    w = 0
        else:
            if avalue == '':
                w = 0
        if not w and file is not None:
            file.write('<h1>Pole <font color="red">"%s"</font> ma błędną wartość!</h1>\n' % (self.FieldNameAsDisplayed, ))
        return w


class ICORWWWEditor:

    def __init__(self, aclass, amenu, afile, areport=None):
        self.ClassItem = aclass
        self.Menu = amenu
        self.Report = areport
        self.file = afile
        self.FieldsList = []
        self.FieldsIDs = {}
        self.EditorScript = 0
        self.OnLoad = []
        self.OnFieldRowBeginBefore = None
        self.OnFieldRowBeginAfter = None
        self.OnFieldRowEndBefore = None
        self.OnFieldRowEndAfter = None
        self.OnWWWGetFieldIteratorEvent = None
        if aclass.IsMethodInClass('OnWWWAction'):
            pagemethod = aclass.OnWWWAction.AsModule()
            if pagemethod and hasattr(pagemethod, 'OnWWWGetFieldIteratorEvent'):
                self.OnWWWGetFieldIteratorEvent = getattr(pagemethod, 'OnWWWGetFieldIteratorEvent')
        self.ParamCID, self.ParamOID, self.ParamField, self.ParamClass, self.ParamObj = None, None, None, None, None
        if len(self.Menu.WWWParam) == 3:
            self.ParamCID, self.ParamOID, self.ParamField = self.Menu.WWWParam
            self.ParamClass = aICORDBEngine.Classes[self.ParamCID]
            if self.ParamOID >= 0:
                self.ParamObj = self.ParamClass[self.ParamOID]
        self.Connection = ICORUtil.GetCONNECTION()
        if not self.Connection:
            self.Connection = None
            self.CurrentMenuOID = -1
        else:
            self.CurrentMenuOID = int(self.Connection.get('MenuOID', -1))
        self.TabIndex = 1
        self.FirstEdit = None
        self.User = ICORSecurity.ICORSecurityUser()
        if self.Menu.asJSON:
            if not self.Menu.jsonres.has_key('fields'):
                self.Menu.jsonres['fields'] = []
            if not self.Menu.jsonres.has_key('values'):
                self.Menu.jsonres['values']={
                   'refCID': -1,
                   'refOID': -1,
                   'refField': '',
                   'refMode': '',
                } # yapf: disable
            if not self.Menu.jsonres.has_key('WWWDescription'):
                self.Menu.jsonres['WWWDescription'] = ''
                if not self.ClassItem.WWWDisableDescription:
                    self.Menu.jsonres['WWWDescription'] = storageutil.CP1250_To_UTF8(self.ClassItem.WWWDescription)

    def __getitem__(self, key):
        awwwfitem = self.FieldsIDs.get(key, None)
        if awwwfitem is not None:
            return awwwfitem.GetValue()
        if self.Report is not None:
            if key in ['refCID', 'refOID']:
                return int(self.Report.get(key, -1))
            elif key in ['refField', 'refMode']:
                return self.Report.get(key, '')
            elif key == 'refRef':
                return self.Report.get('refOID', -1) + ':' + self.Report.get('refCID', -1) + ':'

    def get(self, key, adefault=''):
        v = self.__getitem__(key)
        if not v:
            return adefault
        return v

    def Fields(self, afield):
        return self.FieldsIDs.get(afield, None)

    def RegisterField(self, afield, adisplayed='', aoid=-1, atype=-1, avalue='', adescription='', acols=-1, arows=-1, asubfields=None, aempty='', aactioneditdisable=0, adefaultcheck=0, aupdaterefs=0, aisunique=0, ahidden=0, afieldeditor='', ano_td1=0, ano_tr1=0, ano_td2=0, ano_tr2=0, atag='', adisabledefaultvalue=0, aclassitem=None, asheetname='', awwwsortable=0):
        if aclassitem is None:
            aclassitem = self.ClassItem
        if atype < 0:
            if isinstance(afield, types.StringTypes):
                bfield = aclassitem.FieldsByName(afield)
            else:
                bfield = afield
            if not ICORSecurity.CheckAccessLevelForUser(bfield.AllowReadGroups, self.Menu.uid):
                return
            if not ICORSecurity.CheckAccessLevelForUser(bfield.AllowWriteGroups, self.Menu.uid):
                return
        awwwfitem = ICORWWWInputField(self, self.file, aclassitem, afield, adisplayed, aoid, atype, avalue, adescription, acols, arows, aempty, aactioneditdisable, adefaultcheck, aupdaterefs, aisunique, ahidden, afieldeditor, ano_td1, ano_tr1, ano_td2, ano_tr2, atag, adisabledefaultvalue, asheetname=asheetname, awwwsortable=awwwsortable)
        awwwfitem.Report = self.Report
        self.FieldsList.append(awwwfitem)
        self.FieldsIDs[afield] = awwwfitem
        if self.Menu.asJSON:
            df, vv = awwwfitem.AsJSON()
            self.Menu.jsonres['fields'].append(df)
            self.Menu.jsonres['values'][awwwfitem.FieldID] = vv
        return awwwfitem

    def RegisterFieldsDefault(self, aoid):
        srefs = self.ClassItem.EditorSheets
        sheetsinfo = {}
        i = 0
        while srefs.position >= 0:
            sheetsinfo[i] = srefs.Name[srefs.OID]    #,[],srefs.WWWDisabled.ValuesAsInt(srefs.OID)]
            i = i + 1
            srefs.Next()
        fnl = self.ClassItem.GetFieldsList()
        afields = []
        for afname in fnl:
            afield = self.ClassItem.FieldsByName(afname)
            if (afield.WWWDefaultInput or afield.WWWSortable) and not afield.WWWDisabled:
                asheetid, atabid = int(afield.FieldSheetID), int(afield.FieldTabIndex)
                if atabid < 0:
                    atabid = 999999
                afields.append([asheetid, atabid, afield.Name, afield])
        afields.sort()
        for asheetid, atabid, afieldname, afield in afields:
            self.RegisterField(afield.Name, aoid=aoid, adefaultcheck=afield.WWWDefaultCheck, aupdaterefs=afield.WWWUpdateRefs, aisunique=afield.WWWUnique, asheetname=sheetsinfo.get(asheetid, ''), awwwsortable=afield.WWWSortable)

    def Write(self, arefCID=-1, arefOID=-1, arefField='', arefMode='', acaption='Zapamiętaj', amimesave='', abeforesubmitfunction='', anoreturnbutton=0):
        if len(self.Menu.WWWParam) == 3 and arefCID == -1 and arefOID == -1 and arefField == '':
            arefCID, arefOID, arefField = self.Menu.WWWParam
        if self.Menu.asJSON:
            self.Menu.jsonres['values']['refCID'] = arefCID
            self.Menu.jsonres['values']['refOID'] = arefOID
            self.Menu.jsonres['values']['refField'] = arefField
            self.Menu.jsonres['values']['refMode'] = arefMode
            return
        self.WriteFormBegin(arefCID, arefOID, arefField, arefMode, amimesave=amimesave)
        self.file.write('<!--tabs-->')
        self.TabIndex = 1
        self.FirstEdit = None
        alastsheet = ''
        asheetid = 0
        lsheets = []
        for awwwfitem in self.FieldsList:
            asheetname = awwwfitem.SheetName
            if asheetname != alastsheet or not asheetid:
                if asheetid:
                    self.file.write('</table></div>')
                self.file.write('<div id="tabs-%d"><table width="100%%">' % asheetid)
                if not asheetname:
                    asheetname = 'Dane'
                lsheets.append('<li><a href="#tabs-%d">%s</a></li>' % (asheetid, asheetname, ))
                asheetid = asheetid + 1
                alastsheet = awwwfitem.SheetName
            awwwfitem.Write()
            if self.TabIndex == 1:
                self.FirstEdit = awwwfitem
            self.TabIndex = 1 + self.TabIndex
        if asheetid:
            self.file.write('</table></div>')
        atext = self.file.getvalue()
        self.file.seek(0)
        if asheetid > 1:
            atext = atext.replace('<!--tabs-->', '<div id="tabs"><ul>' + '\n'.join(lsheets) + '</ul>')
            atext = atext + '</div>\n<script type="text/javascript">jQuery(function(){jQuery("#tabs").tabs();});</script>\n'
        else:
            atext = atext.replace('<!--tabs-->', '<div class="ui-widget">')
            atext = atext.replace('<div id="tabs-0">', '<div class="ui-widget-content">')
            atext = atext + '</div>'
        self.file.write(atext)
        self.WriteFormEnd(acaption=acaption, abeforesubmitfunction=abeforesubmitfunction, anoreturnbutton=anoreturnbutton)
        if self.EditorScript:
            self.file.write(GetScriptText())

    def WriteObjectView(self, acid, aoid=None, asbutton=0, abuttoncaption='Powrót'):
        if aoid is None:
            bcid = acid.CID
            boid = acid.OID
        else:
            bcid, boid = acid, aoid
        if bcid < 0 or boid < 0:
            return
        if asbutton:
            self.file.write('<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:window.location=\'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&menuoid=%d\';" tabIndex=%d>Powrót</button>' % (bcid, boid, self.CurrentMenuOID, self.TabIndex + 2))
        else:
            self.file.write("""
<script language="javascript">
<!--
window.location="icormain.asp?jobtype=objectedit&CID=%d&OID=%d&menuoid=%d";
-->
</script>
""" % (bcid, boid, self.CurrentMenuOID))

    def Read(self):
        self.file.write('<table width="100%">')
        for awwwfitem in self.FieldsList:
            awwwfitem.Read()
        self.file.write('</table>')

    def WriteFormBegin(self, arefCID=-1, arefOID=-1, arefField='', arefMode='', amimesave=''):
        #      s='<script language="jscript"></script>'
        #      self.file.write(s)
        script = ICORWWWInterfaceUtil.GetScriptHeader(asasp=0)
        script = script + """
<!-- disable MCE:
<script language="javascript" type="text/javascript" src="/icormanager/lib/tiny_mce/tiny_mce.js"></script>
-->
<script type="text/javascript" src="/icorlib/jquery/plugins/plugins/plugins.min.js"></script>

<!--
<link rel="stylesheet" type="text/css" href="/icorlib/jquery/plugins/flexbox/css/jquery.flexbox.css">
<script type="text/javascript" src="/icorlib/jquery/plugins/flexbox/js/jquery.flexbox.min.js"></script>
-->
<!--
<script type="text/javascript" src="/icorlib/jquery/plugins/ui-multiselect/js/ui.multiselect.js"></script>
<script language="javascript" type="text/javascript">
jQuery.include('/icorlib/jquery/plugins/ui-multiselect/css/smoothness/jquery-ui-1.7.1.custom.css');
</script>
-->
<style type="text/css">
.hover { background: #000; }
.proxy { border: 1px dotted black; }
.sortablelist {padding:0px;margin:0px;}
.sortableitem_old {padding: 3px; border: 1px dotted navy; margin: 1px; background: aliceblue;}
.sortableitem {list-style-type:none;}
</style>
<style type="text/css">
.versionClick {
   cursor:pointer;
}
.versionClick:hover {
   background: #AFC0DA;
}
</style>
<!--
<script language="javascript" type="text/javascript" src="/icormanager/lib/codepress/codepress.js"></script>
<script language="javascript" type="text/javascript" src="/icorlib/jquery/plugins/codepress/jquery.Codepress.js"></script>
-->
<script language="javascript" type="text/javascript" src="/icormanager/lib/editarea_0_8_1_1/edit_area/edit_area_loader.js"></script>
<!-- disable MCE:
<script language="javascript" type="text/javascript">
   tinyMCE.init({
      theme : "advanced",
      mode : "textareas",
      editor_selector : "mceEditor",
      plugins: "contextmenu,advhr,advimage,advlink,preview,nonbreaking,paste,searchreplace,style,table,visualchars,zoom",
         theme_advanced_buttons1_add_before : "pastetext,pasteword,selectall,search,replace",
         extended_valid_elements : "hr[class|width|size|noshade],a[name|href|target|title|onclick]",
         theme_advanced_buttons2_add : "nonbreaking,styleprops,visualchars,zoom",
         nonbreaking_force_tab : true,
         theme_advanced_buttons3_add : "advhr,tablecontrols",
         paste_use_dialog : true,
         paste_auto_cleanup_on_paste : true,
         theme_advanced_toolbar_location : "top",
         theme_advanced_toolbar_align : "left",
         theme_advanced_statusbar_location : "bottom",
         theme_advanced_resizing : true,
         theme_advanced_resize_horizontal : false
   });
</script>
-->
<SCRIPT LANGUAGE=javascript type="text/javascript">
var dCurrentFieldID="";
function htmlDecode(str) {
  var entMap={'quot':34,'amp':38,'apos':39,'lt':60,'gt':62};
  return str.replace(/&([^;]+);/g,function(m,n) {
    var code;
    if (n.substr(0,1)=='#') {
      if (n.substr(1,1)=='x') {
        code=parseInt(n.substr(2),16);
      } else {
        code=parseInt(n.substr(1),10);
      }
    } else {
      code=entMap[n];
    }
    return (code===undefined||code===NaN)?'&'+n+';':String.fromCharCode(code);
  });
}

jQuery(".versionClick").live("click", function(){
   jQuery('#'+dCurrentFieldID).val(htmlDecode(jQuery(this).attr('versionValue')));
   jQuery('#gvd_'+dCurrentFieldID).dialog('close');
});


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

function myFormSubmit() {
   jQuery(".fcnt").each(function(i) {
      var aname='QCNT'+('00000'+i).slice(-6)+'_'+$(this).attr('name');
      jQuery(this).attr('name',aname);
   });
   document.getElementById('form1').submit();
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
        self.file.write(script)
        #      self.file.write('<div class="ui-widget"><div class="ui-widget-content">') #ui-widget
        self.file.write('<form validate="onchange" VALIDATE-ONCHANGE="1" INVALID-COLOR="gold" invalidColor="gold" mark year4 name=form1 id=form1 METHOD="post" ACTION="icormain.asp?jobtype=menuitemsubmit&OID=%d&menuoid=%d">\n' % (self.Menu.oid, self.CurrentMenuOID))
        self.file.write('<INPUT TYPE=hidden name=refCID id=refCID value="%d">' % (arefCID))
        self.file.write('<INPUT TYPE=hidden name=refOID id=refOID value="%d">' % (arefOID))
        self.file.write('<INPUT TYPE=hidden name=refField id=refField value="%s">' % (arefField))
        self.file.write('<INPUT TYPE=hidden name=refMode id=refMode value="%s">' % (arefMode))
        if amimesave:
            self.file.write('<INPUT TYPE=hidden name=MIMESave id=MIMESave value="1">')
            self.file.write('<INPUT TYPE=hidden name=MIMEContentFileName id=MIMEContentFileName value="%s">' % (amimesave, ))
            self.file.write('<INPUT TYPE=hidden name=noscripttags id=noscripttags value="1">')
            self.file.write('<INPUT TYPE=hidden name=nobodytags id=nobodytags value="1">')

    def WriteFormEnd(self, acaption='Zapamiętaj', abeforesubmitfunction='', anoreturnbutton=0):
        ahiddenfields = []
        for awwwfitem in self.FieldsList:
            if awwwfitem.AutoHiddenField:
                if awwwfitem.FieldEditor == 'HTML':
                    ahiddenfields.append('document.getElementById(\'%s\').value=document.frames(\'%sVisible\').document.body.innerHTML;' % (awwwfitem.FieldID, awwwfitem.FieldID))
                elif awwwfitem.FieldEditor == 'Worksheet':
                    ahiddenfields.append('document.getElementById(\'%s\').value=%sVisible.HTMLData;' % (awwwfitem.FieldID, awwwfitem.FieldID))
            ahiddenfields.extend(awwwfitem.OnSubmitFunctions)
        self.file.write('<br>')
        if ahiddenfields or abeforesubmitfunction:
            if abeforesubmitfunction:
                ahiddenfields.append("if(%s==1){myFormSubmit();};" % abeforesubmitfunction)
            else:
                ahiddenfields.append("myFormSubmit();")
            self.file.write('<br><button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:%sreturn false;" tabIndex=%d>%s</button>' % (string.join(ahiddenfields, ''), self.TabIndex + 1, acaption))
        else:
            self.file.write('''<br><button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:jQuery(this).attr('disabled','disabled');myFormSubmit();return false;" tabIndex=%d>%s</button>''' % (self.TabIndex + 1, acaption))
#         self.file.write('<br><input class="pushbutton" TYPE="submit" VALUE="  %s  " tabIndex=%d>'%(acaption,self.TabIndex+1))
        if len(self.Menu.WWWParam) == 3 and not anoreturnbutton:
            pcid, poid, pfieldname = self.Menu.WWWParam
            self.file.write('&nbsp;&nbsp;&nbsp;<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:window.location=\'icormain.asp?jobtype=objectedit&CID=%d&OID=%d&menuoid=%d\';" tabIndex=%d>Powrót</button>' % (pcid, poid, self.CurrentMenuOID, self.TabIndex + 2))
        self.file.write('</form>\n')
        self.file.write('<SCRIPT src="/icormanager/inc/icor_validation.js" language="JScript"></SCRIPT>\n')
        self.file.write(ICORWWWInterfaceUtil.GetScriptInit())
        if self.FirstEdit is not None:
            self.OnLoad.append(('', """
<SCRIPT LANGUAGE=javascript>
jQuery(function() {
   jQuery("#%s").focus();
});
</SCRIPT>
""" % (self.FirstEdit.FieldID, ), ''))
        if self.OnLoad:
            for atext in self.OnLoad:
                if type(atext) in [type([]), type(())]:
                    atext, aonbefore, aafter = atext
                    self.file.write(aonbefore)
            wvb = 0
            for atext in self.OnLoad:
                if type(atext) in [type([]), type(())]:
                    atext, aonbefore, aafter = atext
                if atext:
                    print 'VBScript WWWInterface text: ', atext
                if not wvb:
                    self.file.write("""
<script language="vbscript">
<!--
Sub Window_onLoad()
""")
                    wvb = 1
                self.file.write(atext)
            if wvb:
                self.file.write("""
End Sub
-->
</script>
""")
            for atext in self.OnLoad:
                if type(atext) in [type([]), type(())]:
                    atext, aonbefore, aafter = atext
                    self.file.write(aafter)


#      self.file.write('</div></div>') #ui-widget

    def CheckField(self, afield, file=None):
        awwwfitem = self.FieldsIDs.get(afield, None)
        if awwwfitem is not None:
            return awwwfitem.CheckField(file)
        return 0

    def CheckFields(self, file=None):
        for awwwfitem in self.FieldsList:
            if awwwfitem.DefaultCheck:
                if not awwwfitem.CheckField(file):
                    return 0
        return 1

    def StoreFields(self, aobj):
        for awwwfitem in self.FieldsList:
            awwwfitem.Store(aobj, self.file)

    def WWWAction(self):
        if self.Menu.Action == 'ObjectAdd':
            pcid, poid, pfieldname = self.ClassItem.CID, -1, ''
            if len(self.Menu.WWWParam) == 3:
                pcid, poid, pfieldname = self.Menu.WWWParam
                kclass = aICORDBEngine.Classes[pcid]
                kobj = kclass[poid]
                l = kobj.AsColumnValues(amaxcol=4)
                s = string.join(l, ', ')
                self.file.write('<h3><font color="green">%s</font></h3><hr>' % (s, ))
            self.Write(arefCID=pcid, arefOID=poid, arefField=pfieldname)
        elif self.Menu.Action == 'ObjectEdit':
            pcid, poid, pfieldname = self.Menu.WWWParam
            self.Write(arefCID=pcid, arefOID=poid, arefField=pfieldname)
        elif self.Menu.Action == 'ObjectDelete':
            pcid, poid, pfieldname = self.Menu.WWWParam
            aclass = aICORDBEngine.Classes[pcid]
            bfield = None
            roid, rcid = -1, -1
            flist = aclass.GetFieldsList()
            for afname in flist:
                afield = aclass.FieldsByName(afname)
                if afield.WWWBackRefField:
                    gclass = afield.ClassOfType
                    glist = gclass.GetFieldsList()
                    for gfname in glist:
                        gfield = gclass.FieldsByName(gfname)
                        rclass = gfield.ClassOfType
                        if rclass is not None and rclass.CID == aclass.CID:
                            prefs = afield.GetRefList(poid)
                            while prefs:
                                gfield.DeleteRefs(prefs.OID, [poid, pcid])
                                if prefs.OID >= 0:
                                    roid, rcid = prefs.OID, prefs.CID
                                prefs.Next()
            aclass.DeleteObject(poid)
            if roid >= 0:
                self.WriteObjectView(rcid, roid)
            elif self.file:
                self.file.write('<h1>Obiekt został skasowany</h1>')
            else:
                pass

    def WWWActionSubmit(self, anoobjectview=0, ainsertbeforeoid=0, abaseoid=-1):
        aoid = -1
        if self.Menu.Action in ['ObjectAdd', 'ObjectEdit']:
            aoid = self['refOID']
            w = self.CheckFields(self.file)
            if not w:
                if self.Menu.asJSON:
                    self.Menu.jsonres['status'] = 1
                    self.Menu.jsonres['info'] = 'popraw dane'
                else:
                    self.file.write('<font color="red"><h2><u>Popraw dane i spróbuj jeszcze raz.</u></h2><hr></font>\n')
                    self.file.write('<button class="fg-button-single ui-state-default ui-corner-all uihover" onclick="javascript:history.back();">Powrót</button>')
                return
            robj = None
            if self.Menu.Action == 'ObjectAdd':
                rcid = self['refCID']
                if rcid >= 0:
                    roid = self['refOID']
                    rclass = aICORDBEngine.Classes[rcid]
                    robj = rclass[roid]
                else:
                    roid = -1
                aoid = self.ClassItem.AddObject(arefobject=robj, arangeobject=robj)
                if aoid < 0:
                    self.file.write('<font color="red"><h2><u>Nie można utworzyć nowego obiektu dla refCID: %d, refOID: %d.</u></h2><hr></font>\n' % (rcid, roid))
                    return
                if rcid >= 0 and aoid >= 0:
                    wrefstore = 0
                    if ainsertbeforeoid and abaseoid >= 0:
                        #                     print 'ainsertbefore',aobj.AsColumnValues()
                        brefclasses = []
                        for afname in self.ClassItem.GetFieldsList():
                            afield = self.ClassItem.FieldsByName(afname)
                            tclass = afield.ClassOfType
                            if tclass is None:
                                continue
                            if afield.WWWBackRefField:
                                brefclasses.append(afield.ClassOfType)
                        for bclass in brefclasses:
                            for afname in self.ClassItem.GetFieldsList():
                                afield = self.ClassItem.FieldsByName(afname)
                                tclass = afield.ClassOfType
                                if tclass is None:
                                    continue
                                if afield.WWWBackRefField and tclass.CID == rcid:
                                    afield[aoid] = [roid, rcid]
                                    fupdaterefs = ''
                                    for bfname in tclass.GetFieldsList():
                                        bfield = tclass.FieldsByName(bfname)
                                        if bfield.WWWUpdateRefs and bfield.ClassOfType.CID == self.ClassItem.CID:
                                            fupdaterefs = bfield
                                    if fupdaterefs:
                                        afield.UpdateReferencedObjects(aoid, fupdaterefs, aupdaterefs=1)
                                        wrefstore = 1
                    else:
                        for afname in self.ClassItem.GetFieldsList():
                            afield = self.ClassItem.FieldsByName(afname)
                            tclass = afield.ClassOfType
                            if tclass is None:
                                continue
                            if afield.WWWBackRefField and tclass.CID == rcid:
                                afield[aoid] = [roid, rcid]
                                fupdaterefs = ''
                                for bfname in tclass.GetFieldsList():
                                    bfield = tclass.FieldsByName(bfname)
                                    if bfield.WWWUpdateRefs and bfield.ClassOfType.CID == self.ClassItem.CID:
                                        fupdaterefs = bfield
                                if fupdaterefs:
                                    afield.UpdateReferencedObjects(aoid, fupdaterefs, aupdaterefs=1)
                                    wrefstore = 1
                    if not wrefstore:
                        for bfname in rclass.GetFieldsList():
                            bfield = rclass.FieldsByName(bfname)
                            if bfield.WWWUpdateRefs and bfield.ClassOfType.CID == self.ClassItem.CID:
                                asortedreffield = None
                                l = self.ClassItem.FieldsAsColumns
                                if l:
                                    asortedreffield = l[0]
                                bfield.AddRefs(roid, [aoid, self.ClassItem.CID], ainsertifnotexists=1, asortedreffield=asortedreffield)
                                break
            if aoid >= 0:
                aobj = self.ClassItem[aoid]
                self.StoreFields(aobj)
                if self.ClassItem.IsMethodInClass('OnObjectChanged'):
                    self.ClassItem.OnObjectChanged('', aoid, self.Menu.Action)
                if not anoobjectview:
                    if robj is not None and self.ClassItem.WWWJumpToBackRefObject and not robj.OID == -1:
                        if self.Menu.asJSON:
                            self.Menu.jsonres['data']['returnCID'] = robj.CID
                            self.Menu.jsonres['data']['returnOID'] = robj.OID
                        else:
                            self.WriteObjectView(robj)
                    else:
                        if self.Menu.asJSON:
                            self.Menu.jsonres['data']['returnCID'] = aobj.CID
                            self.Menu.jsonres['data']['returnOID'] = aobj.OID
                        else:
                            self.WriteObjectView(aobj)
        return aoid


def RegisterFields(aclass, amenu, file, aoid=-1, areport=None):
    if amenu.Action == 'ObjectEdit' and len(amenu.WWWParam) == 3:
        pcid, aoid, pfieldname = amenu.WWWParam
    awwweditor = ICORWWWEditor(aclass, amenu, file, areport)
    awwweditor.RegisterFieldsDefault(aoid=aoid)
    return awwweditor


class ICORWWWServerInterface:

    def __init__(self, aname='Default'):
        self.Refresh(aname)

    def Refresh(self, aname):
        self.ServerClass = aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Server']
        self.OID = self.ServerClass.Name.Identifiers(aname)
        if self.OID < 0:
            raise ValueError, 'bad server name: ' + aname
        self.Name = aname
        self._AppPath = ''
        self._OutputPath = ''
        self._AppOutputPath = ''

    def __getattr__(self, name):
        if name == 'OutputPath':
            if self._OutputPath == '':
                self._OutputPath = self.ServerClass.ServerOutputPath[self.OID] + '/'
            return self._OutputPath
        if name == 'AppPath':
            if self._AppPath == '':
                self._AppPath = self.ServerClass.ServerAppPath[self.OID] + '/'
            return self._AppPath
        if name == 'AppOutputPath':
            if self._AppOutputPath == '':
                self._AppOutputPath = self.ServerClass.ServerAppOutputPath[self.OID] + '/'
            return self._AppOutputPath
        #DNS
        if name == 'RFSNameServer':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DNS
                if aobj2:
                    return aobj2.Name
            return ''
        if name == 'RFSNameServerIP':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DNS
                if aobj2:
                    return aobj2.IP
            return ''
        #FTP
        if name == 'RFSFTPServer':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.FTP
                if aobj2:
                    return aobj2.Name
            return ''
        if name == 'RFSFTPServerIP':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.FTP
                if aobj2:
                    return aobj2.IP
            return ''
        if name == 'RFSFTPServerPort':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.FTP
                if aobj2:
                    return aobj2.Port
            return 21
        #DAV
        if name == 'RFSDAVServer':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DAV
                if aobj2:
                    return aobj2.Name
            return ''
        if name == 'RFSDAVServerIP':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DAV
                if aobj2:
                    return aobj2.IP
            return ''
        if name == 'RFSDAVServerPort':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DAV
                if aobj2:
                    return aobj2.Port
            return 8000
        if name == 'RFSDAVServerUrl':
            aobj = self.ServerClass[self.OID]
            aobj1 = aobj.RFSParameters
            if aobj1:
                aobj2 = aobj1.DAV
                if aobj2:
                    return aobj2.Url
            return '/'

    def GetUserDefaultRFSItem(self, auid):
        from CLASSES_Library_NetBase_RemoteFileSystem_Item_RFSInterface import ICORRFSItem
        aobj = self.ServerClass[self.OID]
        robj = aobj.RFS
        if robj:
            return ICORRFSItem(auid, robj.OID)
        return None


def SetXMLClassImages(tclass, d):
    si1 = si2 = '/icormanager/images/icons/silk/icons/folder.png'
    arefs1 = tclass.WWWMenuImageClosedClass
    if arefs1:
        si1 = arefs1.Location[arefs1.OID]
    arefs2 = tclass.WWWMenuImageClass
    if arefs2:
        si2 = arefs2.Location[arefs2.OID]
    if not si2:
        si2 = si1
    if not si1:
        si2 = si1
    if si1:
        d['icon'] = si1
        d['openIcon'] = si2


def SetXMLObjectImages(tclass, d):
    si1 = si2 = '/icormanager/images/icons/silk/icons/folder_page.png'
    arefs1 = tclass.WWWMenuImageClosedObject
    if arefs1:
        si1 = arefs1.Location[arefs1.OID]
    arefs2 = tclass.WWWMenuImageObject
    if arefs2:
        si2 = arefs2.Location[arefs2.OID]
    if not si2:
        si2 = si1
    if not si1:
        si2 = si1
    if si1:
        d['icon'] = si1
        d['openIcon'] = si2


def GetMenuByObjectsInRange(xmlfile, aidmin, aidmax, tclass, tfieldname, adescription, tfieldkey=''):
    if isinstance(tclass, types.StringTypes):
        tclass = aICORDBEngine.Classes[tclass]
    tinfoname = ''
    if tfieldname.find('.') > 0:
        tfieldname, tinfoname = tfieldname.split('.')
    afield = tclass.FieldsByName(tfieldname)
    afieldinfo = None
    if tinfoname:
        afieldinfo = afield.ClassOfType.FieldsByName(tinfoname)
    afieldkey = None
    if tfieldkey:
        afieldkey = tclass.FieldsByName(tfieldkey)
    l = tclass.GetObjectsInRange(aidmin, aidmax)
    if l:
        lusers = []
        for atid in l:
            if tinfoname:
                arefs = afield.GetRefList(atid)
                if arefs:
                    v = afieldinfo[arefs.OID]
                else:
                    v = ''
            else:
                v = afield[atid]
            if afieldkey:
                v2 = afieldkey[atid]
                if v2:
                    v = v + ' - ' + v2
            lusers.append([atid, v, ])
        lusers.sort()
        d = {'text': XMLUtil.GetAsXMLStringNoPL('%s w zakresie (%d)' % (adescription, len(lusers), ))}
        SetXMLClassImages(tclass, d)
        xmlfile.TagOpen('tree', d)
        for atid, ausername in lusers:
            #if not tclass.ObjectExists(atid):
            #   continue
            tobj = tclass[atid]
            d = {'text': XMLUtil.GetAsXMLStringNoPL('%d - %s' % (atid, ausername)), 'action': 'icormain.asp?jobtype=objectedit&CID=%d&OID=%d' % (tobj.CID, tobj.OID)}
            #         d['action']='icormain.asp?jobtype=menuobjrecuraction&CID=%d&OID=%d&type=table&param=%s'%(tobj.CID,tobj.OID,aobjname)
            d['src'] = 'icormain.asp?jobtype=menuclassrecur&CID=%d&OID=%d&XMLData=1' % (tobj.CID, tobj.OID)
            d['context'] = 'icormain.asp?jobtype=menuclassrecurcontext&CID=%d&OID=%d&field=&XMLData=1' % (tobj.CID, tobj.OID)
            SetXMLObjectImages(tclass, d)
            #               if wcontext:
            #      d['context']='icormain.asp?jobtype=menuclassrecurcontext&CID=%d&OID=%d&field=%s&XMLData=1'%(acid,aoid,bfield.Name)
            #                  print 'Context 2:',d['context']
            xmlfile.TagOpen('tree', d, aclosetag=1)
        xmlfile.TagClose('tree')
    return


aICORWWWServerInterface = ICORWWWServerInterface('Default')


def _ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    print FilePathAsSystemPath(aICORWWWServerInterface.OutputPath)
    print FilePathAsSystemPath(aICORWWWServerInterface.AppPath)
    print FilePathAsSystemPath(aICORWWWServerInterface.AppOutputPath)
