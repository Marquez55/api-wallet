from rest_framework import serializers
from django.db.models import Sum
from app.proyect.models import (
    Proyecto,
    PagoProyecto,
    Presupuesto,
    PresupuestoCategoria,
    PresupuestoPartida
)



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


class PresupuestoSerializer(serializers.ModelSerializer):
    total_estimado = serializers.SerializerMethodField()
    total_categorias = serializers.SerializerMethodField()
    total_partidas = serializers.SerializerMethodField()

    class Meta:
        model = Presupuesto
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'activo']

    def get_total_estimado(self, obj):
        total = PresupuestoPartida.objects.filter(
            presupuesto=obj,
            activo=True
        ).aggregate(total=Sum('monto_estimado'))['total']
        return float(total) if total else 0

    def get_total_categorias(self, obj):
        return PresupuestoCategoria.objects.filter(presupuesto=obj, activo=True).count()

    def get_total_partidas(self, obj):
        return PresupuestoPartida.objects.filter(presupuesto=obj, activo=True).count()


class PresupuestoCategoriaSerializer(serializers.ModelSerializer):
    nivel = serializers.SerializerMethodField()
    total_estimado = serializers.SerializerMethodField()

    class Meta:
        model = PresupuestoCategoria
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'activo']

    def validate(self, attrs):
        presupuesto = attrs.get('presupuesto') or getattr(self.instance, 'presupuesto', None)
        padre = attrs.get('padre') if 'padre' in attrs else getattr(self.instance, 'padre', None)

        if padre and presupuesto and padre.presupuesto_id != presupuesto.id:
            raise serializers.ValidationError({
                'padre': 'La categoría padre debe pertenecer al mismo presupuesto.'
            })

        return attrs

    def get_nivel(self, obj):
        nivel = 0
        actual = obj.padre
        while actual:
            nivel += 1
            actual = actual.padre
        return nivel

    def get_total_estimado(self, obj):
        total = PresupuestoPartida.objects.filter(
            categoria=obj,
            activo=True
        ).aggregate(total=Sum('monto_estimado'))['total']
        return float(total) if total else 0


class PresupuestoPartidaSerializer(serializers.ModelSerializer):
    total_calculado = serializers.SerializerMethodField()

    class Meta:
        model = PresupuestoPartida
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'activo']

    def validate(self, attrs):
        presupuesto = attrs.get('presupuesto') or getattr(self.instance, 'presupuesto', None)
        categoria = attrs.get('categoria') or getattr(self.instance, 'categoria', None)

        if categoria and presupuesto and categoria.presupuesto_id != presupuesto.id:
            raise serializers.ValidationError({
                'categoria': 'La categoría debe pertenecer al mismo presupuesto.'
            })

        return attrs

    def get_total_calculado(self, obj):
        cantidad = float(obj.cantidad or 0)
        costo_unitario = float(obj.costo_unitario or 0)
        return round(cantidad * costo_unitario, 2)
