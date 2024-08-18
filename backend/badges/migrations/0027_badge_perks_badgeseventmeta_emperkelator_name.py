# Generated by Django 5.0.7 on 2024-07-29 06:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("badges", "0026_remove_badgeseventmeta_badge_layout"),
    ]

    operations = [
        migrations.AddField(
            model_name="badge",
            name="perks",
            field=models.JSONField(
                blank=True, default=dict, help_text="Perks for the holder of this badge", verbose_name="Perks"
            ),
        ),
        migrations.AddField(
            model_name="badgeseventmeta",
            name="emperkelator_name",
            field=models.CharField(
                choices=[("noop", "Noop (no perks)"), ("tracon2024", "Tracon (2024)")],
                default="noop",
                help_text="The emperkelator defines the perks of a volunteer in the event based on their involvement with the event.",
                max_length=63,
                verbose_name="Emperkelator",
            ),
        ),
    ]