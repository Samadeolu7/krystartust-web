# Generated by Django 5.1.2 on 2024-10-17 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0009_guarantor'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loanpayment',
            options={'ordering': ['payment_date', 'created_at']},
        ),
    ]