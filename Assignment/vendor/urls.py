from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('vendors/login/', views.VendorLoginView.as_view(), name='vendor-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('vendors/', views.VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('vendors/<int:id>/', views.VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-retrieve-update-destroy'),
    path('vendors/<int:pk>/performance/', views.VendorPerformance.as_view(), name='vendor-performance'),
    path('purchase_orders/', views.PurchaseOrderListCreateAPIView.as_view(), name='purchase-orders-list-create'),
    path('purchase_orders/<int:pk>/', views.PurchaseOrderRetrieveUpdateDestroyAPIView.as_view(), name='purchase-orders-retrieve-update-destroy'),
    path('purchase_orders/<int:pk>/acknowledge', views.AcknowledgePurchaseOrder.as_view(), name='acknowledge_purchase_order'),
]


# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

# urlpatterns = [
#     ...
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     ...
# ]