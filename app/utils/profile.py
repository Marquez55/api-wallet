# -*- coding: utf-8 -*-
from rest_framework import status

from app.user.models import Profile
from app.utils.errors import CustomValidation


def userProfile(pk):
    try:
        return Profile.objects.get(pk=pk)
    except Profile.DoesNotExist:
        raise CustomValidation(
            'perfil', detail='El usuario solicitado no cuenta con un perfil', status_code=status.HTTP_404_NOT_FOUND)
