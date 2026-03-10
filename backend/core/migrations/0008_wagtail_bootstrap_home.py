from django.db import migrations


def bootstrap_wagtail_home(apps, schema_editor):
    # Keep this migration as a safe placeholder. Initial page tree seeding is
    # handled through Wagtail defaults/admin to avoid historical model issues.
    return


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_wagtail_setup"),
    ]

    operations = [
        migrations.RunPython(bootstrap_wagtail_home, reverse_code=noop),
    ]
