from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
import bcrypt
import jwt
from uuid import uuid4
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage



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



class RegisterView(APIView):

    def post(self, request):
        data = request.data
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')


        if not full_name or not email or not password or not phone:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"message": "User already exists"}, status=status.HTTP_409_CONFLICT)
        

        try:
            hashed_password = make_password(password)
            activation_token = jwt.encode(
                {"email": email, "exp": datetime.utcnow() + timedelta(minutes=30)},
                settings.SECRET_KEY,
                algorithm="HS256"
            )
        
            user_uid = str(uuid4())

            user = User.objects.create(
                id=user_uid, 
                email=email,
                password=hashed_password,
                full_name=full_name,
                phone=phone,
                activation_token=activation_token
            )

     

            base_url = settings.CORS_ALLOWED_ORIGINS[0] 
            mail_subject = "Account Activation"
            message = f"""
            <h1>Account Activation</h1>
            <p>Please click the link below to activate your account:</p>
            <a href="{base_url}/sign-up/activate?token={activation_token}">Activate Account</a>
            """

            email_message = EmailMessage(
                mail_subject, message, to=[email]
            )
            email_message.content_subtype = "html" 
            email_message.send()


            return Response({"message": "User registered successfully, please check your email to activate your account."}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ActivateView(APIView):

    def post(self, request):
        token = request.query
        if not token:
            return Response({"message": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithm="HS256")
            
            existing_user = User.objects.get(email=decoded.email)
            if not existing_user:
                return Response({'message': 'Invalid token'},status=status.HTTP_404_NOT_FOUND)
            
            if existing_user.is_active:
                return Response({'message': 'User already activated'},status=status.HTTP_409_CONFLICT)
            
            existing_user.is_active = True
            existing_user.activation_token = None

            existing_user.save()

            return Response({"message": "User activated successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
