from celery import shared_task
from .utils import depreciate_fixed_assets


@shared_task
def run_depreciation():
    """
    Task to depreciate fixed assets monthly.
    """
    depreciate_fixed_assets()