# Generated by Django 3.2.12 on 2023-02-11 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bourse', '0009_alter_page_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='add_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date Added'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='bourse.item'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='bourse.order'),
        ),
    ]
