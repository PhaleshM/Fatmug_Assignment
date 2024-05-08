from django.urls import path
from . import views

urlpatterns = [
    path('vendors/', views.VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('vendors/<int:pk>/', views.VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-retrieve-update-destroy'),
    path('vendors/<int:pk>/performance/', views.VendorPerformance.as_view(), name='vendor-performance'),
    path('purchase_orders/', views.PurchaseOrderListCreateAPIView.as_view(), name='purchase-orders-list-create'),
    path('purchase_orders/<int:pk>/', views.PurchaseOrderRetrieveUpdateDestroyAPIView.as_view(), name='purchase-orders-retrieve-update-destroy'),
    path('purchase_orders/<int:pk>/acknowledge', views.AcknowledgePurchaseOrder.as_view(), name='acknowledge_purchase_order'),
]