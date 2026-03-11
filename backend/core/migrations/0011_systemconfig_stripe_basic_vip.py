from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_systemconfig_recaptcha_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="stripe_price_id_basic",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="stripe_price_id_vip",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
