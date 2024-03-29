# Generated by Django 3.0.4 on 2020-03-10 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=200)),
                ('event_location', models.CharField(max_length=200)),
                ('event_date', models.DateTimeField(verbose_name='Event Date')),
                ('status', models.IntegerField(default=2, verbose_name='Event Status')),
                ('comments', models.TextField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField(verbose_name='Sold Price')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('is_sold', models.BooleanField(default=False, verbose_name='Item Sold')),
                ('sold_date', models.DateTimeField(verbose_name='Date Sold')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('is_validated', models.BooleanField(default=False, verbose_name='Order Validated')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourse.Event')),
            ],
        ),
        migrations.CreateModel(
            name='UserList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_status', models.IntegerField(default=1, verbose_name='List Status')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('validated_date', models.DateTimeField(verbose_name='Date Validated')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourse.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourse.Item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourse.Order')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bourse.UserList'),
        ),
    ]
