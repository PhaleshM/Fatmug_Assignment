# Generated by Django 4.2.9 on 2024-05-08 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vendor", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="vendor", name="groups",),
        migrations.RemoveField(model_name="vendor", name="is_staff",),
        migrations.RemoveField(model_name="vendor", name="is_superuser",),
        migrations.RemoveField(model_name="vendor", name="user_permissions",),
    ]
