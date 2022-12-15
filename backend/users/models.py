from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Redefining the default User model.
    Redefined fields: email, username, first_name, last_name, password.
    Added fields: role.
    """
    ADMINISTRATOR = 'admin'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMINISTRATOR, 'admin'),
        (USER, 'user')
    )

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
    password = models.TextField(max_length=150)
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Access rights',
        max_length=50,
    )

    class Meta:
        ordering = ['id']
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    @property
    def access_administrator(self):
        return self.role == self.ADMINISTRATOR


class Follow(models.Model):
    """Follow Model created to be able to follow."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='receipe author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique follow'
            ),
            models.CheckConstraint(
                name="author_not_user",
                check=~models.Q(author=models.F('user'))
            ),
        ]
