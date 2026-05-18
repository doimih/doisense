from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_user_early_discount_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="onboarding_completed",
            field=models.BooleanField(default=False),
        ),
    ]
