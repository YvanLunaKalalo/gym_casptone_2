# Generated by Django 4.2.15 on 2025-02-09 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0012_alter_userprofile_preferred_reps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='preferred_reps',
            field=models.IntegerField(default=1),
        ),
    ]
