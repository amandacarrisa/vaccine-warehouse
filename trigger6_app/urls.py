from django.urls import path
from . import views

app_name = 'trigger6_app'

urlpatterns = [
    path('', views.tes, name = 'tes'),
    path('create-stock-warehouse', views.create_stock_warehouse, name = 'create_stock_warehouse'),
    path('read-stock-warehouse', views.read_stock_warehouse, name='read_stock_warehouse'),
    path('update-stock-warehouse', views.update_stock_warehouse, name='update_stock_warehouse'),
    path('update-stock-warehouse-2', views.update_stock_warehouse_2, name='update_stock_warehouse_2'),
    path('delete-stock-warehouse', views.delete_stock_warehouse, name='delete_stock_warehouse'),
    path('batch-pengiriman', views.batch_pengiriman, name='batch_pengiriman'),
    path('form-batch-pengiriman', views.form_batch_pengiriman, name='form_batch_pengiriman'),
    path('create-batch-pengiriman', views.create_batch_pengiriman, name='create_batch_pengiriman'),
    path('read-batch-pengiriman', views.read_batch_pengiriman, name='read_batch_pengiriman'),
    path('update-riwayat-status', views.update_riwayat_status, name='update_riwayat_status'),
    path('update-riwayat-status-2', views.update_riwayat_status_2, name='update_riwayat_status_2'),
    path('read-riwayat-status', views.read_riwayat_status, name='read_riwayat_status'),
]