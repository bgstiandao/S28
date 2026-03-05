import json

from django.http import JsonResponse
from django.shortcuts import render
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt

from web.forms.file import FileModelForm
from web import models

from utils.tecent.cos import delete_file,delete_file_list,credential

# http://127.0.0.1:8000/manage/2/file/
# http://127.0.0.1:8000/manage/2/file/?folder=9
def file(request,project_id):
    """文件列表 & 添加文件夹"""

    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.tracer.project).first()
    #GET 查看页面
    if request.method == 'GET':

        breadcrumb_list = []
        parent = parent_object
        while parent:
            #breadcrumb_list.insert(0, {'id':parent.id, 'name':parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent,['id','name']))
            parent = parent.parent

        #当前目录下所有文件 & 文件夹获取到即可
        queryset = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            #进入某目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            #根目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form = FileModelForm(request,parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrumb_list': breadcrumb_list,
        }
        return render(request,'file.html',context)


    #POST 添加文件夹 & 文件夹的修改
    fid = request.POST.get('fid','')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2,project=request.tracer.project).first()

    if edit_object:
        form = FileModelForm(request, parent_object, request.POST,instance=edit_object)
    else:
        form = FileModelForm(request,parent_object,request.POST)

    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status':False,'error':form.errors})


# http://127.0.0.1:8000/manage/2/file/delete/?fid=1
def file_delete(request,project_id):
    """删除文件"""
    fid = request.GET.get('fid')

    #删除数据库中的 文件&文件夹 （级联删除）
    delete_object = models.FileRepository.objects.filter(id=fid,project=request.tracer.project).first()
    if delete_object.file_type == 1:
        pass    #删除文件（数据库文件删除，cos文件删除，项目已使用空间容量还回去）

        #删除文件，将容量还给当前项目的已使用空间
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()

        #去cos中删除文件
        delete_file(request.tracer.project.bucket, request.tracer.project.region,delete_object.key)
        #在数据库中删除当前文件
        delete_object.delete()

        return JsonResponse({'status': True})

    #删除文件夹（找到文件夹下所有的文件>数据库文件删除，cos文件删除，项目已使用空间容量还回去)
    # delete_object
    # 找他下面的 文件和文件夹
    # models.FileRepository.objects.filter(parent=delete_object)    #文件删除，文件夹，继续向里查

    total_size = 0
    # 批量删除的key列表
    key_list = []
    folder_list = [delete_object,]

    for folder in folder_list:
        child_list = models.FileRepository.objects.filter(project=request.tracer.project,parent=folder).order_by('-file_type')
        for child in child_list:
            if child.file_type == 2:
                folder_list.append(child)
            else:
                # 文件大小汇总
                total_size += child.file_size

                #删除文件
                # delete_file(request.tracer.project.bucket, request.tracer.project.region,child.key)

                key_list.append({'Key':child.key})
    #cos 批量删除文件
    if key_list:
        delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)

    #归还容量
    if total_size:
        request.tracer.project.use_space -= total_size
        request.tracer.project.save()

    #删除数据库中的文件
    delete_object.delete()
    return JsonResponse({'status': True})

@csrf_exempt
def cos_credential(request,project_id):
    """获取cos上传临时凭证"""
    #单文件的限制大小 M
    per_file_limit = request.tracer.price_policy.per_file_size*1024*1024
    total_file_limit = request.tracer.price_policy.project_space*1024*1024*1024
    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    # 做容量限制：单文件 & 总容量
    for item in file_list:
        #文件的字节大小 item["size"] = B
        #单文件限制的大小 M
        #超出限制
        print(item['size'])
        if item['size'] > per_file_limit:
            msg = '单文件超出限制（最大{}M),文件：{}，请升级套餐'.format(request.tracer.price_policy.per_file_size,item['name'])
            return JsonResponse({'status': False,'error':msg})
        total_size += item['size']

    #总容量进行限制
    if request.tracer.project.use_space + total_size > total_file_limit:
        return JsonResponse({'status': True,'error':"容量超过限制，请升级套餐"})


    data_dict = credential(request.tracer.project.bucket,request.tracer.project.region)
    return JsonResponse({'status':True,'data':data_dict})
