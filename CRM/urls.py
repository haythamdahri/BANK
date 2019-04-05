from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from. import views

app_name = 'crm'

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('login/', views.Login.as_view(), name="login"),
    path('me/', views.Me.as_view(), name="me")
]
