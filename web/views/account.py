"""
用户账户相关功能：注册，短信，登录，注销
"""
import uuid
import datetime
from io import BytesIO

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q

from web.forms.account import RegisterForm, SendSmsForm, LoginSmsForm,LoginForm
from web import models
from utils.image_code import check_code

def register(request):
    """注册"""
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'register.html',context={'form':form})
    form = RegisterForm(request.POST)
    if form.is_valid():
        # 验证通过，写入数据库（密码要是密文）
        # instance = form.save()      #刚刚写入的那条数据
        #form.save()    #保存到数据库

        #用户表中新建一条数据（注册）
        instance = form.save()

        # 创建交易记录
        #方式一，（中间件中的获取当前用户的额度，需要创建免费版的交易记录）
        policy_object = models.PricePolicy.objects.filter(category=1,title='个人免费版').first()
        models.Transaction.objects.create(
            status = 2,
            order = str(uuid.uuid4()),   #随机字符串
            user = instance,
            price_policy=policy_object,
            count = 0,
            price = 0,
            start_datetime=datetime.datetime.now(),
        )

        #方式二（什么都不写）

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
        form = LoginSmsForm()
        return render(request,'login_sms.html',{'form':form})
    form = LoginSmsForm(request.POST)
    if form.is_valid():
        #输入正确，登录成功
        user_object = form.cleaned_data['mobile_phone']     #这样可以直接获取用户对象，少做一次查询
        #models.UserInfo.objects.filter(mobile_phone=form.cleaned_data['mobile_phone']).first()，相当于少做了一次这个数据库查询

        #用户信息放入session中
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60*60*24*12)     #设置过期时间2周



        return JsonResponse({'status': True,'data':'/index/'})
    return JsonResponse({'status': False,'error': form.errors})

def login(request):
    """用户名和密码登录"""
    if request.method == "GET":
        form = LoginForm(request)
        return render(request,'login.html',context={'form':form})
    form = LoginForm(request,request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        #user_object = models.UserInfo.objects.filter(username=username,password=password).first()
        #（手机 = username and pwd = pwd) or （邮箱 = username and pwd = pwd)

        user_object = models.UserInfo.objects.filter(Q(email=username)|Q(mobile_phone=username)).filter(
            password=password).first()

        if user_object:
            #登录成功为止1
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60*60*24)        #设置过期时间2周

            return redirect('index')
        form.add_error('username','用户名或密码错误')
    return render(request,'login.html',context={'form':form})

def image_code(request):
    """生成图片验证码"""


    image_obj,code = check_code()
    #把验证码存入session中
    request.session['image_code'] = code
    request.session.set_expiry(60)      #主动修改过期时间为60s

    #把图片放入内存
    stream = BytesIO()
    image_obj.save(stream, 'png')
    # stream.getvalue()   #把图片从内存中取出

    return HttpResponse(stream.getvalue())

def logout(request):
    """退出登录"""
    request.session.flush()
    return redirect('index')
