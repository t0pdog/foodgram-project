from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from users.models import User


class Tag(models.Model):
    """
    Creates tags for grouping recipes.
    """

    name = models.CharField(
        verbose_name=_("Name of the recipe"),
        max_length=200
    )
    slug = models.SlugField(
        verbose_name=_("Identifier"),
        max_length=200,
        unique=True
    )
    color = ColorField(default='#FF0000')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Ingredient(models.Model):
    """
    Creates ingredients.
    """

    name = models.CharField(
        verbose_name=_("Name of the ingredient"),
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name=_("Measurement"),
        max_length=200
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")
        constraints = (
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit"
            ),
        )


class Recipe(models.Model):
    """
    The base Recipe model.
    Creates recipes.
    """

    name = models.TextField(
        verbose_name=_("Name of the recipe"),
        max_length=200
    )
    text = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name=_("Author"),
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_("Cooking time, min."),
        validators=[
            MinValueValidator(1),
        ],
    )
    image = models.ImageField(
        upload_to="recipes/images/", null=True, default=None
    )
    ingredients = models.ManyToManyField(
        "Ingredient", verbose_name="Ingredient", through="IngredientInRecipe"
    )
    tags = models.ManyToManyField("Tag", verbose_name="Tag")
    pub_date = models.DateTimeField("Publication date", auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ["-pub_date"]


class IngredientInRecipe(models.Model):
    """
    Linking model between recipes and ingredients.
    """

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_amounts"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredient_amounts"
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_("amount of ingredient"),
        validators=[
            MinValueValidator(1),
        ],
    )

    def __str__(self):
        return f"{self.recipe} contain {self.ingredient}"

    class Meta:
        verbose_name = _("Ingredient in recipe")
        verbose_name_plural = _("Ingredients in recipe")
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique_ingredient_recipe"
            ),
        )


class Favorite(models.Model):
    """
    Model for adding recipes to favorites.
    """

    user = models.ForeignKey(
        User, related_name="favorit_user", on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name="favorit_recipe", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.recipe} in the {self.user}'s favorites"

    class Meta:
        verbose_name = _("Favorites list")
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe"
            ),
        )


class ShoppingCart(models.Model):
    """
    Model for adding recipe ingredients to shopping list
    and also downloading shopping list file.
    """

    user = models.ForeignKey(
        User, related_name="shopping_cart", on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name="shopping_cart", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.recipe} in the {self.user}'s shopping list"

    class Meta:
        verbose_name = _("Shopping list")
        ordering = ("user",)
        constraints = (
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shoppingCart"
            ),
        )
