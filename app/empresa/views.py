from django.shortcuts import render


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


from django.contrib.auth.models import User
from django.db import IntegrityError

from app.empresa.models import Empresa
from app.empresa.serializers import EmpresaSerializer

from app.user.models import Perfil
from app.authvalidate.models import TokenEmail

from app.utils.token import generateToken

from app.email.nuevo_usuario import nuevoUsuarioMail

# Create your views here.


class EmpresaAPIView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Crea unanueva empresa

        Servicio que permite crear una nueva empresa para usar el inventario

        *Campos requeridos*

        - **nombre\***
        - **first_name\***
        - **last_name\***
        - **email\***
        - **password\***
        """

        serializer = EmpresaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dataRequest = serializer.data

        try:
            empresa = Empresa(nombre=dataRequest.pop('nombre'))
            empresa.save()
        except Exception as e:
            return Response(data={'message': 'no se puede crear la empresa', 'error-code': 'EMP-001'})

        user = User(
            first_name=dataRequest['first_name'], last_name=dataRequest['last_name'],
            username=dataRequest['email'], email=dataRequest['email'], is_active=False
        )

        user.set_password(dataRequest['password'])

        try:
            user.save()
        except IntegrityError as e:
            empresa.delete()
            return Response(data={"message": "email already exist"}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            empresa.delete()
            return Response(data={"message": "error to create user"}, status=status.HTTP_400_BAD_REQUEST)

        perfil = Perfil(user=user, rol_id=1, empresa_id=empresa.id)

        try:
            perfil.save()
        except Exception as e:
            user.delete()
            empresa.delete()
            return Response(data={"message": "error to create profile of user"}, status=status.HTTP_400_BAD_REQUEST)

        token = ''
        try:
            tokenEmail = TokenEmail.objects.get(user_id=user.id, typeToken="C")
            token = tokenEmail.token
        except TokenEmail.DoesNotExist:
            token = generateToken(32)
            tokenEmail = TokenEmail(user=user, token=token, typeToken="C")
            tokenEmail.save()

        nuevoUsuarioMail(user, token)

        # return Response(data=us, status=status.HTTP_201_CREATED)

        return Response(data={"message": "Empresa creada"}, status=status.HTTP_201_CREATED)
