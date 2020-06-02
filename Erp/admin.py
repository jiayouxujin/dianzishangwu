from django.contrib import admin
from Erp.models import Material, Deploy, Inventory, Order, mrpResult


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('materialId', 'materialName', 'deploy', 'loss', 'unit', 'preDay')


@admin.register(Deploy)
class DeployAdmin(admin.ModelAdmin):
    list_display = ('deployid', 'fatherId', 'sonId', 'areaId', 'number', 'preMatrial', 'preSupplizer')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventoryId', 'materialId', 'materialInventory', 'processInventory')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'productName', 'productNum', 'ddl')


@admin.register(mrpResult)
class mrpResultAdmin(admin.ModelAdmin):
    list_filter = ['orderId']
    list_per_page = 10
    list_display = ('orderId', 'deploy', 'materialId', 'materialName', 'count', 'fixcount', 'askDate', 'finishDate')


admin.site.site_title = "ERP系统"
admin.site.site_header = "ERP系统"
