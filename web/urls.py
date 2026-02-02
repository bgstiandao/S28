
from django.urls import path,re_path,include
from web.views import account,home,project

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

]