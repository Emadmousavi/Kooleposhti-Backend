# Generated by Django 3.2.8 on 2021-11-20 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_course_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='room_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]