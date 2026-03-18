""""项目后台管理"""
from django.shortcuts import render

def dashboard(request, project_id):

    return render(request,'dashboard.html')


def statistics(request, project_id):

    return render(request,'statistics.html')

def file(request, project_id):
    return render(request, 'file.html')




