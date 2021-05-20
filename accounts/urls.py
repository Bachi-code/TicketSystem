from django.contrib.auth import views
from django.urls import path
from .views import RegisterView

urlpatterns = [
    path('login/', views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password_change/', views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
         name='password_change'),
    path('password_change/done/',
         views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/', views.PasswordResetView.as_view(template_name='accounts/password_reset.html',
                                                            email_template_name='accounts/password_reset_email.html'),
         name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
