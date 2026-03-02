from rest_framework import serializers
from rest_framework.response import Response
from django.db.models import Sum
from app.proyect.models import Proyecto, PagoProyecto



class ProyectoSerializer(serializers.ModelSerializer):
    total_pagado = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'activo']

    def get_total_pagado(self, obj):
        total = PagoProyecto.objects.filter(proyecto=obj, activo=True).aggregate(
            total=Sum('monto')
        )['total']
        return float(total) if total else 0



class PagoProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoProyecto
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'activo']
