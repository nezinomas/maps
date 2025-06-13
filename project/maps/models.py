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

    def _generate_unique_slug(self):
        """Generate a unique slug based on the title."""
        base_slug = slugify(self.title)

        # Check if slug exists for other instances (excluding self)
        slug_filter = Trip.objects.filter(slug=base_slug)
        if self.pk:
            slug_filter = slug_filter.exclude(pk=self.pk)

        # If slug doesn't exist, return it
        if not slug_filter.exists():
            return base_slug

        # Append numeric suffix for uniqueness
        suffix = 1
        while Trip.objects.filter(slug=f"{base_slug}-{suffix}").exists():
            suffix += 1
        return f"{base_slug}-{suffix}"

    def save(self, *args, **kwargs):
        # Check if new instance or title changed
        is_new = not self.pk
        title_changed = (
            False if is_new else Trip.objects.get(pk=self.pk).title != self.title
        )

        # Update slug only if new instance or title changed
        if is_new or title_changed:
            self.slug = self._generate_unique_slug()

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
