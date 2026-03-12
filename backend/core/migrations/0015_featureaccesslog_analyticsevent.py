from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_legal_consent_fields"),
        ("core", "0014_notificationdelivery"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeatureAccessLog",
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
                ("feature_key", models.CharField(max_length=64)),
                ("required_tiers", models.JSONField(default=list)),
                ("user_tier", models.CharField(default="anonymous", max_length=16)),
                ("granted", models.BooleanField(default=False)),
                ("reason", models.CharField(blank=True, default="", max_length=128)),
                ("context", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="feature_access_logs",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "core_featureaccesslog",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AnalyticsEvent",
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
                ("event_name", models.CharField(max_length=96)),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("backend", "Backend"),
                            ("frontend", "Frontend"),
                            ("system", "System"),
                        ],
                        default="backend",
                        max_length=16,
                    ),
                ),
                ("schema_version", models.CharField(default="v1", max_length=16)),
                ("session_id", models.CharField(blank=True, default="", max_length=128)),
                ("properties", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="analytics_events",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "core_analyticsevent",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="featureaccesslog",
            index=models.Index(
                fields=["feature_key", "created_at"],
                name="core_featur_feature_c9f4db_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="featureaccesslog",
            index=models.Index(
                fields=["granted", "created_at"],
                name="core_featur_granted_988617_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["event_name", "created_at"],
                name="core_analyt_event_n_8d15f4_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["source", "created_at"],
                name="core_analyt_source_8dd76e_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["user", "created_at"],
                name="core_analyt_user_id_9444b4_idx",
            ),
        ),
    ]
