# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import serverutil as ServerUtil
from icorwwwinterface import aICORWWWServerInterface
import icorwwwinterfaceutil as ICORWWWInterfaceUtil
import icor20interfaceutil as ICOR20InterfaceUtil
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import string
import cStringIO
import types
try:
    import json
except:
    import simplejson as json

LOG_FILE = 'd:/icor_251/extensions/out.log'


def Log(amode='a+', fname=LOG_FILE, aconsole=0):
    if aconsole:
        print string.replace(s, '\n', '')
    try:
        f = open(fname, amode)
        f.write(s)
        f.close()
    except:
        pass


def MIncludeFile(file, fname):
    f = open(aICORWWWServerInterface.AppOutputPath + '/' + fname, 'r')
    try:
        file.write(f.read())
    finally:
        f.close()


def ICORMain(CID=-1, FieldName='', OID=-1, Value='', UID=-1):
    if 0:
        print 'DoProcess:'
        print 'CID:', CID
        print 'FieldName:', FieldName
        print 'OID:', OID
        print 'Value:', Value
        print 'UID:', UID
    ICOR20 = 1
    CONNECTION = {UID: UID, }
    if type(FieldName) == type({}):
        aparms = ServerUtil.ICORReport(FieldName)    #Form
    elif type(FieldName) == type([]):
        aparms = ServerUtil.ICORReport(FieldName)    #Form
    else:
        aServerVariables = ''
        i = FieldName.find(ServerUtil.SPLIT_CHAR_PARAM)
        if i >= 0:
            FieldName, aServerVariables = FieldName[:i], FieldName[i + len(ServerUtil.SPLIT_CHAR_PARAM):]
        if isinstance(Value, ServerUtil.ICORReport):
            aparms = Value
            if aServerVariables:
                aparms.Set(aServerVariables)
            CID = -1
            FieldName = ''
            Value = ''
        elif isinstance(Value, types.StringTypes):
            aparms = ServerUtil.ICORReport(Value, adefPost=1)    #Form
            if aServerVariables:
                aparms.Set(aServerVariables, autfsplit=1)
            aparms.Set(FieldName, adefPost=1)    #QueryString

    CONNECTION.update(aparms.formdict)
    if 0:
        print '*** PROCESS ***'
        print '  jobtype:', aparms['jobtype', '']
        aparms.Dump()
    aclass = aICORDBEngine.Classes['CLASSES_Library_NetBase_WWW_Server']
    if OID == 0:
        file = cStringIO.StringIO()
        noscripttags = int(aparms['noscripttags', '0'])
        nobodytags = int(aparms['nobodytags', '0'])
        passthrupagevalue = aparms['passthrupagevalue', '']
        nodownloadtags = int(aparms['nodownloadtags', '0'])
        ajsondata = 0
        axmldata = 0
        if aparms['XMLData', '0'] == 'json':
            ajsondata = 1
            nobodytags = 1
            noscripttags = 1
            ICOR20 = 0
        elif aparms['XMLData', '0'] == '1':
            axmldata = 1
            nobodytags = 1
            noscripttags = 1
            aparms['MIMEXML'] = '1'
            ICOR20 = 0

        ajob = aparms['jobtype', '']
        if ajob == 'objectedit_xx':
            nobodytags = 1
            noscripttags = 1
            ICOR20 = 0
        if not nobodytags:
            file.write('<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:t="urn:schemas-microsoft-com:time" xmlns="http://www.w3.org/TR/REC-html40" xmlns:tool>')
            file.write('<head>')
            ICORWWWInterfaceUtil.WriteDefIncMeta(file, anodownloadtags=nodownloadtags)
            if not nodownloadtags:
                ICORWWWInterfaceUtil.WriteAlwaysInFrame(file)
            file.write('<title>Main page</title><!--<base target="TEXT">--></head>')
            bodydeftext = '<body topmargin="10">'
        else:
            bodydeftext = ''
            ICOR20 = 0

        if ajob == 'objectedit':
            import doobjectedit
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            eclass = aICORDBEngine.Classes[acid]
            file.write(bodydeftext)
            doobjectedit.ProcessObjectEdit(file, eclass, aoid, UID, brcid=brcid, broid=broid)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, CID=acid, OID=aoid, brCID=brcid, brOID=broid))
        elif ajob == 'objectsview':
            import doobjectsview
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            eclass = aICORDBEngine.Classes[acid]
            file.write(bodydeftext)
            doobjectsview.DoObjectsView(file, eclass)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, CID=acid, OID=aoid))
        elif ajob == 'menuaspage':
            import domenupageview
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            domenupageview.GenerateMenuAsPage(file, aoid, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'menuitemedit':
            import domenuitemedit
            aoid = int(aparms['OID'])
            apassthrupagevalue = aparms['passthrupagevalue', '']
            file.write(bodydeftext)
            domenuitemedit.GenerateMenuItemFramePage(file, aoid, apassthrupagevalue, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid, pagevalue=apassthrupagevalue))
        elif ajob == 'menuitemeditsubmit':
            import domenuitemeditsubmit
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            domenuitemeditsubmit.DoMenuItemEditSubmit(file, aoid, aparms, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'custompagebymethod':
            import docustompagebymethodview
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            docustompagebymethodview.GenerateMenuAsPage(file, aoid, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'reportsubmit':
            import doreportsubmit
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            doreportsubmit.DoReportSubmit(file, aoid, aparms, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'summarylist':
            import dosummarylist
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            dosummarylist.GenerateMenuAsSummaryList(file, aoid, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'summaryexecute':
            import dosummaryexecute
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            dosummaryexecute.GenerateSummaryExecute(file, aoid, aparms)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'summaryparameters':
            import dosummaryparameters
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            dosummaryparameters.GenerateSummaryParameters(file, aoid)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'outputpageget':
            apage = aparms['page']
            amime = aparms['mimetype']
            file.write(bodydeftext)
            MIncludeFile(file, apage)
        elif ajob == 'summaryrecur':
            import dosummaryrecur
            rfield = aparms['rfield']
            summoid = int(aparms['summoid'])
            bcid = int(aparms['bcid'])
            boid = int(aparms['boid'])
            file.write(bodydeftext)
            dosummaryrecur.GenerateSummaryRecur(file, rfield, summoid, bcid, boid)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, CID=bcid, OID=boid, summoid=summoid, rfield=rfield))
        elif ajob == 'sheetget':
            import dosheetget
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            asheet = int(aparms['sheet'])
            file.write(bodydeftext)
            dosheetget.DoSheetGet(file, acid, aoid, asheet, UID, brcid=brcid, broid=broid)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, CID=acid, OID=aoid, brCID=brcid, brOID=broid, sheet=asheet))
        elif ajob == 'menuitem':
            import dodefaultmenuitem
            aoid = int(aparms['OID'])
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            aparam = aparms['param']
            acheckaction = aparms.get('checkaction', '')
            ajsonres = None
            if aparms.get('_jsonres', '') == '1':
                ajsonres = {'status': 0, 'info': ''}
            file.write(bodydeftext)
            dodefaultmenuitem.GenerateDefaultMenuItem(file, aoid, UID, aparam, brcid=brcid, broid=broid, checkaction=acheckaction, jsonres=ajsonres)
            if ajsonres is not None:
                return json.dumps(ajsonres)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid, brCID=brcid, brOID=broid, param=aparam))
        elif ajob == 'menuitemsubmit':
            import dodefaultmenuitemsubmit
            aoid = int(aparms['OID'])
            file.write(bodydeftext)
            dodefaultmenuitemsubmit.DoDefaultMenuItemSubmit(file, aoid, aparms, UID)
            if ICOR20:
                file.write(ICOR20InterfaceUtil.JobTypeTrigger(jobtype=ajob, OID=aoid))
        elif ajob == 'gethtmlfieldvalue':
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            afieldname = aparms['FieldName']
            bclass = aICORDBEngine.Classes[acid]
            if bclass is None:
                return ''
            afield = bclass.FieldsByName(afieldname)
            if afield is None:
                return ''
            file.write(afield[aoid])
        elif ajob == 'getfieldvalues':
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            afieldname = aparms['FieldName']
            afieldid = aparms['FieldID']
            bclass = aICORDBEngine.Classes[acid]
            if bclass is None:
                return ''
            afield = bclass.FieldsByName(afieldname)
            if afield is None:
                return ''
            ICORWWWInterfaceUtil.DoGetFieldValues(file, bclass, afield, afieldid, aoid)
        elif ajob == 'getfieldvaluesac':
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            afieldname = aparms['FieldName']
            afieldid = aparms['FieldID']
            bclass = aICORDBEngine.Classes[acid]
            if bclass is None:
                return ''
            afield = bclass.FieldsByName(afieldname)
            if afield is None:
                return ''
            ICORWWWInterfaceUtil.DoGetFieldValuesAC(file, bclass, afield, afieldid, aoid)
        elif ajob == 'getfieldversions':
            acid = int(aparms['CID'])
            aoid = int(aparms['OID'])
            afieldname = aparms['FieldName']
            afieldid = aparms['FieldID']
            bclass = aICORDBEngine.Classes[acid]
            if bclass is None:
                return ''
            afield = bclass.FieldsByName(afieldname)
            if afield is None:
                return ''
            ICORWWWInterfaceUtil.DoGetFieldVersions(file, bclass, afield, afieldid, aoid)
        elif ajob == 'menuxml':
            import docontentsview
            aoid = int(aparms['OID'])
            agroup = aparms.get('group', '')
            return docontentsview.ProcessContents('MenuXML', UID, aoid, '', ajson=ajsondata, agroup=agroup)
        elif ajob == 'menufavget':
            atext = aclass.DoContentsView('', -1, 'MenuFavGet')
            return atext
        elif ajob == 'menufavset':
            import docontentsview
            amenufav = aparms.get('data', '')
            amenufav = XMLUtil.UTF8_To_CP1250(amenufav)
            return docontentsview.ProcessContents('MenuFavSet', UID, -1, amenufav)
        elif ajob == 'menuclassrecur':
            import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
            aoid = int(aparms.get('OID', '-1'))
            acid = int(aparms.get('CID', '-1'))
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            afieldname = aparms.get('field', '')
            DoMenuClassRecur.DoMenuClassRecur(file, acid, afieldname, aoid, UID, brcid=brcid, broid=broid, ajson=ajsondata)
        elif ajob == 'menuclassrecuraction':
            import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
            aoid = int(aparms.get('OID', '-1'))
            acid = int(aparms.get('CID', '-1'))
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            aparam = aparms.get('param', '')
            atype = aparms.get('type', '')
            acontext = aparms.get('context', '')
            DoMenuClassRecur.DoMenuClassRecurAction(file, acid, aoid, [atype, aparam, acontext], UID, brcid=brcid, broid=broid, ajson=ajsondata)
        elif ajob == 'menuclassrecurcontext':
            import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
            aoid = int(aparms.get('OID', '-1'))
            acid = int(aparms.get('CID', '-1'))
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            afieldname = aparms.get('field', '')
            DoMenuClassRecur.DoMenuClassRecurContext(file, acid, afieldname, aoid, UID, brcid=brcid, broid=broid, ajson=ajsondata)
        elif ajob == 'menuclassrecurcontextsubmit':
            import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
            aoid = int(aparms.get('OID', '-1'))
            acid = int(aparms.get('CID', '-1'))
            brcid = int(aparms.get('brCID', '-1'))
            broid = int(aparms.get('brOID', '-1'))
            afieldname = aparms.get('field', '')
            aid = aparms.get('id', '-1')
            DoMenuClassRecur.DoMenuClassRecurContextSubmit(file, acid, afieldname, aoid, aid, UID, brcid=brcid, broid=broid, ajson=ajsondata)
        elif ajob == 'menuobjrecuraction':
            import icorlib.wwwserver.domenuclassrecur as DoMenuClassRecur
            aoid = int(aparms.get('OID', '-1'))
            acid = int(aparms.get('CID', '-1'))
            aparam = aparms.get('param', '')
            atype = aparms.get('type', '')
            DoMenuClassRecur.DoMenuObjRecurAction(file, acid, aoid, [atype, aparam], UID)
        elif ajob == 'workflowmenustruct':
            import domenuworkflowrecur
            aoid = int(aparms.get('OID', '-1'))
            coid = int(aparms.get('coid', '-1'))
            aparam = aparms.get('param', '')
            domenuworkflowrecur.DoMenuWorkflowRecur(file, aoid, coid, aparam, UID, ajson=ajsondata)
        elif ajob == 'workflowmenustructcontext':
            import domenuworkflowrecur
            aoid = int(aparms.get('OID', '-1'))
            coid = int(aparms.get('coid', '-1'))
            aparam = aparms.get('param', '')
            domenuworkflowrecur.DoMenuWorkflowRecurContext(file, aoid, coid, aparam, UID, ajson=ajsondata)
        elif ajob == 'workflowmenustructcontextsubmit':
            import domenuworkflowrecur
            aoid = int(aparms.get('OID', '-1'))
            coid = int(aparms.get('coid', '-1'))
            aid = aparms.get('id', '-1')
            aparam = aparms.get('param', '')
            domenuworkflowrecur.DoMenuWorkflowRecurContextSubmit(file, aoid, coid, aparam, aid, UID, ajson=ajsondata)
        elif ajob == 'workflowmenustructchaptermove':
            import CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterMove
            coid1 = int(aparms.get('coid1', '-1'))
            coid2 = int(aparms.get('coid2', '-1'))
            aparam = aparms.get('param', '0')
            CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterMove.DoMenuWorkflowChapterMove(file, coid1, coid2, aparam, UID)
        elif ajob == 'workflowmenustructchaptermovedrag':
            import CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterMove
            coid1 = int(aparms.get('coid1', '-1'))
            coid2 = int(aparms.get('coid2', '-1'))
            atype = aparms.get('type', '')
            arel1 = aparms.get('rel1', '')
            arel2 = aparms.get('rel2', '')
            CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterMove.DoMenuWorkflowChapterMoveDrag(file, coid1, coid2, atype, arel1, arel2, UID)
        elif ajob == 'workflowmenustructattachmentmovedrag':
            import CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterAttachmentMove
            coid1 = int(aparms.get('coid1', '-1'))
            coid2 = int(aparms.get('coid2', '-1'))
            atype = aparms.get('type', '')
            arel1 = aparms.get('rel1', '')
            arel2 = aparms.get('rel2', '')
            aatt = aparms.get('att', '')
            CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Rozdzial_WWWChapterAttachmentMove.DoMenuWorkflowAttachmentMoveDrag(file, coid1, coid2, atype, arel1, arel2, aatt, UID)
        if not nobodytags:
            file.write(ICORWWWInterfaceUtil.GetScriptInit())
            file.write('\n</BODY></HTML>\n')
        if 0:
            f = open('d:/icor/out.txt', 'w')
            f.write(file.getvalue())
            f.close()
        return file.getvalue()
    elif OID == 1:    #Introduction
        return aclass.DoContentsView('', -1, 'Introduction')
    elif OID == 2:    #Contents
        return aclass.DoContentsView('', -1, 'Contents')
    elif OID == 3:    #NavigationBar
        return aclass.DoContentsView('', -1, 'NavigationBar')
    elif OID == 4:    #NavigationButtons
        aoid = int(aparms['OID', '-1'])
        return aclass.DoContentsView('', -1, 'NavigationButtons')
    elif OID == 5:    #FirstPageRedirect
        return '<html><head><meta http-equiv="X-UA-Compatible" content="IE=8"><meta http-equiv="refresh" content="0; URL=framemain.asp"></head><body></body></html>'
    elif OID == 6:    #LogonPage
        file = cStringIO.StringIO()
        file.write('<html><head>')
        ICORWWWInterfaceUtil.WriteDefIncMeta(file)
        file.write("""<title>Default</title>
</head>
<body>
<p><font color="#000080"><big>Logowanie użytkownika. Wprowadź sw&oacute;j identyfikator oraz hasło dostępu.</big></font></p>
<form METHOD="post" ACTION="default.asp">
<table width="523" height="145" border="0">
<tr>
<td width="315" height="39"><div align="center"><center><p><IMG align=right alt="ICORLogo - small" height=53 src="images/icorlogosmall.gif" width=53></p></center></div></td>
<td width="146" align="right" height="39"><em>Użytkownik:</em></td>
<td width="13" height="39"></td>
<td width="215" height="39"><input NAME="User" id="User" VALUE="" & objRequest.Form("User") & "" size="22" maxLength=1024 tabIndex=1></td>
</tr>
<tr>
<td width="315" height="46"></td>
<td width="146" align="right" height="46"><em>Hasło:</em></td>
<td width="13" height="46"></td>
<td width="215" height="46"><input TYPE="password" NAME="Password" id="Password" size="22" maxLength=1024 tabIndex=2></td>
</tr>
<tr>
<td width="315" height="48"></td>
<td width="146" height="48"><br></td>
<td width="13" height="48"></td>
<td width="215" height="48"><div align="center"><center><p><input TYPE="submit" VALUE="  OK  " tabIndex=3></p></center></div> </td>
</tr>
</table>
</form>
</body>
</html>
""")
        return file.getvalue()
    elif OID < 0:    #Error!
        file = cStringIO.StringIO()
        file.write('<html><head>')
        ICORWWWInterfaceUtil.WriteDefIncMeta(file)
        file.write('<title>Błąd konfiguracji</title></head><body>')
        file.write('<p>&nbsp;</p><p align="center"><u><font color="#FF0000" size="6">UWAGA!</font></u></p>')
        file.write('<p align="left"><font size="5" color="#000080">Konfiguracja Twojego komputera nie spełnia wszystkich wymagań. Sprawdź, który element z poniższej listy <u>nie opisuje</u> Twojego środowiska:</font></p>')
        file.write('<ul>')
        file.write('  <li><p align="left"><font size="3">MS Internet Explorer w wersji 6.0 lub wyższej</font></p>')
        file.write('  </li>')
        file.write('  <li><p align="left"><font size="3">Akceptacja tzw. Cookies</font></p>')
        file.write('  </li>')
        file.write('  <li><p align="left"><font size="3">Akceptacja stron wykorzystujących ramki (ang. Frames)</font></p>')
        file.write('  </li>')
        file.write('</ul>')
        file.write('</body></html>')
        return file.getvalue()

    return '<html><body>Nieznana komenda: %d</body></html>' % OID
