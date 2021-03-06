# Generated by Django 2.1.2 on 2018-10-21 15:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_webpage_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='webpage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webpage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
