# Generated by Django 3.0.2 on 2020-01-29 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('quartet_vrs', '0002_delete_vrsgs1locations'),
    ]

    operations = [
        migrations.CreateModel(
            name='GTINMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gtin', models.CharField(db_index=True, help_text='A GTIN that represents a Trade Item', max_length=14, unique=True, verbose_name='GTIN')),
                ('path', models.CharField(help_text='The Sub Path of the VRS Service. For Example: If the URL path is http://vrs.qu4rtet.io/vrs, then the path is: /vrs', max_length=256, null=True, verbose_name='Path')),
                ('host', models.CharField(db_index=True, help_text='The Hostname of the VRS Router. If the URL is https://vrs.qu4rtet.io, then the host is: vrs.qu4rtet.io.', max_length=256, unique=True, verbose_name='Hostname')),
                ('gs1_compliant', models.BooleanField(default=True, help_text='True if the VRS Router is compliant with GS1.', verbose_name='GS1 Compliant')),
                ('use_ssl', models.BooleanField(default=True, help_text='True if the VRS Router should use SSL when connecting to the host and path.', verbose_name='Use SSL')),
            ],
            options={
                'db_table': 'quartet_vrs_gtin_map',
            },
        ),
    ]