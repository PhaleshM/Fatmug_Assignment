from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from django.utils import timezone

class VendorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id','name', 'contact_details', 'address', 'vendor_code']

    read_only=['id']
    def validate(self, attrs):

        contact=attrs.get('contact_details')
        if contact[0]=='+' and len(contact)==13:
            attrs['contact_details']=contact[3:]
        elif len(contact)==0 and contact[0]=='0':
            attrs['contact_details']=contact[1:]
        elif len(contact)<10:
             raise serializers.ValidationError("enter valid contact details.")
            
        return attrs

class VendorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    vendor = serializers.CharField(max_length=50)
    
    class Meta:
        model = PurchaseOrder
        fields = ['po_number','vendor', 'order_date', 'status','delivery_date', 'items', 'quantity', 'quality_rating' ,'issue_date']

    def create(self, validated_data):
        vendor_code = validated_data.pop('vendor', None)
        quality_rating=validated_data.pop('quality_rating',None)
        if quality_rating != None:
            if quality_rating<0 and quality_rating>5:
                raise serializers.ValidationError("quality_rating should be between 0 to 5")

        # Check if vendor_code is provided
        if vendor_code:
            try:
                # Fetch the Vendor object based on the provided vendor_code
                vendor = Vendor.objects.get(vendor_code=vendor_code)
            except Vendor.DoesNotExist:
                # If vendor does not exist, raise a ValidationError
                raise serializers.ValidationError("Vendor does not exist")
            
            # Assign the fetched Vendor object to the vendor field of the validated data
            validated_data['vendor'] = vendor
        
        # Create and return the PurchaseOrder instance
        return PurchaseOrder.objects.create(**validated_data)       

class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['order_date', 'delivery_date', 'items', 'quantity', 'status', 'quality_rating', "issue", "issue_date"]

    read_only=['issue_date']

    # Make every field optional
    order_date = serializers.DateTimeField(required=False)
    delivery_date = serializers.DateTimeField(required=False)
    items = serializers.JSONField(required=False)
    quantity = serializers.IntegerField(required=False)
    issue = serializers.BooleanField(required=False)


    def update(self, instance, validated_data):
        issue = validated_data.pop('issue', None)

        if issue:
            instance.issue_date = timezone.now()

        return super().update(instance, validated_data)  
        

class PurchaseOrderRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class HistoricalPerformancerSerializer(serializers.ModelSerializer):
    
    class Meta:
        Model=HistoricalPerformance
        fields=['name','contact_details','address','vendor_code']
                