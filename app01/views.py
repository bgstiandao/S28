from django.conf import settings
from django.shortcuts import render,HttpResponse
from utils.tecent.sms import send_sms_single
import random
from django.conf import settings

# Create your views here.

def send_sms(request):
    """发送短信
        ?tpl=login  ->548762
        ?tpl=register  ->548760
    """
    tpl = request.GET.get('tpl')
    template_id = settings.TECENT_SMS_TEMPLATES.get(tpl)
    if not template_id:
        return HttpResponse('模板不存在')

    code = random.randrange(1000,9999)
    res = send_sms_single('18309280693',template_id,[code,])
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])