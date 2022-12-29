import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags.
    """

    class Meta:
        fields = "__all__"
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for Ingredients.
    """

    class Meta:
        fields = "__all__"
        model = Ingredient


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for IngredientInRecipe.
    """

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe safe methods.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = GetIngredientRecipeSerializer(
        source="ingredient_amounts", many=True, read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe

        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, object):
        """
        Returns a bool value when asked if there is a recipe in favorites.
        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorit_user.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        """
        Returns a bool value when asked
        if there is a recipe in the shopping list.
        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=object).exists()


class CreateIngredientRecipeSerializer(ModelSerializer):
    """
    To return summary information about ingredients when creating a recipe.
    """

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class CreateRecipeSerializer(ModelSerializer):
    """
    The serializer for the Recipe model.
    Serves for unsafe requests to recipes.
    """

    image = Base64ImageField(required=False, allow_null=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = CreateIngredientRecipeSerializer(many=True)

    def to_representation(self, value):
        """Serializing data with the RecipeSerializer."""
        return RecipeSerializer(
            value, context={"request": self.context.get("request")}
        ).data

    def validate_ingredients(self, ingredients):
        """Checking that the recipe contains unique ingredients."""
        ingredients_data = [ingredient.get("id") for ingredient in ingredients]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise ValidationError("Recipe ingredients must be unique")
        return ingredients

    def validate_tags(self, tags):
        """Check that the recipe contains unique tags."""
        if len(tags) != len(set(tags)):
            raise ValidationError("Recipe tags must be unique")
        return tags

    def add_ingredients(self, ingredients_data, recipe):
        """Adds ingredients to recipes."""
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient=ingredient.get("id"),
                    recipe=recipe,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data):
        """
        Custom 'create' method.
        Created to load the author, tags and ingredients.
        """
        author = self.context.get("request").user
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Custom 'update' method.
        Created to load the author, tags and ingredients.
        """
        recipe = instance
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        self.add_ingredients(ingredients, recipe)
        return instance

    class Meta:
        model = Recipe
        fields = (
            "ingredients", "tags", "image", "name", "text", "cooking_time"
        )


class FavoriteSerializer(ModelSerializer):
    """Serializer for the Favorites model."""

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="You have already bookmarked this recipe.",
            )
        ]


class ShoppingCartSerializer(ModelSerializer):
    """Serializer for the ShoppingCart mode."""

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message="You have already added this recipe to shopping list",
            )
        ]
