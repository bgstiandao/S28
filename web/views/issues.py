from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.forms.issues import IssuesModelForm,IssuesReplyModelForm
from utils.pagination import Pagination
from web import models

def issues(request, project_id):
    if request.method == 'GET':
        queryset = models.Issues.objects.filter(project_id=project_id)
        page_obj = Pagination(request, queryset)

        form = IssuesModelForm(request)
        context = {
            'form' : form,
            'issues_object_list': page_obj.page_queryset,  # 分完页的数据
            'page_string': page_obj.html(),  # 页码
        }


        return render(request,'issues.html',context)

    print(request.POST)
    form = IssuesModelForm(request,data=request.POST)
    if form.is_valid():
        #添加问题
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False,'error':form.errors})

def issues_detail(request, project_id,issues_id):
    """编辑问题"""
    issues_object = models.Issues.objects.filter(id=issues_id,project_id=project_id).first()
    form = IssuesModelForm(request,instance=issues_object)
    return render(request,'issues_detail.html',{'form':form,'issues_object':issues_object})

@csrf_exempt
def issues_record(request, project_id,issues_id):
    """初始化操作记录"""

    #最好再加一个判断，判断是否可以评论和是否可以操作这个问题

    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id,issues__project=request.tracer.project)

        # 将queryset转换成json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'create_datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M'),
                'parent_id': row.reply_id,
            }
            data_list.append(data)

        return JsonResponse({'status':True,'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'create_datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': instance.reply_id,
        }
        return JsonResponse({'status':True,'data': info})
    return JsonResponse({'status':False,'error':form.errors})
