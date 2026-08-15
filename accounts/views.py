from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework import generics, serializers
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer


@extend_schema(
    tags=["Authentication"],
    summary="Register a new user",
    description="Creates a new user account.",
    responses={201: RegisterSerializer},
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RegisterPageView(TemplateView):
    template_name = "accounts/register.html"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginPageView(TemplateView):
    template_name = "accounts/login.html"


class BrowserLoginView(View):
    """
    Authenticates a browser user using Django's session authentication.

    JWT authentication remains available through the DRF login endpoint
    at /api/accounts/login/.
    """

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Username and password are required.",
                },
                status=400,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid username or password.",
                },
                status=401,
            )

        login(request, user)

        return JsonResponse(
            {
                "success": True,
                "message": "Login successful.",
                "username": user.username,
            },
            status=200,
        )