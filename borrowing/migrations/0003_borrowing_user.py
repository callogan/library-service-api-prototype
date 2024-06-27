
import django
from django.conf import settings

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0002_remove_borrowing_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to=settings.AUTH_USER_MODEL,
                default=1
            ),
        ),
    ]
