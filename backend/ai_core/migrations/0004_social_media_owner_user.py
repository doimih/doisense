from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ai_core", "0003_social_media_owner_doisense"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialmediapost",
            name="owner_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="social_media_posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
