# Generated by Django 2.2 on 2019-04-06 10:07

import CRM.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0013_auto_20190406_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiration_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 5, 10, 7, 18, 361550, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='receiver_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver_account', to='CRM.Account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='sender_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_account', to='CRM.Account'),
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default=CRM.models.generateTransactionId, max_length=365000)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawal_account', to='CRM.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default=CRM.models.generateTransactionId, max_length=365000)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_account', to='CRM.Account')),
            ],
        ),
    ]
