from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from app.user.serializers import UserSerializer
from app.user.models import Perfil, Rol, Administradores, Usuario, Nexuz
from app.utils.paginator import CustomPagination

from app.company.models import Company

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from app.email.nuevo_admin import nuevoAdminMail
from app.email.nuevo_usuario import nuevoUsuarioMail
from rest_framework.generics import UpdateAPIView
import logging





class ListUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Listado de usuarios (usuarios, administradores y Nexuz) de la empresa autenticada.
        Visible para administradores y empresas.
        """
        company = None

        # Determinar si el usuario es una empresa o un administrador
        try:
            # Si es una empresa, obtener la compañía desde el perfil
            perfil = Perfil.objects.get(user=request.user)
            company = perfil.company
        except ObjectDoesNotExist:
            # Si no tiene perfil, verificar si es un administrador
            try:
                administrador = Administradores.objects.get(email=request.user.email)
                company = administrador.empresa
            except Administradores.DoesNotExist:
                return Response({"error": "El usuario no tiene permisos para acceder al listado."},
                                status=status.HTTP_403_FORBIDDEN)

        if not company:
            return Response({"error": "No se pudo determinar la empresa asociada."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Filtrar usuarios por la empresa y excluir al usuario autenticado
        usuarios = Usuario.objects.filter(empresa=company).exclude(email=request.user.email)
        administradores = Administradores.objects.filter(empresa=company).exclude(email=request.user.email)
        nexuz = Nexuz.objects.filter(empresa=company).exclude(email=request.user.email)

        # Preparar los datos para el serializer
        all_users = []

        for usuario in usuarios:
            try:
                rol = Rol.objects.get(id=usuario.rol_id)
                nombre_rol = rol.descripcion
            except Rol.DoesNotExist:
                nombre_rol = "Desconocido"

            all_users.append({
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellidoP": usuario.apellidoP,
                "apellidoM": usuario.apellidoM,
                "email": usuario.email,
                "avatar": usuario.avatar,
                "theme": usuario.theme,
                "rol": usuario.rol_id,
                "nombreRol": nombre_rol,
                "tipo_usuario": 3  # Usuario
            })

        for administrador in administradores:
            try:
                rol = Rol.objects.get(id=administrador.rol_id)
                nombre_rol = rol.descripcion
            except Rol.DoesNotExist:
                nombre_rol = "Desconocido"

            all_users.append({
                "id": administrador.id,
                "nombre": administrador.nombre,
                "apellidoP": administrador.apellidoP,
                "apellidoM": administrador.apellidoM,
                "email": administrador.email,
                "avatar": administrador.avatar,
                "theme": administrador.theme,
                "rol": administrador.rol_id,
                "nombreRol": nombre_rol,
                "tipo_usuario": 2  # Administrador
            })

        for user_nexuz in nexuz:
            try:
                rol = Rol.objects.get(id=user_nexuz.rol_id)
                nombre_rol = rol.descripcion
            except Rol.DoesNotExist:
                nombre_rol = "Desconocido"

            all_users.append({
                "id": user_nexuz.id,
                "nombre": user_nexuz.nombre,
                "apellidoP": user_nexuz.apellidoP,
                "apellidoM": user_nexuz.apellidoM,
                "email": user_nexuz.email,
                "avatar": user_nexuz.avatar,
                "theme": user_nexuz.theme,
                "rol": user_nexuz.rol_id,
                "nombreRol": nombre_rol,
                "tipo_usuario": 4  # Nexuz
            })

        # Aplicar paginación
        paginator = CustomPagination()
        paginated_response = paginator.paginate_queryset(all_users, request)
        return paginator.get_paginated_response(paginated_response, "usuarios")




class CreateUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Crea un nuevo usuario, administrador o Nexuz

        Permite a la empresa o administrador crear un nuevo usuario, administrador o Nexuz.
        """

        # 🔹 Validar si el usuario autenticado tiene permisos para crear usuarios
        company = None

        try:
            # Si es una empresa, obtener la compañía desde el perfil
            perfil = Perfil.objects.get(user=request.user)
            company = perfil.company
        except ObjectDoesNotExist:
            # Si no tiene perfil, verificar si es un administrador
            try:
                administrador = Administradores.objects.get(email=request.user.email)
                company = administrador.empresa
            except Administradores.DoesNotExist:
                return Response(
                    {"error": "El usuario no tiene permisos para crear usuarios."},
                    status=status.HTTP_403_FORBIDDEN
                )

        if not company:
            return Response(
                {"error": "No se pudo determinar la empresa asociada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Generar contraseña aleatoria para el usuario
        password_aleatoria = get_random_string(length=10)
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 🔹 Verificar si el correo ya está registrado
        if User.objects.filter(email=data['email']).exists():
            return Response(
                data={'email': 'El correo electrónico ya está registrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Obtener el rol
        rol_id = data['tipo_usuario']
        try:
            rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            return Response(
                data={'tipo_usuario': 'Rol no válido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Crear usuario en auth_user
        user = User.objects.create_user(
            username=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=password_aleatoria,
            is_active=False  # El usuario no se activa automáticamente
        )

        # 🔹 Obtener avatar y theme con valores predeterminados si no se envían
        avatar = data.get('avatar', 'user-1.jpg')
        theme = data.get('theme', 'light')

        # 🔹 Crear el perfil según el tipo de usuario
        if rol_id == 3:  # Usuario
            perfil = Usuario(
                id=user.id,
                nombre=data['first_name'],
                apellidoP=data['last_name'],
                apellidoM=data['apellidoM'],
                email=data['email'],
                empresa=company,
                rol=rol,
                avatar=avatar,
                theme=theme,
            )
        elif rol_id == 2:  # Administrador
            perfil = Administradores(
                id=user.id,
                nombre=data['first_name'],
                apellidoP=data['last_name'],
                apellidoM=data['apellidoM'],
                email=data['email'],
                empresa=company,
                rol=rol,
                avatar=avatar,
                theme=theme,
            )
        elif rol_id == 4:  # Nexuz
            perfil = Nexuz(
                id=user.id,
                nombre=data['first_name'],
                apellidoP=data['last_name'],
                apellidoM=data['apellidoM'],
                email=data['email'],
                empresa=company,
                rol=rol,
                avatar=avatar,
                theme=theme,
            )
        else:
            return Response(
                data={'tipo_usuario': 'Rol no válido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        perfil.save()

        # 🔹 Generar token JWT de validación
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)

        # 🔹 Enviar correo electrónico (según el rol)
        if rol_id == 3:  # Usuario
            nuevoUsuarioMail(user, jwt_token, password_aleatoria)
        elif rol_id == 2:  # Administrador
            nuevoAdminMail(user, jwt_token, password_aleatoria)
        elif rol_id == 4:  # Nexuz
            nuevoUsuarioMail(user, jwt_token, password_aleatoria)

        # 🔹 Devolver la respuesta con los datos originales
        return Response(data=data, status=status.HTTP_201_CREATED)



class UpdateUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, user_id):
        """
        Permite a una empresa o administrador actualizar un usuario existente, incluyendo el cambio de correo.
        """
        company = None

        # 🔹 Validar si el usuario autenticado tiene permisos para actualizar usuarios
        try:
            # Si es una empresa, obtener la compañía desde el perfil
            perfil = Perfil.objects.get(user=request.user)
            company = perfil.company
        except ObjectDoesNotExist:
            # Si no tiene perfil, verificar si es un administrador
            try:
                administrador = Administradores.objects.get(email=request.user.email)
                company = administrador.empresa
            except Administradores.DoesNotExist:
                return Response(
                    {"error": "El usuario no tiene permisos para actualizar usuarios."},
                    status=status.HTTP_403_FORBIDDEN
                )

        if not company:
            return Response(
                {"error": "No se pudo determinar la empresa asociada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Verificar si el usuario existe
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔹 Verificar si el usuario tiene un perfil (Usuario, Administrador o Nexuz)
        perfil = None
        if Usuario.objects.filter(id=user.id, empresa=company).exists():
            perfil = Usuario.objects.get(id=user.id)
        elif Administradores.objects.filter(id=user.id, empresa=company).exists():
            perfil = Administradores.objects.get(id=user.id)
        elif Nexuz.objects.filter(id=user.id, empresa=company).exists():
            perfil = Nexuz.objects.get(id=user.id)
        else:
            return Response(
                {"error": "El usuario no pertenece a la empresa."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 🔹 Serializar los datos de entrada
        data = request.data

        # 🔹 Permitir cambio de correo, pero validar que no esté repetido
        nuevo_email = data.get("email", user.email)
        if nuevo_email != user.email:
            if User.objects.filter(email=nuevo_email).exclude(id=user.id).exists():
                return Response(
                    {"error": "El nuevo correo ya está registrado en otro usuario."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = nuevo_email
            perfil.email = nuevo_email  # Actualizar en el modelo de perfil también

        # 🔹 Validar y actualizar los demás campos
        perfil.nombre = data.get("first_name", perfil.nombre)
        perfil.apellidoP = data.get("last_name", perfil.apellidoP)
        perfil.apellidoM = data.get("apellidoM", perfil.apellidoM)
        perfil.avatar = data.get("avatar", perfil.avatar)
        perfil.theme = data.get("theme", perfil.theme)

        # 🔹 Actualizar el rol si se envía
        if "tipo_usuario" in data:
            try:
                nuevo_rol = Rol.objects.get(id=data["tipo_usuario"])
                perfil.rol = nuevo_rol
            except Rol.DoesNotExist:
                return Response(
                    {"error": "El rol proporcionado no es válido."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        perfil.save()

        # 🔹 Actualizar el usuario en `auth_user`
        user.first_name = perfil.nombre
        user.last_name = perfil.apellidoP  # Se mantiene el apellido paterno en `auth_user`
        user.save()

        return Response(
            {"message": "Usuario actualizado exitosamente."},
            status=status.HTTP_200_OK
        )



#Informacion del perfil

class UsuarioInfoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id

        try:
            # 1. Verificar si el usuario tiene un Perfil (empresa)
            perfil = Perfil.objects.get(user_id=user_id)
            company = Company.objects.get(id=perfil.company_id)
            rol = Rol.objects.get(id=perfil.rol_id)

            data = {
                'id': company.id,
                'empresa': company.id,
                'rol': perfil.rol_id,
                'nombreRol': rol.descripcion,
                'nombre': company.nombre,
                'email': request.user.email,
                'avatar': perfil.avatar,
                'theme': perfil.theme

            }
            return Response(data=data, status=status.HTTP_200_OK)

        except Perfil.DoesNotExist:
            try:
                # 2. Verificar si es un Administrador
                administrador = Administradores.objects.get(id=user_id)
                company = Company.objects.get(id=administrador.empresa_id)
                rol = Rol.objects.get(id=administrador.rol_id)

                data = {
                    'id': administrador.id,
                    'nombre': administrador.nombre,
                    'apellidoP': administrador.apellidoP,
                    'apellidoM': administrador.apellidoM,
                    'email': administrador.email,
                    'rol': administrador.rol_id,
                    'nombreRol': rol.descripcion,
                    'empresa': administrador.empresa_id,
                    'nombreEmpresa': company.nombre,
                    'avatar': administrador.avatar,
                    'theme': administrador.theme
                }
                return Response(data=data, status=status.HTTP_200_OK)

            except Administradores.DoesNotExist:
                try:
                    # 3. Verificar si es un Usuario
                    usuario = Usuario.objects.get(id=user_id)
                    company = Company.objects.get(id=usuario.empresa_id)
                    rol = Rol.objects.get(id=usuario.rol_id)

                    data = {
                        'id': usuario.id,
                        'nombre': usuario.nombre,
                        'apellidoP': usuario.apellidoP,
                        'apellidoM': usuario.apellidoM,
                        'email': usuario.email,
                        'rol': usuario.rol_id,
                        'nombreRol': rol.descripcion,
                        'empresa': usuario.empresa_id,
                        'nombreEmpresa': company.nombre,
                        'avatar': usuario.avatar,
                        'theme': usuario.theme
                    }
                    return Response(data=data, status=status.HTTP_200_OK)

                except Usuario.DoesNotExist:
                    try:
                        # 4. Verificar si es un Nexuz
                        nexuz = Nexuz.objects.get(id=user_id)
                        company = Company.objects.get(id=nexuz.empresa_id)
                        rol = Rol.objects.get(id=nexuz.rol_id)

                        data = {
                            'id': nexuz.id,
                            'nombre': nexuz.nombre,
                            'apellidoP': nexuz.apellidoP,
                            'apellidoM': nexuz.apellidoM,
                            'email': nexuz.email,
                            'rol': nexuz.rol_id,
                            'nombreRol': rol.descripcion,
                            'empresa': nexuz.empresa_id,
                            'nombreEmpresa': company.nombre,
                            'avatar': nexuz.avatar,
                            'theme': nexuz.theme
                        }
                        return Response(data=data, status=status.HTTP_200_OK)

                    except Nexuz.DoesNotExist:
                        # Si no se encuentra en ninguna de las tablas
                        return Response(
                            {"detail": "Usuario no encontrado"},
                            status=status.HTTP_404_NOT_FOUND
                        )



class UpdateAvatarAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, user_id):
        avatar = request.data.get('avatar')

        if not avatar:
            return Response({'error': 'Avatar es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            perfil = Perfil.objects.get(user_id=user_id)
            perfil.avatar = avatar
            perfil.save()
            return Response({'message': 'Avatar actualizado'}, status=status.HTTP_200_OK)

        except Perfil.DoesNotExist:
            try:
                admin = Administradores.objects.get(id=user_id)
                admin.avatar = avatar
                admin.save()
                return Response({'message': 'Avatar actualizado'}, status=status.HTTP_200_OK)

            except Administradores.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(id=user_id)
                    usuario.avatar = avatar
                    usuario.save()
                    return Response({'message': 'Avatar actualizado'}, status=status.HTTP_200_OK)

                except Usuario.DoesNotExist:
                    try:
                        nexuz = Nexuz.objects.get(id=user_id)
                        nexuz.avatar = avatar
                        nexuz.save()
                        return Response({'message': 'Avatar actualizado'}, status=status.HTTP_200_OK)

                    except Nexuz.DoesNotExist:
                        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class UpdateThemeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, user_id):
        theme = request.data.get('theme')

        if not theme:
            return Response({'error': 'El tema es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            perfil = Perfil.objects.get(user_id=user_id)
            perfil.theme = theme
            perfil.save()
            return Response({'message': 'Tema actualizado'}, status=status.HTTP_200_OK)

        except Perfil.DoesNotExist:
            try:
                admin = Administradores.objects.get(id=user_id)
                admin.theme = theme
                admin.save()
                return Response({'message': 'Tema actualizado'}, status=status.HTTP_200_OK)

            except Administradores.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(id=user_id)
                    usuario.theme = theme
                    usuario.save()
                    return Response({'message': 'Tema actualizado'}, status=status.HTTP_200_OK)

                except Usuario.DoesNotExist:
                    try:
                        nexuz = Nexuz.objects.get(id=user_id)
                        nexuz.theme = theme
                        nexuz.save()
                        return Response({'message': 'Tema actualizado'}, status=status.HTTP_200_OK)

                    except Nexuz.DoesNotExist:
                        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)