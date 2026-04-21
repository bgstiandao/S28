""""项目后台管理"""
import collections
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from web import models


def statistics(request, project_id):
    """统计页面"""
    return render(request, 'statistics.html')


def statistics_priority(request, project_id):
    """按照优先级生成饼图"""

    start = request.GET.get('start')
    end = request.GET.get('end')

    # 找到所有的问题，根据优先级分组，每个优先级的问题数量
    # 1.构造有序字典
    # data_dict = collections.OrderedDict()   #python3.6之前的字典是无序的，防止页面上顺序一直变，加上这个
    data_dict = {}
    for key, text in models.Issues.priority_choices:
        data_dict[key] = {'name': text, 'y': 0}

    # 2.去数据库查询所有分组得到的数量
    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end).values('priority').annotate(
        ct=Count('id'))  # 起到分组的效果，使用annotate(Count('id'))会默认产生一个id_count字段，然后ct表示该字段的重命名

    # 3.把分组得到的数据更新到data_dict中
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']

    """data_list = [
        {
            'name': 'Internet',
            'y': 11
        }, {
            'name': 'IF1t',
            'y': 10
        }, {
            'name': 'EDGE',
            'y': 4
        },
    ]"""
    return JsonResponse({'status': True, 'data': list(data_dict.values())})


def statistics_project_user(request, project_id):
    """项目成员每个人被分配的任务数量（问题类型的配比）"""
    start = request.GET.get('start')
    end = request.GET.get('end')

    """
    info = {
        1:{
            name:"吴佩琦",
            status:(
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
            )
        },
        2:{
            name:"汪洋",
            status:(
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
            )
        },
    }
    """
    #1.所有项目成员 及 未指派
    all_user_dict = {
        request.tracer.project.creator.id:{
            'name':request.tracer.project.creator.username,
            'status': {item[0]:0 for item in models.Issues.status_choices},
        },
        None:{
            'name':'未指派',
            'status': {item[0]: 0 for item in models.Issues.status_choices},
        }
    }
    user_list = models.ProjectUser.objects.filter(project_id=project_id)
    for item in user_list:
        all_user_dict[item.user_id] = {
            'name': item.user.username,
            'status': {item[0]: 0 for item in models.Issues.status_choices},
        }


    #2.去数据库获取相关的所有问题
    issues_list = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end)
    for item in issues_list:
        if not item.assign:
            all_user_dict[None]['status'][item.status] += 1
        else:
            all_user_dict[item.assign.id]['status'][item.status] += 1

    # 3.获取所有的成员
    categories = [data['name'] for data in all_user_dict.values()]

    # 4.构造字典
    """
    data_result_dict = {
        1:(name:新建.data:[]),
        2: (name:处理中.data:[]),
        3: (name:已解决.data:[]),
        4: (name:已忽略.data:[]),
    }
    """

    data_result_dict = {}
    for item in models.Issues.status_choices:
        data_result_dict[item[0]] = {'name':item[1],'data':[]}

    for key,text in models.Issues.status_choices:
        # key =1 ,text= '新建‘
        for row in all_user_dict.values():
            count = row['status'][key]
            data_result_dict[key]['data'].append(count)
    print(list(data_result_dict.values()))
    context = {
        'status': True,
        'data': {
            'categories': categories,
            'series': list(data_result_dict.values()),
        },

    }

    return JsonResponse(context)
