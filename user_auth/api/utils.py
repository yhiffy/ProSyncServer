import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
import requests
from rest_framework import status


def gen_jwt(id, email, is_staff):

    payload = {
        "user_id": id,
        "email": email,
        "is_staff": is_staff,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return jwt_token

def get_token(code):

    token_url = 'https://oauth2.googleapis.com/token'

    token_data = {
        'code':code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
        }

    token_response = requests.post(token_url, token_data).json()
    access_token = token_response['access_token']

    if 'error' in token_response:
        return Response({'message': 'Error getting token'},status=status.HTTP_400_BAD_REQUEST)

    return access_token

def get_user_info(access_token):

    userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'

    userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'}).json()

    if 'error' in userinfo_response:
        return Response({'message': 'Error getting userinfo'},status=status.HTTP_400_BAD_REQUEST)


    return userinfo_response
