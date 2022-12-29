from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import ShortRecipeSerializer

from .filters import IngredientSearchFilter, RecipeFilter
from .pdf_downloader import create_pdf_file
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Viewset for Tag class objects."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Viewset for Ingredient class objects."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    """Viewset for Recipe model."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    filterset_class = RecipeFilter
    filter_backends = [
        DjangoFilterBackend,
    ]

    def get_serializer_class(self):
        """Selects a serializor depending on the request."""
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializer_req):
        """For post requests to shopping_cart and favorite."""
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": request.user.id, "recipe": pk}
        serializer = serializer_req(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_data = ShortRecipeSerializer(recipe)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, error, model):
        """For delete requests to shopping_cart and favorite."""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=request.user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": f"The recipe has already been removed from {error}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=["post", "delete"], detail=True)
    def favorite(self, request, pk):
        """Method for adding and removing a recipe in favorite."""
        if request.method == "POST":
            return self.post_method_for_actions(
                request, pk, FavoriteSerializer
            )
        return self.delete_method_for_actions(
            request, pk, "favorite", Favorite
        )

    @action(
        methods=["post", "delete"],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        """Method for adding and removing a recipe in shopping_cart."""
        if request.method == "POST":
            return self.post_method_for_actions(
                request, pk, ShoppingCartSerializer
            )
        return self.delete_method_for_actions(
            request, pk, "shopping cart", ShoppingCart
        )

    @action(
        detail=False, methods=["get"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Allows the current user to download the shopping list."""
        shopping_cart = (
            IngredientInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .order_by("ingredient__name")
            .annotate(ingredient_amount_sum=Sum("amount"))
        )
        return create_pdf_file(shopping_cart)
