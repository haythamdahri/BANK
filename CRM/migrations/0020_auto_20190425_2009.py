# Generated by Django 2.2 on 2019-04-25 20:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0019_auto_20190425_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 24, 20, 9, 12, 382989, tzinfo=utc)),
        ),
    ]