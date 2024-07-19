from django.db.models.signals import post_migrate
from django.dispatch import receiver
from app.empresa.models import Empresa
from app.user.models import Rol, Perfil
from app.authvalidate.models import TokenEmail
from app.utils.token import generateToken
from app.email.nuevo_usuario import nuevoUsuarioMail
from django.contrib.auth.models import User

@receiver(post_migrate)
def create_roles_and_empresa(sender, **kwargs):
    # Verificar si los roles ya existen solo es para la primera migraciòn
    if Rol.objects.count() == 0:
        # Crear roles si no existen
        Rol.objects.create(clave='Empresa', descripcion='Empresa', activo=True)
        Rol.objects.create(clave='Administrador', descripcion='Administrador', activo=True)
        Rol.objects.create(clave='Usuario', descripcion='Usuario', activo=True)

    # Verificar si la empresa ya existe
    if Empresa.objects.count() == 0:
        # Crear empresa si no existe
        empresa = Empresa.objects.create(nombre='Wallet Nexuz', activo=True,
                                         descripcion='Wallet Nexuz es una empresa de tecnología',
                                         direccion='Puebla')

        # Crear un usuario y un perfil vinculados a la empresa solo es para la primera migraciòn
        user = User.objects.create(
            first_name='Wallet',
            last_name='Nexuz',
            username='wallet@nexuz.com',
            email='wallet@nexuz.com',
            is_active=True
        )

        user.set_password('Wallet@21h!')  # Cambia esto por la contraseña predeterminada que desees solo es para la primera migraciòn

        user.save()

        perfil = Perfil.objects.create(user=user, rol_id=1, empresa=empresa)

        perfil.save()

        token = ''
        try:
            tokenEmail = TokenEmail.objects.get(user_id=user.id, typeToken="C")
            token = tokenEmail.token
        except TokenEmail.DoesNotExist:
            token = generateToken(32)
            tokenEmail = TokenEmail(user=user, token=token, typeToken="C")
            tokenEmail.save()

        nuevoUsuarioMail(user, token)