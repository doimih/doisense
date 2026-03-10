from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


STREAM_BLOCKS = [
    (
        "heading",
        wagtail.blocks.CharBlock(form_classname="title", icon="title"),
    ),
    (
        "paragraph",
        wagtail.blocks.RichTextBlock(icon="doc-full"),
    ),
    (
        "cta",
        wagtail.blocks.StructBlock(
            [
                ("title", wagtail.blocks.CharBlock(required=True)),
                ("text", wagtail.blocks.TextBlock(required=False)),
                ("button_text", wagtail.blocks.CharBlock(required=False)),
                ("button_url", wagtail.blocks.URLBlock(required=False)),
            ],
            icon="placeholder",
        ),
    ),
    (
        "faq",
        wagtail.blocks.StructBlock(
            [
                ("question", wagtail.blocks.CharBlock(required=True)),
                ("answer", wagtail.blocks.RichTextBlock(required=True)),
            ],
            icon="help",
        ),
    ),
]


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_wagtail_bootstrap_home"),
    ]

    operations = [
        migrations.CreateModel(
            name="WagtailAboutPage",
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
                ("subtitle", models.CharField(blank=True, max_length=255)),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                (
                    "content",
                    wagtail.fields.StreamField(
                        STREAM_BLOCKS,
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("seo_title_override", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Wagtail About Page",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="WagtailContactPage",
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
                ("subtitle", models.CharField(blank=True, max_length=255)),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                (
                    "content",
                    wagtail.fields.StreamField(
                        STREAM_BLOCKS,
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("seo_title_override", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Wagtail Contact Page",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="WagtailFeaturesPage",
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
                ("subtitle", models.CharField(blank=True, max_length=255)),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                (
                    "content",
                    wagtail.fields.StreamField(
                        STREAM_BLOCKS,
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("seo_title_override", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Wagtail Features Page",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="WagtailPricingPage",
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
                ("subtitle", models.CharField(blank=True, max_length=255)),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                (
                    "content",
                    wagtail.fields.StreamField(
                        STREAM_BLOCKS,
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("seo_title_override", models.CharField(blank=True, max_length=255)),
                ("seo_description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Wagtail Pricing Page",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.AddField(
            model_name="wagtailhomepage",
            name="content",
            field=wagtail.fields.StreamField(
                STREAM_BLOCKS,
                blank=True,
                default=list,
                use_json_field=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wagtailhomepage",
            name="seo_description",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wagtailhomepage",
            name="seo_title_override",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wagtailhomepage",
            name="subtitle",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
    ]
