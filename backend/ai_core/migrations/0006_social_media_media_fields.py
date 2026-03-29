from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0005_social_media_settings_token_expires_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialmediapost",
            name="video_url",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="socialmediasettings",
            name="media_image_folder",
            field=models.CharField(blank=True, default="social/images", max_length=255),
        ),
        migrations.AddField(
            model_name="socialmediasettings",
            name="media_video_folder",
            field=models.CharField(blank=True, default="social/videos", max_length=255),
        ),
    ]
