# Generated by Django 5.1.2 on 2024-10-17 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0008_alter_savingspayment_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='savingspayment',
            options={'ordering': ['payment_date', 'created_at']},
        ),
    ]
