# Generated by Django 4.2.4 on 2023-09-14 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0008_presupuesto_anticipo_presupuesto_monto_anticipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='obra',
            name='plazo',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
