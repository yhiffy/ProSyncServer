from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
import bcrypt
import jwt
from .utils import gen_jwt, get_token, get_user_info
from .serializers import UserSerializer

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

            hash_password = bcrypt.hashpw(existing_user.password.encode('utf-8'), bcrypt.gensalt(10))

            correct_password = bcrypt.checkpw(password.encode('utf-8'), hash_password)

            if correct_password:

                token = gen_jwt(str(existing_user.id), existing_user.email, existing_user.is_staff )

                return Response({'token': token, "message": "Login Successful"},
                                status=status.HTTP_200_OK)

            else:
                return Response ('Incorrect Password',
                             status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Internal server error: {e}")
            return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleCallbackView(APIView):

    def get(self, request):

        try:
            code = request.GET.get('code')
            if not code:
                return Response({'message': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)

            access_token = get_token(code)
            if not access_token:
                return Response({'message': 'Missing access_token'}, status=status.HTTP_400_BAD_REQUEST)

            user_info = get_user_info(access_token)

            if not user_info:
                return Response({'message': 'Missing user ino'}, status=status.HTTP_400_BAD_REQUEST)

            google_id = user_info['sub']
            email = user_info['email']
            name = user_info['name']

            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                if not existing_user.google_id:
                    serializer = UserSerializer(existing_user, data={'google_id': google_id}, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                jwt_token = gen_jwt(str(existing_user.id), existing_user.email, existing_user.is_staff)

                url_wz_token = f'{settings.FRONTEND_URL}?token={jwt_token}'
                return redirect (url_wz_token)


#             如果没有已存在的用户
            serializer = UserSerializer(data={'google_id': google_id, 'email': email, 'full_name': name})
            if serializer.is_valid():
                new_user = serializer.save()
                jwt_token = gen_jwt(str(new_user.id), new_user.email, new_user.is_staff)

                url_wz_token = f'{settings.FRONTEND_URL}?token={jwt_token}'
                return redirect (url_wz_token)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









