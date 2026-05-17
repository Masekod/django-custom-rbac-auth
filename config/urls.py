from django.contrib import admin
from django.urls import path
from auth_app.views import (
    RegisterView, LoginView, ProfileUpdateView,
    LogoutView, ProfileDeleteView, ManagePermissionsView, DocumentMockView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),

    path('api/admin/permissions/', ManagePermissionsView.as_view(), name='manage_permissions'),

    path('api/business/documents/', DocumentMockView.as_view(), name='mock_documents'),
]
