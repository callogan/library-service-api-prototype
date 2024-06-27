from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from .models import Book
from .serializers import BookSerializer, BookListSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action == "retrieve":
            return BookDetailSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return super().get_permissions()
