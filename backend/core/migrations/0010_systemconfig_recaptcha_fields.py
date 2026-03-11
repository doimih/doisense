# Generated manually to sync DB schema for SystemConfig reCAPTCHA fields.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_landing_pages"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecaptchaConfig",
            fields=[],
            options={
                "verbose_name": "reCAPTCHA Configuration",
                "verbose_name_plural": "reCAPTCHA Configuration",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.systemconfig",),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="recaptcha_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="recaptcha_min_score",
            field=models.DecimalField(decimal_places=2, default=0.5, max_digits=3),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="recaptcha_secret_key",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="recaptcha_site_key",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
