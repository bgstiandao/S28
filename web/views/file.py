from django.http import JsonResponse
from django.shortcuts import render
from django.forms import model_to_dict

from web.forms.file import FileModelForm
from web import models


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
    else:
        pass    #删除文件夹（找到文件夹下所有的文件>数据库文件删除，cos文件删除，项目已使用空间容量还回去)

    delete_object.delete()
    return JsonResponse({'status':True})