from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_systemconfig_qa_allowed_source_ips"),
        ("core", "0023_add_stripe_product_ids"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="google_client_secret",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
