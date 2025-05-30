# Generated by Django 5.1.2 on 2025-01-30 08:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0014_alter_tickets_repayment_schedule'),
        ('expenses', '0012_alter_expense_options_alter_expense_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensepayment',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expense_payments', to='administration.transaction'),
        ),
    ]
