from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_bootstrap_home"),
    ]

    operations = [
        migrations.RunSQL(sql="SELECT 1", reverse_sql="SELECT 1"),
    ]
