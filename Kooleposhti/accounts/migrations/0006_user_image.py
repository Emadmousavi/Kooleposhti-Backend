# Generated by Django 3.2.8 on 2021-11-11 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_phone_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to='images/', verbose_name='profile image'),
        ),
    ]