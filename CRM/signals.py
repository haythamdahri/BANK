from django.db.models.signals import post_save
from django.dispatch import receiver

from CRM.models import Transaction,Withdrawal, Payment

#-------------------------- After transaction operation --------------------------
@receiver(post_save, sender=Transaction)
def save_transaction(sender, instance, created, **kwargs):
    if created:
        sender_account = instance.sender_account
        receiver_account = instance.receiver_account
        sender_account.balance -= instance.amount
        receiver_account.balance += instance.amount
        sender_account.save()
        receiver_account.save()

#-------------------------- After transaction operation --------------------------
@receiver(post_save, sender=Withdrawal)
def save_withdrawal(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        account.balance -= instance.amount
        account.save()


#-------------------------- After transaction operation --------------------------
@receiver(post_save, sender=Payment)
def save_payment(sender, instance, created, **kwargs):
    if created:
        account = instance.account
        account.balance += instance.amount
        account.save()