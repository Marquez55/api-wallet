from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from app.company.models import Company
from app.user.models import Rol, Perfil
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken  # Importamos JWT
from app.email.nuevo_usuario import nuevoUsuarioMail  # Módulo que enviará el correo con el token JWT


@receiver(post_migrate)
def create_roles_and_company(sender, **kwargs):
    # Verificar si los roles ya existen (solo para la primera migración)
    if Rol.objects.count() == 0:
        Rol.objects.bulk_create([
            Rol(clave='Empresa', descripcion='Empresa', activo=True),
            Rol(clave='Administrador', descripcion='Administrador', activo=True),
            Rol(clave='Usuario', descripcion='Usuario', activo=True),
            Rol(clave='Nexuz', descripcion='Nexuz', activo=True),
        ])

    # Verificar si la empresa ya existe
    if Company.objects.count() == 0:
        # Crear empresa si no existe
        company = Company.objects.create(
            nombre='Wallet Nexuz',
            activo=True,
            descripcion='Wallet Nexuz billetera digital',
            direccion='México'
        )

        # Definir la contraseña antes de crear el usuario
        password = 'Nexuz@21!'

        # Crear usuario
        user = User.objects.create(
            first_name='Wallet',
            last_name='Nexuz',
            username='wallet@nexuzcorp.com',
            email='wallet@nexuzcorp.com',
            is_active=False  # Lo marcamos como inactivo hasta que valide su correo
        )
        user.set_password(password)  # Asignar la contraseña
        user.save()

        # Asociar perfil con usuario y empresa
        perfil = Perfil.objects.create(user=user, rol_id=1, company=company)

        # Generar token JWT de validación
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)

        # Enviar el token y la contraseña por correo
        nuevoUsuarioMail(user, jwt_token, password)


