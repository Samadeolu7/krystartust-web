# Generated by Django 5.1.2 on 2024-10-20 18:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_transaction'),
        ('income', '0004_alter_income_options_alter_incomepayment_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='incomepayment',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='income_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='incomepayment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='administration.transaction'),
        ),
    ]
