from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin panel class responsible for ingredients."""

    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name', )
    list_filter = ('name', )


class IngredientRecipeInline(admin.TabularInline):
    """Admin panel class that allows you to add ingredients to a recipe."""

    model = IngredientInRecipe
    extra = 1
    verbose_name = 'Ingredient'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin panel class responsible for tags."""

    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_filter = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin panel class responsible for recipes."""

    list_display = ('pk', 'name', 'author', 'favorite_count',)
    search_fields = ('author', 'name',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [
        IngredientRecipeInline,
    ]

    def favorite_count(self, obj):
        """Displays the total number of favorites for this recipe."""
        return obj.favorit_recipe.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin panel class responsible for favorite."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin panel class responsible for the shopping list."""

    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )


admin.sites.AdminSite.empty_value_display = '-blank-'
