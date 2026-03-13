# Generated migration for adding Stripe product IDs

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_support_ticket_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="stripe_product_id_basic",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="stripe_product_id_premium",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="systemconfig",
            name="stripe_product_id_vip",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
