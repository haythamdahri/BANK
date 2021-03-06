# Generated by Django 2.2 on 2019-04-05 21:27

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0011_auto_20190405_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='join_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='account',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 4, 21, 27, 9, 402023, tzinfo=utc)),
        ),
    ]
