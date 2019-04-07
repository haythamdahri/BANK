from CRM.models import Client


def global_vars(request):
    context = dict()
    client = Client()
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(person_id=request.user.person.id)
        except Client.DoesNotExist as ex:
            client = None
    else:
        client = None
    context['client'] = client
    return context