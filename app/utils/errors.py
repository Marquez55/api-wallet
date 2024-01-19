# -*- coding: utf-8 -*-
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.encoding import force_text

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Lo setimos, ha ocurrido un error interno del servidor que no podemos solventar'

    def __init__(self, detail, field, status_code):
        if status_code is not None: self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_text(detail)}
        else: self.detail = {'detail': force_text(self.default_detail)}



def BAD_REQUEST(clave, mensaje):
	if mensaje is None:
		mensaje = "Campo obligatorio"
	raise CustomValidation(mensaje, clave, status_code = status.HTTP_400_BAD_REQUEST)