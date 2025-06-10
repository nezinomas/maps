import json

from django.http import HttpResponse
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event
from vanilla import CreateView, DeleteView, UpdateView


def rendered_content(request, view_class, **kwargs):
    # update request kwargs
    request.resolver_match.kwargs.update({**kwargs})

    return view_class.as_view()(request, **kwargs).rendered_content


def http_htmx_response(hx_trigger_name=None, status_code=204):
    headers = {}
    if hx_trigger_name:
        headers = {
            "HX-Trigger": json.dumps({hx_trigger_name: None}),
        }

    return HttpResponse(
        status=status_code,
        headers=headers,
    )


class CreateUpdateMixin:
    hx_trigger_django = "reload"

    def get_hx_trigger_django(self):
        return self.hx_trigger_django

    def form_valid(self, form, **kwargs):
        response = super().form_valid(form)
        if self.hx_trigger_django:
            response.status_code = 204

        trigger_client_event(response=response, name=self.hx_trigger_django, params={})

        return response


class DeleteMixin:
    hx_trigger_django = "reload"
    hx_redirect = None

    def get_hx_trigger_django(self):
        return self.hx_trigger_django

    def get_hx_redirect(self):
        return self.hx_redirect

    def post(self, *args, **kwargs):
        if not self.get_object():
            return HttpResponse()

        super().post(*args, **kwargs)

        if hx_redirect := self.get_hx_redirect():
            return HttpResponseClientRedirect(hx_redirect)

        return http_htmx_response(self.get_hx_trigger_django())


class CreateViewMixin(CreateUpdateMixin, CreateView):
    pass


class UpdateViewMixin(CreateUpdateMixin, UpdateView):
    pass


class DeleteViewMixin(DeleteMixin, DeleteView):
    pass
