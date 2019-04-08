from CRM.models import Withdrawal


def generate_withrawals(number):
    import random
    for i in range(number):
        Withdrawal.objects.create(account_id=1, amount=random.randrange(100, 600))
