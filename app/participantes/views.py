from django.shortcuts import render
from app.email.nuevo_registro import enviarNumeroParticipanteMail
from app.participantes.models import Participante
from app.participantes.serializers import ParticipantesListSerializer, ParticipantesSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny



class ParticipantesCreateAPIView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Creación de registro de participantes

        Servicio que crea múltiples documentos de planeación en una sola petición
        """

        # Comprobar si el email ya está registrado
        email = request.data.get('email')
        if Participante.objects.filter(email=email).exists():
            return Response({'error': 'El email ya está registrado.'}, status=status.HTTP_409_CONFLICT)

        serializer = ParticipantesSerializer(data=request.data)
        if serializer.is_valid():
            participante = serializer.save()
            enviarNumeroParticipanteMail(participante.email, participante.nombre, participante.apellidos, participante.numero_de_participante)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParticipantesListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Lista de participantes
        """
        participantes = Participante.objects.all()
        serializer = ParticipantesListSerializer(participantes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ParticipanteSearchByEmailAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Buscar participante por email
        """
        email = request.data.get('email', None)
        
        # Si el email no se envía o está vacío.
        if not email:
            return Response({"error": "El email es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        participantes = Participante.objects.filter(email=email)

        # Si no hay resultados en la búsqueda.
        if not participantes.exists():
            return Response({"error": "Email no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParticipantesListSerializer(participantes, many=True)
        
        # Envolvemos el resultado en un diccionario con la clave "participantes"
        return Response({"participantes": serializer.data}, status=status.HTTP_200_OK)

