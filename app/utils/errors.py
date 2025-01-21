from rest_framework.response import Response
from rest_framework import status

def BAD_REQUEST(field, message):
    return Response({field: message}, status=status.HTTP_400_BAD_REQUEST)
