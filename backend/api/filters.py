from django_filters import FilterSet
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    author = filters.CharFilter(
        field_name="author__id", lookup_expr="icontains"
    )
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited",
        method="get_is_favorit",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart"
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    def get_is_favorit(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorit_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ["author", "tags", "is_favorited", "is_in_shopping_cart"]


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
