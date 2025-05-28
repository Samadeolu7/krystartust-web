from django import forms

from administration.models import Transaction
from liability.models import Liability, LiabilityPayment
from .models import AssetCategory, AssetRecord, FixedAsset, Inventory


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description', 'depreciation_rate']


class AssetRecordForm(forms.ModelForm):
    class Meta:
        model = AssetRecord
        fields = [ 'inventory', 'fixed_asset', 'transaction_type', 'quantity', 'price', 'description','payment_date']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the transaction to the current date if not provided
        tran = Transaction(description=f'{instance.fixed_asset.name} {instance.transaction_type} Transaction')
        tran.save(prefix='ASS')
        if instance.inventory and instance.fixed_asset:
            raise 
        elif instance.inventory:
            inventory = instance.inventory
            inventory.quantity += instance.quantity
            seller = inventory.seller
        elif instance.fixed_asset:
            fixed_asset = instance.fixed_asset
            fixed_asset.quantity += instance.quantity
            seller = instance.fixed_asset.seller

        LiabilityPayment.objects.create(
            liability=seller,
            amount=instance.price,
            description=instance.description,
            transaction=tran,
            payment_date=instance.payment_date
        )
        if commit:
            instance.save()
        return instance


class FixedAssetForm(forms.ModelForm):

    seller = forms.ModelChoiceField(queryset=Liability.objects.filter(seller=True), required=False, label="Seller")
    class Meta:
        model = FixedAsset
        fields = [
            'name', 'description', 'category', 'capitalization_date',
            'depreciation_start', 'useful_life_years', 'seller', 'price', 'status'
        ]
        widgets = {
            'capitalization_date': forms.DateInput(attrs={'type': 'date'}),
            'depreciation_start': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, user,commit=True):
        instance = super().save(commit=False)
        # Set the depreciation start date to the capitalization date if not provided
        seller = self.cleaned_data.get('seller')
        tran=Transaction(description=f'{instance.name} Purchase from {seller.name}')
        tran.save(prefix='ASS')
        instance.depreciation_start = instance.capitalization_date
        if commit == True:
            instance.save()
            seller_payment = LiabilityPayment.objects.create(
                liability=seller,
                amount=self.cleaned_data['price'],
                description=f"Purchase of {instance.name}",
                transaction=tran,
                payment_date=self.cleaned_data['capitalization_date'],
                created_by=user # Assuming office has a created_by field
            )
            asset_record = AssetRecord.objects.create(
                fixed_asset=instance,
                transaction_type=AssetRecord.ADDITION,
                quantity=1,
                price=self.cleaned_data['price'],
                description=f"Purchase of {instance.name} from {seller.name}",
                payment_date=self.cleaned_data['capitalization_date'],
                transaction=tran
            )


class InventoryForm(forms.ModelForm):
    seller = forms.ModelChoiceField(queryset=Liability.objects.filter(seller=True), required=False, label="Seller")
    class Meta:
        model = Inventory
        fields = ['name', 'description', 'seller','inventory_type', 'office', 'price', 'quantity']

    def save(self, commit=True):
        instance = super().save(commit=False)
        seller = self.cleaned_data.get('seller')
        quantity = self.cleaned_data.get('quantity')
        tran=Transaction(description=f'{instance.name} Purchase from {seller.name}')
        tran.save(prefix='ASS')
        instance.depreciation_start = instance.capitalization_date
        seller_payment = LiabilityPayment.objects.create(
            liability=seller,
            amount=self.cleaned_data['price'],
            description=f"Purchase of {instance.name}",
            transaction=tran,
            payment_date=self.cleaned_data['capitalization_date'],
            created_by=self.instance.seller.office.created_by  # Assuming office has a created_by field
        )
        asset_record = AssetRecord.objects.create(
            definition=self.instance,
            item=self.instance,
            transaction_type=AssetRecord.ADDITION,
            quantity=quantity,
            price=self.cleaned_data['price'],
            description=f"Purchase of {instance.name} from {seller.name}",
            transaction=tran
        )