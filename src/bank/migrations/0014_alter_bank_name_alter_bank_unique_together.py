# Generated by Django 5.1.2 on 2025-01-16 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0013_remove_bankpayment_idx_bank_payment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='bank',
            unique_together={('name', 'year')},
        ),
    ]
