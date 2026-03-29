from django.db import migrations, models


def seed_social_media_rules_prompt(apps, schema_editor):
    Prompt = apps.get_model("ai_core", "Prompt")

    content = (
        "All generated social media content must be wellness-related only.\n"
        "Adapt the tone and writing style to the selected platform.\n"
        "Every post must end with a closing line that explicitly references the platform name."
    )

    Prompt.objects.get_or_create(
        name="social_media_global_wellness_rules",
        defaults={
            "type": "rules",
            "content": content,
            "language": "en",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SocialMediaPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "platform",
                    models.CharField(
                        choices=[
                            ("instagram", "Instagram"),
                            ("tiktok", "TikTok"),
                            ("linkedin", "LinkedIn"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("hashtags", models.CharField(blank=True, default="", max_length=500)),
                ("image_url", models.TextField(blank=True, default="")),
                ("wellness_topic", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("posted", "Posted")],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("posted_at", models.DateTimeField(blank=True, null=True)),
                ("publish_log", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "Social Media Post",
                "verbose_name_plural": "Social Media Posts",
                "db_table": "ai_core_socialmediapost",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SocialMediaSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("instagram_app_id", models.CharField(blank=True, default="", max_length=255)),
                ("instagram_app_secret", models.CharField(blank=True, default="", max_length=255)),
                ("instagram_access_token", models.TextField(blank=True, default="")),
                ("instagram_refresh_token", models.TextField(blank=True, default="")),
                ("instagram_business_account_id", models.CharField(blank=True, default="", max_length=255)),
                ("tiktok_app_id", models.CharField(blank=True, default="", max_length=255)),
                ("tiktok_app_secret", models.CharField(blank=True, default="", max_length=255)),
                ("tiktok_access_token", models.TextField(blank=True, default="")),
                ("tiktok_refresh_token", models.TextField(blank=True, default="")),
                ("linkedin_client_id", models.CharField(blank=True, default="", max_length=255)),
                ("linkedin_client_secret", models.CharField(blank=True, default="", max_length=255)),
                ("linkedin_access_token", models.TextField(blank=True, default="")),
                ("linkedin_refresh_token", models.TextField(blank=True, default="")),
                ("linkedin_organization_id", models.CharField(blank=True, default="", max_length=255)),
            ],
            options={
                "verbose_name": "Social Media API Settings",
                "verbose_name_plural": "Social Media API Settings",
                "db_table": "ai_core_socialmediasettings",
            },
        ),
        migrations.RunPython(seed_social_media_rules_prompt, migrations.RunPython.noop),
    ]
