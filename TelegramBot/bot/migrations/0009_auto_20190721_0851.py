# Generated by Django 2.2.3 on 2019-07-21 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_auto_20190721_0848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='category',
        ),
        migrations.RemoveField(
            model_name='user',
            name='content',
        ),
    ]
