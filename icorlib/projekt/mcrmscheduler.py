# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.mcrmbasesimple as MCRMBaseSimple


def Main(leventschedulernames=None):
    uclass = aICORDBEngine.Classes['CLASSES_Library_DBBase_DMSWorkflow_Prototyp_XMLRozdzialy_Component_Plugin']
    if leventschedulernames is None:
        leventschedulernames=['OnSchedulerMinute','OnSchedulerHour','OnSchedulerDay','OnSchedulerWeek','OnSchedulerMonth',
        'OnSchedulerMinute1',
        'OnSchedulerMinute2',
        'OnSchedulerMinute3',
        'OnSchedulerMinute4',
        'OnSchedulerMinute5',
        'OnSchedulerMinute6',
        'OnSchedulerMinute7',
        'OnSchedulerMinute8',
        'OnSchedulerMinute9',
        'OnSchedulerMinute10',
        'OnSchedulerMinute15',
        'OnSchedulerMinute20',
        'OnSchedulerMinute25',
        'OnSchedulerMinute30',
        'OnSchedulerMinute35',
        'OnSchedulerMinute40',
        'OnSchedulerMinute45',
        'OnSchedulerMinute50',
        'OnSchedulerMinute55',
        ] # yapf: disable
    acms = MCRMBaseSimple.CMS(alogname='scheduler', aconsole=1, acominitialize=1)
    try:
        aobj = uclass.GetFirstObject()
        while aobj:
            if aobj['SGIsDisabled']:
                aobj.Next()
                continue
            aplugin = None
            eobj = aobj.PluginEvents
            while eobj:
                try:
                    aeventname = eobj.EventKind.EventName
                    if aeventname in leventschedulernames:
                        if aplugin is None:
                            aproject = acms.GetProject(aobj.Struktura.Projekt)
                            if aproject is not None:
                                awwwmenustruct = aproject.GetWWWMenuStruct(aobj.Struktura)
                                if awwwmenustruct is not None:
                                    aplugin = awwwmenustruct.GetPlugin(aobj)
                        if aplugin is not None:
                            aevent = aplugin.GetEvent(eobj, aeventname, eobj.EventSource)
                except:
                    acms.LogException()
                eobj.Next()
            tobj = aobj.Template
            while tobj:
                atemplate = None
                eobj = tobj.TemplateEvents
                while eobj:
                    try:
                        aeventname = eobj.EventKind.EventName
                        if aeventname in leventschedulernames:
                            if aplugin is None:
                                aproject = None
                                aprobj = aobj.Struktura.Projekt
                                if aprobj:
                                    aproject = acms.GetProject(aprobj)
                                if aproject is not None:
                                    awwwmenustruct = aproject.GetWWWMenuStruct(aobj.Struktura)
                                    if awwwmenustruct is not None:
                                        aplugin = awwwmenustruct.GetPlugin(aobj)
                            if aplugin is not None:
                                if atemplate is None:
                                    atemplate = aplugin.GetTemplate(tobj)
                                aevent = atemplate.GetEvent(eobj, aeventname, eobj.EventSource)
                    except:
                        acms.LogException()
                    eobj.Next()
                tobj.Next()
            aobj.Next()
        acms.Dump()
    except:
        acms.LogException()
    try:
        acms.ProcessEvents(leventschedulernames=leventschedulernames)
    except:
        acms.LogException()
