from datetime import datetime
from django.db.models import Count
from loan.models import Loan

from django.db import transaction, connection