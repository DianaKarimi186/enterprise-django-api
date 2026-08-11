from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer
from .services import process_payment

from drf_spectacular.utils import extend_schema
from rest_framework import serializers


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        return Payment.objects.filter(
            order__user=self.request.user
        ).select_related("order")


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        return Payment.objects.filter(
            order__user=self.request.user
        ).select_related("order")


class PaymentRequestSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(
        choices=Payment.Provider.choices
    )
    


class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaymentRequestSerializer,
        responses=PaymentSerializer,
    )
    def post(self, request, order_id):
        provider = request.data.get("provider")

        if not provider:
            return Response(
                {"error": "Provider is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
        )

        if hasattr(order, "payment"):
            return Response(
                {"error": "Payment already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = process_payment(
            order,
            provider,
        )

        serializer = PaymentSerializer(payment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )