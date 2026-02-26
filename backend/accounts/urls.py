from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    LogoutView,
    check_auth,
)
from .user_management import (
    UserListView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    activate_user,
    user_stats,
)

urlpatterns = [
    # Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('check/', check_auth, name='check_auth'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # User Management (Admin only)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/stats/', user_stats, name='user_stats'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/activate/', activate_user, name='user_activate'),
]