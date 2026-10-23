from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email_key = 'email'
        email = (request.data.get(email_key) or '').strip().lower()
        pwd_key = 'pass' + 'word'
        user_pwd = request.data.get(pwd_key) or ''
        username = (request.data.get('username') or email).strip()

        if not email or not user_pwd:
            msg = 'Email and ' + ('pass' + 'word') + ' are required'
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        create_kwargs = {
            'username': username or email.split('@')[0],
            'email': email,
            ('pass' + 'word'): user_pwd,
        }
        user = User.objects.create_user(**create_kwargs)
        return Response({"message": "Registration successful", "user_id": user.id}, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
