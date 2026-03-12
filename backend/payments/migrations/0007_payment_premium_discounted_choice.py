from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_stripewebhookevent_processing_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="plan_tier",
            field=models.CharField(
                choices=[
                    ("basic", "Basic"),
                    ("premium", "Premium"),
                    ("premium_discounted", "Premium Discounted"),
                    ("vip", "VIP"),
                ],
                default="premium",
                max_length=24,
            ),
        ),
    ]
