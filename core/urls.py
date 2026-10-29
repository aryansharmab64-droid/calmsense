from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthForm

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html",
        authentication_form=StyledAuthForm,
        redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
]