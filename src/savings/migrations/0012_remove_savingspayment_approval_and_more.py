# Generated by Django 5.1.2 on 2024-10-22 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savings', '0011_savingspayment_approval_savingspayment_bank_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='savingspayment',
            name='approval',
        ),
        migrations.AddField(
            model_name='savingspayment',
            name='approved',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]