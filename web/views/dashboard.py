import datetime
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from web import models
def dashboard(request, project_id):
    """概览"""

    #问题的数据处理
    # status_dict = collections.OrderedDict()  #python3.6之前字典是无序的，防止页面上字段顺序一直变，建议加上这个
    status_dict = {}
    for key,text in models.Issues.status_choices:
        status_dict[key] = {'text': text,'count':0}

    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    #项目成员
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')

    #最近的10个问题
    top_ten = models.Issues.objects.filter(project_id=project_id,assign__isnull=False).order_by('-id')[0:10]   # assigin__isnull=False指派不为空

    context = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten_object': top_ten,
    }

    return render(request,'dashboard.html',context)

def issues_chart(request, project_id):
    """在概览页面生成highchart所需的数据"""

    """
    date_dict = {
        '2026-04-09': [1775664000000.0, 0],
         '2026-04-08': [1775577600000.0, 0],
         '2026-04-07': [1775491200000.0, 0],
     }
    """
    today = datetime.datetime.now().date()
    date_dict = {}
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple()) * 1000, 0]

    #去数据库中查询最后30天的所有数据 & 根据日期每天都分组
    #extra用于定制的高级SQL语句
    #select xxx,strftime("%Y-%m-%d", create_datetime) as ctime from xxxx
    # web_issues是django生成的真正的表名
    # annotate()给数据库查询结果动态添加字段
    #{'ctime':'strftime("%%Y-%%m-%%d", web_issues.create_datetime)'}是当前sqlite数据库，在mysql中应该是{'ctime':'DATE_FORMAT(web_issues.create_datetime,"%%Y-%%m-%%d")'}
    result = models.Issues.objects.filter(project_id=project_id,create_datetime__gte=today-datetime.timedelta(days=30)).extra(
        select={'ctime':'strftime("%%Y-%%m-%%d", web_issues.create_datetime)'}).values('ctime').annotate(ct=Count('id'))

    # print(result)
    # < QuerySet[{'ctime': '2026-03-25', 'ct': 2}] >

    for item in result:
        date_dict[item['ctime']][1] = item['ct']



    return JsonResponse({'status':True,'data': list(date_dict.values())})