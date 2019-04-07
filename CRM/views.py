from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic.base import View
from CRM.forms import LoginForm, TransactionForm

# -------------------------- Acceuil --------------------------
from CRM.models import Transaction, Client, Employee, Account, Withdrawal, Deposit, generateTransactionId


class Home(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        context = dict()
        client = Client()
        try:
            client = Client.objects.get(person_id=request.user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        return render(request, 'CRM/index.html', context)

    def post(self, request, *args, **kwargs):
        return redirect('crm:home')


# -------------------------- Connexion --------------------------
class Login(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('crm:home')
        context = dict()
        context['login_form'] = LoginForm()
        return render(request, 'CRM/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next', reverse('crm:home'))
                return redirect(redirect_url)
            else:
                messages.error(request, 'Email ou mot de passe invalide!')
                return redirect('crm:login')

        messages.error(request, 'Veuillez verifier les champs puis ressayer')
        return redirect('crm:login')


# -------------------------- Deconnexion --------------------------
class Logout(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return redirect('crm:home')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, "Vous êtes déconnecté!")
        return redirect('crm:login')


# -------------------------- Transactions --------------------------
class Transactions(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            accounts = Account.objects.filter(client_id=client.id)
            context['transactions'] = Transaction.objects.filter(
                Q(sender_account__in=accounts) | Q(receiver_account__in=accounts)).order_by('-date')
            return render(request, 'CRM/transactions.html', context)
        return redirect('crm:home')


# -------------------------- Transactions --------------------------
class Withdrawals(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            accounts = Account.objects.filter(client_id=client.id)
            client = request.user.person
            context['withdrawals'] = Withdrawal.objects.filter(account__in=accounts)
            return render(request, 'CRM/withdrawals.html', context)
        return redirect('crm:home')


# -------------------------- Transactions --------------------------
class Deposits(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            accounts = Account.objects.filter(client_id=client.id)
            print(accounts)
            context['deposits'] = Deposit.objects.filter(account__in=accounts)
            return render(request, 'CRM/deposits.html', context)
        return redirect('crm:home')


# -------------------------- Add Transaction --------------------------
class AddTransaction(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            context['transaction_form'] = TransactionForm()
            return render(request, 'CRM/add-transaction.html', context)
        return redirect('crm:home')

    def post(self, request, *args, **kwargs):
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            form = TransactionForm(request.POST or None)
            if form.is_valid():
                password = form.cleaned_data.get('password')
                if check_password(password, user.password):
                    form.save()
                    messages.success(request, "Transaction efféctuée avec succée")
                    return redirect('crm:transactions')
                form.add_error('password', 'Mot de passe invalide')
            context['transaction_form'] = form
            return render(request, 'CRM/add-transaction.html', context)
        return redirect('crm:home')
