from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from .models import UserStatus
from django.utils import timezone

from .models import Visit

class LogVisitsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        ip_address = self.get_client_ip(request)
        Visit.objects.create(ip_address=ip_address)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            UserStatus.objects.update_or_create(
                user=request.user,
                defaults={'last_activity': timezone.now(), 'is_online': True}
            )
        response = self.get_response(request)
        return response
