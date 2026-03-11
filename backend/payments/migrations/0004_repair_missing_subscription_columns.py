from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_payment_cancel_at_period_end_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE payments_payment "
                        "ADD COLUMN IF NOT EXISTS current_period_end timestamp with time zone NULL"
                    ),
                    reverse_sql=(
                        "ALTER TABLE payments_payment "
                        "DROP COLUMN IF EXISTS current_period_end"
                    ),
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE payments_payment "
                        "ADD COLUMN IF NOT EXISTS cancel_at_period_end boolean NOT NULL DEFAULT FALSE"
                    ),
                    reverse_sql=(
                        "ALTER TABLE payments_payment "
                        "DROP COLUMN IF EXISTS cancel_at_period_end"
                    ),
                ),
            ],
            state_operations=[],
        ),
    ]