# Generated by Django 5.1.2 on 2024-10-16 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0005_expensepayment_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
