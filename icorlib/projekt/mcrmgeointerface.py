# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_XMLUtil as XMLUtil
import CLASSES_Library_ICORBase_Interface_ICORUtil as ICORUtil
import string
import re
import os


class GeoPersistent:

    def __init__(self, adata):
        self.Data = adata
        self.Len = len(self.Data)
        if self.Len > 0:
            self.GeoStatus = 1
        else:
            self.GeoStatus = 0

    def WriteJSON(self, afname):
        foutgeostatus = ICORUtil.OpenText(afname, 'w', 'utf-8')
        foutgeostatus.write('{geostatus:%d,itemcnt:%d}' % (self.GeoStatus, self.Len))
        foutgeostatus.close()

    def WriteKML(self, afname):
        if not self.Len:
            try:
                os.unlink(afname)
            except:
                pass
            return
        fout = XMLUtil.MXMLFile(afname, anopl=1, aencoding='utf-8', astemp=1)
        fout.Header()
        fout.TagOpen('kml', {'xmlns': 'http://earth.google.com/kml/2.2'})
        fout.TagOpen('Document')
        for d in self.Data:
            ainfo = XMLUtil.CP1250_To_UTF8(d.get('info', ''))
            alat = d['lat']
            alon = d['lon']
            fout.TagOpen('Placemark')
            fout.TagOpen('name', aclosetag=1, avalue=ainfo)
            fout.TagOpen('description', aclosetag=1)
            fout.TagOpen('Point')
            fout.TagOpen('coordinates', aclosetag=1, avalue='%s,%s' % (alon, alat))
            fout.TagClose()
            fout.TagOpen('address', aclosetag=1, avalue='%s,%s' % (alat, alon))
            fout.TagClose()
        fout.TagClose()
        fout.TagClose()
        fout.close()

    def WriteGPX(self, afname):
        if not self.Len:
            try:
                os.unlink(afname)
            except:
                pass
            return
        fout = XMLUtil.MXMLFile(afname, anopl=1, aencoding='utf-8', astemp=1)
        fout.Header(astandalone='no')
        fout.TagOpen('gpx',{
           'xmlns':'http://www.topografix.com/GPX/1/1',
           'creator':'ICOR',
           'version':'1.1',
           'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
           'xsi:schemaLocation':'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
           }
        ) # yapf: disable
        for d in self.Data:
            ainfo = XMLUtil.CP1250_To_UTF8(d.get('info', ''))
            alat = d['lat']
            alon = d['lon']
            fout.TagOpen('wpt', {'lat': alat, 'lon': alon})
            fout.TagOpen('ele', aclosetag=1)
            fout.TagOpen('time', aclosetag=1)
            fout.TagOpen('name', aclosetag=1, avalue=ainfo)
            fout.TagOpen('sym', aclosetag=1)
            fout.TagClose()
        fout.TagClose()
        fout.close()

    def WriteMiniMap(self, afname):
        if not self.Len:
            try:
                os.unlink(afname)
            except:
                pass
            return
        fout = XMLUtil.MXMLFile(afname, anopl=1, aencoding='utf-8', astemp=1)
        fout.Header()
        fout.TagOpen('Placemarks')
        for d in self.Data:
            ainfo = XMLUtil.CP1250_To_UTF8(d.get('info', ''))
            alat = d['lat']
            alon = d['lon']
            fout.TagOpen('Placemark')
            fout.TagOpen('title', aclosetag=1, avalue=ainfo)
            fout.TagOpen('address', aclosetag=1, avalue='%s,%s' % (alat, alon))
            fout.TagOpen('description', aclosetag=1)
            fout.TagOpen('url', aclosetag=1, avalue='http://maps.google.com/maps?q=%s,%s' % (alat, alon))
            fout.TagOpen('lat', aclosetag=1, avalue=alat)
            fout.TagOpen('lng', aclosetag=1, avalue=alon)
            fout.TagOpen('accuracy', aclosetag=1, avalue='8')
            fout.TagOpen('altd', aclosetag=1)
            fout.TagOpen('country', aclosetag=1)
            fout.TagOpen('state', aclosetag=1)
            fout.TagOpen('county', aclosetag=1)
            fout.TagOpen('locality', aclosetag=1)
            fout.TagOpen('street', aclosetag=1)
            fout.TagOpen('postal', aclosetag=1)
            fout.TagClose()
        fout.TagClose()
        fout.close()

    def WriteLMX(self, afname):
        if not self.Len:
            try:
                os.unlink(afname)
            except:
                pass
            return
        fout = XMLUtil.MXMLFile(afname, anopl=1, aencoding='utf-8', astemp=1)
        fout.Header()
        fout.TagOpen('lm:lmx', {'xmlns:lm': 'http://www.nokia.com/schemas/location/landmarks/1/0', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:schemaLocation': 'http://www.nokia.com/schemas/location/landmarks/1/0 lmx.xsd'})
        fout.TagOpen('lm:landmarkCollection')
        for d in self.Data:
            ainfo = XMLUtil.CP1250_To_UTF8(d.get('info', ''))
            alat = d['lat']
            alon = d['lon']
            fout.TagOpen('lm:landmark')
            fout.TagOpen('lm:name', aclosetag=1, avalue=ainfo)
            fout.TagOpen('lm:coordinates')
            fout.TagOpen('lm:latitude', aclosetag=1, avalue='%s' % (alat, ))
            fout.TagOpen('lm:longitude', aclosetag=1, avalue='%s' % (alon, ))
            fout.TagClose()
            fout.TagClose()
        fout.TagClose()
        fout.TagClose()
        fout.close()
