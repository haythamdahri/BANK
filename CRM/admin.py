from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Employee)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Client)
admin.site.register(Transaction)
admin.site.register(Withdrawal)
admin.site.register(Payment)