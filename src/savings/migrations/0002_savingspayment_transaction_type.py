# Generated by Django 5.1 on 2024-09-09 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingspayment',
            name='transaction_type',
            field=models.CharField(choices=[('S', 'Savings'), ('W', 'Withdrawal')], default='S', max_length=1),
        ),
    ]