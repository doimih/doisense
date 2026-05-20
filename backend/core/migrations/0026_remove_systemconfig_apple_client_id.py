from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_systemconfig_google_client_secret"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="systemconfig",
            name="apple_client_id",
        ),
    ]
