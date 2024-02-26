from django.urls import path
from . import views

app_name = "trigger4"

urlpatterns = [
    path('formKendaraan/', views.tambahKendaraan, name='tambahKendaraan'),
    path('createKendaraan/', views.form_tambah_kendaraan, name='tambahinKendaraan'),
    path('updatekendaraan/<id>', views.update_kendaraan, name='updateKendaraan'),
    path('listKendaraan/', views.list_kendaraan, name='listKendaraan'),
    path('deletekendaraan/<id>', views.delete_kendaraan, name='deleteKendaraan<id>'),
]
