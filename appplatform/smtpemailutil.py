# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import smtplib
import base64

import string

from email.MIMEMultipart import MIMEMultipart    #pylint: disable=E0611,E0401
from email.MIMEText import MIMEText    #pylint: disable=E0611,E0401
from email.MIMEImage import MIMEImage    #pylint: disable=E0611,E0401
from email.Header import Header    #pylint: disable=E0611,E0401
from email.MIMEBase import MIMEBase    #pylint: disable=E0611,E0401
try:
    from email import encoders
except:
    from email import Encoders as encoders
from email.Utils import COMMASPACE, formatdate    #pylint: disable=E0611,E0401

import appplatform.storageutil as storageutil


def encode_base64(s, eol=None):
    return "".join(base64.encodestring(s).split("\n"))


class AuthSMTP(smtplib.SMTP):

    def login(self, user, password):

        def encode_cram_md5(challenge, user, password):
            import hmac
            challenge = base64.decodestring(challenge)
            response = user + " " + hmac.HMAC(password, challenge).hexdigest()
            return encode_base64(response, eol="")

        def encode_plain(user, password):
            return encode_base64("%s\0%s\0%s" % (user, user, password), eol="")

        AUTH_PLAIN = "PLAIN"
        AUTH_CRAM_MD5 = "CRAM-MD5"
        AUTH_LOGIN = "LOGIN"
        if self.helo_resp is None and self.ehlo_resp is None:
            if not (200 <= self.ehlo()[0] <= 299):
                (code, resp) = self.helo()
                if not (200 <= code <= 299):
                    raise smtplib.SMTPHeloError(code, resp)
        if not self.has_extn("auth"):
            raise smtplib.SMTPException("Rozszerzenie SMTP AUTH nie jest wspierane przez serwer.")
        authlist = self.esmtp_features["auth"].split()
        preferred_auths = [AUTH_PLAIN, AUTH_LOGIN, AUTH_CRAM_MD5]
        authmethod = None
        for method in preferred_auths:
            if method in authlist:
                authmethod = method
                break
        if authmethod == AUTH_CRAM_MD5:
            (code, resp) = self.docmd("AUTH", AUTH_CRAM_MD5)
            if code == 503:
                return (code, resp)
            (code, resp) = self.docmd(encode_cram_md5(resp, user, password))
        elif authmethod == AUTH_PLAIN:
            (code, resp) = self.docmd("AUTH", AUTH_PLAIN + " " + encode_plain(user, password))
        elif authmethod == AUTH_LOGIN:
            (code, resp) = self.docmd("AUTH", "%s %s" % (AUTH_LOGIN, encode_base64(user, eol="")))
            if code != 334:
                raise smtplib.SMTPAuthenticationError(code, resp)
            (code, resp) = self.docmd(encode_base64(password, eol=""))
        elif authmethod == None:
            raise smtplib.SMTPException("Nie znaleziono dostepnej metody autentykacji.")
        if code not in [235, 503]:
            raise smtplib.SMTPAuthenticationError(code, resp)
        return (code, resp)


class SMTPServer:

    def __init__(self, aSMTPServer, aSMTPUser, aSMTPPassword, aSMTPFrom):
        self.SMTPServer = aSMTPServer
        self.SMTPUser = aSMTPUser
        self.SMTPPassword = aSMTPPassword
        self.SMTPFrom = aSMTPFrom

    def Send(self, ato, asubject, atext, alog=None, afiles=None, afrom=None):
        if not self.SMTPServer:
            if alog:
                alog.Log('brak konfiguracji SMTP %s - "%s"' % (ato, asubject), aconsole=0)
            return 7
        if afiles is None:
            afiles = []
        if 1:
            msgRoot = MIMEMultipart()
            msgRoot.set_charset('utf-8')
            msgRoot['Subject'] = Header(asubject.replace(':', ' - '), 'utf-8')    #XMLUtil
            msgRoot['From'] = string.strip(self.SMTPFrom)
            utc_from_epoch = time.time()
            msgRoot['Date'] = formatdate(utc_from_epoch, localtime=True)
            if type(ato) == type([]):
                msgRoot['To'] = COMMASPACE.join(ato)    #XMLUtil
            else:
                msgRoot['To'] = ato    #XMLUtil
            msgRoot.preamble = 'This is a multi-part message in MIME format.'
            msgRoot.epilogue = ''
            #         msgAlternative = MIMEMultipart('alternative')
            #         msgRoot.attach(msgAlternative)
            #         msgText = MIMEText(XMLUtil.CP1250_To_UTF8('Ten komunikat należy odczytać w postaci HTML.'),'plain','utf-8')
            #         msgRoot.attach(msgText)
            if atext.find('<p') < 0:
                atext = '\n<p>\n' + atext + '\n</p>\n'
            if atext.find('<body') < 0:
                atext = '\n<body>\n' + atext + '\n</body>\n'
            if atext.find('<html') < 0:
                atext = '\n<html>\n' + atext + '\n</html>\n'
            if alog:
                alog.Log('Treść EMAIL do: ' + str(ato), aconsole=0)
                alog.Log(storageutil.UTF8_To_CP1250(atext), aconsole=0)
            msgText = MIMEText(atext, 'html', 'utf-8')    #XMLUtil
            msgRoot.attach(msgText)

        if 1:
            for afpath in afiles:
                if type(afpath) in [type([]), type(())]:
                    afpath, afname = afpath
                else:
                    afname = afpath
                part = MIMEBase('application', 'octet-stream')
                asize1, asize2 = 0, 1
                while asize1 != asize2:
                    asize1 = asize2
                    asize2 = os.path.getsize(afpath)
                    time.sleep(0.9)
                if alog:
                    alog.Log('Dodanie zalacznika: ' + afpath + ' rozmiar ' + str(asize1), aconsole=0)
                fb = open(afpath, 'rb')
                bfile = fb.read()
                fb.close()
                part.set_payload(bfile)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(afname))
                msgRoot.attach(part)

        w = 1
        if alog:
            alog.Log('Wysyłanie potwierdzenia na adres: ' + str(ato), aconsole=0)
        try:
            asmtp = AuthSMTP(self.SMTPServer)    #SMTPUtil
            if self.SMTPUser != '' and self.SMTPPassword != '':
                asmtp.login(self.SMTPUser, self.SMTPPassword)
            if type(ato) != type([]):
                lto = [ato, ]
            else:
                lto = ato
            lto = map(string.strip, lto)
            stext = msgRoot.as_string()
            if alog:
                alog.Log('message text: len=' + str(len(stext)), aconsole=0)
                alog.Log(stext, aconsole=0)
            asmtp.sendmail(string.strip(self.SMTPFrom), lto, stext)
            asmtp.quit()
            w = 0
        except smtplib.SMTPRecipientsRefused, e:
            _rejects = {str(e): 'Recipients refused'}
            if alog:
                alog.LogException()
            w = 2
        except smtplib.SMTPSenderRefused, e:
            _rejects = {str(e): self.SMTPFrom}
            if alog:
                alog.LogException()
            w = 3
        except smtplib.SMTPDataError, e:
            _rejects = {smtplib.SMTPDataError: ''}
            w = 4
            if string.find(e.smtp_error, 'try again later') > 0:
                w = 5
            if alog:
                alog.LogException()


#      except socket.error, e:
#         rejects = {sockerror(e): ''}
#         if alog:
#            alog.LogException()
        except Exception, e:
            _rejects = {'Error sending mail': e}    # fake the rejects dict
            if alog:
                alog.LogException()
            w = 6
        return w
