# Generated by Django 3.2.12 on 2022-04-28 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourse', '0007_alter_event_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='slug',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
