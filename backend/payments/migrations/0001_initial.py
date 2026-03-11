import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


CREATE_PAYMENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS payments_payment (
    id SERIAL PRIMARY KEY,
    stripe_customer_id VARCHAR(255) NULL,
    stripe_subscription_id VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);
"""


DROP_PAYMENT_TABLE_SQL = "DROP TABLE IF EXISTS payments_payment;"


class Migration(migrations.Migration):
    """Record the existing payments_payment table state without re-creating it."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(CREATE_PAYMENT_TABLE_SQL, reverse_sql=DROP_PAYMENT_TABLE_SQL),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="Payment",
                    fields=[
                        ("id", models.AutoField(auto_created=True, primary_key=True, verbose_name="ID")),
                        (
                            "user",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="payments",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                        ("stripe_customer_id", models.CharField(blank=True, max_length=255, null=True)),
                        ("stripe_subscription_id", models.CharField(blank=True, max_length=255, null=True)),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("active", "Active"),
                                    ("cancelled", "Cancelled"),
                                    ("past_due", "Past due"),
                                    ("trialing", "Trialing"),
                                ],
                                default="active",
                                max_length=20,
                            ),
                        ),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        "db_table": "payments_payment",
                    },
                ),
            ],
        ),
    ]
