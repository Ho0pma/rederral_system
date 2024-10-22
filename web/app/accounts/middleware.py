from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        login_url = reverse('accounts:login')
        register_url = reverse('accounts:register')

        if request.path not in [login_url, register_url]:
            if access_token:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            else:
                return redirect('accounts:login')
