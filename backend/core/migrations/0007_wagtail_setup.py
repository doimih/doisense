from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_userwellbeingcheckin"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="WagtailHomePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("intro", wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                "verbose_name": "Wagtail Home Page",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="AIConfig",
            fields=[],
            options={
                "verbose_name": "AI Configuration",
                "verbose_name_plural": "AI Configuration",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.systemconfig",),
        ),
        migrations.CreateModel(
            name="OAuthConfig",
            fields=[],
            options={
                "verbose_name": "OAuth Configuration",
                "verbose_name_plural": "OAuth Configuration",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.systemconfig",),
        ),
        migrations.CreateModel(
            name="StripeConfig",
            fields=[],
            options={
                "verbose_name": "Stripe Configuration",
                "verbose_name_plural": "Stripe Configuration",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("core.systemconfig",),
        ),
    ]
