# Generated by Django 2.2.3 on 2019-07-24 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0014_auto_20190724_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='channel_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='channel_link',
            new_name='link',
        ),
    ]
