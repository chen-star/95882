# Generated by Django 2.1.3 on 2018-12-01 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coolcars', '0005_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='favorite',
            field=models.IntegerField(default=0),
        ),
    ]
