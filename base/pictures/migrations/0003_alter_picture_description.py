# Generated by Django 3.2.7 on 2021-09-14 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pictures', '0002_picture_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='description',
            field=models.TextField(blank=True, max_length=3000),
        ),
    ]
