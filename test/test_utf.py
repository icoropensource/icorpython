import appplatform.storageutil as storageutil
import icorlib.projekt.mcrmlib as mcrmlib

class MCRM(object):
    def __init__(self):
        self.DefaultEncoding = 'utf-8'
        self.DefaultCodePage = '65001'

def Main():
    acrm=MCRM()
    aitem=mcrmlib.MCRMItemBase(acrm)
    l=[
        '%>',
        'AA ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ BB',
        storageutil.UTF8_To_CP1250('CC ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ DD'),
        '<%',
    ]
    aitem.WriteASP('c:/icor/wwwroot/appdata/test/crm/test_utf.asp', l)


if __name__ == '__main__':
    Main()
