# Generated by Django 2.2 on 2019-04-05 11:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0008_auto_20190405_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 4, 11, 12, 26, 676305, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='client',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='person', to='CRM.Person'),
        ),
    ]
