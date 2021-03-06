# Generated by Django 2.2.1 on 2019-07-21 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_auto_20190721_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='category',
            field=models.ManyToManyField(blank=True, default='', null=True, to='bot.Category'),
        ),
        migrations.AlterField(
            model_name='user',
            name='content',
            field=models.ManyToManyField(blank=True, default='', null=True, to='bot.Content'),
        ),
    ]
