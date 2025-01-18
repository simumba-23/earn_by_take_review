from django.core.management.base import BaseCommand
from django.utils import timezone
from myearn.models import UserStatus
from datetime import timedelta

class Command(BaseCommand):
    help = 'Update user online status'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        timeout = now - timedelta(minutes=5)  # set to offline after 5 minutes of inactivity
        UserStatus.objects.filter(last_activity__lt=timeout).update(is_online=False)
