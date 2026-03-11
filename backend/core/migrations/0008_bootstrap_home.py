from django.db import migrations


def bootstrap_home_placeholder(apps, schema_editor):
    # Keep this migration as a safe placeholder for historical continuity.
    return


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_content_setup"),
    ]

    operations = [
        migrations.RunPython(bootstrap_home_placeholder, reverse_code=noop),
    ]
