# Generated by Django 4.2.15 on 2025-01-31 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0009_remove_userprogress_day_1_progress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='week_number',
            field=models.IntegerField(default=1),
        ),
    ]
