import random
import string

def generateToken(length=32):
    """
    Generar un token aleatorio de longitud específica.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
