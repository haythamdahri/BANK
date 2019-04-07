from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from. import views

app_name = 'crm'

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', views.Logout.as_view(), name="logout"),
    path('transactions/', views.Transactions.as_view(), name="transactions"),
    path('transactions/add', views.AddTransaction.as_view(), name="add_transaction"),
    path('withdrawals/', views.Withdrawals.as_view(), name="withdrawals"),
    path('deposits/', views.Deposits.as_view(), name="payments"),
]
