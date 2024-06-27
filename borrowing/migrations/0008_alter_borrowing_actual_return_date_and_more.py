# Generated by Django 5.0.6 on 2024-06-12 08:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0007_alter_borrowing_actual_return_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="borrow_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="expected_return_date",
            field=models.DateTimeField(),
        ),
    ]
