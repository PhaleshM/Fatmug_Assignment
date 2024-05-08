from django.contrib import admin
from .models import PurchaseOrder,Vendor,HistoricalPerformance
# Register your models here.


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display=['po_number','vendor','status']

class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display=['vendor','date']


admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(HistoricalPerformance)