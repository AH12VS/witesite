# Generated by Django 4.2.3 on 2023-11-02 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_usermodel_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermodel",
            name="image_prof",
            field=models.ImageField(blank=True, null=True, upload_to="images/users/"),
        ),
    ]
