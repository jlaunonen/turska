# Generated by Django 4.2 on 2023-04-21 11:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0035_ticketseventmeta_max_count_per_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticketseventmeta",
            name="max_count_per_product",
            field=models.SmallIntegerField(blank=True, default=99),
        ),
    ]