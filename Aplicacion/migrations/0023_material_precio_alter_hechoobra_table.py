# Generated by Django 4.2.4 on 2024-06-19 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0022_presupuesto_fecha_asignacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='precio',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name='hechoobra',
            table='hecho_obra',
        ),
    ]
