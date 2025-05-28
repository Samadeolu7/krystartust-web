from django.urls import reverse
from django.db import models
from administration.manager import OfficeScopedManager
from administration.models import Transaction
from liability.models import Liability, LiabilityPayment


class AssetCategory(models.Model):
    """
    Defines a category of fixed assets, sharing the same depreciation rate.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual depreciation rate as a percentage")

    class Meta:
        verbose_name = "Asset Category"
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name


class FixedAsset(models.Model):
    """
    Represents a fixed asset with depreciation and capitalization details.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(AssetCategory,on_delete=models.PROTECT,related_name='fixed_assets',help_text="Category of the fixed asset")
    capitalization_date = models.DateField(help_text="Date when the asset was capitalized")
    depreciation_start = models.DateField(help_text="When depreciation begins; defaults to capitalization date")
    useful_life_years = models.PositiveIntegerField(help_text="Expected useful life in years")
    seller = models.ForeignKey(Liability,on_delete=models.SET_NULL,null=True,blank=True,related_name='sold_fixed_assets',help_text="The seller of the fixed asset")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,choices=[('in_service', 'In Service'),('disposed', 'Disposed'),('under_repair', 'Under Repair'),],default='in_service')

    class Meta:
        verbose_name = "Fixed Asset"
        verbose_name_plural = "Fixed Assets"

    def __str__(self):
        return self.name

    @property
    def depreciation_rate(self):
        return self.category.depreciation_rate


class Inventory(models.Model):
    """
    Represents an inventory item or cost of sales ledger item.
    """
    STOCK = "stock"
    LEDGER = "ledger"

    INVENTORY_TYPE_CHOICES = [
        (STOCK, "Stock Item"),
        (LEDGER, "Cost of Sales Ledger Item"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    seller = models.ForeignKey(Liability,on_delete=models.SET_NULL,null=True,blank=True,related_name='sold_inventory',help_text="The seller of the inventory item")
    inventory_type = models.CharField(max_length=10,choices=INVENTORY_TYPE_CHOICES,default=STOCK,help_text="Determines behavior and related attributes")
    office = models.ForeignKey('administration.Office',on_delete=models.CASCADE,null=True,blank=True,related_name='inventory_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        unique_together = ['name', 'seller']
        ordering = ['name']

    def __str__(self):
        return self.name

    def add_stock(self, quantity, price):
        """
        Adds stock to the inventory.
        """
        self.quantity += quantity
        self.price = price
        self.save()

    def remove_stock(self, quantity):
        """
        Removes stock from the inventory.
        """
        if quantity > self.quantity:
            raise ValueError("Not enough stock available")
        self.quantity -= quantity
        self.save()


class AssetRecord(models.Model):
    """
    Tracks changes to inventory and fixed asset disposals/additions.
    """
    ADDITION = 'Addition'
    REMOVAL = 'Removal'
    SALE = 'Sale'
    DEPRECATION = 'Depreciation'

    TRANSACTION_TYPE_CHOICES = [
        (ADDITION, 'Addition'),
        (REMOVAL, 'Removal'),
        (SALE, 'Sale'),
        (DEPRECATION, 'Depreciation'),
    ]

    # For inventory: link to inventory; for fixed assets: link to fixed asset
    inventory = models.ForeignKey(Inventory,on_delete=models.CASCADE,related_name='records',null=True,blank=True,)
    fixed_asset = models.ForeignKey(FixedAsset,on_delete=models.CASCADE,related_name='records',null=True,blank=True,)
    transaction_type = models.CharField(max_length=50,choices=TRANSACTION_TYPE_CHOICES,default=ADDITION,help_text="Type of transaction (addition, removal, sale)")
    quantity = models.IntegerField(help_text="Positive for additions, negative for consumption (inventory only)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    payment_date = models.DateField(null=True, blank=True, help_text="Date of the transaction")
    transaction = models.ForeignKey(Transaction,on_delete=models.CASCADE,related_name='asset_records',null=True,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Asset Record"
        verbose_name_plural = "Asset Records"

    def __str__(self):
        target = self.fixed_asset or self.inventory
        return f"{target} - {self.transaction_type} - {self.quantity if self.inventory else 'N/A'}"

    def get_absolute_url(self):
        return reverse('assetrecord_detail', kwargs={'pk': self.pk})