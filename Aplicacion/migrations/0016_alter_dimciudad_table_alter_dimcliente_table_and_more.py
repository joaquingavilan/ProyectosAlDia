# Generated by Django 4.2.4 on 2024-06-08 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion', '0015_alter_hechoestadoingeniero_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='dimciudad',
            table='dim_ciudad',
        ),
        migrations.AlterModelTable(
            name='dimcliente',
            table='dim_cliente',
        ),
        migrations.AlterModelTable(
            name='dimmaterial',
            table='dim_material',
        ),
        migrations.AlterModelTable(
            name='dimproveedor',
            table='dim_proveedor',
        ),
        migrations.AlterModelTable(
            name='dimproyecto',
            table='dim_proyecto',
        ),
        migrations.AlterModelTable(
            name='dimusuario',
            table='dim_usuario',
        ),
        migrations.AlterModelTable(
            name='hechocertificado',
            table='hecho_certificado',
        ),
        migrations.AlterModelTable(
            name='hechodevolucion',
            table='hecho_devolucion',
        ),
        migrations.AlterModelTable(
            name='hechomaterialpedido',
            table='hecho_materialpedido',
        ),
        migrations.AlterModelTable(
            name='hechopedido',
            table='hecho_pedido',
        ),
        migrations.AlterModelTable(
            name='hechopresupuesto',
            table='hecho_presupuesto',
        ),
    ]