# -*- coding: utf-8 -*-
from icorlib.icorinterface import *
import CLASSES_Library_NetBase_Utils_JSONUtil as JSONUtil


def JobTypeTrigger(**kwargs):
    kwargs['type'] = 'setJobType'
    sd = JSONUtil.write(kwargs)
    ret = '''
<script type="text/javascript">
var dp=%s;
dp['thisPageTitle']=''
dp['thisPageSubTitle']=''
dp['thisPageAction']=''
dp['thisPageDescription']=''
try {
  dp['tabs']=ltabs
} catch (e) {
}
try {
  dp['thisPageTitle']=thisPageTitle
} catch (e) {
}
try {
  dp['thisPageSubTitle']=thisPageSubTitle
} catch (e) {
}
try {
  dp['thisPageAction']=thisPageAction
} catch (e) {
}
try {
  dp['thisPageDescription']=thisPageDescription
} catch (e) {
}
dp['documentURL']=window.location.href;
function listenTabWindowMessage(event) {
   try {
      if (event.data.type === 'tabInfo') {
         window.ownerTab=event.data.ownerTab
         window.ownerSheet=event.data.ownerSheet
         dp['ownerTab']=event.data.ownerTab
         dp['ownerSheet']=event.data.ownerSheet
         window.parent.postMessage(dp,'*');
      }
      if ((event.data.type === 'editorButtonClickSubmit') && (event.data.ownerTab === window.ownerTab) && (event.data.ownerSheet === window.ownerSheet)) {
         CKEDITOR.instances[event.data.fieldname].insertHtml(event.data.fieldvalue);
      }
   } catch (e) {
   }
}
if (window.addEventListener) {
   window.addEventListener('message', listenTabWindowMessage, false)
} else {
   window.attachEvent('onmessage', listenTabWindowMessage)
}
</script>
''' % (sd)
    return ret
