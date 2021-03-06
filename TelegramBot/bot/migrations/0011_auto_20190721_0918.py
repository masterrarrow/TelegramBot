# Generated by Django 2.2.3 on 2019-07-21 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0010_auto_20190721_0854'),
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
        migrations.CreateModel(
            name='User_content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_content', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.Content')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.User')),
            ],
        ),
        migrations.CreateModel(
            name='User_category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.Category')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.User')),
            ],
        ),
    ]
