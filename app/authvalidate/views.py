
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from app.utils.errors import BAD_REQUEST
from app.utils.password import valid_password
from app.utils.token import generateToken

from app.email.reset_password import resetPassword

from app.authvalidate.models import TokenEmail
from app.authvalidate.serializers import ChangePasswordSerializer, EmailSerializer, PasswordSerializer
from app.authvalidate.swagger import validateEmailDocs, resetPasswordSwagger, updateResetPasswordSwagger, userSwagger


from datetime import datetime


# Create your views here.


class ValidateEmail(APIView):
    """
        Valida una cuenta de correo electrónico

        Servicio que se utiliza para la validación de un correo electrónico
    """

    permission_classes = (AllowAny,)
    response_post, request_params_form = validateEmailDocs()

    @swagger_auto_schema(manual_parameters=request_params_form,  responses={
        200: response_post, 404: "User or token are not valid", 409: "account already validated"})
    def put(self, request, format=None, userID=None, token=None,):

        try:
            tokenEmail = TokenEmail.objects.get(
                user_id=userID, token=token, typeToken='C')
        except TokenEmail.DoesNotExist:
            return Response(data={'message': 'El codigo de confirmación no es valido, por favor solicita un nuevo codigo'}, status=status.HTTP_409_CONFLICT)

        cantidad = User.objects.filter(pk=userID).update(is_active=True)

        if cantidad < 1:
            return Response(data={'message': 'User i not valid'}, status=status.HTTP_409_CONFLICT)

        tokenEmail.delete()
        return Response(status=status.HTTP_200_OK, data={'user': 'El usuario se activo de forma correcta'})


class ChangePassword(APIView):
    """
            Servicio que se encarga de cambiar el password de un usuario.
            Campos requeridos

            1.- password
            2.- newPassword

            Caracteristicas que debe tener el nuevo password.
                - At least 1 letter between [a-z] and 1 letter between [A-Z].
                - At least 1 number between [0-9].
                - At least 1 character from [$#@].
                - Minimum length 6 characters.
                - Maximum length 16 characters.
    """

    permission_classes = (IsAuthenticated,)
    response_post, request_body_post = userSwagger(
        '', 'Actualiza el password de un usuario', 'User')

    @swagger_auto_schema(request_body=request_body_post, responses={
        201: response_post, 400: "Error from bad request"}, )
    def post(self, request, format=None):

        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pass_valid = authenticate(
            username=request.user,
            password=request.data.get('password'))

        if pass_valid is None:
            return Response(data={'message': 'La contraseña actual es incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        if actualizarPassCorrecto(request.user.id,  request.data.get('newPassword')) == False:
            return BAD_REQUEST("newPassword", u'No cumple con los requisitos minimos solicitados')

        return Response(status=status.HTTP_201_CREATED, data={'result': 'El password se actualizo de forma correcta'})


class ResetPassword(APIView):
    """
        Recupear un password mediante correo electrónico

        Servicio que se encarga de solicitar la recuperación de contraseña
        para un usuario. El campo necesario obligatorio es  {'email':'email@com.mx'}
    """
    permission_classes = (AllowAny,)
    response_post, request_body_post = resetPasswordSwagger(
        '', 'Reset pasword', 'User account')

    @swagger_auto_schema(request_body=request_body_post, responses={
        200: response_post, 400: "Error from bad request", 409: "User does not exist"}, )
    def post(self, request, format=None):

        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=request.data.get('email'))
        except User.DoesNotExist:
            return Response(data={"username": "Nombre de usuario incorrecto"}, status=status.HTTP_409_CONFLICT)

        token = ''
        try:
            tokenEmail = TokenEmail.objects.get(user_id=user.id, typeToken='R')
            token = tokenEmail.token
        except TokenEmail.DoesNotExist:
            token = generateToken(32)
            tokenEmail = TokenEmail(
                user=user, token=token, typeToken="R", date=datetime.now())
            tokenEmail.save()

        resetPassword(user, token)

        return Response(status=status.HTTP_200_OK, data={'result': 'Se ha enviado un correo electronico para restablecer'})


class updateResetPassword(APIView):
    """
        Actualiza la contraseña de un usuario al cual se le envío un email con token

        Servicio que se encarga de actualizar el pasword de un usuario
        el cual solicito reestablecerlo por medio del correo electronico.
    """
    permission_classes = (AllowAny, )
    response_post, request_body_post, params_path = updateResetPasswordSwagger(
        '', 'Update reset pasword', 'User account')

    @swagger_auto_schema(request_body=request_body_post, manual_parameters=params_path, responses={
        201: response_post, 400: "Error from bad request", 409: "Token is not valid"}, )
    def post(self, request, userID, token, format=None):
        serializer = PasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            tokenEmail = TokenEmail.objects.get(
                token=token, user_id=userID, typeToken='R')
        except Exception as e:
            tokenEmail = None

        if not tokenEmail:
            return Response(data={"token": "Token invalido"}, status=status.HTTP_409_CONFLICT)

        if actualizarPassCorrecto(userID,  request.data.get('password')) == False:
            return BAD_REQUEST("newPassword", u'No cumple con los requisitos minimos solicitados')

        tokenEmail.delete()

        return Response(status=status.HTTP_201_CREATED, data={'result': 'El password se actualizo de forma correcta'})


def actualizarPassCorrecto(user_id, password):
    """
            Función que se utiliza unicamente para actualizar el password
            de un usuario
    """
    if valid_password(password):
        try:
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
        except Exception as e:
            return False
    else:
        return False
    return True
