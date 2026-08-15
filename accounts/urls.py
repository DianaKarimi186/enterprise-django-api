from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    RegisterPageView,
    LoginPageView,
    BrowserLoginView
)


urlpatterns = [
    # Authentication API
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),

    # Browser pages
    path("browser-login/",BrowserLoginView.as_view(),name="browser-login",),
    path("register-page/", RegisterPageView.as_view(), name="register-page"),
    path("login-page/", LoginPageView.as_view(), name="login-page"),
]