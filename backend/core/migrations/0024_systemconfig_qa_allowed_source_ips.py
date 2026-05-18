from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_add_stripe_product_ids"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfig",
            name="qa_allowed_source_ips",
            field=models.TextField(
                blank=True,
                default="",
                help_text=(
                    "Optional allowlist for QA source IPs/CIDRs. "
                    "Use comma or newline separated values (e.g. 203.0.113.10, 198.51.100.0/24)."
                ),
            ),
        ),
    ]
