from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0005_ai_budget_monthly_target"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ailog",
            name="provider",
            field=models.CharField(default="unknown", max_length=50),
        ),
        migrations.AlterField(
            model_name="aibudgetcredit",
            name="provider",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="aibudgetmonthlytarget",
            name="provider",
            field=models.CharField(max_length=50),
        ),
    ]
