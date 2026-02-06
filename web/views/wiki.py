from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from web.forms.wiki import WikiModelForm
from web import models

def wiki(request, project_id):
    """wiki首页"""
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    #文章详细
    wiki_object = models.Wiki.objects.filter(id=wiki_id,project_id=project_id).first()

    return render(request, 'wiki.html',{'wiki_object':wiki_object})

def wiki_add(request, project_id):
    """wiki添加"""
    if request.method == "GET":
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html',{'form': form})

    form = WikiModelForm(request,request.POST)
    if form.is_valid():
        #判断用户是否已选择了父文章
        if form.instance.parent:
            form.instance.depth += form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_add.html',{'form': form})


def wiki_catalog(request, project_id):
    """wiki目录"""

    # 获取当前项目所有的目录:data = QuerySet类型
    # data = models.Wiki.objects.filter(project=request.tracer.project).values_list('id','title','parent_id')

    # 建议用values，这样获取的是字典格式的
    # data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id')
    data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id').order_by('depth','id')

    #json.dumps(QuerySet)这样序列化不了，所以建议转换成列表类型
    return JsonResponse({'status':True,'data':list(data)})

#可以不用
# def wiki_detail(request, project_id):
#     """
#     查看文章详细页面
#         /detail?wiki_id=1
#         /detail?wiki_id=2
#         /detail?wiki_id=3
#     :param request:
#     :param project_id:
#     :return:
#     """
#     return HttpResponse('查看文章详情')