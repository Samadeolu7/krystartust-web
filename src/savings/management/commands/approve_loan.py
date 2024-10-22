from django.core.management.base import BaseCommand, CommandError
from user.models import User
from administration.models import Approval
from loan.utils import approve_loan

class Command(BaseCommand):
    help = 'Approve a loan by its approval ID'

    def add_arguments(self, parser):
        parser.add_argument('approval_id', type=int, help='The ID of the approval to approve')
        parser.add_argument('user_id', type=int, help='The ID of the user approving the loan')

    def handle(self, *args, **kwargs):
        approval_id = kwargs['approval_id']
        user_id = kwargs['user_id']

        try:
            approval = Approval.objects.get(pk=approval_id)
            user = User.objects.get(pk=user_id)
        except Approval.DoesNotExist:
            raise CommandError(f'Approval with ID {approval_id} does not exist')
        except User.DoesNotExist:
            raise CommandError(f'User with ID {user_id} does not exist')

        if approval.type != 'loan':
            raise CommandError(f'Approval with ID {approval_id} is not of type loan')

        approve_loan(approval, user)
        approval.approved = True
        approval.approved_by = user
        approval.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully approved loan with approval ID {approval_id}'))