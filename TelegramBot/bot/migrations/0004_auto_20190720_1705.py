# Generated by Django 2.2.1 on 2019-07-20 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20190720_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='category',
            field=models.ManyToManyField(blank=True, null=True, related_name='users_catgory', to='bot.Category'),
        ),
        migrations.AlterField(
            model_name='user',
            name='content',
            field=models.ManyToManyField(blank=True, null=True, related_name='users_content', to='bot.Content'),
        ),
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='bot.Country'),
        ),
    ]
