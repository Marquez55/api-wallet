from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import threading


def execSendMail(msg):
    msg.send()


def sendEmail(templateHtml, templateTxt, data, headerEmail):
    """
            Función que se encarga de enviar los email,
            cualquier tipo de email podrá ser enviado
            desde está funcón.
    """

    plaintext = get_template(templateTxt)
    htmly = get_template(templateHtml)

    context = dict({'data': data})

    subject, from_email, to = headerEmail['subject'], headerEmail['from_email'], headerEmail['to']
    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    t = threading.Thread(target=execSendMail, args=(msg, ))
    t.start()


def sendEmailWhitAttachmen(templateHtml, templateTxt, data, headerEmail, pdf):
    """
            Función que se encarga de enviar los email,
            cualquier tipo de email podrá ser enviado
            desde está funcón.
    """

    plaintext = get_template(templateTxt)
    htmly = get_template(templateHtml)

    context = dict({'data': data})

    subject, from_email, to = headerEmail['subject'], headerEmail['from_email'], headerEmail['to']
    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    t = threading.Thread(target=execSendMail, args=(msg, ))
    t.start()


def createEmailList(templateHtml, templateTxt, data, headerEmail, connection):
    """
            Función que se encarga de crear las instancias para
            los email que se van a enviar.
    """
    plaintext = get_template(templateTxt)
    htmly = get_template(templateHtml)

    context = dict(data)
    subject, from_email, to = headerEmail['subject'], headerEmail['from_email'], headerEmail['to']
    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to, connection=connection)
    msg.attach_alternative(html_content, "text/html")

    return msg