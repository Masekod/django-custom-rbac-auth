import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from django.core.exceptions import ObjectDoesNotExist
from auth_app.models import User


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class CustomJWTAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        header_parts = auth_header.split(' ')
        if len(header_parts) != 2:
            raise exceptions.AuthenticationFailed('Неверный формат заголовка Authorization')

        token = header_parts[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, ObjectDoesNotExist):
            raise exceptions.AuthenticationFailed('Невалидный токен или пользователь удален')

        return user, None
