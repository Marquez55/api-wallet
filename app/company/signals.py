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
        # Crear roles si no existen
        Rol.objects.create(clave='Empresa', descripcion='Empresa', activo=True)
        Rol.objects.create(clave='Administrador', descripcion='Administrador', activo=True)
        Rol.objects.create(clave='Editor', descripcion='Editor', activo=True)

    # Verificar si la empresa ya existe
    if Company.objects.count() == 0:
        # Crear empresa si no existe
        company = Company.objects.create(nombre='Wallet Nexuz', activo=True,
                                         descripcion='Wallet Nexuz billetera digital',
                                         direccion='México')

        # Crear un usuario y un perfil vinculados a la empresa (solo para la primera migración)
        user = User.objects.create(
            first_name='Wallet',
            last_name='Nexuz',
            username='wallet@nexuzcorp.com',
            email='wallet@nexuzcorp.com',
            is_active=False  # Lo marcamos como inactivo hasta que valide su correo
        )

        user.set_password('Nexuz@21!')  # Contraseña predeterminada (cámbiala si es necesario)
        user.save()

        # Asociar perfil con usuario y empresa
        perfil = Perfil.objects.create(user=user, rol_id=1, company=company)
        perfil.save()

        # Generar token JWT de validación
        refresh = RefreshToken.for_user(user)
        jwt_token = str(refresh.access_token)

        # Enviar el token por correo (modifica la lógica de `nuevoUsuarioMail` para incluir el token JWT)
        nuevoUsuarioMail(user, jwt_token)

