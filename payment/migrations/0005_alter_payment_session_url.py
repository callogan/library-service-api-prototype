# Generated by Django 5.0.6 on 2024-06-06 18:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0004_alter_payment_session_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="session_url",
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]