"""
用户账户相关功能：注册，短信，登录，注销
"""
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse

from web.forms.account import RegisterForm,SendSmsForm

def register(request):
    """注册"""
    form = RegisterForm()
    return render(request, 'register.html',context={'form':form})

def send_sms(request):
    """发送短信"""
    mobile_phone = request.POST.get('mobile_phone')
    tpl = request.POST.get('tpl')

    form = SendSmsForm(request,data=request.GET)
    #只是校验手机号：不能为空、格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False,'error': form.errors})