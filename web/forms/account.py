from wsgiref.validate import validator
import random
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from django_redis import get_redis_connection
from web import models
from utils.tecent.sms import send_sms_single
from utils import encrypt

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length':'密码长度不能小于8个字符',
            'max_length': '密码长度不能大于8个字符',
        },
        widget=forms.PasswordInput(),
    )

    confirm_password = forms.CharField(
        label='重复密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': '密码长度不能小于8个字符',
            'max_length': '密码长度不能大于8个字符',
        },
        widget=forms.PasswordInput(),
    )

    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$','手机号格式错误'),])

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

    def clean_username(self):
        username = self.cleaned_data['username']
        exist = models.UserInfo.objects.filter(username=username).exists()
        if exist:
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exist = models.UserInfo.objects.filter(email=email).exists()
        if exist:
            raise ValidationError('邮箱已存在')
        return email
    def clean_password(self):
        password = self.cleaned_data['password']
        #加密&返回
        return encrypt.md5(password)

    def clean_confirm_password(self):   #优先级顺序
        password = self.cleaned_data['password']
        confirm_password = encrypt.md5(self.cleaned_data['confirm_password'])
        if password != confirm_password:
            raise ValidationError('两次密码不一致')
        return confirm_password

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exist:
            raise ValidationError('手机号已注册')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data['mobile_phone']

        conn = get_redis_connection('default')
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')
        return code



class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$','手机号格式错误'),])

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request


    def clean_mobile_phone(self):
        """手机号校验的钩子"""
        mobile_phone = self.cleaned_data.get('mobile_phone')

        #判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATES.get(tpl)
        if not template_id:
            # self.add_error('mobile_phone','短信模板错误')
            raise ValidationError('短信模板错误')

        #校验数据库中是否已有手机号
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exist:
            raise ValidationError('手机号已存在')

        #发短信&写redis
        code = random.randrange(1000,9999)

        #发送短信
        sms = send_sms_single(mobile_phone,template_id,[code,])
        if sms['result'] != 0:
            raise ValidationError('短信发送失败，{}'.format(sms['errmsg']))
        # 验证码写入redis（django-redis）
        conn = get_redis_connection('default')
        conn.set(mobile_phone, code,ex=60)

        return mobile_phone

