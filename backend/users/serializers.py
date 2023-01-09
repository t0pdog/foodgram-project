import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer

from .models import Follow, User

from recipes.models import Recipe


logger = logging.getLogger(__name__)


class CustomUserSerializer(UserSerializer):
    """
    Serializer for response to GET request User
    with an additional field is_subscribed.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        """
        Returns a bool True or False for request:
        if the current user subscribed on profile.
        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for response to create User.
    """

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name", "password"
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer to briefly display recipe details.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowListSerializer(CustomUserSerializer):
    """
    Response when creating a subscription.
    """

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, object):
        """
        Reports the number of recipes in a get request for subscriptions.
        """
        return object.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Response when querying my subscriptions."""

    def validate_following(self, following):
        """Field validation following."""
        user = self.context.get("request").user
        if user == following:
            raise serializers.ValidationError(
                "It is impossible to follow yourself"
            )
        return following

    class Meta:
        model = Follow
        fields = ("user", "following")

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=("user", "following"),
                message="You are already following",
            )
        ]

    def to_representation(self, instance):
        """Serializing data with FollowListSerializer."""
        return FollowListSerializer(
            instance.following,
            context={"request": self.context.get("request")}
        ).data


class SubscriptionShowSerializer(CustomUserSerializer):
    """serializer for displaying Subscriptions."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Get recipes of author."""
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")
        try:
            recipes = recipes[: int(recipes_limit)]
        except TypeError:
            logger.exception('recipes_limit is not convertible to int')

        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """
        Reports the number of recipes in a get request for subscriptions.
        """
        return obj.recipes.count()
