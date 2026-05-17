
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .models import User, UserRole, Role
from .authentication import generate_token
from .permissions import CustomRBACPermission


# --- МОДУЛЬ 1: ВЗАИМОДЕЙСТВИЕ С ПОЛЬЗОВАТЕЛЕМ ---

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    # noinspection PyMethodMayBeStatic
    def post(self, request: Request) -> Response:
        registration_data = request.data

        if registration_data.get('password') != registration_data.get('password_confirm'):
            return Response({"error": "Пароли не совпадают"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=registration_data.get('email')).exists():
            return Response({"error": "Email уже занят"}, status=status.HTTP_400_BAD_REQUEST)

        new_user = User.objects.create(
            first_name=registration_data.get('first_name'),
            last_name=registration_data.get('last_name'),
            email=registration_data.get('email'),
            password_hash=make_password(registration_data.get('password'))
        )

        default_role, _ = Role.objects.get_or_create(name='User')
        UserRole.objects.create(user=new_user, role=default_role)

        return Response({"message": "Пользователь зарегистрирован"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    # noinspection PyMethodMayBeStatic
    def post(self, request: Request) -> Response:
        login_email = request.data.get('email')
        login_password = request.data.get('password')

        try:
            authenticated_user = User.objects.get(email=login_email, is_active=True)
            if check_password(login_password, authenticated_user.password_hash):
                auth_token = generate_token(authenticated_user.id)
                return Response({"token": auth_token})
            return Response({"error": "Неверный пароль"}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist:
            return Response({"error": "Пользователь не найден или деактивирован"}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileUpdateView(APIView):
    """ОБНОВЛЕНИЕ ИНФОРМАЦИИ: Редактирование профиля текущего пользователя"""

    # noinspection PyMethodMayBeStatic
    def put(self, request: Request) -> Response:
        current_user = request.user
        update_data = request.data

        if 'first_name' in update_data:
            current_user.first_name = update_data.get('first_name')
        if 'last_name' in update_data:
            current_user.last_name = update_data.get('last_name')
        if 'password' in update_data:
            current_user.password_hash = make_password(update_data.get('password'))

        current_user.save()
        return Response({"message": "Профиль успешно обновлен"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """LOGOUT: Выход из системы"""

    # noinspection PyMethodMayBeStatic
    def post(self) -> Response:
        return Response({"message": "Вы успешно вышли из системы. Удалите токен на клиенте."},
                        status=status.HTTP_200_OK)


class ProfileDeleteView(APIView):
    """Мягкое удаление аккаунта"""

    # noinspection PyMethodMayBeStatic
    def delete(self, request: Request) -> Response:
        current_user = request.user
        current_user.is_active = False
        current_user.save()
        return Response({"message": "Аккаунт деактивирован. Сессия завершена."}, status=status.HTTP_200_OK)


# --- МОДУЛЬ 2: АДМИНИСТРИРОВАНИЕ ПРАВИЛ ---

class ManagePermissionsView(APIView):
    permission_classes = [CustomRBACPermission(resource_name='permissions', action_name='update')]

    def get(self, request: Request) -> Response:
        """ПОЛУЧЕНИЕ ПРАВИЛ: Выгружает текущую матрицу доступа из БД (Только для Админа)"""
        from .models import Permission

        permissions_queryset = Permission.objects.all().select_related('role', 'resource', 'action')

        rules_list = []
        for perm in permissions_queryset:
            rules_list.append({
                "id": perm.id,
                "role": perm.role.name,
                "resource": perm.resource.name,
                "action": perm.action.name
            })

        return Response({"current_matrix": rules_list}, status=status.HTTP_200_OK)

    # noinspection PyMethodMayBeStatic
    def post(self, request: Request) -> Response:
        return Response({"message": "Правило доступа успешно обновлено в БД"}, status=status.HTTP_200_OK)


# --- МОДУЛЬ 3: ВЫМЫШЛЕННЫЕ БИЗНЕС-ОБЪЕКТЫ (Mock-Views) ---

class DocumentMockView(APIView):
    permission_classes = [CustomRBACPermission(resource_name='documents', action_name='read')]

    # noinspection PyMethodMayBeStatic
    def get(self, request: Request)  -> Response:
        mock_documents_list = [
            {"id": 1, "title": "Годовой отчет компании", "confidential": True},
            {"id": 2, "title": "План развития 2026", "confidential": False},
            {"id": 3, "title": "Уровень заработных плат сотрудников", "confidential": True}
        ]
        return Response(mock_documents_list, status=status.HTTP_200_OK)
