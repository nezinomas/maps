from django.contrib import admin

from . import models


class TrackAdmin(admin.ModelAdmin):
    pass


class TripAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Trip, TripAdmin)
admin.site.register(models.Track, TrackAdmin)
