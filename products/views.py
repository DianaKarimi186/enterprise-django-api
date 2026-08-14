from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from celery.result import AsyncResult

from rest_framework import filters, generics, status, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.parsers import (
    JSONParser,
    MultiPartParser,
    FormParser,
)

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from drf_spectacular.utils import extend_schema,  inline_serializer

from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category
from .permissions import IsOwnerOrReadOnly
from .serializers import ProductSerializer
from .tasks import simulate_heavy_background_job

INVENTORY_CACHE_KEY = "inventory_products"


@extend_schema(
    tags=["Products"],
    summary="List or create products",
    description=(
        "Returns products belonging to the authenticated user. "
        "Anonymous users can read the product list but cannot create products."
    ),
)
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["category"]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "price",
        "stock",
        "created_at",
    ]

    def get_queryset(self):
        queryset = Product.objects.select_related(
            "category",
            "owner",
        )

        if self.request.user.is_authenticated:
            return queryset.filter(
                owner=self.request.user
            ).order_by("-created_at")

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@extend_schema(
    tags=["Products"],
    summary="Retrieve, update, or delete a product",
    description=(
        "Retrieve a product by ID. "
        "Only the product owner can update or delete the product."
    ),
)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related(
        "category",
        "owner"
    ).all()
    serializer_class = ProductSerializer

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    permission_classes = [ IsAuthenticated, IsOwnerOrReadOnly,]

@extend_schema(
    summary="Start background product processing",
    description="Queues a Celery background task for the specified product.",
    responses={
        202: inline_serializer(
            name="ProductProcessResponse",
            fields={
                "message": serializers.CharField(),
                "task_id": serializers.CharField(),
                "product_id": serializers.IntegerField(),
                "product_name": serializers.CharField(),
            },
        )
    },
)
class ProductProcessView(generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def post(self, request, pk):
        product = self.get_object()

        task = simulate_heavy_background_job.delay(product.name)

        return Response(
            {
                "message": "Product processing started",
                "task_id": task.id,
                "product_id": product.id,
                "product_name": product.name,
            },
            status=status.HTTP_202_ACCEPTED,
        )
    
@extend_schema(
    summary="Check background task status",
    description="Returns the current Celery task status and result.",
    responses={
        200: inline_serializer(
            name="TaskStatusResponse",
            fields={
                "task_id": serializers.CharField(),
                "status": serializers.CharField(),
                "result": serializers.CharField(
                    allow_null=True,
                    required=False,
                ),
            },
        )
    },
)
class TaskStatusView(generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, task_id):
        task = AsyncResult(task_id)

        if request.headers.get("HX-Request") == "true":

            if task.successful():
                return HttpResponse(
                    '<span class="text-emerald-400">✓ Background processing complete</span>'
                )

            if task.failed():
                return HttpResponse(
                    '<span class="text-red-400">✗ Background processing failed</span>'
                )

            return HttpResponse(
                '<span class="text-yellow-400">⏳ Background processing...</span>'
            )

        return Response(
            {
                "task_id": task.id,
                "status": task.status,
                "result": task.result if task.successful() else None,
            },
            status=status.HTTP_200_OK,
        )
    
class DashboardView(View):
    def get(self, request):

        if not request.user.is_authenticated:
            return redirect("/login/")

        products = cache.get(
            f"{INVENTORY_CACHE_KEY}_{request.user.id}"
        )

        if products is None:
            print("CACHE MISS → Querying database")

            products = list(
                Product.objects
                .select_related("category")
                .filter(owner=request.user)
            )

            cache.set(
                f"{INVENTORY_CACHE_KEY}_{request.user.id}",
                products,
                timeout=300
            )

        else:
            print("CACHE HIT → Using Redis")

        categories = Category.objects.all().order_by("name")

        return render(
            request,
            "products/dashboard.html",
            {
                "products": products,
                "categories": categories,
            }
        )


@extend_schema(exclude=True)
class HTMXCreateProductView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        description = request.POST.get("description", "").strip()

        if not name:
            return render(
                request,
                "products/partials/form_errors.html",
                {"error_message": "Product name is required."},
                status=422
            )

        if not category_id:
            return render(
                request,
                "products/partials/form_errors.html",
                {"error_message": "Please select a category."},
                status=422
            )

        try:
            category = Category.objects.get(pk=category_id)
        except (Category.DoesNotExist, ValueError, TypeError):
            return render(
                request,
                "products/partials/form_errors.html",
                {"error_message": "Selected category is invalid."},
                status=422
            )

        try:
            price = Decimal(price)

            if price <= 0:
                raise ValueError

        except (InvalidOperation, TypeError, ValueError):
            return render(
                request,
                "products/partials/form_errors.html",
                {"error_message": "Price must be greater than zero."},
                status=422
            )

        try:
            stock = int(stock)

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):
            return render(
                request,
                "products/partials/form_errors.html",
                {"error_message": "Stock cannot be negative."},
                status=422
            )

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description,
            owner=request.user,
            category=category,
        )

        cache.delete(
            f"{INVENTORY_CACHE_KEY}_{request.user.id}"
        )

        task = simulate_heavy_background_job.delay(product.name)

        return render(
            request,
            "products/partials/products_row.html",
            {
                "product": product,
                "task_id": task.id,
            }
        )

@extend_schema(exclude=True)
class HTMXEditProductView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    """Returns the inline edit form for a single product."""

    def get(self, request, pk):
        product = Product.objects.filter(
            pk=pk,
            owner=request.user
        ).first()

        if not product:
            return HttpResponse(
                "Product not found.",
                status=404
            )

        return render(
            request,
            "products/partials/product_edit_row.html",
            {"product": product}
        )

@extend_schema(exclude=True)
class HTMXUpdateProductView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    """Updates a product and returns the refreshed table row."""

    def put(self, request, pk):
        product = Product.objects.filter(
            pk=pk,
            owner=request.user
        ).first()

        if not product:
            return HttpResponse(
                "Product not found.",
                status=404
            )

        from django.http import QueryDict

        data = QueryDict(request.body)

        name = data.get("name", "").strip()
        price = data.get("price")
        stock = data.get("stock")

        if not name or price in (None, "") or stock in (None, ""):
            return HttpResponse(
                "Missing required fields.",
                status=400
            )

        try:
            price = Decimal(price)

            if price <= 0:
                raise ValueError

        except (InvalidOperation, TypeError, ValueError):
            return HttpResponse(
                "Price must be greater than zero.",
                status=422
            )

        try:
            stock = int(stock)

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):
            return HttpResponse(
                "Stock cannot be negative.",
                status=422
            )

        product.name = name
        product.price = price
        product.stock = stock
        product.save()

        cache.delete(
            f"{INVENTORY_CACHE_KEY}_{request.user.id}"
        )


        return render(
            request,
            "products/partials/products_row.html",
            {"product": product}
        )

@extend_schema(exclude=True)
class DeleteProductView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        product = Product.objects.filter(
            pk=pk,
            owner=request.user
        ).first()

        if not product:
            return HttpResponse(
                "Product not found.",
                status=404
            )

        product.delete()

        cache.delete(
            f"{INVENTORY_CACHE_KEY}_{request.user.id}"
        )


        if not Product.objects.exists():
            return render(
                request,
                "products/partials/empty_table.html"
            )

        return HttpResponse("")