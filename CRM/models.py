from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
import uuid

# Create your models here.
from django.utils.timezone import now

transactions_types = [('transfer', 'Transfer'), ('withdrawal', 'Withdrawal'), ('payment', 'Payment')]

def generateCreditCardNumber():
    credit = str()
    for i in range(4):
        credit += str(uuid.uuid4().fields[-1])[:4]
    return credit

def generateTransactionId():
    return uuid.uuid4()

class Person(models.Model):
    cin = models.CharField(unique=True, blank=False, max_length=255)
    birthDate = models.DateField(null=False, blank=False)
    city = models.CharField(blank=False, null=False, max_length=30)
    state = models.CharField(blank=False, null=False, max_length=100)
    nationality = models.CharField(blank=False, null=False, max_length=150)
    image = models.ImageField(upload_to='images/')

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    person = models.OneToOneField(Person, on_delete=models.CASCADE)


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='person')
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

class Account(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='client')
    balance = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)
    credit_card = models.CharField(max_length=16, unique=True, blank=False, null=False, default=generateCreditCardNumber, auto_created=True)
    expiration_date = models.DateField(default=(now()+timedelta(days=(365*4))))
    data_opened = models.DateField(default=now)
    opening_balance = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='sender_account')
    receiver_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='receiver_account')
    number = models.CharField(max_length=365000, null=False, blank=False, default=generateTransactionId)
    date = models.DateTimeField(default=now, null=False, blank=False)
    type = models.CharField(choices=transactions_types, null=False, blank=False, max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

