from django.contrib.auth.models import User
from django.shortcuts import render


def project_list(request):
    """项目列表"""
    #这样写会比较麻烦，所以可以在中间件中再弄个类封装一下
    # request.tracer
    # request.price_policy

    print(request.tracer.user)
    print(request.tracer.price_policy)

    return render(request,'project_list.html')