from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0002_social_media_models_and_rules_prompt"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialmediapost",
            name="owner",
            field=models.CharField(default="doisense", max_length=64),
        ),
    ]
