from CRM.models import Withdrawal, Deposit


def generate_withrawals(number):
    import random
    for i in range(number):
        Withdrawal.objects.create(account_id=1, amount=random.randrange(100, 600))

def generate_deposits(number):
    import random
    for i in range(number):
        Deposit.objects.create(account_id=1, amount=random.randrange(100, 600))
