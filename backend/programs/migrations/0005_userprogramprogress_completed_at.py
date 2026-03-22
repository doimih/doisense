from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0004_programs_phase2"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprogramprogress",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
