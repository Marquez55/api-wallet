from config.settings import URL_APP, DEFAULT_FROM_EMAIL, EMAIL_DEFAULT_ACTIVE, EMAIL_DEFAULT_TO
from app.email.sendEmail import sendEmail

def enviarNumeroParticipanteMail(email, nombre, apellidos, numero_de_participante):
    """
    Función que se encarga de enviar un mail al participante con su número.
    """
    emailTo = email
    if EMAIL_DEFAULT_ACTIVE:
        emailTo = EMAIL_DEFAULT_TO

    subject = 'Gracias por participar'
    templateHtml = 'numero_participante.html'
    templateTxt = 'numero_participante.txt'

    data = {
        'nombre': nombre,  # Añade el nombre al contexto del correo
        'apellidos': apellidos,
        'numero_de_participante': numero_de_participante
    }

    headerEmail = {
        'subject': subject,
        'from_email': DEFAULT_FROM_EMAIL,
        'to': [emailTo]
    }

    sendEmail(templateHtml, templateTxt, data, headerEmail)

