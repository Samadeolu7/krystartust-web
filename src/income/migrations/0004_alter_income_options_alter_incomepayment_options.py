# Generated by Django 5.1.2 on 2024-10-17 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0003_alter_incomepayment_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='income',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterModelOptions(
            name='incomepayment',
            options={'ordering': ['created_at']},
        ),
    ]
