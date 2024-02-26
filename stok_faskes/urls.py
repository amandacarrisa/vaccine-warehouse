from django.urls import path
from . import views

app_name = 'stok_faskes'

urlpatterns = [
    path('create/', views.getSF, name = 'getSF'),
    path('create/post/', views.createSF, name = 'createSF'),
    path('read/', views.read, name = 'read'),
    path('update/<str:id_faskes>/<str:id_item>/', views.getUpdate, name="getUpdate"),
    path('update/<str:id_faskes>/<str:id_item>/post/', views.postUpdate, name="postUpdate"),
    path('delete/<str:id_faskes>/<str:id_item>/', views.delete, name="delete")
]