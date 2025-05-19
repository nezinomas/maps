from django.apps import AppConfig


class MapsConfig(AppConfig):
    name = "project.maps"

    def ready(self):
        from .signals import create_points_file_for_new_trip, delete_points_file
