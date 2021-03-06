# Generated by Django 2.2.3 on 2019-07-21 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_auto_20190721_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='category',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_category', to='bot.Category'),
        ),
        migrations.AddField(
            model_name='user',
            name='content',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_content', to='bot.Content'),
        ),
    ]
