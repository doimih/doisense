from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0004_repair_missing_subscription_columns"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeWebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_id", models.CharField(max_length=255, unique=True)),
                ("event_type", models.CharField(max_length=100)),
                ("delivery_attempts", models.PositiveIntegerField(default=1)),
                ("first_received_at", models.DateTimeField(auto_now_add=True)),
                ("last_received_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "payments_stripewebhookevent",
                "ordering": ["-first_received_at"],
            },
        ),
        migrations.AddIndex(
            model_name="stripewebhookevent",
            index=models.Index(fields=["event_type", "first_received_at"], name="payments_st_event_t_2719e6_idx"),
        ),
    ]
