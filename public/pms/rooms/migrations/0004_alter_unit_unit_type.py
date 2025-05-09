# Generated by Django 5.1.6 on 2025-03-24 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='unit_type',
            field=models.CharField(choices=[('BASIC_CABIN', 'Cabaña básica'), ('DELUXE_CABIN', 'Cabaña deluxe'), ('SINGLE_BED', 'Cama individual'), ('BUNK_BED', 'Litera'), ('QUEEN_BED', 'Cama queen'), ('KING_BED', 'Cama king'), ('GLAMPING_TENT', 'Tienda de glamping'), ('GLAMPING_POD', 'Cápsula de glamping'), ('TENT_SPACE', 'Espacio para tienda'), ('CAMPER_SPACE', 'Espacio para caravana'), ('HAMMOCK', 'Hamaca'), ('PRIVATE_ROOM', 'Habitación privada'), ('PRIVATE_SUITE', 'Suite privada'), ('SPECIAL_BED', 'Cama especial'), ('SPECIAL_ROOM', 'Habitación especial'), ('STUDIO', 'Estudio'), ('ONE_BEDROOM', 'Una habitación'), ('TWO_BEDROOM', 'Dos habitaciones'), ('ENTIRE_APARTMENT', 'Apartamento completo'), ('ENTIRE_VILLA', 'Villa completa'), ('AIRSTREAM', 'Airstream'), ('TEEPEE', 'Tipi'), ('YURT', 'Yurta'), ('TREEHOUSE', 'Casa en el árbol'), ('OTHER', 'Otra unidad')], default='SINGLE_BED', max_length=32, verbose_name='Tipo de cama'),
        ),
    ]
