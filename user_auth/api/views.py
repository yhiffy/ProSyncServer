from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
import bcrypt
import jwt

# Create your views here.

class LoginView(APIView):

    def post(self, request, *args, **kwargs):

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:

            return Response({'message': 'Email and Password are required'},status=status.HTTP_400_BAD_REQUEST)

        try:
            existing_user = User.objects.get(email=email)


        except User.DoesNotExist:
            return Response({'message': 'User Not Found'},
                            status=status.HTTP_404_NOT_FOUND)

        try:

            # hash_password = bcrypt.hashpw(existing_user.password.encode('utf-8'), bcrypt.gensalt(10))

            correct_password = bcrypt.checkpw(password.encode('utf-8'), existing_user.password.encode('utf-8'))

            if correct_password:
                payload = {
                    'user_id': str(existing_user.id),
                    'email':existing_user.email,
                    'is_staff': existing_user.is_staff,
                    'exp': datetime.utcnow() + timedelta(hours=1)}

                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                return Response({'token': token, "message": "Login Successful"},
                                status=status.HTTP_200_OK)

            else:
                return Response ('Incorrect Password',
                             status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Internal server error: {e}")
            return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



