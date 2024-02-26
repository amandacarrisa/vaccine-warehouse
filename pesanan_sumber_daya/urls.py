from django.urls import path
from . import views

app_name = 'pesanan_sumber_daya'

urlpatterns = [
    path('create/', views.getPSD, name='getPSD'),
    path('create/post/', views.createPSD, name='createPSD'),
    path('read/', views.read, name='read'),
    path('detail/<str:id>/', views.detail, name='detail'),
    path('update/<str:id>/', views.getUpdate, name='getUpdate'),
    path('update/<str:id>/post/', views.postUpdate, name='postUpdate'),
    path('delete/<str:id>/', views.delete, name='delete'),
    path('status/create/<str:id>/', views.postStatus, name='postStatus'),
    path('status/<str:id>/', views.getStatus, name='getStatus'),
]