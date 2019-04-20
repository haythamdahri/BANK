import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Avg, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic.base import View
from django_countries.templatetags.countries import get_countries

from CRM.forms import LoginForm, TransactionForm, SearchForm, WithdrawalForm, ClientSearchForm, ClientForm, \
    UserForm, PersonForm, ClientForm, ResetPasswordForm, AccountSettingsForm
from CRM.models import Transaction, Client, Employee, Account, Withdrawal, Deposit, generateTransactionId, Person
from datetime import datetime, timedelta

# -------------------------- Acceuil --------------------------
from CRM.tasks import generate_withrawals, generate_deposits


def getWeatherData(city):
    default_city = 'Casablanca'
    api_key = settings.API_KEY
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}&lang=fr'
    response = requests.get(url.format(city, api_key)).json()
    if response['cod'] is None or response['cod'] == '404':
        response = requests.get(url.format(default_city, api_key)).json()
    return response


class Home(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        city = request.user.person.city
        # ------------- Weather Data -------------
        try:
            r = getWeatherData(city)
            city_weather = {
                'city': r['name'],
                'country': r['sys']['country'],
                'humidity': r['main']['humidity'],
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
                'sunrise': (timedelta(hours=1) + datetime.utcfromtimestamp(int(r['sys']['sunrise']))).strftime(
                    '%H:%M:%S'),
                'sunset': (timedelta(hours=1) + datetime.utcfromtimestamp(int(r['sys']['sunset']))).strftime(
                    '%H:%M:%S'),
                'today': datetime.now()
            }
        except Exception as ex:
            pass

        context = dict()
        client = Client()
        try:
            client = Client.objects.get(person_id=request.user.person.id)
        except Client.DoesNotExist as ex:
            client = None
        if client is not None:
            transactions = Transaction.objects.filter(
                sender_account__in=Account.objects.filter(client_id=client.id))
            transactions_amount = transactions.aggregate(Avg('amount'))['amount__avg']
            context['transactions_amount'] = round(transactions_amount if transactions_amount is not None else 0, 2)
            context['transactions_count'] = transactions.count()

            withdrawals = Withdrawal.objects.filter(
                account__in=Account.objects.filter(client_id=client.id))
            withdrawals_amount = withdrawals.aggregate(Avg('amount'))['amount__avg']
            context['withdrawals_amount'] = round(withdrawals_amount if withdrawals_amount is not None else 0, 2)
            context['withdrawals_count'] = withdrawals.count()

            deposits = Deposit.objects.filter(
                account__in=Account.objects.filter(client_id=client.id))
            deposits_amount = withdrawals.aggregate(Avg('amount'))['amount__avg']
            context['deposits_amount'] = round(deposits_amount if deposits_amount is not None else 0, 2)
            context['deposits_count'] = deposits.count()
        else:
            total_balance = nb_clients = nb_transactions = nb_deposits = nb_withdrawals = transactions_balance = deposits_balance = withdrawals_balance = 0
            employee = Employee.objects.filter(person_id=request.user.person.id)[0]
            for account in Account.objects.filter(client__in=Client.objects.filter(creator=employee)):
                total_balance += account.balance

                temp_transactions = Transaction.objects.filter(Q(sender_account=account) | Q(receiver_account=account))
                nb_transactions += temp_transactions.count()
                t_b = temp_transactions.aggregate(Sum('amount'))['amount__sum']
                transactions_balance += t_b if t_b is not None else 0

                temp_deposits = Deposit.objects.filter(account=account)
                nb_deposits += temp_deposits.count()
                d_b = temp_deposits.aggregate(Sum('amount'))['amount__sum']
                deposits_balance += d_b if temp_deposits.aggregate(Sum('amount'))['amount__sum'] is not None else 0

                temp_withdrawals = Withdrawal.objects.filter(account=account)
                nb_withdrawals += temp_withdrawals.count()
                w_b = temp_withdrawals.aggregate(Sum('amount'))['amount__sum']
                withdrawals_balance += w_b if w_b is not None else 0

            context['nb_clients'] = Client.objects.filter(creator=employee).count()
            context['total_balance'] = total_balance
            context['transactions_balance'] = transactions_balance
            context['deposits_balance'] = deposits_balance
            context['withdrawals_balance'] = withdrawals_balance
            context['nb_transactions'] = nb_transactions
            context['nb_deposits'] = nb_deposits
            context['nb_withdrawals'] = nb_withdrawals

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
            try:
                if form.is_valid():
                    password = form.cleaned_data.get('password')
                    if check_password(password, user.password):
                        sender_account = form.cleaned_data.get('sender_account')
                        reciever_account = form.cleaned_data.get('receiver_account')
                        if sender_account.expiration_date < datetime.now().date():
                            messages.error(request, f'Votre compte numero {sender_account.credit_card} est expiré!')
                            form.add_error('sender_account', 'Compte expiré')
                        elif reciever_account.expiration_date < datetime.now().date():
                            messages.error(request,
                                           f'Le compte récepteur numero {reciever_account.credit_card} est expiré!')
                            form.add_error('receiver_account', 'Compte expiré')
                        else:
                            form.save()
                            messages.success(request, "Transaction efféctuée avec succée")
                            return redirect('crm:transactions')
                    else:
                        form.add_error('password', 'Mot de passe invalide')
                context['transaction_form'] = form
                return render(request, 'CRM/add-transaction.html', context)
            except Exception as ex:
                print(ex)
                messages.error(request, "Une erreur est survenue, veuillez ressayer")
                return redirect('crm:add_transaction')
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


# -------------------------- Clients(Only for employees) --------------------------
class Clients(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        employee = Employee()
        try:
            employee = Employee.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            employee = None
        if employee is not None:
            context = dict()
            client_search_form = ClientSearchForm(request.GET or None)
            if client_search_form.is_valid():
                search = client_search_form.cleaned_data['search']
                try:
                    clients = Client.objects.filter(
                        Q(pk=int(search)) | Q(person__cin=client_search_form.cleaned_data['search']), creator=employee)
                except ValueError:
                    clients = Client.objects.filter(person__cin=client_search_form.cleaned_data['search'],
                                                    creator=employee)
            else:
                clients = Client.objects.filter(creator=employee).order_by('-id')

            for client in clients:
                client.accounts_count = Account.objects.filter(client=client).count()
            # ------------- Get requested page -------------
            page = request.GET.get('page', 1)
            paginator = Paginator(clients, 10)
            try:
                clients = paginator.page(page)
            except PageNotAnInteger:
                clients = paginator.page(1)
            except EmptyPage:
                clients = paginator.page(paginator.num_pages)

            context['clients'] = clients
            context['client_search_form'] = client_search_form
            return render(request, 'CRM/clients.html', context)
        return redirect('crm:home')


# -------------------------- Add client(Only for employees) --------------------------
class AddClient(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        employee = Employee()
        try:
            employee = Employee.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            employee = None
        if employee is not None:
            context = dict()
            context['client_form'] = ClientForm()
            return render(request, 'CRM/add-client.html', context)
        return redirect('crm:home')

    def post(self, request, *args, **kwargs):
        user = request.user
        employee = Employee()
        try:
            employee = Employee.objects.get(person_id=user.person.id)
        except Client.DoesNotExist as ex:
            employee = None
        if employee is not None:
            context = dict()
            client_form = ClientForm(request.POST or None, request.FILES or None)
            if client_form.is_valid():
                user_form = UserForm(request.POST or None)
                person_form = PersonForm(request.POST or None, request.FILES or None, initial={})
                if user_form.is_valid() and person_form.is_valid():
                    user = user_form.save()
                    person = person_form.save(commit=False)
                    person.user = user
                    person.save()
                    Client.objects.create(person=person, creator=employee)
                    messages.success(request, "Compte client à été crée avec succé")
                    return redirect('crm:clients')
            context['client_form'] = client_form
            return render(request, 'CRM/add-client.html', context)
        return redirect('crm:home')


# -------------------------- Reset Account Password --------------------------
class ResetPassword(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        context = dict()
        form = ResetPasswordForm()
        context['reset_password_form'] = form
        return render(request, 'CRM/reset-password.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        context = dict()
        form = ResetPasswordForm(request.POST or None)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            if check_password(old_password, user.password):
                try:
                    temp_user = User.objects.get(id=user.id)
                    temp_user.set_password(form.cleaned_data.get('new_password'))
                    temp_user.save()
                    messages.success(request, "Mot de passe à été réinitialisé avec succé!")
                    messages.info(request, "Veuillez se connecter avec votre nouveau mot de passe!")
                except:
                    pass
                return redirect('crm:reset_password')
            form.add_error('old_password', 'Ancien mot de passe invalide')
        context['reset_password_form'] = form
        return render(request, 'CRM/reset-password.html', context)


# -------------------------- Account Settings --------------------------
class AccountSettings(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        context = dict()
        try:
            person = Person.objects.get(user=user)
            context = dict()
            initial = {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'cin': person.cin,
                'birth_date': person.birth_date,
                'city': person.city,
                'state': person.state,
                'nationality': person.nationality,
                'image': person.image.url
            }
            context['account_form'] = AccountSettingsForm(initial=initial)
        except:
            return redirect('crm:home')
        return render(request, 'CRM/account-settings.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        context = dict()
        try:
            person = Person.objects.get(user_id=user.id)
            account_form = AccountSettingsForm(request.POST or None, request.FILES or None)
            if account_form.is_valid():
                if User.objects.filter(~Q(id=user.id), username__iexact=account_form.cleaned_data.get(
                        'username')) and account_form.cleaned_data.get('username') != user.username:
                    account_form.add_error('username', "Nom d'utilisateur déja utilisé!")
                    messages.error(request, "Données invalides, veuillez corriger les erreurs puis ressayer!")
                elif User.objects.filter(~Q(id=user.id), email__iexact=account_form.cleaned_data.get(
                        'email')).exists() and account_form.cleaned_data.get('email') != user.email:
                    account_form.add_error('email', 'L\'adresse Email est déja utilisée')
                    messages.error(request, "Données invalides, veuillez corriger les erreurs puis ressayer!")
                elif Person.objects.filter(~Q(user_id=user.id), cin__iexact=account_form.cleaned_data.get(
                        'cin')).exists() and account_form.cleaned_data.get('cin') != person.cin:
                    account_form.add_error('cin', 'Cin est déja utilisée')
                    messages.error(request, "Données invalides, veuillez corriger les erreurs puis ressayer!")
                else:
                    user = User.objects.get(id=user.id)
                    user.username = account_form.cleaned_data.get('username')
                    user.first_name = account_form.cleaned_data.get('first_name')
                    user.last_name = account_form.cleaned_data.get('last_name')
                    user.email = account_form.cleaned_data.get('email')
                    person.image = account_form.cleaned_data.get('image')
                    person.cin = account_form.cleaned_data.get('cin')
                    person.birth_date = account_form.cleaned_data.get('birth_date')
                    person.city = account_form.cleaned_data.get('city')
                    person.state = account_form.cleaned_data.get('state')
                    person.birth_date = account_form.cleaned_data.get('birth_date')
                    person.nationality = account_form.cleaned_data.get('nationality')
                    user.save()
                    person.save()
                    messages.success(request, "Les informations de votre compte sont changées avec succé")
                    return redirect('crm:account_settings')
            context['account_form'] = account_form
            return render(request, 'CRM/account-settings.html', context)
        except Exception as ex:
            print(ex)
            return redirect('crm:account_settings')
