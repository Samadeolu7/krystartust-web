# Generated by Django 5.1.2 on 2024-10-17 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_alter_client_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='account_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='bank_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='marital_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='next_of_kin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='next_of_kin_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]