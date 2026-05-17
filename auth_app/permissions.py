from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated
from .models import User, UserRole, Permission

class CustomRBACPermission(permissions.BasePermission):
    """
    Проверяет доступ на основе переданных в класс параметров ресурса и действия.
    """
    def __init__(self, resource_name, action_name):
        self.resource_name = resource_name
        self.action_name = action_name

    def __call__(self):
        return self

    def has_permission(self, request, view):
        # 1. Проверяем аутентификацию (401 ошибка)
        if not request.user or not isinstance(request.user, User):
            raise NotAuthenticated()

        # 2. Получаем все ID ролей пользователя
        user_roles = UserRole.objects.filter(user=request.user).values_list('role_id', flat=True)

        # 3. Ищем явное разрешение в БД для ролей пользователя
        has_access = Permission.objects.filter(
            role_id__in=user_roles,
            resource__name=self.resource_name,
            action__name=self.action_name
        ).exists()

        return has_access
