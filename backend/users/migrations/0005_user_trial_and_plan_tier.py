from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_onboarding_completed"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="plan_tier",
            field=models.CharField(
                choices=[
                    ("free", "Free"),
                    ("trial", "Trial"),
                    ("basic", "Basic"),
                    ("premium", "Premium"),
                    ("vip", "VIP"),
                ],
                default="free",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="trial_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="trial_ends_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
