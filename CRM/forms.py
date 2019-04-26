import datetime

from django import forms
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.templatetags.countries import get_countries
from django_countries.widgets import CountrySelectWidget

from CRM.models import Transaction, Account, Withdrawal, Deposit, Client, Person
import re


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={"placeholder": "Email...", "class": "form-control"}),
        required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe...", "class": "form-control"}),
        required=True)

    def clean_email(self):
        try:
            email = self.cleaned_data["email"]
            if re.match(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", email, re.I) is None:
                raise forms.ValidationError("Email invalide")
            return email
        except:
            pass


class TransactionForm(forms.ModelForm):
    accounts_choices = [(account.id, account) for account in Account.objects.all()]
    sender_account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(),
                                            widget=forms.Select(attrs={"class": "form-control"}))
    receiver_account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(),
                                              widget=forms.Select(attrs={"class": "form-control"}))
    amount = forms.DecimalField(required=True,
                                widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "999.99"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Mot de passe..."}))

    class Meta:
        model = Transaction
        exclude = ["date", "number"]

    def clean(self):
        try:
            cleaned_data = super().clean()
            sender_account = cleaned_data.get("sender_account")
            receiver_account = cleaned_data.get("receiver_account")
            amount = cleaned_data.get("amount")
            if sender_account == receiver_account:
                self.add_error("sender_account", "Le compte émetteur et le compte récepteur sont les mémes.")
                self.add_error("receiver_account", "Le compte émetteur et le compte récepteur sont les mémes.")
            if amount <= 200 or amount > 5000:
                self.add_error("amount", "Montant invalide (250 < Montant < 5000)")
            if sender_account.balance <= amount:
                self.add_error("sender_account", "Le compte selectionné ne dispose pas d'un montant suffisant!")
        except:
            pass


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control mr-sm-2", "type": "search", "placeholder": "Numero de transaction ...",
               "aria-label": "Search"}), required=True)


class AccountSearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control mr-sm-2", "type": "search", "placeholder": "Numero du compte ou de la carte...",
               "aria-label": "Search"}), required=True)


class ClientSearchForm(forms.Form):
    search = forms.CharField(widget=forms.NumberInput(
        attrs={"class": "form-control mr-sm-2", "type": "search", "placeholder": "Numero du client Ou Cin...",
               "aria-label": "Search"}), required=True)


class WithdrawalForm(forms.ModelForm):
    accounts_choices = [(account.id, account) for account in Account.objects.all()]
    account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}))
    amount = forms.DecimalField(required=True,
                                widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "999.99"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Mot de passe..."}))

    class Meta:
        model = Withdrawal
        fields = ["amount", "account"]

    def clean(self):
        try:
            cleaned_data = super().clean()
            account = cleaned_data.get("account")
            amount = cleaned_data.get("amount")
            if amount <= 100 or amount > 3000:
                self.add_error("amount", "Montant invalide (100 < Montant < 3000)")
            elif amount > account.balance:
                self.add_error("amount", "Le montant saisi est indisponible dans le compte selectionné!")
        except:
            pass


class DepositForm(forms.ModelForm):
    accounts_choices = [(account.id, account) for account in Account.objects.all()]
    account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}))
    amount = forms.DecimalField(required=True,
                                widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "999.99"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Mot de passe..."}))

    class Meta:
        model = Deposit
        fields = ["amount", "account"]

    def clean(self):
        try:
            cleaned_data = super().clean()
            account = cleaned_data.get("account")
            amount = cleaned_data.get("amount")
            print(f"Account: {account}")
            if amount <= 100 or amount > 3000:
                self.add_error("amount", "Montant invalide (100 < Montant < 3000)")
        except:
            pass


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ["user"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class ClientForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}))
    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}))
    last_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Mot de passe..."}))
    password_confirm = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Mot de passe..."}))
    cin = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Cin"}))
    birth_date = forms.DateField(required=True, widget=forms.DateInput(format="%Y-%m-%d",
                                                                       attrs={"class": "form-control",
                                                                              "id": "birthdate_timepicker",
                                                                              "placeholder": "Date de naissance"}))
    city = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ville"}))
    state = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Région"}))
    nationality = forms.ChoiceField(required=True,
                                    widget=forms.Select(attrs={"class": "form-control", "placeholder": "Nationalité"}),
                                    choices=get_countries)
    image = forms.ImageField(required=True,
                             widget=forms.FileInput(attrs={"class": "custom-file-input", "id": "imageFile"}))

    def clean_email(self):
        try:
            email = self.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                self.add_error("email", "L'adresse Email est déja utilisée")
        except:
            pass

    def clean_cin(self):
        try:
            cin = self.cleaned_data["cin"]
            if Person.objects.filter(cin=cin).exists():
                self.add_error("cin", "Cin déja existe!")
        except:
            pass

    def clean(self):
        try:
            cleaned_data = super().clean()
            password = cleaned_data.get("password")
            nationaltity = cleaned_data.get("nationality")
            password_confirm = cleaned_data.get("password_confirm")
            username = cleaned_data.get("username")
            birth_date = cleaned_data.get("birth_date")
            codes = [code for code, country in get_countries()]
            if len(password) < 8:
                self.add_error("password", "Mot de passe trés court!")
            if password != password_confirm:
                self.add_error("password_confirm", "Les deux mots de passe sont différents!")
            if nationaltity not in codes:
                self.add_error("nationality", "La nationalité selectionné n'est pas valide!")
            if User.objects.filter(username=username).exists():
                self.add_error("username", "Nom d'utilisateur déja utilisé!")
            if birth_date > datetime.now().date():
                self.add_error("birth_date", "Date de naissance invalide, choisir une date valide!")
        except Exception as e:
            pass


class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Ancien mot de passe..."}))
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Nouveau mot de passe..."}))
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Confirmer le nouveau mot de passe..."}))

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data["old_password"]
        new_password = cleaned_data["new_password"]
        confirm_new_password = cleaned_data["confirm_new_password"]
        if len(new_password) < 8:
            self.add_error("new_password", "Mot de passe trés court!")
        elif new_password != confirm_new_password:
            self.add_error("new_password", "Les deux mots de passe sont différents!")
            self.add_error("confirm_new_password", "Les deux mots de passe sont différents!")


class AccountSettingsForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}))
    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}))
    last_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
    cin = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Cin"}))
    birth_date = forms.DateField(required=True, input_formats=["%m/%d/%Y"], widget=forms.DateInput(
        attrs={"class": "form-control", "id": "birthdate_timepicker", "placeholder": "Date de naissance"}))
    city = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ville"}))
    state = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Région"}))
    nationality = forms.ChoiceField(required=True,
                                    widget=forms.Select(attrs={"class": "form-control", "placeholder": "Nationalité"}),
                                    choices=get_countries)
    image = forms.ImageField(required=True,
                             widget=forms.FileInput(attrs={"class": "custom-file-input", "id": "imageFile"}))

    def clean(self):
        try:
            cleaned_data = super().clean()
            nationality = cleaned_data.get("nationality")
            birth_date = cleaned_data.get("birth_date")
            codes = [code for code, country in get_countries()]
            if nationality not in codes:
                self.add_error("nationality", "La nationalité selectionné n'est pas valide!")
            if birth_date > datetime.now().date():
                self.add_error("birth_date", "Date de naissance invalide, choisir une date valide!")
        except Exception as ex:
            pass

class EditAccountForm(forms.ModelForm):
    balance = forms.CharField(required=True,
                           widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Montant"}))
    expiration_date = forms.DateField(required=True, widget=forms.DateInput(format="%Y-%m-%d",
        attrs={"class": "form-control", "id": "expiration_date_timepicker", "placeholder": "Date d'expiration"}))
    opening_balance = forms.CharField(required=True,
                           widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Montant d'ouverture"}))
    opening_date = forms.DateField(required=True, widget=forms.DateInput(format="%Y-%m-%d",
        attrs={"class": "form-control", "id": "opening_date_timepicker", "placeholder": "Date d'ouverture"}))
    class Meta:
        model = Account
        fields = ["balance", "expiration_date", "opening_balance", "opening_date"]

    def clean(self):
        cleaned_data = super().clean()
        balance = cleaned_data.get("balance")
        expiration_date = cleaned_data.get("expiration_date")
        opening_balance = cleaned_data.get("opening_balance")
        opening_date = cleaned_data.get("opening_date")
        try:
            if expiration_date < datetime.date.today():
                self.expiration_date("expiration_date", "La date d'éxpiration n'est pas valide pour un compte")
        except Exception as ex:
            print(ex)
            self.expiration_date("expiration_date", "La date d'éxpiration n'est pas valide pour un compte")
        try:
            if opening_date < datetime.date.today():
                self.expiration_date("opening_date", "La date d'ouverture n'est pas valide pour un compte")
        except:
            self.expiration_date("opening_date", "La date d'ouverture n'est pas valide pour un compte")
        try:
            if float(opening_balance) < 100:
                self.add_error("opening_balance", "Le montant d'ouverture du compte  doit être superieur a 100 Dhs")
        except:
            self.add_error("opening_balance", "Montant invalid, veuillez ressayer")

class AddAccountForm(forms.ModelForm):
    balance = forms.CharField(required=True,
                           widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Montant"}))
    opening_balance = forms.CharField(required=True,
                           widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Montant d'ouverture"}))
    client = forms.ModelChoiceField(required=True, queryset=Client.objects.all(),
                                            widget=forms.Select(attrs={"class": "form-control"}))
    class Meta:
        model = Account
        fields = ["balance", "opening_balance", "client"]

    def clean(self):
        cleaned_data = super().clean()
        balance = cleaned_data.get("balance")
        opening_balance = cleaned_data.get("opening_balance")
        try:
            if float(balance) < 100:
                self.add_error("balance", "Le montant du compte  doit être superieur a 100 Dhs")
        except:
            self.add_error("balance", "Montant invalid, veuillez ressayer")
        try:
            if float(opening_balance) < 100:
                self.add_error("opening_balance", "Le montant d'ouverture du compte  doit être superieur a 100 Dhs")
        except:
            self.add_error("opening_balance", "Montant invalid, veuillez ressayer")
















