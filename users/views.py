import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import render

import jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User no found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!!')

        now = datetime.datetime.now(datetime.timezone.utc)

        payload = {
            'id': user.id,
            'exp': int((now + datetime.timedelta(minutes=60)).timestamp()),  # стандарт JWT — exp
            'iat': int(now.timestamp())
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response
