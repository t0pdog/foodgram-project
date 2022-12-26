from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Redefining the default User model.
    Redefined fields: email, username, first_name, last_name, password.
    """

    email = models.EmailField(
        max_length=254,
        unique=True
    )
    username = models.TextField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='The username contains an invalid character',
                code='invalid_character'
            )]
    )
    first_name = models.TextField(max_length=150)
    last_name = models.TextField(max_length=150)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Follow Model created to be able to follow."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='receipe author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['following', 'user'],
                name='unique follow'
            ),
            models.CheckConstraint(
                name="author_not_user",
                check=~models.Q(following=models.F('user'))
            ),
        ]
