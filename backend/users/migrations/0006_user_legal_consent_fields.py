from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_trial_and_plan_tier"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="ai_usage_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="legal_consent_language",
            field=models.CharField(blank=True, default="", max_length=2),
        ),
        migrations.AddField(
            model_name="user",
            name="privacy_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="terms_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]