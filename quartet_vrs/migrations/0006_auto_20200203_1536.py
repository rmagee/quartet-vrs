# Generated by Django 2.2.6 on 2020-02-03 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quartet_vrs', '0005_auto_20200203_1514'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestlog',
            name='method',
        ),
        migrations.AddField(
            model_name='requestlog',
            name='success',
            field=models.BooleanField(default=False, help_text='True if request resulted in a verification or a returned Requestor GLN, False if not.', verbose_name='Success'),
        ),

    ]
