from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, vendor_code, password=None, **extra_fields):
        if not vendor_code:
            raise ValueError('The Vendor Code field must be set')
        user = self.model(vendor_code=vendor_code, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, vendor_code, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(vendor_code, password, **extra_fields)

class Vendor(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    contact_details = models.TextField(unique=True)
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'vendor_code'
    REQUIRED_FIELDS = ['name', 'contact_details', 'address']

    objects = CustomUserManager()

    def __str__(self):
        return self.vendor_code


# class Vendor(models.Model):
#     name = models.CharField(max_length=100)
#     contact_details = models.TextField(unique=True)
#     address = models.TextField()
#     vendor_code = models.CharField(max_length=50, unique=True)
#     on_time_delivery_rate = models.FloatField(default=0)
#     quality_rating_avg = models.FloatField(default=0)
#     average_response_time = models.FloatField(default=0)
#     fulfillment_rate = models.FloatField(default=0)

#     def __str__(self):
#         return self.vendor_code

class PurchaseOrder(models.Model):
    PENDING ='Pending'
    COMPLETED = 'Completed'
    CANCELED = 'Canceled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    po_number = models.AutoField(primary_key=True)    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(null=True, blank=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return "{po}_{vendor}".format(po=self.po_number,vendor=self.vendor)
    


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def __str__(self):
        return f"{self.vendor} - {self.date}"


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# from .models import PurchaseOrder, HistoricalPerformance
from datetime import datetime
from django.utils import timezone
from datetime import timedelta


from django.db.models import Avg

def calculate_on_time_delivery_rate(vendor,historical_data):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed')
    total_completed_orders = completed_orders.count()
    print(total_completed_orders)
    if total_completed_orders == 0:
        return 0
    
    on_time_deliveries = historical_data.on_time_delivery_rate*(total_completed_orders-1)/100+1
    return (on_time_deliveries / total_completed_orders) * 100

def calculate_quality_rating_avg(vendor,historical_data,instance):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed')
    total_completed_orders = completed_orders.count()
    total_quality_ratings=historical_data.quality_rating_avg*(total_completed_orders-1)+instance.quality_rating if instance.quality_rating else 0
    
    return total_quality_ratings/total_completed_orders

def calculate_fulfillment_rate(vendor,historical_data,instance):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='Completed')
    total_completed_orders = completed_orders.count()
    
    if total_completed_orders == 0:
        return 0
    
    fulfilled_orders = completed_orders.filter(issue_date__isnull=False).count()
    return (fulfilled_orders / total_completed_orders) * 100

def calculate_average_response_time(vendor, historical_data, instance):
    acknowledged_orders = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False)
    total_acknowledged_orders = acknowledged_orders.count()
    
    if total_acknowledged_orders == 0:
        return 0  # Return zero if there are no acknowledged orders
    
    response_time_minutes = historical_data.average_response_time * (total_acknowledged_orders - 1)
    if instance.issue_date:
        response_time_minutes += (instance.acknowledgment_date - instance.issue_date).total_seconds() / 60
    
    # Calculate average response time in minutes
    average_response_time_minutes = response_time_minutes / total_acknowledged_orders

    return round(average_response_time_minutes)

def save_historical_performance(current_data):
    vendor=current_data
    on_time_delivery_rate = current_data.on_time_delivery_rate
    quality_rating_avg = current_data.quality_rating_avg
    average_response_time = current_data.average_response_time
    fulfillment_rate = current_data.fulfillment_rate

    HistoricalPerformance.objects.create(vendor=vendor,
                                         date=datetime.now(),
                                         on_time_delivery_rate=on_time_delivery_rate,
                                         quality_rating_avg=quality_rating_avg,
                                         average_response_time=average_response_time,
                                         fulfillment_rate=fulfillment_rate

                                         )


@receiver(post_save, sender=PurchaseOrder)
def purchase_order_saved(sender, instance, created, **kwargs):
    vendor = instance.vendor
    # Get or create HistoricalPerformance instance for the vendor
    current_data= Vendor.objects.get(vendor_code=vendor)
    save_historical_performance(current_data)
    
    # Update vendor performance metrics based on the saved purchase order
    print(instance.status)
    if instance.status == 'Completed':
        # Calculate on-time delivery rate
        on_time_delivery_rate = calculate_on_time_delivery_rate(vendor,current_data)
        
        # Calculate quality rating average
        quality_rating_avg = calculate_quality_rating_avg(vendor,current_data,instance)
        
        if instance.issue_date:
            # Calculate fulfillment rate
            fulfillment_rate = calculate_fulfillment_rate(vendor,current_data,instance)
            
            # Update or create historical performance record
            current_data.fulfillment_rate = fulfillment_rate
            current_data.save()

        # Update or create historical performance record
        current_data.on_time_delivery_rate = on_time_delivery_rate
        current_data.quality_rating_avg = quality_rating_avg
        current_data.save()
    
    # if instance.issue_date:
    # Calculate fulfillment rate
    fulfillment_rate = calculate_fulfillment_rate(vendor,current_data,instance)
    
    # Update or create historical performance record
    current_data.fulfillment_rate = fulfillment_rate
    current_data.save()
    
    if instance.acknowledgment_date:
        print("nk")
        # Calculate average response time
        average_response_time = calculate_average_response_time(vendor,current_data,instance)
        
        # Update or create historical performance record
        current_data.average_response_time = average_response_time
        current_data.save()

