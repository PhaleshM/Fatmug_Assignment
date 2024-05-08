from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Vendor,PurchaseOrder,HistoricalPerformance
from .serializers import VendorCreateSerializer,VendorRetrieveSerializer,PurchaseOrderCreateSerializer,PurchaseOrderRetrieveSerializer,PurchaseOrderUpdateSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone


class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class=VendorCreateSerializer
    

class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ["PUT","PATCH"]:
            return VendorCreateSerializer
        return VendorRetrieveSerializer
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Vendor has been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseOrderCreateSerializer
        return PurchaseOrderRetrieveSerializer

class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
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


class AcknowledgePurchaseOrder(APIView):
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
            
            serialised_data=VendorRetrieveSerializer(vendor)
            

            return Response(serialised_data.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)