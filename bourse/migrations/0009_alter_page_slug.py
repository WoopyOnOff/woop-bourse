# Generated by Django 3.2.12 on 2022-04-28 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bourse', '0008_page_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]