# Generated by Django 3.2.16 on 2022-12-15 13:00

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Favorites list",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.TextField(
                        max_length=200, verbose_name="Name of the ingredient"
                    ),
                ),
                (
                    "measurement_unit",
                    models.TextField(max_length=200, verbose_name="Measurement"),
                ),
            ],
            options={
                "verbose_name": "Ingredient",
                "verbose_name_plural": "Ingredients",
            },
        ),
        migrations.CreateModel(
            name="IngredientInRecipe",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="amount of ingredient",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ingredient in recipe",
                "verbose_name_plural": "Ingredients in recipe",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.TextField(max_length=200, verbose_name="Name of the recipe"),
                ),
                (
                    "text",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Cooking time, min.",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        default=None, null=True, upload_to="recipes/images/"
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Publication date"
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipe",
                "verbose_name_plural": "Recipes",
                "ordering": ["-pub_date"],
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.TextField(max_length=200, verbose_name="Name of the recipe"),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=200,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_character",
                                message="The slug contains an invalid character",
                                regex="^[-\\w_]+$",
                            )
                        ],
                        verbose_name="Identifier",
                    ),
                ),
                ("color", models.CharField(max_length=7, verbose_name="Color in HEX")),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to="recipes.recipe",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shopping list",
                "ordering": ("user",),
            },
        ),
    ]
