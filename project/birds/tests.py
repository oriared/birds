from datetime import date

from django.db.models import Count, Avg
from django.test import TestCase

from birds import models


class TestQuery(TestCase):
    def setUp(self) -> None:
        self.specie_1 = models.Specie.objects.create(
            name='Ворона'
        )
        self.nest_1 = models.Nest.objects.create(
            name='Воронье',
            lon=55.3456,
            lat=50.2434,
            created=date.today()
        )
        self.nest_2 = models.Nest.objects.create(
            name='Воронье',
            lon=51.7896,
            lat=53.1230,
            created=date.today()
        )
        self.bird_1 = models.Bird.objects.create(
            slug='nastya',
            name='Настя',
            specie=self.specie_1,
            birth=date(2022, 6, 10),
            gender='F'
        )
        self.bird_2 = models.Bird.objects.create(
            slug='igor',
            name='Игорь',
            specie=self.specie_1,
            birth=date(2022, 5, 28),
            gender='M'
        )
        models.BirdNest.objects.create(
            bird=self.bird_1,
            nest=self.nest_1,
            date_check_inn=date.today()
        )
        models.BirdNest.objects.create(
            bird=self.bird_2,
            nest=self.nest_1,
            date_check_inn=date.today()
        )

    def test_managers(self):
        self.assertEqual(models.Bird.ringed.count(), 0)
        self.assertEqual(models.Bird.objects.count(), 2)

    def test_annotate(self):
        a = models.Bird.objects.values_list('name',).annotate(num_of_nests=Count('nests'))
        self.assertEqual(list(a), [('Игорь', 1), ('Настя', 1)])

    def test_aggregate(self):
        avlat = {'average_latitude': (self.nest_1.lat + self.nest_2.lat) / 2}
        self.assertEqual(models.Nest.objects.aggregate(average_latitude=Avg('lat')), avlat)
