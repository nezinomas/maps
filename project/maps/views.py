from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls.base import reverse
from django_htmx.http import retarget
from vanilla import FormView, ListView, TemplateView

from . import forms, models
from .mixins.views import (
    CreateViewMixin,
    UpdateViewMixin,
    rendered_content,
)
from .utils import views_map, wp_comments_qty, wp_content, views_posts
from .utils.garmin_service import GarminService
from .utils.tracks_service import TracksService, TracksServiceData


class Trips(ListView):
    template_name = "maps/trips.html"
    model = models.Trip


class Map(TemplateView):
    template_name = "maps/map.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        context = views_map.create_context(trip)

        return super().get_context_data(*args, **kwargs) | context


class Posts(TemplateView):
    template_name = "maps/posts.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        offset = int(self.request.GET.get("offset", 0))
        context = views_posts.create_context(trip, offset)

        return super().get_context_data(*args, **kwargs) | context


class Comments(TemplateView):
    template_name = "maps/comments.html"

    def get_context_data(self, **kwargs):
        post_id = self.kwargs.get("post_id")
        link = f"comments?post={post_id}&_fields=author_name,date,content"
        context = {
            "comments": wp_content.get_content(link),
        }

        return super().get_context_data(**kwargs) | context


class Login(auth_views.LoginView):
    form_class = forms.CustomAuthForm
    template_name = "maps/login.html"
    redirect_authenticated_user = True


class Logout(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.user.is_authenticated:
            logout(request)
            return redirect(reverse("maps:trips"))

        return response


class Utils(LoginRequiredMixin, TemplateView):
    model = models.Trip
    template_name = "maps/utils.html"

    def get_context_data(self, **kwargs):
        context = {"trips": rendered_content(self.request, TripList)}

        return super().get_context_data(**kwargs) | context


class TripList(LoginRequiredMixin, ListView):
    model = models.Trip


class TripCreate(LoginRequiredMixin, CreateViewMixin):
    model = models.Trip
    form_class = forms.TripForm
    title = "Create Trip"

    def url(self):
        return reverse_lazy("maps:create_trip")


class TripUpdate(LoginRequiredMixin, UpdateViewMixin):
    model = models.Trip
    form_class = forms.TripForm
    success_url = reverse_lazy("maps:utils_index")
    title = "Update Trip"

    def url(self):
        return self.object.get_absolute_url() if self.object else None


class DownloadTcx(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": GarminService(trip).get_data()}

        return super().get_context_data(*args, **kwargs) | context


class GetTcxByDate(LoginRequiredMixin, FormView):
    form_class = forms.GetTcxByDateForm
    hx_trigger_django = "reload"
    template_name = "maps/download_tcx_form.html"
    success_url = reverse_lazy("maps:utils_index")

    def url(self):
        return reverse_lazy("maps:tcx_date", kwargs={"trip": self.kwargs.get("trip")})

    def form_valid(self, form, **kwargs):
        trip = trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        msg = GarminService(
            trip=trip,
            start_date=start_date,
            end_date=end_date,
        ).get_data()

        response = render(self.request, "maps/utils_messages.html", {"message": msg})
        return retarget(response, "#utils-messages")


class SaveNewTracks(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        data = TracksServiceData(trip)
        context = {"message": TracksService(data).create()}

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllTracks(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        models.Track.objects.filter(trip=trip).delete()
        models.Statistic.objects.filter(track__trip=trip).delete()

        data = TracksServiceData(trip)
        context = {"message": TracksService(data).create_or_update()}

        return super().get_context_data(*args, **kwargs) | context


class CommentQty(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        wp_comments_qty.push_comments_qty(trip)

        context = {"message": "Successfully synced with wordpress blog"}

        return super().get_context_data(*args, **kwargs) | context
