# Generated by Django 5.1.2 on 2025-04-29 20:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0017_alter_office_bank"),
        ("bank", "0018_alter_bank_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="office",
            name="bank",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="branch",
                to="bank.bank",
            ),
        ),
    ]
