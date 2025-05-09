# Generated by Django 5.1.6 on 2025-03-24 03:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_alter_room_room_type_alter_unit_unit_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='El nombre del plan debe ser único.', max_length=128, unique=True, verbose_name='Nombre')),
                ('start_date', models.DateField(verbose_name='Fecha inicio')),
                ('end_date', models.DateField(verbose_name='Fecha fin')),
                ('description', models.TextField(blank=True, help_text='Descripción del plan (incluye, no incluye, etc.)', verbose_name='Descripción')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Precio')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='rooms.room', verbose_name='Habitación')),
            ],
            options={
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Planes',
                'ordering': ['name'],
            },
        ),
    ]
