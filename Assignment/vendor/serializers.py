from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from django.utils import timezone

class VendorCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code', 'password']
        read_only_fields = ['id']

    def validate(self, attrs):
        contact = attrs.get('contact_details')
        if contact and contact[0] == '+' and len(contact) == 13:
            attrs['contact_details'] = contact[3:]
        elif contact and len(contact) == 0 and contact[0] == '0':
            attrs['contact_details'] = contact[1:]
        elif contact and len(contact) < 10:
            raise serializers.ValidationError("Enter valid contact details.")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')  
        vendor = Vendor.objects.create(**validated_data)
        vendor.set_password(password)
        vendor.save()
        return vendor
    

class VendorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code']
        read_only_fields = ['id']

    def validate(self, attrs):
        contact = attrs.get('contact_details')
        if contact and contact[0] == '+' and len(contact) == 13:
            attrs['contact_details'] = contact[3:]
        elif contact and len(contact) == 0 and contact[0] == '0':
            attrs['contact_details'] = contact[1:]
        elif contact and len(contact) < 10:
            raise serializers.ValidationError("Enter valid contact details.")

        return attrs

    def update(self, instance, validated_data):
        
        instance.name = validated_data.get('name', instance.name)
        instance.contact_details = validated_data.get('contact_details', instance.contact_details)
        instance.address = validated_data.get('address', instance.address)
        instance.vendor_code = validated_data.get('vendor_code', instance.vendor_code)
        instance.save()
        return instance

class VendorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code']


class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id','vendor_code','on_time_delivery_rate','quality_rating_avg','average_response_time','fulfillment_rate']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'order_date', 'status','delivery_date', 'items', 'quantity', 'quality_rating' ,'issue_date']

    def create(self, validated_data):
        quality_rating = validated_data.pop('quality_rating', None)
        
        # Validate quality_rating if it exists
        if quality_rating is not None and not (0 <= quality_rating <= 5):
            raise serializers.ValidationError("quality_rating should be between 0 to 5")

        vendor = self.context['request'].user
        validated_data['vendor'] = vendor
        
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
                