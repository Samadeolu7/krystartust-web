# Generated by Django 5.1.2 on 2024-11-30 13:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_monthstatus'),
        ('income', '0005_incomepayment_created_by_incomepayment_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomepayment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='income_payments', to='administration.transaction'),
        ),
    ]