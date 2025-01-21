import re

def valid_password(password):
    """
    Validar que el password cumpla con las siguientes características:
    - Al menos 1 letra minúscula [a-z]
    - Al menos 1 letra mayúscula [A-Z]
    - Al menos 1 número [0-9]
    - Al menos 1 carácter especial [$#@]
    - Longitud mínima: 6 caracteres
    - Longitud máxima: 16 caracteres
    """
    if (len(password) < 6 or len(password) > 16):
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[$#@]", password):
        return False
    return True
