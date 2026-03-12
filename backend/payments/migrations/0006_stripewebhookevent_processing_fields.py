from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0005_stripewebhookevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="stripewebhookevent",
            name="last_status",
            field=models.CharField(
                choices=[
                    ("received", "Received"),
                    ("processed", "Processed"),
                    ("ignored", "Ignored"),
                    ("failed", "Failed"),
                ],
                default="received",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="stripewebhookevent",
            name="payload",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="stripewebhookevent",
            name="processed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stripewebhookevent",
            name="processing_error",
            field=models.TextField(blank=True, default=""),
        ),
    ]
