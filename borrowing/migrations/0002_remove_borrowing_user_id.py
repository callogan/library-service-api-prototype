# Generated by Django 5.0.6 on 2024-06-04 08:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="borrowing",
            name="user_id",
        ),
    ]
