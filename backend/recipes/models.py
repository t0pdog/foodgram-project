from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """
    Creates tags for grouping recipes.
    """
    name = models.TextField(
        'Name of the recipe',
        max_length=200
    )
    slug = models.SlugField(
        'Identifier', max_length=200, unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-\w_]+$',
                message='The slug contains an invalid character',
                code='invalid_character'
            )]
    )
    color = models.CharField('Color in HEX', max_length=7)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Ingredient(models.Model):
    """
    Creates ingredients.
    """
    name = models.TextField(
        'Name of the ingredient',
        max_length=200
    )
    measurement_unit = models.TextField(
        'Measurement',
        max_length=200
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Recipe(models.Model):
    """
    The base Recipe model.
    Creates recipes.
    """
    name = models.TextField(
        'Name of the recipe',
        max_length=200
    )
    text = models.TextField(
        'Description',
        blank=True, null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Author',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Cooking time, min.',
        validators=[
            MinValueValidator(1),
        ],
    )
    image = models.ImageField(
        upload_to='recipes/images/', 
        null=True,  
        default=None
        )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ingredient',
        through='IngredientInRecipe'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Tag'
    )
    pub_date = models.DateTimeField(
        'Publication date',
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-pub_date']


class IngredientInRecipe(models.Model):
    """
    Linking model between recipes and ingredients.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    amount = models.PositiveIntegerField(
        verbose_name='amount of ingredient',
        validators=[
            MinValueValidator(1),
        ],
    )

    def __str__(self):
        return f'{self.recipe} contain {self.ingredient}'

    class Meta: 
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipe'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            ),
        )


class Favorite(models.Model):
    """
    Model for adding recipes to favorites.
    """
    user = models.ForeignKey(
        User,
        related_name='favorit_user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorit_recipe',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.recipe} in the {self.user}\'s favorites'

    class Meta:
        verbose_name = 'Favorites list'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            ),
        )


class ShoppingCart(models.Model):
    """
    Model for adding recipe ingredients to shopping list
    and also downloading shopping list file.
    """
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.recipe} in the {self.user}\'s shopping list'

    class Meta:
        verbose_name = 'Shopping list'
        ordering = ('user',)
