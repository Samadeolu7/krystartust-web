# Generated by Django 5.1.2 on 2025-02-02 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0014_alter_tickets_repayment_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval',
            name='type',
            field=models.CharField(choices=[('Expenses', 'expenses'), ('Batch_Expense', 'batch_expense'), ('Loan', 'loan'), ('Withdrawal', 'withdrawal'), ('Salary', 'salary'), ('Cash_Transfer', 'cash_transfer')], max_length=100),
        ),
    ]
