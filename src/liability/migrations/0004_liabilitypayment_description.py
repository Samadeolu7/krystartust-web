# Generated by Django 5.1 on 2024-09-26 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liability', '0003_liability_year_alter_liability_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='liabilitypayment',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
