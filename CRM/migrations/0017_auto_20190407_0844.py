# Generated by Django 2.2 on 2019-04-07 08:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0016_auto_20190407_0524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 6, 8, 44, 2, 987640, tzinfo=utc)),
        ),
    ]
