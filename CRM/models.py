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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cin = models.CharField(unique=True, blank=False, max_length=255)
    birthDate = models.DateField(null=False, blank=False)
    city = models.CharField(blank=False, null=False, max_length=30)
    state = models.CharField(blank=False, null=False, max_length=100)
    nationality = models.CharField(blank=False, null=False, max_length=150)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.user.username + " | Cin: " + self.cin

    @property
    def full_name(self):
        return self.user.first_name + " " + self.user.last_name


class Employee(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    join_date = models.DateField(default=now)

    def __str__(self):
        return self.person.__str__()


class Client(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='person')
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.person.__str__() + " | " + self.creator.person.user.__str__()

class Account(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='client')
    balance = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)
    credit_card = models.CharField(max_length=16, unique=True, blank=False, null=False, default=generateCreditCardNumber, auto_created=True)
    expiration_date = models.DateField(default=(now()+timedelta(days=(365*4))))
    data_opened = models.DateField(default=now)
    opening_balance = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

    def __str__(self):
        return self.client.__str__() + " | Balance: " + self.balance.__str__()

class Transaction(models.Model):
    sender_account = models.ForeignKey(Account, default=1, on_delete=models.SET_DEFAULT, related_name='sender_account')
    receiver_account = models.ForeignKey(Account, default=1, on_delete=models.SET_DEFAULT, related_name='receiver_account')
    number = models.CharField(max_length=365000, null=False, blank=False, default=generateTransactionId)
    date = models.DateTimeField(default=now, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

    def __str__(self):
        return self.sender_account.__str__() + " | " + self.receiver_account.__str__() + " | Amount: " + self.amount.__str__()

#------------------- Retrait -------------------
class Withdrawal(models.Model):
    account = models.ForeignKey(Account, default=1, on_delete=models.SET_DEFAULT, related_name="withdrawal_account")
    number = models.CharField(max_length=365000, null=False, blank=False, default=generateTransactionId)
    date = models.DateTimeField(default=now, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

    def __str__(self):
        return self.account.__str__() + " | " + self.number.__str__() + " | " + self.date.__str__() + " | " + self.amount.__str__()

#------------------- Mettre de l'argent en compte -------------------
class Deposit(models.Model):
    account = models.ForeignKey(Account, default=1, on_delete=models.SET_DEFAULT, related_name="payment_account")
    number = models.CharField(max_length=365000, null=False, blank=False, default=generateTransactionId)
    date = models.DateTimeField(default=now, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False, default=0)

    def __str__(self):
        return self.account.__str__() + " | " + self.number.__str__() + " | " + self.date.__str__() + " | " + self.amount.__str__()