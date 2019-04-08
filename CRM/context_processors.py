from CRM.models import Client, Account


def global_vars(request):
    context = dict()
    client = Client()
    total_balance = 0
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(person_id=request.user.person.id)
            for account in Account.objects.filter(client_id=client.pk):
                total_balance += account.balance
        except Client.DoesNotExist as ex:
            client = None
    else:
        client = None
    context['client'] = client
    context['total_balance'] = total_balance
    return context