import random
import string


def generateToken(longitud):
    return ''.join(random.choice(string.digits) for i in range(longitud))
