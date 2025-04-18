# Generated by Django 5.1.2 on 2025-03-31 14:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0015_alter_approval_type"),
        ("loan", "0016_alter_loan_transaction_alter_loanpayment_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loan",
            name="transaction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="loans",
                to="administration.transaction",
            ),
        ),
    ]
