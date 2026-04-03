from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

from web.forms.issues import IssuesModelForm,IssuesReplyModelForm
from utils.pagination import Pagination
from web import models
import json

class CheckFilter(object):
    def __init__(self,name,data_list,request):
        self.name = name
        self.data_list = data_list
        self.request = request
    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            ck = ''
            #如果当前用户请求的URL中status和当前循环key相等ck = 'checked'
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            #为自己生成URL
            #在当前URL的基础上去增加一项
            # status=1&age=19
            query_dict = self.request.GET.copy()
            query_dict.__mutable = True
            query_dict.setlist(self.name, value_list)    # {'status':[1,2,3],'age':19}
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)    #status=1&status=2&status=3&age=19
            else:
                url = self.request.path_info

            html = "<a class='cell' href='{url}'><input type='checkbox' {ck} /><label>{text}</label></a>".format(url=url,ck=ck,text=text)
            yield mark_safe(html)


def issues(request, project_id):
    if request.method == 'GET':
        # 根据URL做筛选，筛选条件（根据用户通过GET传来的参数实现）
        # ?status =1 & status=2 & issues_type=1
        allow_filter_name = ['issues_type','status','priority']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)   #[1,2]
            if not value_list:
                continue
            condition['{}__in'.format(name)] = value_list
            """
            condition={
                'status__in':[1,2],     #等价于SQL语句中的：WHERE status IN (1, 2)
                'priority__in':[1,],
                }
            """

        queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
        page_obj = Pagination(request, queryset)

        form = IssuesModelForm(request)
        context = {
            'form' : form,
            'issues_object_list': page_obj.page_queryset,  # 分完页的数据
            'page_string': page_obj.html(),  # 页码
            'status_filter':CheckFilter('status',models.Issues.status_choices,request),
            'priority_filter': CheckFilter('priority', models.Issues.priority_choices, request),
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


@csrf_exempt
def issues_change(request, project_id,issues_id):
    issues_object = models.Issues.objects.filter(id=issues_id,project_id=project_id).first()

    #老版本用：post_dict = json.loads(request.body.decode('utf-8'))
    post_dict = json.loads(request.body)
    """
    {'name': 'issues_type', 'value': '4'}
    {'name': 'subject', 'value': '新的一个问题21我请问企鹅'}
    """
    name = post_dict.get('name')
    value = post_dict.get('value')

    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(content):
        """生成返回给前端的操作记录"""
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=content,
            creator=request.tracer.user,
        )
        new_reply = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'create_datetime': new_object.create_datetime.strftime('%Y-%m-%d %H:%M'),
            'parent_id': new_object.reply_id,
        }

        return new_reply


    #1.数据库字段更新  2.生成操作记录
    #1.1 文本
    if name in ['subject','desc','start_date','end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status':False,'error':'您选择的值不能为空'})
            setattr(issues_object, name, None)
            issues_object.save()

            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            setattr(issues_object, name, value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name,value)

        return JsonResponse({'status': True,'data': create_reply_record(change_record)})
    #1.2 fk字段(assign指派的话要判断是否创建者或参与者)
    if name in ['issues_type', 'module', 'parent', 'assign']:
        #用户选择为空
        if not value:
            #不允许为空
            if not field_object.null:
                return JsonResponse({'status':False,'error':'您选择的值不能为空'})
            #允许为空
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        #用户输入不为空
        else:
            if name == 'assign':
                #是否是项目创建者
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status':False,'error':'您选择的值不存在'})
            else:
                #条件判断：用户输入的值，是自己的值。
                instance = field_object.remote_field.model.objects.filter(id=value,project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status':False,'error':'您选择的值不存在'})

            setattr(issues_object, name, instance)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))  # value根据文本获取到内容

        return JsonResponse({'status': True,'data': create_reply_record(change_record)})

    #1.3 choice字段
    if name in ['priority', 'status', 'model']:
        selected_text = None
        for key,text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': '您选择的值不存在'})
        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}更新为{}".format(field_object.verbose_name,selected_text)
        return JsonResponse({'status': True,'data': create_reply_record(change_record)})
    #1.4 m2m字段
    if name == 'attention':
        # {'name':'attention','value':[1,2,3]}
        if not isinstance(value,list):
            return JsonResponse({'status': False, 'error': '数据格式错误'})
        if not value:
            issues_object.attention.set([])
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # values = ['1','2','3',4]  ->   id是否是项目成员（参与者，创建者）
            #获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id):request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username

            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': '数据错误'})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name,','.join(username_list))
        return JsonResponse({'status': True,'data': create_reply_record(change_record)})

    return JsonResponse({'status':False,'error':'滚'})
