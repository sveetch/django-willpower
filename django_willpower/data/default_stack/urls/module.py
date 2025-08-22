from django.urls import path

from ..views import (
    {{ model_inventory.name }}IndexView,
    {{ model_inventory.name }}DetailView,
)


urlpatterns = [
    path(
        "",
        {{ model_inventory.name }}IndexView.as_view(),
        name="{{ model_inventory.module_name }}-index"
    ),
    path(
        "<int:{{ model_inventory.module_name }}_pk>/",
        {{ model_inventory.name }}DetailView.as_view(),
        name="{{ model_inventory.module_name }}-detail"
    ),
]

