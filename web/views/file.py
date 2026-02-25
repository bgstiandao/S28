from django.http import JsonResponse
from django.shortcuts import render
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

    if request.method == 'GET':
        form = FileModelForm(request,parent_object)
        return render(request,'file.html',{'form':form})


    #添加文件夹
    form = FileModelForm(request,parent_object,request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status':False,'error':form.errors})
