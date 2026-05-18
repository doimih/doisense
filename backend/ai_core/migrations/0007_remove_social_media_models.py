from django.db import migrations


def drop_social_rules_prompt(apps, schema_editor):
    Prompt = apps.get_model("ai_core", "Prompt")
    Prompt.objects.filter(name="social_media_global_wellness_rules").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ai_core", "0006_social_media_media_fields"),
    ]

    operations = [
        migrations.RunPython(drop_social_rules_prompt, migrations.RunPython.noop),
        migrations.DeleteModel(
            name="SocialMediaSettings",
        ),
        migrations.DeleteModel(
            name="SocialMediaPost",
        ),
    ]
