# Generated by Django 4.2.3 on 2023-10-07 19:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_usermodel_user_uniqe_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usermodel",
            name="user_uniqe_id",
        ),
        migrations.AddField(
            model_name="usermodel",
            name="user_unique_id",
            field=models.SlugField(default=django.utils.timezone.now, unique=True),
            preserve_default=False,
        ),
    ]