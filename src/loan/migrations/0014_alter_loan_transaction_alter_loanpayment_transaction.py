# Generated by Django 5.1.2 on 2024-11-30 13:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_monthstatus'),
        ('loan', '0013_alter_loanrepaymentschedule_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='administration.transaction'),
        ),
        migrations.AlterField(
            model_name='loanpayment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='loan_payments', to='administration.transaction'),
        ),
    ]
