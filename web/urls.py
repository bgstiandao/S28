
from django.urls import path,re_path,include
from web.views import account,home,project,manage,wiki

urlpatterns = [
    path('register/', account.register, name='register'),   #'register'
    path('login/sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('image/code', account.image_code, name='image_code'),
    path('send/sms/', account.send_sms, name='send_sms'),
    path('logout/', account.logout, name='logout'),
    path('index/', home.index, name='index'),


    #项目管理
    re_path(r'^project/list/$', project.project_list, name='project_list'),  #re_path用于正则表达式的url路径

    #/project/star/my/1
    #/project/star/join/1
    re_path(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    re_path(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    #项目管理
    re_path(r'^manage/(?P<project_id>\d+)/',include([
        re_path(r'^dashboard/$',manage.dashboard, name='dashboard'),
        re_path(r'^issues/$',manage.issues, name='issues'),
        re_path(r'^statistics/$',manage.statistics, name='statistics'),
        re_path(r'^file/$',manage.file, name='file'),
        re_path(r'^wiki/$',wiki.wiki, name='wiki'),
        re_path(r'^wiki/add/$',wiki.wiki_add, name='wiki_add'),
        re_path(r'^wiki/catalog/$',wiki.wiki_catalog, name='wiki_catalog'),

        # re_path(r'^wiki/detail/$', wiki.wiki_detail, name='wiki_detail'),不需要多写一个url，直接用wiki那个后面加参数

        re_path(r'^wiki/delete/(?P<wiki_id>\d+)/$',wiki.wiki_delete, name='wiki_delete'),

        re_path(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),

        re_path(r'^setting/$',manage.setting, name='setting'),

    ])),


]

"""
    re_path(r'^manage/(?P<project_id>\d+)/dashboard/$',project.project_dashboard, name='project_dashboard'),
    re_path(r'^manage/(?P<project_id>\d+)/issues/$',project.project_issues, name='project_issues'),
    re_path(r'^manage/(?P<project_id>\d+)/statistics/$',project.project_statistics, name='project_statistics'),
    re_path(r'^manage/(?P<project_id>\d+)/file/$',project.project_file, name='project_file'),
    re_path(r'^manage/(?P<project_id>\d+)/wiki/$',project.project_wiki, name='project_wiki'),
"""