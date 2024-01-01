# -*- coding: utf-8 -*-
import ldap
from ldap.controls import SimplePagedResultsControl

VERBOSE = 0
PAGE_SIZE = 1000

LATTRS_EMPTY=[
   ['objectCategory','objectCategory','objectCategory'],
] # yapf: disable

LATTRS_ORGANIZATIONALUNIT=[
   ['cn','ICoR_test_email','użytkownik'],
   ['memberOf','grupy','memberOf'],
   ['groups','grupy','groups'],
] # yapf: disable

LATTRS_USER=[
   ['c','PL','kraj skrót'],
   ['cn','ICoR_test_email','użytkownik'],
   ['co','Polska','kraj'],
   ['company','firma','firma'],
   ['countryCode','616','kod kraju'],
   ['department','dzial','dział'],
   ['description','opis','opis'],
   ['displayName','test email konto','nazwa użytkownika'],
   ['facsimileTelephoneNumber','faks','telefon faks'],
   ['givenName','imie','imię'],
   ['homePhone','telefon','telefon domowy'],
   ['info','uwagi','uwagi'],
   ['initials','r.s.','inicjały'],
   ['ipPhone','','telefon ip'],
   ['l','miasto','miasto'],
   ['mail','testemail@example.pl','email'],
   #['memberOf','grupy','grupy'],
   ['mobile','telefon','telefon komórkowy'],
   ['pager','telefon','pager'],
   ['physicalDeliveryOfficeName','biuro','biuro'],
   ['postalCode','kod','kod pocztowy'],
   ['postOfficeBox','skrytka','skrytka pocztowa'],
   ['sn','nazwisko','nazwisko'],
   ['st','wojewodztwo','województwo'],
   ['streetAddress','ulica1 ulica2','ulica'],
   ['telephoneNumber','telefon','telefon'],
   ['title','stanowisko','stanowisko'],
   ['userPrincipalName','ICOR_test_email@localnet.local','główna nazwa użytkownika'],
   ['wWWHomePage','strona www','www'],
] # yapf: disable

LATTRS_USERS=[
   ['cn','ICoR_test_email','użytkownik'],
   ['memberOf','grupy','grupy'],
] # yapf: disable

LATTRS_SCHEMA=[
   ['name','name','name'],
   ['cn','cn','cn'],
   ['lDAPDisplayName','lDAPDisplayName','lDAPDisplayName'],
   ['attributeSyntax','attributeSyntax','attributeSyntax'],
   ['isSingleValued','isSingleValued','isSingleValued'],
   ['oMSyntax','oMSyntax','oMSyntax'],
] # yapf: disable

# Syntax, attribute-Syntax, oMSyntax, TypeCategory, Type, Description
ATTRIBUTE_SYNTAX={
   '2.5.5.8_1':['Boolean','2.5.5.8','1','simple','boolean','Values can be either TRUE or FALSE.'],
   '2.5.5.9_2':['Integer','2.5.5.9','2','simple','integer','32-bit number.'],
   '2.5.5.9_10':['Enumeration','2.5.5.9','10','simple','integer','32-bit number. Active Directory treats this as an integer.'],
   '2.5.5.16_65':['Large integer(INTEGER8)','2.5.5.16','65','simple','integer','64-bit number.'],
   '2.5.5.2_6':['OID string','2.5.5.2','6','string','string','An object ID string (e.g., 2.5.5.2) consisting of digits (0–9) and dots'],
   '2.5.5.3_27':['Case-sensitive string (case- exact string)','2.5.5.3','27','string','string','Case-sensitive6 string, each character of which belongs to the General- String character set7'],
   '2.5.5.4_20':['Case-ignore string(teletex)','2.5.5.4','20','string','string','Case-insensitive string, each character of which belongs to the teletex character set7'],
   '2.5.5.5_19':['Printable string','2.5.5.5','19','string','string','Case-sensitive string, each character of which belongs to the Printable character set7'],
   '2.5.5.5_22':['IA5 string','2.5.5.5','22','string','string','Case-sensitive string, each character of which belongs to the International Alphabet 5 (IA5) character set7'],
   '2.5.5.6_18':['Numeric string','2.5.5.6','18','string','string','String, each character of which is a digit7'],
   '2.5.5.10_4':['Octet string','2.5.5.10','4','string','bytes','Array of bytes (i.e., binary data)'],
   '2.5.5.12_64':['Unicode string (directory string)','2.5.5.12','64','string','string','Normal case-insensitive string using any Unicode characters'],
   '2.5.5.15_66':['NT security descriptor','2.5.5.15','66','string','bytes','An octet string that contains a Windows NT/2000 security descriptor(SD)'],
   '2.5.5.17_4':['SID string','2.5.5.17','4','string','bytes','An octet string that contains a Windows NT/2000 security identifier (SID)'],
   '2.5.5.11_23':['UTC time string','2.5.5.11','23','time','time','Time-string format defined by ASN.1 standards. See standards ISO 8601 and X.680 for more information.8 UTC, or Coordinated Universal Time, is roughly the same as GMT, or Greenwich Mean Time. This syntax uses only two characters to represent the year.'],
   '2.5.5.11_24':['Generalized time string','2.5.5.11','24','time','time','Time-string format defined by ASN.1 standards. See standards ISO 8601 and X.680 for more information.8 This syntax uses four characters to represent the year.'],
   '2.5.5.1_127':['DN (distinguished name or DN String)','2.5.5.1','127','reference','dn','Distinguished name of an object in the directory. If the target object is moved or renamed, Active Directory updates the DN attribute accordingly.'],
   '2.5.5.7_127':['DN with binary (DN with octet string) ','2.5.5.7','127','reference','bytes','This syntax stores a distinguished name along with some binary data. Active Directory keeps the DN up-to-date. The format is B:hex digit count:bytes as hex:DN (e.g., B:6:F12A4B:someDN).'],
   '2.5.5.7_127':['OR name','2.5.5.7','127','reference','bytes','An X.400 syntax (related to e-mail addresses).'],
   '2.5.5.10_127':['Replica link','2.5.5.10','127','reference','bytes','Syntax that repsFrom and repsTo attributes use to control replication. The corresponding attributes contain things such as the up-to-date vector of a replication partition.'],
   '2.5.5.13_127':['Presentation address','2.5.5.13','127','reference','bytes','OSI application entities use presentation addresses to address other application entities. See RFCs 1278 and 2252 and ISO DIS 7498-3 for more information.'],
   '2.5.5.14_127':['DN with Unicode string','2.5.5.14','127','reference','bytes','This syntax stores a distinguished name along with a string. Active Directory keeps the DN up-to-date. The format is S:character count:string:DN (e.g., S:5: hello:someDN).'],
   '2.5.5.14_127':['Access point DN','2.5.5.14','127','reference','bytes','An X.400 distinguished name.'],
} # yapf: disable

SCHEMA_ATTRIBUTES = {}
SCHEMA_FIELDS = {}


class LDAPField(object):

    def __init__(self, ahelper, aname):
        self.helper = ahelper
        self.name = aname
        aattrs = self.helper.GetAttributes()
        dattr = aattrs.get(aname, {})
        self.attributeSyntax = dattr.get('attributeSyntax', '')
        self.oMSyntax = dattr.get('oMSyntax', '')
        self.isSingleValued = dattr.get('isSingleValued', '') != 'FALSE'
        atypeid = self.attributeSyntax + '_' + self.oMSyntax
        ltype = ATTRIBUTE_SYNTAX.get(atypeid, [])
        if not ltype:
            print 'UNKNOWN FIELD SYNTAX: %s: %s' % (aname, atypeid)
            ltype = ['', '', '', '', '', '']
        self.syntax, self.typeCategory, self.typeField, self.description = ltype[0], ltype[3], ltype[4], ltype[5]

    def AsDict(self, avalue):
        if self.isSingleValued and (type(avalue) == type([])):
            if avalue:
                avalue = avalue.pop()
            else:
                avalue = ''
        d={
           'name':self.name,
           'syntax':self.syntax,
           'typeCategory':self.typeCategory,
           'typeField':self.typeField,
           'isSingleValued':self.isSingleValued,
           'value':avalue,
        } # yapf: disable
        return d


class LDAPHelper(object):

    def __init__(self, server, ldomain=None):
        self.LDAP_SERVER = server
        self.LDAP_USERNAME = ''
        self.LDAP_PASSWORD = ''
        if ldomain is None:
            ldomain = []
        elif type(ldomain) != type([]):
            ldomain = ldomain.split('.')
        self.LDAP_DN_LIST = ldomain
        if ldomain:
            self.LDAP_DN = '.'.join(ldomain)
            self.LDAP_BASE_DN = ','.join(['DC=%s' % x for x in ldomain])
        else:
            self.LDAP_DN = ''
            self.LDAP_BASE_DN = ''
        self.ldap_client = None

    def GetUserName(self, username=''):
        if not username:
            return self.LDAP_USERNAME
        if self.LDAP_DN and (username.find('@') < 0):
            username = '%s@%s' % (username, self.LDAP_DN)
        return username

    def Open(self, username, password):
        if self.ldap_client is not None:
            self.Close()
        self.LDAP_USERNAME = self.GetUserName(username)
        self.LDAP_PASSWORD = password
        try:
            # Ignore server side certificate errors (assumes using LDAPS and
            # self-signed cert). Not necessary if not LDAPS or it's signed by
            # a real CA.
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
            # Don't follow referrals
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            self.ldap_client = ldap.initialize(self.LDAP_SERVER)
            self.ldap_client.set_option(ldap.OPT_REFERRALS, 0)
            self.ldap_client.protocol_version = 3
            self.ldap_client.simple_bind_s(self.LDAP_USERNAME, self.LDAP_PASSWORD)
        except ldap.INVALID_CREDENTIALS:
            self.Close()
            return 1    #'Wrong username or password'
        except ldap.SERVER_DOWN:
            return 2    #'AD server not awailable'
        return 0

    def Close(self):
        if self.ldap_client is None:
            return
        self.ldap_client.unbind()
        self.ldap_client = None
        self.LDAP_USERNAME = ''
        self.LDAP_PASSWORD = ''

    def SearchSimple(self, ldap_filter, basedn=None, lattrs=None, attrsonly=0):
        if self.ldap_client is None:
            return {}
        if basedn is None:
            basedn = self.LDAP_BASE_DN
        attrs = lattrs
        if lattrs is not None:
            attrs = []
            for aattr in lattrs:
                attrs.append(aattr[0])
        ret = self.ldap_client.search_s(basedn, ldap.SCOPE_SUBTREE, ldap_filter, attrlist=attrs, attrsonly=attrsonly)
        #if VERBOSE:
        #print 'RET:',json.dumps(ret,indent=2,ensure_ascii=False,encoding='utf-8',sort_keys=True)
        return ret

    def Search(self, ldap_filter, basedn=None, lattrs=None, attrsonly=0):
        ret = []
        if self.ldap_client is None:
            return ret
        if basedn is None:
            basedn = self.LDAP_BASE_DN
        attrs = lattrs
        if lattrs is not None:
            attrs = []
            for aattr in lattrs:
                attrs.append(aattr[0])
        # Create the page control to work from
        lc = SimplePagedResultsControl(True, size=PAGE_SIZE, cookie='')
        # Do searches until we run out of "pages" to get from
        # the LDAP server.
        while True:
            # Send search request
            try:
                # If you leave out the ATTRLIST it'll return all attributes
                # which you have permissions to access. You may want to adjust
                # the scope level as well (perhaps "ldap.SCOPE_SUBTREE", but
                # it can reduce performance if you don't need it).
                msgid = self.ldap_client.search_ext(basedn, ldap.SCOPE_SUBTREE, ldap_filter, attrlist=attrs, attrsonly=attrsonly, serverctrls=[lc])
            except ldap.LDAPError as e:
                print 'LDAP SEARCH E1:', e
                break
            # Pull the results from the search request
            try:
                rtype, rdata, rmsgid, serverctrls = self.ldap_client.result3(msgid)
            except ldap.LDAPError as e:
                print 'LDAP SEARCH E2:', e
                break
            # Each "rdata" is a tuple of the form (dn, attrs), where dn is
            # a string containing the DN (distinguished name) of the entry,
            # and attrs is a dictionary containing the attributes associated
            # with the entry. The keys of attrs are strings, and the associated
            # values are lists of strings.
            ret.extend(rdata)
            # Get cookie for next request
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if not pctrls:
                print 'LDAP SEARCH W1:', 'Warning: Server ignores RFC 2696 control.'
                break
            # Ok, we did find the page control, yank the cookie from it and
            # insert it into the control for our next search. If however there
            # is no cookie, we are done!
            cookie = pctrls[0].cookie
            if not cookie:
                break
            lc.cookie = cookie
        return ret

    def GetSchemaAttributes(self):
        ldap_filter = '(objectCategory=attributeSchema)'
        ret = self.Search(ldap_filter, basedn='cn=Schema,cn=Configuration,' + self.LDAP_BASE_DN, lattrs=LATTRS_SCHEMA, attrsonly=0)
        return ret

    def GetAttributes(self, adn=''):
        if not adn:
            adn = self.LDAP_DN
        global SCHEMA_ATTRIBUTES
        aattrs = SCHEMA_ATTRIBUTES.get(adn, None)
        if aattrs is None:
            aattrs = {}
            la = self.GetSchemaAttributes()
            for lai in la:
                d = {}
                for k, v in lai[1].items():
                    d[k] = v[0]
                aattrs[d.get('lDAPDisplayName', '')] = d
            SCHEMA_ATTRIBUTES[adn] = aattrs
        return aattrs

    def GetField(self, aname, adn=''):
        if not adn:
            adn = self.LDAP_DN
        global SCHEMA_FIELDS
        dfields = SCHEMA_FIELDS.get(adn, {})
        afield = dfields.get(aname, None)
        if afield is None:
            afield = LDAPField(self, aname)
            dfields[aname] = afield
            SCHEMA_FIELDS[adn] = dfields
        return afield

    def GetItem(self, aitem, asnone=0, adnasstring=0, anoemptyvalues=0):
        dret = {}
        if asnone:
            dret = None
        if not aitem:
            return dret
        if type(aitem) not in [type([]), type(())]:
            print 'BAD ITEM TYPE:', aitem
            return dret
        if len(aitem) != 2:
            print 'BAD ITEM LENGTH:', aitem
            return dret
        if aitem[0] is None:
            return dret
        dret = {}
        if adnasstring:
            dret['_dn'] = aitem[0]
        else:
            dret['_dn'] = ldap.dn.str2dn(aitem[0])
        da = aitem[1]
        for akey in da.keys():
            afield = self.GetField(akey)
            if not afield.typeField in ['bytes']:
                v = da[akey]
                if not v and anoemptyvalues:
                    continue
                dret[akey] = afield.AsDict(v)
        return dret

    def GetItems(self, aitems, asnone=0, adnasstring=0, anoemptyvalues=0, asort=None):
        l = []
        for aitem in aitems:
            v = self.GetItem(aitem, asnone=asnone, adnasstring=adnasstring, anoemptyvalues=anoemptyvalues)
            if asnone and v is None:
                continue
            l.append(v)
        if asort:
            l.sort(asort)
        return l

    def GetUser(self, username=''):
        username = self.GetUserName(username)
        ldap_filter = 'userPrincipalName=%s' % username
        ret = self.Search(ldap_filter)    #lattrs=LATTRS_USER
        d = {}
        if ret:
            d = self.GetItem(ret[0])
        return d

    def GetGroups(self):
        ldap_filter = '(objectClass=group)'
        ret = self.Search(ldap_filter)    #lattrs=LATTRS_ORGANIZATIONALUNIT
        return ret

    def GetAllUserObjects(self):
        ldap_filter = '(&(objectCategory=person)(objectClass=user))'
        l = self.Search(ldap_filter, lattrs=LATTRS_USERS)
        ret = self.GetItems(l, asnone=1)
        return ret

    def GetCustomQueryTree(self, aquery):
        l = self.Search(aquery, lattrs=LATTRS_EMPTY, attrsonly=0)
        ret = self.GetItems(l, asnone=1, adnasstring=1, anoemptyvalues=1, asort=lambda x, y: cmp(x['_dn'].lower(), y['_dn'].lower()))
        return ret

    def GetCustomQuery(self, aquery):
        l = self.Search(aquery)
        ret = self.GetItems(l, asnone=1, adnasstring=1, anoemptyvalues=1, asort=lambda x, y: cmp(x['_dn'].lower(), y['_dn'].lower()))
        return ret

    def GetAllUserObjectsTree(self):
        return self.GetCustomQueryTree('(&(objectCategory=person)(objectClass=user))')
