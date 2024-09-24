from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import User
import bcrypt
import jwt
from jwt import ExpiredSignatureError
from uuid import uuid4
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .utils import gen_jwt, get_token, get_user_info

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

                jwt_token = gen_jwt(str(existing_user.id), existing_user.email, existing_user.is_staff )

                return Response({
                    "message": "Login successful",
                    "token": jwt_token
                }, status=status.HTTP_200_OK)

            else:
                return Response ('Incorrect Password',
                             status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Internal server error: {e}")
            return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class test(APIView):
    def get(self):
        print('test')


class RegisterView(APIView):

    def post(self, request):
        data = request.data
        full_name = data.get('fullName')
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
        token = request.query_params.get('token')
        if not token:
            return Response({"message": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            decoded = jwt.decode(token, settings.SECRET_KEY,algorithms=["HS256"])
       
            email = decoded.get('email')
            existing_user = User.objects.get(email=email)
            if not existing_user:
                return Response({'message': 'Invalid token'},status=status.HTTP_404_NOT_FOUND)
            
            if existing_user.is_active:
                return Response({'message': 'User already activated'},status=status.HTTP_409_CONFLICT)
            
            existing_user.is_active = True
            existing_user.activation_token = None

            existing_user.save()

            return Response({"message": "User activated successfully."}, status=status.HTTP_200_OK)
        
        except ExpiredSignatureError:
            return Response({"message": "The activation token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
        

        except jwt.InvalidTokenError as e:
            return Response({"message": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserInfoView(APIView):

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"message": "Token is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = jwt.decode(token, settings.SECRET_KEY,algorithms=["HS256"])
       
            email = decoded.get('email')
            existing_user = User.objects.get(email=email)
            if not existing_user:
                return Response({'message': 'Invalid token'},status=status.HTTP_404_NOT_FOUND)
            
     
            return Response({"email":existing_user.email,"isActive":existing_user.is_active}, status=status.HTTP_200_OK)
        
        except ExpiredSignatureError:
            return Response({"message": "The activation token has expired."}, status=status.HTTP_401_UNAUTHORIZED)
     
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
class GoogleLoginView(APIView):
    def post(self, request):

        code = request.data.get('code')
        if not code:
            return Response({'message': 'Authorization code is missing'}, status=status.HTTP_400_BAD_REQUEST)

        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        }

        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            token = tokens.get('id_token')

        try:
            # verify Google ID token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError:
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        # get Google user info
        email = idinfo.get('email')
        full_name = idinfo.get('name')
        google_id = idinfo.get('sub')

        # find/create user
        try:
            user = User.objects.get(email=email)
            if not user.google_id:
                    # Update googleId to the original user
                    user.google_id = google_id
                    user.is_active = True
                    if not user.full_name:
                        user.full_name = full_name 
                    user.save()

        except User.DoesNotExist:
            user_uid = str(uuid4())
            user = User.objects.create(
                id=user_uid,
                email=email,
                is_active=True,
                google_id=google_id,
                full_name=full_name
            )

            mail_subject = "Welcome to ProSync"
            message = f"""
            <h1>Welcome!</h1>
            <p>Thank you for signing up with our service!</p>
            """

            email_message = EmailMessage(
                mail_subject, message, to=[email]
            )
            email_message.content_subtype = "html" 
            email_message.send()

        # create JWT token
        payload = {
                'userUId': str(user.id),  
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(hours=2) 
            }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


        return Response({
                'message': 'Google login successful',
                'token': token
            }, status=status.HTTP_200_OK)

