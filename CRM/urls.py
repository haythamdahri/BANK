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
    path('deposits/add/', views.AddDeposit.as_view(), name="add_deposit"),
    #------------------- Employee Features -------------------
    path('clients/', views.Clients.as_view(), name="clients"),
    path('clients/add', views.AddClient.as_view(), name="add_client"),
    #------------------- Account Features -------------------
    path('password-reset/', views.ResetPassword.as_view(), name="password_reset"),
    path('account-settings/', views.AccountSettings.as_view(), name="account_settings"),
    path('accounts/', views.Accounts.as_view(), name="accounts"),
    path('clients-accounts/', views.ClientsAccounts.as_view(), name="clients_accounts"),
    path('delete-account/', views.DeleteAccount.as_view(), name="delete_account"),
    path('add-account/', views.AddAccount.as_view(), name="add_account"),
    path('edit-account/<int:id>/', views.EditAccount.as_view(), name="edit_account"),
]
