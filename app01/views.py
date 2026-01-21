from django.conf import settings
from django.core.validators import RegexValidator
from django.shortcuts import render,HttpResponse
from utils.tecent.sms import send_sms_single
import random
from django.conf import settings

# Create your views here.

def send_sms(request):
    """发送短信（注册和登录模板id不一样）
        ?tpl=login  ->2589479
        ?tpl=register  ->2589477
    """
    tpl = request.GET.get('tpl')
    template_id = settings.TECENT_SMS_TEMPLATES.get(tpl)
    if not template_id:
        return HttpResponse('模板不存在')

    code = random.randrange(1000,9999)
    res = send_sms_single('14215241452',template_id,[code,])
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])



from django import forms
from app01 import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$','手机号格式错误'),])
    password = forms.CharField(label='密码',widget=forms.PasswordInput())

    confirm_password = forms.CharField(label='重复密码',widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.UserInfo
        # fields = '__all__'
        fields = ['username','email','password','confirm_password','mobile_phone','code']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入{}'.format(field.label)

def register(request):
    form = RegisterForm()
    return render(request, 'app01/register.html', {'form':form})
