from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_legal_consent_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="early_discount_eligible",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="vip_manual_override",
            field=models.BooleanField(default=False),
        ),
    ]
