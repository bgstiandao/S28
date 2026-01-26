
from django.urls import path,include
from web.views import account,home

urlpatterns = [
    path('register/', account.register, name='register'),   #'register'
    path('login/sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('image/code', account.image_code, name='image_code'),
    path('send/sms/', account.send_sms, name='send_sms'),

    path('index/', home.index, name='index'),


]