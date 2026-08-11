from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .serializers import CartSerializer
from .services import (
    get_or_create_cart,
    add_to_cart,
    remove_from_cart,
    update_quantity,
)


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_or_create_cart(self.request.user)


class CartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
        help_text="New quantity for the cart item."
    )
class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: MessageResponseSerializer},
    )
    def post(self, request, product_id):
        try:
            add_to_cart(request.user, product_id)

            return Response(
                {"message": "Product added successfully"},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={204: None},
    )
    def delete(self, request, product_id):
        remove_from_cart(request.user, product_id)

        return Response(
            {"message": "Product removed successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CartQuantitySerializer,
        responses={200: MessageResponseSerializer},
    )
    def patch(self, request, product_id):
        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {"error": "Quantity is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)

            if quantity < 1:
                raise ValueError(
                    "Quantity must be at least 1."
                )

            update_quantity(
                request.user,
                product_id,
                quantity,
            )

            return Response(
                {"message": "Quantity updated successfully"}
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )