from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_phone_contact"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="onboarding_completed",
            field=models.BooleanField(default=True),
        ),
    ]