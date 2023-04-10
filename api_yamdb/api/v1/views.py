from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsOwnerModeratorAdminOrReadOnly,
    IsProfileOwner,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    ConfirmationCodeSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateUpdateSerializer,
    TitleViewSerializer,
    UserSerializer,
)
from .utils import code_generator, confirmation_code_email


class TitleViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для работы с моделью Title.
    Разрешено частичное обновление, добавление, удаление,
    получение списка всех элементов и одного элемента.
    Доступен всем для чтения и администратору для модификации.
    Подключена фильтрация по полям: category, genre, name, year.
    """

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleCreateUpdateSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['patch', 'get', 'post', 'delete']

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return TitleViewSerializer
        return TitleCreateUpdateSerializer


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Эндпоинт для работы с моделью Category.
    Разрешено добавление, удаление и получение списка всех элементов.
    Доступен всем для чтения и администратору для модификации.
    Подключена фильтрация по полю: name
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Эндпоинт для работы с моделью Genre.
    Разрешено добавление, удаление и получение списка всех элементов.
    Доступен всем для чтения и администратору для модификации.
    Подключена фильтрация по полю: name
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ConfirmationCodeView(APIView):
    """
    Самостоятельная регистрация пользователя на портале.
    Если данные прошли валидацию новый пользователь будет зарегистрирован и
    получит письмо с кодом подтверждения. Если пользователь был
    зарегистрирован ранее, он также получит письмо с кодом подтверждения.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        user = User.objects.filter(username=username, email=email)
        if username:
            confirmation_code = code_generator(username)
        if user:
            confirmation_code_email(email, confirmation_code)
            return Response(
                ({'message': 'Письмо успешно отправлено'}, request.data),
                status=status.HTTP_200_OK,
            )
        serializer = ConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            confirmation_code_email(email, confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для управления пользователями.
    Можно осуществлять добавление и поиск по пользователям.
    Пользователь может дополнить данные о себе через обращение к эндпоинту
    /me/.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly, permissions.IsAuthenticated)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_name='get_user',
        permission_classes=(IsProfileOwner, permissions.IsAuthenticated),
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отправки отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [
        IsOwnerModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))

        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для отправки комментария."""

    serializer_class = CommentSerializer
    permission_classes = [
        IsOwnerModeratorAdminOrReadOnly,
        IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title__id=self.kwargs.get("title_id"),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
