from rest_framework import generics

from .serializers import UserSerializer, CreateUserSerializer


class CreateUserView(generics.CreateAPIView):
    """Users can be registered"""
    serializer_class = CreateUserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    Users can manage their accounts, in particular change their information
    and delete the accounts.
    """
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
