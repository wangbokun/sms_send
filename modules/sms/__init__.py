
from sms_web import SmsWeb
from sms_sender import SmsSender

def get_module_config():
    
    return {"webmgt" : {"smsapi" : SmsWeb},
            "webapi" : None,
            "service" : {"sender":SmsSender}}
