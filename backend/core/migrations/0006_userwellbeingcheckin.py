from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_cmspage_multilingual_slug"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserWellbeingCheckin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mood", models.CharField(blank=True, choices=[("low", "Low"), ("ok", "OK"), ("good", "Good"), ("great", "Great")], max_length=16)),
                ("energy_level", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wellbeing_checkins", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "core_userwellbeingcheckin",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="userwellbeingcheckin",
            index=models.Index(fields=["user", "created_at"], name="core_userwe_user_id_a8deb2_idx"),
        ),
    ]
