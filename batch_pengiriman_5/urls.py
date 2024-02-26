from django.urls import path
from . import views

app_name = 'batch_pengiriman_5'

urlpatterns = [
    path('', views.land, name = 'land'),
    path('showwares/', views.trig5forshow, name = 'showwares'),
    path('createwares/', views.trig5, name = 'createwares'),
    path('createfaskes/', views.trig5fas, name = 'createfaskes'),
    path('showfask/', views.trig5fasshow, name = 'showfaskes'),
    path('updatewares/<kode>/', views.updatewares, name = 'updatewares'),
    path('updatefask/<kode>/', views.updatefask, name = 'updatefask'),
]