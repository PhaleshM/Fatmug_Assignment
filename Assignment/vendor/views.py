from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Vendor,PurchaseOrder,HistoricalPerformance
from .serializers import VendorCreateSerializer,VendorRetrieveSerializer,PurchaseOrderCreateSerializer,PurchaseOrderRetrieveSerializer,PurchaseOrderUpdateSerializer,VendorPerformanceSerializer,VendorUpdateSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate



from rest_framework.permissions import BasePermission

class IsVendorOrReadOnly(BasePermission):
    """
    Custom permission to only allow vendors to edit their own purchase orders.
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Check if the user is the vendor of the purchase order.
        return obj.vendor == request.user

class VendorLoginView(APIView):
    def post(self, request):
        vendor_code = request.data.get('vendor_code')
        password = request.data.get('password')

        # Authenticate the vendor
        user = authenticate(vendor_code=vendor_code, password=password)

        if user:
            # Generate JWT token for the authenticated user
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class VendorListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Vendor.objects.all()
    serializer_class = VendorCreateSerializer 

    def perform_create(self, serializer):
        serializer.save()

# class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Vendor.objects.all()
#     serializer_class = VendorRetrieveSerializer
#     lookup_field = 'id'
#     permission_classes = [IsAuthenticated]


class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    
    
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        print(self.request.user)
        # Filter queryset to retrieve only the vendor belonging to the logged-in user
        return Vendor.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.request.method in ["PUT","PATCH"]:
            return VendorUpdateSerializer
        return VendorRetrieveSerializer
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Vendor has been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = PurchaseOrder.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseOrderCreateSerializer
        return PurchaseOrderRetrieveSerializer

class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsVendorOrReadOnly]
    queryset = PurchaseOrder.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PurchaseOrderUpdateSerializer
        return PurchaseOrderRetrieveSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Modify the response data to use 'vendor_code' instead of 'id'
        response_data = serializer.data
        response_data.pop("vendor")
        response_data['vendor_code'] = str(instance.vendor)
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Purchase order has been deleted."}, status=status.HTTP_204_NO_CONTENT)

class IsVendorAcknowledge(BasePermission):
    """
    Custom permission to only allow the vendor of a purchase order to acknowledge it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is authenticated and is a vendor.
        if not request.user.is_authenticated or not hasattr(request.user, 'vendor'):
            return False

        # Check if the user is the vendor of the purchase order.
        return obj.vendor == request.user.vendor

class AcknowledgePurchaseOrder(APIView):
    
    permission_classes = [IsAuthenticated,IsVendorAcknowledge]
    def post(self, request, pk):
        try:
            # Retrieve the purchase order instance
            purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

            # Update acknowledgment date
            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.save()

            return Response({'message': f'Purchase Order {pk} acknowledged successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class VendorPerformance(APIView):
    def get(self, request, pk):
        try:
            # Retrieve the purchase order instance
            vendor = get_object_or_404(Vendor, pk=pk)
            
            serialised_data=VendorPerformanceSerializer(vendor)
            

            return Response(serialised_data.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)