from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0004_social_media_owner_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialmediasettings",
            name="instagram_token_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="socialmediasettings",
            name="linkedin_token_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
