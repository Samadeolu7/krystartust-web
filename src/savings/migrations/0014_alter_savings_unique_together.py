# Generated by Django 5.1.2 on 2024-11-01 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0006_client_date_alter_client_created_at'),
        ('savings', '0013_savings_type_alter_savingspayment_transaction_type_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='savings',
            unique_together={('client', 'type')},
        ),
    ]