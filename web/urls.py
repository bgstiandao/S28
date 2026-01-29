
from django.urls import path,include
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
    path(r'^project/list$', project.project_list, name='project_list'),

]