from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from. import views

app_name = 'crm'

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    #------------------- Login/Logout -------------------
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', views.Logout.as_view(), name="logout"),
    #------------------- Customer Features -------------------
    path('transactions/', views.Transactions.as_view(), name="transactions"),
    path('transactions/add/', views.AddTransaction.as_view(), name="add_transaction"),
    path('withdrawals/', views.Withdrawals.as_view(), name="withdrawals"),
    path('withdrawals/add/', views.AddWithdrawal.as_view(), name="add_withdrawal"),
    path('deposits/', views.Deposits.as_view(), name="deposits"),
    #------------------- Employee Features -------------------
    path('clients/', views.Clients.as_view(), name="clients"),
    path('clients/add', views.AddClient.as_view(), name="add_client"),
    #------------------- Account Features -------------------
    path('password-reset/', views.ResetPassword.as_view(), name="password_reset"),
    path('account-settings/', views.AccountSettings.as_view(), name="account_settings"),
    path('accounts/', views.Accounts.as_view(), name="accounts"),
]
