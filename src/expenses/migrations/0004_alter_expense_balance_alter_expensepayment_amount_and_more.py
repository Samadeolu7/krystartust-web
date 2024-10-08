# Generated by Django 5.1 on 2024-09-26 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0003_rename_duration_expense_year_remove_expense_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='expensepayment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='expensepayment',
            name='balance',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
