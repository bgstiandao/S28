
from django.urls import path,include
from web.views import account

urlpatterns = [
    path('register/', account.register, name='register'),   #'register'
    path('login/sms/', account.login_sms, name='login_sms'),
    path('send/sms/', account.send_sms, name='send_sms'),

]