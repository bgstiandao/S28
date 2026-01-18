from django.contrib import admin
from django.urls import path,include
from app01 import views

app_name = 'app01'  # 主urls中用了namespace,建议这里加上app的名字

urlpatterns = [
    path('send/sms/', views.send_sms_single),
    path('register/', views.register,name='register'),  #"app01:register"

]