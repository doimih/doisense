from django.conf import settings
from django.db import migrations, models


CREATE_CONVERSATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_conversation (
    id BIGSERIAL PRIMARY KEY,
    module VARCHAR(32) NOT NULL DEFAULT '',
    plan_tier VARCHAR(10) NOT NULL DEFAULT 'free',
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id BIGINT NULL REFERENCES users_user(id) ON DELETE SET NULL
);
"""


CREATE_TEMPLATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_conversationtemplate (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    language VARCHAR(2) NOT NULL,
    prompt TEXT NOT NULL
);
"""


CREATE_AILOG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_ailog (
    id BIGSERIAL PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    prompt_hash VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id BIGINT NULL REFERENCES users_user(id) ON DELETE SET NULL
);
"""


CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS ai_conversation_user_created_idx
ON ai_conversation (user_id, created_at);
"""


DROP_INDEX_SQL = "DROP INDEX IF EXISTS ai_conversation_user_created_idx;"
DROP_CONVERSATION_TABLE_SQL = "DROP TABLE IF EXISTS ai_conversation;"
DROP_TEMPLATE_TABLE_SQL = "DROP TABLE IF EXISTS ai_conversationtemplate;"
DROP_AILOG_TABLE_SQL = "DROP TABLE IF EXISTS ai_ailog;"


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(CREATE_TEMPLATE_TABLE_SQL, reverse_sql=DROP_TEMPLATE_TABLE_SQL),
                migrations.RunSQL(CREATE_AILOG_TABLE_SQL, reverse_sql=DROP_AILOG_TABLE_SQL),
                migrations.RunSQL(CREATE_CONVERSATION_TABLE_SQL, reverse_sql=DROP_CONVERSATION_TABLE_SQL),
                migrations.RunSQL(CREATE_INDEX_SQL, reverse_sql=DROP_INDEX_SQL),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="ConversationTemplate",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=100)),
                        ("language", models.CharField(max_length=2)),
                        ("prompt", models.TextField()),
                    ],
                    options={"db_table": "ai_conversationtemplate"},
                ),
                migrations.CreateModel(
                    name="AILog",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("model", models.CharField(max_length=50)),
                        ("prompt_hash", models.CharField(blank=True, max_length=64)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "user",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL,
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={"db_table": "ai_ailog"},
                ),
                migrations.CreateModel(
                    name="Conversation",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("module", models.CharField(blank=True, max_length=32)),
                        (
                            "plan_tier",
                            models.CharField(
                                choices=[
                                    ("free", "Free"),
                                    ("trial", "Trial"),
                                    ("basic", "Basic"),
                                    ("premium", "Premium"),
                                    ("vip", "VIP"),
                                ],
                                default="free",
                                max_length=10,
                            ),
                        ),
                        ("user_message", models.TextField()),
                        ("ai_response", models.TextField()),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "user",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL,
                                related_name="conversations",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "db_table": "ai_conversation",
                        "ordering": ["-created_at"],
                    },
                ),
                migrations.AddIndex(
                    model_name="conversation",
                    index=models.Index(fields=["user", "created_at"], name="ai_conversation_user_created_idx"),
                ),
            ],
        ),
    ]