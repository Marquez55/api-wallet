from config.settings import URL_APP, DEFAULT_FROM_EMAIL, EMAIL_DEFAULT_ACTIVE, EMAIL_DEFAULT_TO
from app.email.sendEmail import sendEmail


def resetPassword(user, token):
    """
        Función que se encarga de enviar un mail al usuario
        para recuperar su contraseña
    """

    emailTo = user.email
    if EMAIL_DEFAULT_ACTIVE:
        emailTo = EMAIL_DEFAULT_TO

    subject = 'Restablecer contraseña'
    templateHtml = 'reset_password.html'
    templateTxt = 'reset_password.txt'
    segmento_url = 'reestablecer-contraseña/%s' %token

    data = {
        'usuario': {
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'url': URL_APP + segmento_url,
        'domain': URL_APP,
        'phone': 'PHONE',
        'email_suport': 'EMAIL_SUPORT',
        'facebook': 'FACEBOOK',
        'twitter': 'TWITTER',
        'instagram': 'INSTAGRAM'
    }

    headerEmail = {
        'subject': subject,
        'from_email': DEFAULT_FROM_EMAIL,
        'to': [emailTo]
    }

    sendEmail(templateHtml, templateTxt, data, headerEmail)