from datetime import date
from decimal import Decimal

from asset.models import FixedAsset


def depreciate_fixed_assets():
    """
    Depreciates the value of all fixed assets monthly from their capitalization date.
    """
    today = date.today()
    fixed_assets = FixedAsset.objects.filter(status='in_service')

    for asset in fixed_assets:
        if asset.capitalization_date and asset.depreciation_start:
            months_in_service = (today.year - asset.depreciation_start.year) * 12 + (today.month - asset.depreciation_start.month)
            if months_in_service > 0:
                depreciation_rate = asset.depreciation_rate / Decimal(100)
                monthly_depreciation = (depreciation_rate / 12) * asset.definition.default_price
                total_depreciation = monthly_depreciation * months_in_service

                # Ensure depreciation does not exceed the asset's value
                current_value = asset.definition.default_price - total_depreciation
                if current_value < 0:
                    current_value = 0

                # Log or update the asset's value (you can add a field for current value if needed)
                print(f"Asset: {asset}, Depreciated Value: {current_value}")