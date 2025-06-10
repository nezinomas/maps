from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.contrib.gis.db import models
from django.urls import reverse_lazy
from django.utils.text import slugify


class Trip(models.Model):
    title = models.CharField(max_length=254)
    slug = models.SlugField(editable=False)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    blog_category = models.SmallIntegerField()

    class Meta:
        ordering = [
            "-start_date",
        ]

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        if qs := Trip.objects.filter(slug__contains=self.slug).count():
            self.slug = f"{self.slug}-{qs + 1}"

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy("maps:update_trip", kwargs={"pk": self.pk})


class CommentQty(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    post_id = models.IntegerField(
        null=True,
        blank=True,
    )
    qty = models.IntegerField(default=0)
    post_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    trip = models.ForeignKey(
        Trip,
        related_name="comment_qty",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (("post_id", "trip"),)

    def __str__(self):
        return str(self.post_id)


class Track(models.Model):
    title = models.CharField(max_length=254)
    date = models.DateTimeField()
    activity_type = models.CharField(
        max_length=30,
    )
    path = models.LineStringField(srid=4326, null=True, blank=True)

    trip = models.ForeignKey(
        Trip,
        related_name="tracks",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = [
            "-date",
        ]

    def __str__(self):
        return self.title


class Statistic(models.Model):
    total_km = models.FloatField()
    total_time_seconds = models.FloatField()
    avg_speed = models.FloatField(null=True, blank=True)
    max_speed = models.FloatField(null=True, blank=True)
    ascent = models.FloatField(null=True, blank=True)
    descent = models.FloatField(null=True, blank=True)
    min_altitude = models.FloatField(null=True, blank=True)
    max_altitude = models.FloatField(null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    avg_cadence = models.FloatField(null=True, blank=True)
    avg_heart = models.FloatField(null=True, blank=True)
    max_heart = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)

    track = models.OneToOneField(Track, related_name="stats", on_delete=models.CASCADE)
