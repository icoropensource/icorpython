# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil


def GetScriptText():
    return "<script type='text/javascript' src='/icorlib/ckeditor/3.1/ckeditor.js'></script>"


def GetEditorText(aid='0', awidth='100%', aheight='100%', avalue='', ahref='', adefaulttext=''):
    ddict = {
        'EditorWidth':awidth,
        'EditorHeight':aheight,
        'ID':aid,
        'IDlower':ICORUtil.strLowerPL(aid),
        'Value':avalue,
        'HRefSrc':ahref,
        'ASPVarBegin':'<%=',
        'ASPEnd':'%>',
    } # yapf: disable
    aEditorText = """
<script type='text/javascript'>
jQuery(function(){
    editor=CKEDITOR.replace('%(ID)s',{customConfig:'/icormanager/inc/CKconfig.js'});

    editor.on('pluginsLoaded', function( ev ) {
        editor.addCommand( 'IcorFiles', {
            exec : function( editor ) {
                window.parent.postMessage({
                    type: 'editorButtonClick',
                    ownerTab: window.ownerTab,
                    ownerSheet: window.ownerSheet,
                    mode: 'file',
                    fieldname: '%(ID)s',
                    ioid: "%(ASPVarBegin)sDataOID%(ASPEnd)s",
                    tid: "%(ASPVarBegin)saTableID%(ASPEnd)s",
                    poid: "%(ASPVarBegin)sPOID%(ASPEnd)s",
                    chapterid: "%(ASPVarBegin)sachapterid%(ASPEnd)s"
                }, '*');
            }
        });
        editor.addCommand('IcorTable', {
            exec : function( editor ){
                window.parent.postMessage({
                    type: 'editorButtonClick',
                    ownerTab: window.ownerTab,
                    ownerSheet: window.ownerSheet,
                    mode: 'table',
                    fieldname: '%(ID)s',
                    ioid: "%(ASPVarBegin)sDataOID%(ASPEnd)s",
                    tid: "%(ASPVarBegin)saTableID%(ASPEnd)s",
                    poid: "%(ASPVarBegin)sPOID%(ASPEnd)s",
                    chapterid: "%(ASPVarBegin)sachapterid%(ASPEnd)s"
                }, '*');
            }
        });
        editor.ui.addButton('IcorFiles', {
            label : 'Wstaw plik',
            command : 'IcorFiles',
            icon: '/icorimg/silk/page.png'
        });
        editor.ui.addButton('IcorTable', {
            label : 'Wstaw tabelę z ICOR',
            command : 'IcorTable',
            icon: '/icorimg/silk/table_go.png'
        });
    });

   CKEDITOR.instances['%(ID)s'].on('instanceReady', function(ev) {
""" % ddict
    if adefaulttext:
        aEditorText = aEditorText + """
      src=htmlDecode("%s");
      CKEDITOR.instances['%s'].setData(src);
""" % (adefaulttext, aid, )
    if ahref:
        aEditorText = aEditorText + """
      jQuery.get('%(HRefSrc)s',function(data){
         ev.editor.setData(data);
      },"text");
""" % ddict

    aEditorText = aEditorText + """
   });
});
</script>
"""
    return aEditorText


def GetEditorTextFCK(aid='0', awidth='100%', aheight='100%', avalue='', ahref='', adefaulttext=''):
    ddict = {'EditorWidth': awidth, 'EditorHeight': aheight, 'ID': aid, 'IDlower': ICORUtil.strLowerPL(aid), 'Value': avalue, 'HRefSrc': ahref}
    aEditorText = """
<script language="javascript">
<!--
var oFCKeditor%(ID)s ;
oFCKeditor%(ID)s = new FCKeditor('%(IDlower)s') ;
oFCKeditor%(ID)s.BasePath = '/icormanager/inc/fckeditor/' ;
oFCKeditor%(ID)s.Width      = '%(EditorWidth)s' ;
oFCKeditor%(ID)s.Height     = '%(EditorHeight)s' ;
oFCKeditor%(ID)s.ToolbarSet = 'Default' ;
oFCKeditor%(ID)s.CanUpload = true ;   // Overrides fck_config.js default configuration
oFCKeditor%(ID)s.CanBrowse = true ;   // Overrides fck_config.js default configuration
""" % ddict
    tmp = """
/////////////////////////////////////////////
//config.BaseUrl = document.location.protocol + '//' + document.location.host + '/' ;
//config.StartupShowBorders = false ;
//config.StartupShowDetails = false ;
//config.ForcePasteAsPlainText  = false ;
//config.AutoDetectPasteFromWord   = true ;
//config.UseBROnCarriageReturn  = false ;
//config.TabSpaces = 4 ;
//config.AutoDetectLanguage = false ;
//config.DefaultLanguage    = "en" ;
//config.SpellCheckerDownloadUrl = "http://www.rochen.com/ieSpellSetup201325.exe" ;
//config.ImageBrowser = true ;
//config.ImageBrowserURL = config.BasePath + "filemanager/browse/sample_html/browse.html" ;
//config.ImageUpload = true ;
//config.LinkBrowser = true ;
//config.LinkUpload = true ;
//oFCKeditor%(ID)s.Config['SmileyPath'] = config.BasePath + "images/smiley/msn/" ;
//oFCKeditor%(ID)s.Config['SmileyImages']  = ["regular_smile.gif","sad_smile.gif","wink_smile.gif","teeth_smile.gif","confused_smile.gif","tounge_smile.gif","embaressed_smile.gif","omg_smile.gif","whatchutalkingabout_smile.gif","angry_smile.gif","angel_smile.gif","shades_smile.gif","devil_smile.gif","cry_smile.gif","lightbulb.gif","thumbs_down.gif","thumbs_up.gif","heart.gif","broken_heart.gif","kiss.gif","envelope.gif"] ;
//oFCKeditor%(ID)s.Config['SmileyColumns'] = 7 ;
//oFCKeditor%(ID)s.Config['SmileyWindowWidth']   = 500 ;
//oFCKeditor%(ID)s.Config['SmileyWindowHeight']  = 300 ;
""" % ddict
    aEditorText = aEditorText + """
oFCKeditor%(ID)s.Config['ToolbarImagesPath'] = oFCKeditor%(ID)s.BasePath + "images/toolbar/" ;
//oFCKeditor%(ID)s.Config['ImageBrowserURL'] = oFCKeditor%(ID)s.BasePath + "filemanager/browse/browseimages_icor.asp" ;
//oFCKeditor%(ID)s.Config['ImageBrowserWindowWidth']  = 600 ;
//oFCKeditor%(ID)s.Config['ImageBrowserWindowHeight'] = 480 ;
//oFCKeditor%(ID)s.Config['ImageUploadURL'] = oFCKeditor%(ID)s.BasePath + "filemanager/upload/uploadimages_icor.asp" ;
//oFCKeditor%(ID)s.Config['ImageUploadWindowWidth'] = 300 ;
//oFCKeditor%(ID)s.Config['ImageUploadWindowHeight']   = 150 ;
//oFCKeditor%(ID)s.Config['ImageUploadAllowedExtensions'] = ".gif .jpg .jpeg .png" ;
//oFCKeditor%(ID)s.Config['LinkBrowserURL'] = oFCKeditor%(ID)s.BasePath + "filemanager/browse/browsefiles_icor.asp" ;
//oFCKeditor%(ID)s.Config['LinkBrowserWindowWidth'] = 600 ;
//oFCKeditor%(ID)s.Config['LinkBrowserWindowHeight']   = 480 ;
//oFCKeditor%(ID)s.Config['LinkUploadURL'] = oFCKeditor%(ID)s.BasePath + "filemanager/upload/uploadfiles_icor.asp" ;
//oFCKeditor%(ID)s.Config['LinkUploadWindowWidth']  = 300 ;
//oFCKeditor%(ID)s.Config['LinkUploadWindowHeight'] = 150 ;
//oFCKeditor%(ID)s.Config['LinkUploadAllowedExtensions']  = "*" ;     // * or empty for all
//oFCKeditor%(ID)s.Config['LinkUploadDeniedExtensions']   = ".exe .asp .php .aspx .js .cfm .dll .cmd .com .bat .vbs .py .cpl .hta" ;  // empty for no one
""" % ddict
    if adefaulttext:
        aEditorText = aEditorText + """
src="%s";
oFCKeditor%s.Value = htmlDecode(src);
""" % (adefaulttext, aid)

    aEditorText = aEditorText + """
oFCKeditor%(ID)s.Create() ;
""" % ddict

    if ahref:
        aEditorText = aEditorText + """
lEditorsInit.push(function(){
   jQuery(function(){
      jQuery.get("%(HRefSrc)s",function(data){
         var oEditor=FCKeditorAPI.GetInstance("%(IDlower)s");
         oEditor.SetHTML(data);
      },"text");
   });
})
""" % ddict
    aEditorText = aEditorText + """
//-->
</script>
""" % ddict
    return aEditorText
