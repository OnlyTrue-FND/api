# Generated by Django 2.1.2 on 2018-10-11 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_webpage_scores_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='webpage',
            name='category',
            field=models.CharField(choices=[('SCIENCE', 'science'), ('POLITICS', 'politics'), ('NEWS', 'news'), ('UNKNOWN', 'unknown')], max_length=20, null=True),
        ),
    ]
