from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework import generics

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RegisterPageView(TemplateView):
    template_name = "accounts/register.html"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginPageView(TemplateView):
    template_name = "accounts/login.html"