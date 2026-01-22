"""
用户账户相关功能：注册，短信，登录，注销
"""
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse

from web.forms.account import RegisterForm, SendSmsForm, LoginForm


def register(request):
    """注册"""
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'register.html',context={'form':form})
    form = RegisterForm(request.POST)
    if form.is_valid():
        # 验证通过，写入数据库（密码要是密文）
        # instance = form.save()      #刚刚写入的那条数据
        form.save()
        return JsonResponse({'status':True,'data':'/login/'})

    return JsonResponse({'status':False,'error':form.errors})


def send_sms(request):
    """发送短信"""
    # mobile_phone = request.POST.get('mobile_phone')
    # tpl = request.POST.get('tpl')

    form = SendSmsForm(request,data=request.GET)
    #只是校验手机号：不能为空、格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False,'error': form.errors})


def login_sms(request):
    """短信登录"""
    if request.method == "GET":
        form = LoginForm()
        return render(request,'login_sms.html',{'form':form})
    form = LoginForm(request.POST)
    if form.is_valid():
        #输入正确，登录成功
        user_object = form.cleaned_data['mobile_phone']     #这样可以直接获取用户对象，少做一次查询
        #models.UserInfo.objects.filter(mobile_phone=form.cleaned_data['mobile_phone']).first()，相当于少做了一次这个数据库查询

        #用户信息放入session中
        request.session['user_id'] = user_object.id
        request.session['user_name'] = user_object.username

        return JsonResponse({'status': True,'data':'/index/'})
    return JsonResponse({'status': False,'error': form.errors})