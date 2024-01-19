from rest_framework import serializers
from .models import Participante
import random

class ParticipantesListSerializer(serializers.ModelSerializer):
    formatted_numero_de_participante = serializers.SerializerMethodField()

    class Meta:
        model = Participante
        fields = ['nombre', 'apellidos', 'email', 'sexo', 'formatted_numero_de_participante']

    def get_formatted_numero_de_participante(self, obj):
        return str(obj.numero_de_participante).zfill(4)


class ParticipantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participante
        # Excluye el campo 'numero_de_participante' de la validación
        exclude = ('numero_de_participante',)

    def create(self, validated_data):
        # Obtener el número de participante más alto en la base de datos
        max_participante = Participante.objects.all().order_by('-numero_de_participante').first()

        # Si aún no hay participantes en la base de datos, comenzamos desde 001.
        if max_participante is None:
            numero = 1
        else:
            numero = max_participante.numero_de_participante + 1

        # Aquí convertimos el número a una cadena y luego lo rellenamos con ceros a la izquierda para tener al menos 3 dígitos
        numero_str = str(numero).zfill(4)

        validated_data['numero_de_participante'] = numero_str
        participante = super().create(validated_data)
        return participante