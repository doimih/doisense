from django.conf import settings
from django.db import migrations, models


CREATE_USER_PROFILE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS profiles_userprofile (
    id BIGSERIAL PRIMARY KEY,
    preferred_tone VARCHAR(100) NOT NULL DEFAULT '',
    sensitivities TEXT NOT NULL DEFAULT '',
    communication_style VARCHAR(100) NOT NULL DEFAULT '',
    emotional_baseline VARCHAR(100) NOT NULL DEFAULT '',
    keywords JSONB NOT NULL DEFAULT '{}'::jsonb,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users_user(id) ON DELETE CASCADE
);
"""


DROP_USER_PROFILE_TABLE_SQL = "DROP TABLE IF EXISTS profiles_userprofile;"


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(CREATE_USER_PROFILE_TABLE_SQL, reverse_sql=DROP_USER_PROFILE_TABLE_SQL),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="UserProfile",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("preferred_tone", models.CharField(blank=True, max_length=100)),
                        ("sensitivities", models.TextField(blank=True)),
                        ("communication_style", models.CharField(blank=True, max_length=100)),
                        ("emotional_baseline", models.CharField(blank=True, max_length=100)),
                        ("keywords", models.JSONField(blank=True, default=dict)),
                        (
                            "user",
                            models.OneToOneField(
                                on_delete=models.CASCADE,
                                related_name="profile",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "profiles_userprofile",
                    },
                ),
            ],
        ),
    ]