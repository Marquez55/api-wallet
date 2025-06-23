from rest_framework import serializers
from django.db import models
from app.financing.models import Prestamo, PagosPrestamo, ConceptoPrestamo


class PrestamoSerializer(serializers.ModelSerializer):
    total_pagado = serializers.SerializerMethodField()
    total_restante = serializers.SerializerMethodField()

    class Meta:
        model = Prestamo
        fields = ['id', 'nombre', 'monto', 'total_pagado', 'total_restante']

    def get_total_pagado(self, obj):
        pagos = obj.pagos.filter(activo=True)
        total = pagos.aggregate(total=models.Sum('monto'))['total']
        return float(total) if total else 0.0

    def get_total_restante(self, obj):
        total_pagado = self.get_total_pagado(obj)
        return float(obj.monto) - total_pagado

class PagosPrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagosPrestamo
        fields = ['id', 'prestamo', 'monto', 'fecha_pago']



class ConceptoPrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoPrestamo
        fields = '__all__'
        read_only_fields = ['id', 'activo']