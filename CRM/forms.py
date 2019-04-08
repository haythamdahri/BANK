from django import forms
from CRM.models import Transaction, Account, Withdrawal
import re


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'placeholder': 'Email...', 'class': 'form-control'}),
        required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe...', 'class': 'form-control'}),
        required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if re.match(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', email, re.I) is None:
            raise forms.ValidationError('Email invalide')
        return email

class TransactionForm(forms.ModelForm):
    accounts_choices = [(account.id, account) for account in Account.objects.all()]
    sender_account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(), widget=forms.Select(attrs={"class": "form-control form-control-sm"}))
    receiver_account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(), widget=forms.Select(attrs={"class": "form-control form-control-sm"}))
    amount = forms.DecimalField(required=True, widget=forms.NumberInput(attrs={"class":"form-control", "placeholder": "999.99"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe..."}))

    class Meta:
        model = Transaction
        exclude = ['date', 'number']

    def clean(self):
        cleaned_data = super().clean()
        sender_account = cleaned_data.get('sender_account')
        receiver_account = cleaned_data.get('receiver_account')
        amount = cleaned_data.get('amount')
        if sender_account == receiver_account:
            self.add_error('sender_account', 'Le compte émetteur et le compte récepteur sont les mémes.')
            self.add_error('receiver_account', 'Le compte émetteur et le compte récepteur sont les mémes.')
        if amount <= 200 or amount > 5000:
            self.add_error('amount', 'Montant invalide (250 < Montant < 5000)')
        if sender_account.balance <= amount:
            self.add_error('sender_account', 'Le compte selectionné ne dispose pas d\'un montant suffisant!')

class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mr-sm-2', 'type': 'search', 'placeholder': 'Numero de transaction ...', 'aria-label': 'Search'}), required=True)


class WithdrawalForm(forms.ModelForm):
    accounts_choices = [(account.id, account) for account in Account.objects.all()]
    account = forms.ModelChoiceField(required=True, queryset=Account.objects.all(), widget=forms.Select(attrs={"class": "form-control form-control-sm"}))
    amount = forms.DecimalField(required=True, widget=forms.NumberInput(attrs={"class":"form-control", "placeholder": "999.99"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe..."}))

    class Meta:
        model = Withdrawal
        fields = ['amount', 'account']

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        amount = cleaned_data.get('amount')
        print(f"Account: {account}")
        if amount <= 100 or amount > 3000:
            self.add_error('amount', 'Montant invalide (100 < Montant < 3000)')
        elif amount > account.balance:
            self.add_error('amount', 'Le montant saisi est indisponible dans le compte selectionné!')
