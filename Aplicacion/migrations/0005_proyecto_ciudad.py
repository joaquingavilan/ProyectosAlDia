# Generated by Django 4.2.4 on 2023-09-05 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0004_remove_cliente_nombre_contacto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='ciudad',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]
