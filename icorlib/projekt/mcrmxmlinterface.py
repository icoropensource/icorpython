# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import icorlib.projekt.msqlquery as MSQLQuery
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
#import xmllib
import string

DEBUG = 0


class ICORXMLCRMQueryDefinitionParser(XMLUtil.ICORBaseXMLParser):

    def __init__(self, acrm, queryparams=None):
        #      xmllib.XMLParser.__init__(self,accept_utf8=1,accept_unquoted_attributes=1,accept_missing_endtag_name=1)
        XMLUtil.ICORBaseXMLParser.__init__(self)
        self.CRM = acrm
        if queryparams is None:
            queryparams = {}
        self.status = []
        self.querysql = MSQLQuery.QuerySQL(acrm, **queryparams)
        self._context = []
        self.context = ''

    def Parse(self, atext):
        self.skiptablecnt = 0
        self.linkfields = []
        XMLUtil.ICORBaseXMLParser.Parse(self, atext)
        if 0:
            self.reset()
            self.elements = {}
            self.elements['ICORCRMTEMPLATE'] = (self.start_ICORCRMTEMPLATE, self.end_ICORCRMTEMPLATE)
            self.elements['EVENTPIVOTDETAILS'] = (self.start_EVENTPIVOTDETAILS, self.end_EVENTPIVOTDETAILS)
            self.elements['DOCUMENT'] = (self.start_DOCUMENT, self.end_DOCUMENT)
            self.elements['SQLTABLE'] = (self.start_SQLTABLE, self.end_SQLTABLE)
            self.elements['SQLFIELD'] = (self.start_SQLFIELD, self.end_SQLFIELD)
            self.elements['RULE'] = (self.start_RULE, self.end_RULE)
            self.elements['WIZARDS'] = (self.start_WIZARDS, self.end_WIZARDS)
            self.elements['WIZARD'] = (self.start_WIZARD, self.end_WIZARD)
            self.elements['WIZARDSTEP'] = (self.start_WIZARDSTEP, self.end_WIZARDSTEP)
            self.elements['SOURCETABLE'] = (self.start_SOURCETABLE, self.end_SOURCETABLE)
            self.elements['BASETABLE'] = (self.start_BASETABLE, self.end_BASETABLE)
            self.elements['TABLELINKS'] = (self.start_TABLELINKS, self.end_TABLELINKS)
            self.elements['TABLELINK'] = (self.start_TABLELINK, self.end_TABLELINK)
            self.elements['MARKER'] = (self.start_MARKER, self.end_MARKER)
            self.elements['MARKERRULE'] = (self.start_MARKERRULE, self.end_MARKERRULE)
            self.elements['DICTVALUE'] = (self.start_DICTVALUE, self.end_DICTVALUE)
            self.elements['FORMINFO'] = (self.start_FORMINFO, self.end_FORMINFO)
            self.elements['FORMELEMENT'] = (self.start_FORMELEMENT, self.end_FORMELEMENT)
            self.elements['QUERYDEPENDENCY'] = (self.start_QUERYDEPENDENCY, self.end_QUERYDEPENDENCY)
            self.elements['DEPENDENCYID'] = (self.start_DEPENDENCYID, self.end_DEPENDENCYID)
            self.elements['ALERTLINK'] = (self.start_ALERTLINK, self.end_ALERTLINK)
            self.elements['ALERTPARAM'] = (self.start_ALERTPARAM, self.end_ALERTPARAM)
            self.feed(atext)

    def PushContext(self, acontext):
        if DEBUG:
            print '%sPushContext: %s' % (' ' * (len(self._context) * 2), acontext)
        self._context.append(self.context)
        self.context = acontext

    def PopContext(self):
        self.context = self._context.pop()
        if DEBUG:
            print '%sPopContext: %s' % (' ' * (len(self._context) * 2), self.context)

    def AsSQL(self):
        return self.querysql.AsSQL()

    def start_ICORCRMTEMPLATE(self, attrs):
        self.querysql.SetTemplateParms(attrs)

    def start_EVENTPIVOTDETAILS(self, attrs):
        self.TagData = ''

    def start_DOCUMENT(self, attrs):
        self.PushContext('DOCUMENT')

    def start_SQLTABLE(self, attrs):
        if self.skiptablecnt:
            self.skiptablecnt = self.skiptablecnt + 1
            return
        if self.context == 'SQLFIELD':
            aextdictfield = self.querysql.ThisTable.ThisField
            asqlrevfield = aextdictfield.Name
            asqlparentextconstraint = aextdictfield.ExtDictConstraint
        atable = self.querysql.PushTable(attrs)
        if atable is None:
            self.skiptablecnt = 1
            return
        if self.context == 'WIZARDSTEP':
            atable.ContextField = '_KreatorOID'
        elif self.context in ['SOURCETABLE', 'BASETABLE']:
            if 'TABLELINKS' in self._context:
                atable.RevContextField = self.querysql.LinkFields[1]
            else:
                atable.RevContextField = '_Dotyczy'
        elif self.context == 'SQLFIELD':
            aextdictfield.ExternalDictTable = atable
            atable.RevContextField = asqlrevfield
            atable.ParentExtConstraint = asqlparentextconstraint

    def start_SQLFIELD(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.ThisTable.AddField(attrs)
        self.linkfields.append(self.querysql.LinkFields)
        if self.querysql.ThisTable.ThisField.Type in ['external dict', 'external dict multiple']:
            self.querysql.LinkFields = None
        self.PushContext('SQLFIELD')

    def start_RULE(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.ThisTable.ThisField.AddRule(attrs)

    def start_WIZARDS(self, attrs):
        if self.skiptablecnt:
            return
        atable = self.querysql.PushTable(self.CRM.Table_Kreator)
        if self.context == 'DOCUMENT':
            atable.ContextField = 'DokumentOID'

    def start_WIZARD(self, attrs):
        pass

    def start_WIZARDSTEP(self, attrs):
        self.PushContext('WIZARDSTEP')

    def start_SOURCETABLE(self, attrs):
        self.PushContext('SOURCETABLE')

    def start_BASETABLE(self, attrs):
        self.PushContext('BASETABLE')

    def start_TABLELINKS(self, attrs):
        self.PushContext('TABLELINKS')

    def start_TABLELINK(self, attrs):
        if self.skiptablecnt:
            return
        self.linkfields.append(self.querysql.LinkFields)
        self.querysql.LinkFields = attrs['srcfield'], attrs['dstfield'], attrs.get('linkconstraint', '')
        self.querysql.IsTableView = int(attrs.get('istableview', '0'))
        self.querysql.IsExtensionTable = int(attrs.get('isextension', '0'))

    def start_MARKER(self, attrs):
        if self.skiptablecnt:
            return
        if self.context == 'SQLFIELD':
            self.querysql.ThisTable.ThisField.AddMarker(attrs)

    def start_MARKERRULE(self, attrs):
        if self.skiptablecnt:
            return
        if self.context == 'SQLFIELD':
            self.querysql.ThisTable.ThisField.ThisMarker.AddMarkerRule(attrs)

    def end_MARKERRULE(self):
        pass

    def start_DICTVALUE(self, attrs):
        if self.skiptablecnt:
            return
        if self.context == 'SQLFIELD':
            self.querysql.ThisTable.ThisField.AddDictValue(attrs)

    def end_DICTVALUE(self):
        pass

    def start_FORMINFO(self, attrs):
        pass

    def end_FORMINFO(self):
        pass

    def start_FORMELEMENT(self, attrs):
        #      print '   [[[ ELEMENT:',str(attrs)
        if self.skiptablecnt:
            return
        self.formelementattrs = attrs
        self.TagData = ''

    def end_FORMELEMENT(self):
        if self.skiptablecnt:
            return
        if self.context == 'SQLFIELD':
            self.querysql.ThisTable.ThisField.AddFormElement(self.formelementattrs, self.TagData)
        elif self.context == 'SOURCETABLE':
            self.querysql.ThisTable.AddFormElement(self.formelementattrs, self.TagData)
        else:
            self.querysql.AddFormElement(self.formelementattrs, self.TagData)
        self.formelementattrs = None

    def start_QUERYDEPENDENCY(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.AddQueryDependency(attrs)

    def end_QUERYDEPENDENCY(self):
        if self.skiptablecnt:
            return

    def start_DEPENDENCYID(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.AddDependencyID(attrs)

    def end_DEPENDENCYID(self):
        if self.skiptablecnt:
            return

    def start_ALERTLINK(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.AddAlertLink(attrs)

    def end_ALERTLINK(self):
        if self.skiptablecnt:
            return

    def start_ALERTPARAM(self, attrs):
        if self.skiptablecnt:
            return
        self.querysql.AddAlertParam(attrs)

    def end_ALERTPARAM(self):
        if self.skiptablecnt:
            return

    def end_MARKER(self):
        pass

    def end_TABLELINK(self):
        self.querysql.LinkFields = self.linkfields.pop()

    def end_TABLELINKS(self):
        self.PopContext()

    def end_WIZARDS(self):
        if self.skiptablecnt:
            return
        self.querysql.PopTable()

    def end_WIZARD(self):
        pass

    def end_WIZARDSTEP(self):
        self.PopContext()

    def end_SQLTABLE(self):
        if self.skiptablecnt:
            self.skiptablecnt = self.skiptablecnt - 1
            return
        if not self.context in ['DOCUMENT', 'SOURCETABLE']:
            self.querysql.PopTable()

    def end_SQLFIELD(self):
        if self.skiptablecnt:
            return
        self.querysql.LinkFields = self.linkfields.pop()
        self.PopContext()

    def end_RULE(self):
        pass

    def end_SOURCETABLE(self):
        self.PopContext()
        if self.skiptablecnt:
            return
        self.querysql.PopTable()

    def end_BASETABLE(self):
        self.PopContext()

    def end_DOCUMENT(self):
        self.PopContext()
        if self.skiptablecnt:
            return
        self.querysql.PopTable()

    def end_EVENTPIVOTDETAILS(self):
        self.querysql.SetEventPivotDetails(self.TagData)

    def end_ICORCRMTEMPLATE(self):
        pass
