# Generated by Django 5.1 on 2024-10-01 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_alter_bank_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankpayment',
            old_name='bank_balance',
            new_name='balance',
        ),
    ]