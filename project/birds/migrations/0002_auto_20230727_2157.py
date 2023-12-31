# Generated by Django 4.2.3 on 2023-07-27 16:57
import datetime

from django.db import migrations


def set_data(apps, schema_editor):
    Nest = apps.get_model('birds', 'Nest')
    nest1 = Nest.objects.create(
        name='Воронье',
        lon=54.43543,
        lat=43.23455,
        description='Гнездо преимущественно из веток сосны, утеплено мхом и монтажной пеной',
        created=datetime.date(2021, 8, 23),
        translation_url='',
    )

    Specie = apps.get_model('birds', 'Specie')
    specie = Specie.objects.create(
        name='Ворона',
    )

    Bird = apps.get_model('birds', 'Bird')
    Bird.objects.create(
        slug='Igor',
        name='Игорь',
        specie=specie,
        birth=datetime.date(2022, 5, 25),
        gender='M',
        last_seen=datetime.datetime(2023, 6, 30, 12, 30),
        current_nest=nest1,
        birth_nest=nest1,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('birds', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_data),
    ]
