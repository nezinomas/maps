from django.db import models
from django.utils.text import slugify


class Trip(models.Model):
    title = models.CharField(
        max_length = 254
    )
    slug = models.SlugField(editable=False)
    description = models.TextField(
        blank=True,
        null=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    blog = models.URLField(
        blank=True,
        null=True,
    )
    blog_category = models.CharField(
        blank=True,
        null=True,
        max_length = 20,
    )


    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Track(models.Model):
    title = models.CharField(
        max_length = 254
    )
    date = models.DateTimeField()
    activity_type = models.CharField(
        max_length = 30,
    )

    trip = models.ForeignKey(
        Trip,
        related_name = 'tracks',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['date',]

    def __str__(self):
        return str(self.title)



class Point(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(
        null=True,
        blank=True
    )
    distance_meters = models.FloatField(
        null=True,
        blank=True,
    )
    cadence = models.IntegerField(
        null=True,
        blank=True
    )
    heart_rate = models.IntegerField(
        null=True,
        blank=True
    )
    temperature = models.FloatField(
        null=True,
        blank=True
    )
    datetime = models.DateTimeField()

    track = models.ForeignKey(
        Track,
        related_name='points',
        on_delete=models.CASCADE
    )


class Statistic(models.Model):
    total_km = models.FloatField()
    total_time_seconds = models.FloatField()
    max_speed = models.FloatField()
    calories = models.IntegerField(
        null=True,
        blank=True
    )
    avg_speed = models.FloatField(
        null=True,
        blank=True
    )
    avg_cadence = models.FloatField(
        null=True,
        blank=True
    )
    avg_heart = models.FloatField(
        null=True,
        blank=True
    )
    max_heart = models.FloatField(
        null=True,
        blank=True
    )
    avg_temperature = models.FloatField(
        null=True,
        blank=True
    )
    min_altitude = models.FloatField(
        null=True,
        blank=True
    )
    max_altitude = models.FloatField(
        null=True,
        blank=True
    )
    ascend = models.FloatField(
        null=True,
        blank=True
    )
    descend = models.FloatField(
        null=True,
        blank=True
    )

    track = models.OneToOneField(
        Track,
        related_name = 'stats',
        on_delete = models.CASCADE
    )


class Note(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    note = models.TextField(
        blank=True,
        null=True,
    )

    track = models.ForeignKey(
        Track,
        related_name = 'notes',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
