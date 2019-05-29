from django.urls import path

from . import views_api

urlpatterns = [
    path('legisladores', views_api.legisladores),
    path('legisladores/<int:id_legislador>', views_api.legisladores_by_id),
    path('legisladores/index', views_api.legisladores_index),
]