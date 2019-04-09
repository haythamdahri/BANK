import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Avg
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic.base import View
from CRM.forms import LoginForm, TransactionForm, SearchForm, WithdrawalForm
from CRM.models import Transaction, Client, Employee, Account, Withdrawal, Deposit, generateTransactionId
from datetime import datetime, timedelta

# -------------------------- Acceuil --------------------------
from CRM.tasks import generate_withrawals, generate_deposits

def getWeatherData(city):
    defaultçcity = 'Casablanca'
    api_key = settings.API_KEY
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}&lang=fr'
    response = requests.get(url.format(city, api_key)).json()
    if response['cod'] is None or response['cod'] == '404':
        response = requests.get(url.format(defaultçcity, api_key)).json()
    return response

class Home(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        city = request.user.person.city
        #------------- Weather Data -------------
        r = getWeatherData(city)
        city_weather = {
            'city': r['name'],
            'country': r['sys']['country'],
            'humidity': r['main']['humidity'],
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'sunrise': (timedelta(hours=1)+datetime.utcfromtimestamp(int(r['sys']['sunrise']))).strftime('%H:%M:%S'),
            'sunset': (timedelta(hours=1)+datetime.utcfromtimestamp(int(r['sys']['sunset']))).strftime('%H:%M:%S'),
            'today': datetime.now()
        }

        context = dict()
        client = Client()
        try:
            client = Client.objects.get(person_id=request.user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            transactions = Transaction.objects.filter(
                sender_account__in=Account.objects.filter(client_id=client.id))
            context['transactions_amount'] = round(transactions.aggregate(Avg('amount'))['amount__avg'], 2)
            context['transactions_count'] = transactions.count()

            withdrawals = Withdrawal.objects.filter(
                account__in=Account.objects.filter(client_id=client.id))
            context['withdrawals_amount'] = round(withdrawals.aggregate(Avg('amount'))['amount__avg'], 2)
            context['withdrawals_count'] = withdrawals.count()

            deposits = Deposit.objects.filter(
                account__in=Account.objects.filter(client_id=client.id))
            context['deposits_amount'] = round(deposits.aggregate(Avg('amount'))['amount__avg'], 2)
            context['deposits_count'] = deposits.count()

        context['city_weather'] = city_weather
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
            search_form = SearchForm(request.GET or None)
            if search_form.is_valid():
                transactions = Transaction.objects.filter(
                    Q(sender_account__in=accounts) | Q(receiver_account__in=accounts),
                    number=search_form.cleaned_data['search']).order_by('-date')
            else:
                transactions = Transaction.objects.filter(
                    Q(sender_account__in=accounts) | Q(receiver_account__in=accounts)).order_by('-date')

            # ------------- Get requested page -------------
            page = request.GET.get('page', 1)
            paginator = Paginator(transactions, 5)
            try:
                transactions = paginator.page(page)
            except PageNotAnInteger:
                transactions = paginator.page(1)
            except EmptyPage:
                transactions = paginator.page(paginator.num_pages)

            context['search_form'] = search_form
            context['transactions'] = transactions
            return render(request, 'CRM/transactions.html', context)
        return redirect('crm:home')


# -------------------------- Transactions --------------------------
class Withdrawals(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        # generate_withrawals(120)
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            accounts = Account.objects.filter(client_id=client.id)
            search_form = SearchForm(request.GET or None)
            if search_form.is_valid():
                withdrawals = Withdrawal.objects.filter(account__in=accounts,
                                                        number=search_form.cleaned_data['search']).order_by('-date')
            else:
                withdrawals = Withdrawal.objects.filter(account__in=accounts).order_by('-date')

            # ------------- Get requested page -------------
            page = request.GET.get('page', 1)
            paginator = Paginator(withdrawals, 50)
            try:
                withdrawals = paginator.page(page)
            except PageNotAnInteger:
                withdrawals = paginator.page(1)
            except EmptyPage:
                withdrawals = paginator.page(paginator.num_pages)

            context['search_form'] = search_form
            context['withdrawals'] = withdrawals
            return render(request, 'CRM/withdrawals.html', context)
        return redirect('crm:home')


# -------------------------- Transactions --------------------------
class Deposits(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        # generate_deposits(150)
        user = request.user
        client = Client()
        try:
            client = Client.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            context = dict()
            accounts = Account.objects.filter(client_id=client.id)
            search_form = SearchForm(request.GET or None)
            if search_form.is_valid():
                deposits = Deposit.objects.filter(account__in=accounts,
                                                  number=search_form.cleaned_data['search']).order_by('-date')
            else:
                deposits = Deposit.objects.filter(account__in=accounts).order_by('-date')

            # ------------- Get requested page -------------
            page = request.GET.get('page', 1)
            paginator = Paginator(deposits, 50)
            try:
                deposits = paginator.page(page)
            except PageNotAnInteger:
                deposits = paginator.page(1)
            except EmptyPage:
                deposits = paginator.page(paginator.num_pages)

            context['search_form'] = search_form
            context['deposits'] = deposits
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


# -------------------------- Add Transaction --------------------------
class AddWithdrawal(LoginRequiredMixin, View):
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
            context['withdrawal_form'] = WithdrawalForm()
            return render(request, 'CRM/add-withdarawal.html', context)
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
            form = WithdrawalForm(request.POST or None)
            if form.is_valid():
                password = form.cleaned_data.get('password')
                if check_password(password, user.password):
                    form.save()
                    messages.success(request, "Retrait efféctué avec succée")
                    return redirect('crm:withdrawals')
                form.add_error('password', 'Mot de passe invalide')
            context['withdrawal_form'] = form
            return render(request, 'CRM/add-withdarawal.html', context)
        return redirect('crm:home')
