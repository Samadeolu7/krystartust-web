# Generated by Django 5.1 on 2024-09-17 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0002_loan_balance_alter_loan_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanpayment',
            name='emi',
        ),
    ]