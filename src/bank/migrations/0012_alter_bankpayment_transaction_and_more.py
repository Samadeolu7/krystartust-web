# Generated by Django 5.1.2 on 2024-11-30 13:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_monthstatus'),
        ('bank', '0011_bankpayment_idx_payment_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankpayment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_payments', to='administration.transaction'),
        ),
        migrations.AddIndex(
            model_name='bankpayment',
            index=models.Index(fields=['bank', 'payment_date'], name='idx_bank_payment_date'),
        ),
    ]