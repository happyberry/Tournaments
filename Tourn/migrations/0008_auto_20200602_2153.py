# Generated by Django 3.0.6 on 2020-06-02 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tourn', '0007_auto_20200530_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logo',
            name='image',
        ),
        migrations.AddField(
            model_name='logo',
            name='image_src',
            field=models.CharField(default='a', max_length=200),
            preserve_default=False,
        ),
    ]
