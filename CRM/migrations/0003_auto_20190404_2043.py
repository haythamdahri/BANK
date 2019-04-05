# Generated by Django 2.2 on 2019-04-04 20:43

import CRM.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0002_auto_20190404_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='account',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='number',
            field=models.CharField(default=CRM.models.generateTransactionId, max_length=365000),
        ),
    ]
