from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.conf import settings
from djoser.views import TokenCreateView, UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import Follow, User
from .serializers import FollowSerializer, SubscriptionShowSerializer


class CustomTokenCreateView(TokenCreateView):
    """To get a token."""

    def _action(self, serializer):
        super()._action(serializer)
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class UsersViewSet(UserViewSet):
    """Viewset for subscriptions, model Follow."""

    pagination_class = LimitOffsetPagination

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """Returns the authors the user is following."""
        authors = User.objects.filter(following__user=request.user)
        result_pages = self.paginate_queryset(
            queryset=authors
        )
        serializer = SubscriptionShowSerializer(
            result_pages,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        """Allows you to add or remove authors from subscriptions."""
        if request.method != 'POST':
            subscription = Follow.objects.filter(
                user=request.user,
                following=get_object_or_404(User, id=id)
            )
            if subscription.exists():
                self.perform_destroy(subscription)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'You have already unsubscribed or have not been subscribed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'following': get_object_or_404(User, id=id).id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
