from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from drf_yasg.utils import swagger_auto_schema

from app.email.reset_password import resetPassword
from app.utils.errors import BAD_REQUEST
from app.utils.password import valid_password
from app.authentication.serializers import ChangePasswordSerializer, EmailSerializer, PasswordSerializer
from app.authentication.swagger import validateEmailDocs, resetPasswordSwagger, updateResetPasswordSwagger, userSwagger
from datetime import datetime


class ValidateEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, token=None):
        try:

            decoded_token = UntypedToken(token)
            user_id = decoded_token.get('user_id')

            if not user_id:
                return Response({"error": "El token no contiene un user_id válido."}, status=status.HTTP_400_BAD_REQUEST)

            # Obtén el usuario y verifica si ya está activado
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return Response({"error": "Este usuario ya está activado."}, status=status.HTTP_400_BAD_REQUEST)

            # Activa el usuario
            user.is_active = True
            user.save()

            return Response(status=status.HTTP_200_OK, data={'message': 'El usuario se activó correctamente.'})

        except TokenError as e:
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)


class ChangePassword(APIView):
    """
    Servicio que se encarga de cambiar el password de un usuario.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=userSwagger('', 'Actualiza el password de un usuario', 'User')[1])
    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pass_valid = authenticate(username=request.user, password=request.data.get('password'))

        if pass_valid is None:
            return Response(data={'message': 'La contraseña actual es incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        if actualizarPassCorrecto(request.user.id, request.data.get('newPassword')) == False:
            return BAD_REQUEST("newPassword", 'No cumple con los requisitos minimos solicitados')

        return Response(status=status.HTTP_201_CREATED, data={'result': 'El password se actualizo de forma correcta'})


class ResetPassword(APIView):
    """
    Recupear un password mediante correo electrónico
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=resetPasswordSwagger('', 'Reset password', 'User account')[1])
    def post(self, request, format=None):
        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=request.data.get('email'))
        except User.DoesNotExist:
            return Response(data={"username": "Nombre de usuario incorrecto"}, status=status.HTTP_409_CONFLICT)

        if not user.is_active:
            return Response(data={"username": "El usuario está inactivo"}, status=status.HTTP_409_CONFLICT)

        # Aquí se puede generar un JWT y enviarlo por correo
        refresh = RefreshToken.for_user(user)
        resetPassword(user, str(refresh.access_token))  # Envía el token JWT por correo

        return Response(status=status.HTTP_200_OK, data={'result': 'Se ha enviado un correo electrónico para restablecer'})




class updateResetPassword(APIView):
    """
    Actualiza la contraseña de un usuario al cual se le envió un email con token.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=updateResetPasswordSwagger('', 'Update reset password', 'User account')[1])
    def post(self, request, token, format=None):

        serializer = PasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:

            payload = AccessToken(token).payload
            user_id = payload.get('user_id')
        except TokenError:
            return Response({"token": "Token inválido o expirado"}, status=status.HTTP_409_CONFLICT)

        if not user_id:
            return Response({"error": "El token no contiene información válida del usuario"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar al usuario usando el user_id extraído del token
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar la contraseña del usuario
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 8:  # Validación básica
            return Response({"error": "La contraseña no cumple con los requisitos mínimos"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"result": "La contraseña se actualizó correctamente"}, status=status.HTTP_201_CREATED)



def actualizarPassCorrecto(user_id, password):
    if valid_password(password):
        try:
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            return True
        except Exception as e:
            return False
    return False
