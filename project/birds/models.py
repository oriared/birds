from datetime import date, datetime
import uuid

from django.db import models


class RingedManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_ringed=True)
        return queryset


class Bird(models.Model):
    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский')
    )
    uuid = models.UUIDField('UUID идентификатор', default=uuid.uuid4, editable=False)
    slug = models.SlugField('slug')
    name = models.CharField('Имя', max_length=255)
    specie = models.ForeignKey('Specie', verbose_name='Вид', related_name='birds', on_delete=models.PROTECT)
    birth = models.DateField('Дата рождения', editable=False)
    gender = models.CharField('Пол', choices=GENDER_CHOICES, max_length=2)
    is_ringed = models.BooleanField('Окольцована', default=False)
    last_seen = models.DateTimeField('Время последнего наблюдения', default=datetime.now())
    description = models.TextField('Описание', max_length=3000, blank=True)
    eggs_number = models.PositiveSmallIntegerField('Снесённых яиц', default=0)
    photo = models.ImageField('Фото', upload_to='images/photos', default='images/no_photo.jpg')
    nests = models.ManyToManyField('Nest', through='BirdNest', verbose_name='Гнёзда', related_name='birds')
    current_nest = models.ForeignKey('Nest', verbose_name='Гнездо проживания', null=True,
                                     related_name='current_birds', on_delete=models.SET_NULL)
    birth_nest = models.ForeignKey('Nest', verbose_name='Гнездо рождения', null=True,
                                     related_name='birth_birds', on_delete=models.SET_NULL)
    parent = models.ForeignKey('Bird', verbose_name='Родитель', null=True,
                               related_name='childs', on_delete=models.PROTECT)

    objects = models.Manager()
    ringed = RingedManager()

    class Meta:
        verbose_name = 'Птица'
        verbose_name_plural = 'Птицы'
        ordering = ('birth',)
        get_latest_by = ('birth', '-last_seen')
        constraints = [
            models.CheckConstraint(check=models.Q(birth__lte=date.today()), name='birth_lte_today'),
        ]

    def __str__(self) -> str:
        return f'{self.specie} {self.name}'


class Nest(models.Model):
    name = models.CharField('Название', max_length=255, blank=True)
    uuid = models.UUIDField('UUID идентификатор', default=uuid.uuid4, editable=False)
    lon = models.FloatField('Долгота')
    lat = models.FloatField('Широта')
    description = models.TextField('Описание', max_length=3000, blank=True)
    created = models.DateField('Дата постройки')
    created_by = models.ForeignKey(Bird, verbose_name='Кто свил', null=True, related_name='created_nests',
                                   on_delete=models.PROTECT)
    translation_url = models.URLField('Трансляция гнезда', blank=True)

    class Meta:
        verbose_name = 'Гнездо'
        verbose_name_plural = 'Гнёзда'
        ordering = ('-created',)
        constraints = [
            models.CheckConstraint(check=models.Q(lon__lte=90) & models.Q(lat__lte=90), name='lon_lat_90_deg'),
        ]

    def __str__(self) -> str:
        if self.name:
            return f'{self.id} ("{self.name}")'
        return self.id


class BirdNest(models.Model):
    bird = models.ForeignKey(Bird, verbose_name='Птица', related_name='bird_nests', on_delete=models.CASCADE)
    nest = models.ForeignKey(Nest, verbose_name='Гнездо', related_name='nest_birds', on_delete=models.CASCADE)
    date_check_inn = models.DateField(verbose_name='Дата заселения')
    date_leaving = models.DateField(verbose_name='Дата покидания', null=True)
    eggs = models.PositiveSmallIntegerField(verbose_name='Кол-во снесённых яиц', default=0)

    class Meta:
        verbose_name = 'Гнездо птицы'
        verbose_name_plural = 'Гнёзда птиц'
        ordering = ('-date_check_inn',)

    def __str__(self) -> str:
        return f'{self.bird}: {self.nest}'

    def save(self, *args, **kwargs):
        creating = bool(self.id)
        old_leaving = bool(self.date_leaving)

        super().save(*args, **kwargs)

        if not creating:
            self.bird.current_nest = self.nest
            self.bird.save()
        elif not old_leaving and self.date_leaving:
            self.bird.current_nest = None
            self.bird.save()


class Specie(models.Model):
    name = models.CharField('Название', max_length=255)
    is_endemic = models.BooleanField('Эндемик', default=False)
    is_endangered = models.BooleanField('Исчезающий вид', default=False)

    class Meta:
        verbose_name = 'Вид'
        verbose_name_plural = 'Виды'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name
