# Generated by Django 5.0.4 on 2024-04-10 07:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("program_v2", "0010_programv2eventmeta_importer_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="favorited_by",
            field=models.ManyToManyField(blank=True, related_name="favorite_programs", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="programv2eventmeta",
            name="location_dimension",
            field=models.ForeignKey(
                blank=True,
                help_text="If set, this dimension will be used as the location dimension for the event. This is used at least by the calendar export for the iCalendar location field.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="location_dimension_for_event_meta",
                to="program_v2.dimension",
            ),
        ),
    ]