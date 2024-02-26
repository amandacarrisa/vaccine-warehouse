from django.urls import path
from . import views

app_name = "crulokasi"

urlpatterns = [
    path('daftarlokasi/', views.daftar_lokasi_view, name='daftarlokasi'),
    path('formcreatelokasi/', views.form_buat_lokasi_view, name='formcreatelokasi'),
    path('createlokasi/', views.buat_lokasi, name='buatlokasi'),
    path('updatelokasi/<id>', views.update_lokasi, name='updatelokasi'),
    # path('deletelokasi/<id>', views.delete_lokasi, name='deletelokasi<id>'),
]