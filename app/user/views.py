from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from app.user.serializers import AdministradorSerializer
from app.user.models import Perfil, Rol, Administradores, Usuario
from app.company.models import Company

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from app.email.nuevo_admin import nuevoAdminMail
from rest_framework.generics import UpdateAPIView
import logging






class CreateAdministradorAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Crea un nuevo administrador

        Permite crear un nuevo administrador para el sistema wallet


        **Campos**

        - **first_name\***
        - **last_name\***
        - **email\***
        - **password\***
        - **rol\***

        """
        password_aleatoria = get_random_string(length=10)
        serializer = AdministradorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Verificar si ya existe un usuario con el mismo correo electrónico
        if User.objects.filter(email=data['email']).exists():
            return Response(data={'email': 'El correo electrónico ya está registrado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtener instancias fijas para empresa, rol y tipo
        empresa = Company.objects.get(id=1)
        rol = Rol.objects.get(id=2)

        # Crear usuario en la tabla de auth_user de Django
        user = User.objects.create_user(
            username=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=password_aleatoria,
            is_active=False
        )

        administrador = Administradores(
            id=user.id,
            nombre=data['first_name'],
            apellidoP=data['last_name'],
            apellidoM=data['apellidoM'],
            email=data['email'],
            empresa=empresa,
            rol=rol,
            activo=False,
        )

        administrador.save()

        # Generar token JWT de validación
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)


        nuevoAdminMail(user, jwt_token, password_aleatoria)

        return Response(data=data, status=status.HTTP_201_CREATED)


#Informacion del perfil

class UsuarioInfoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        try:
            perfil = Perfil.objects.get(user_id=user_id)

            company = Company.objects.get(id=perfil.company_id)

            rol = Rol.objects.get(id=perfil.rol_id)

            data = {
                'id': company.id,
                'empresa': company.id,
                'rol': perfil.rol_id,
                'nombreRol': rol.descripcion,
                'nombre': company.nombre,
                'email': request.user.email
            }
            return Response(data=data, status=status.HTTP_200_OK)

        except Perfil.DoesNotExist:
            try:
                administrador = Administradores.objects.get(id=user_id)
                company = Company.objects.get(id=administrador.company_id)
                rol = Rol.objects.get(id=administrador.rol_id)

                data = {
                    'id': administrador.id,
                    'nombre': administrador.nombre,
                    'apellidoP': administrador.apellidoP,
                    'apellidoM': administrador.apellidoM,
                    'email': administrador.email,
                    'activo': administrador.activo,
                    'rol': administrador.rol_id,
                    'nombreRol': rol.descripcion,
                    'empresa': administrador.company_id_id,
                    'nombreEmpresa': company.nombre  # Asumiendo que quieres incluir el nombre de la empresa
                }
                return Response(data=data, status=status.HTTP_200_OK)

            except Administradores.DoesNotExist:
                return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
