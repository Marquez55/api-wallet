from rest_framework import serializers
from app.cashflow.models import Ingresos, Tipo, Egresos, Subcategoria

class IngresosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingresos
        fields = ['id', 'fecha', 'tipoingreso', 'monto', 'descripcion', 'anio', 'mes', 'activo']
        read_only_fields = ['activo', 'usuario']  # El usuario es asignado automáticamente

    def create(self, validated_data):
        # Asignar automáticamente el tipo como 'ingreso' (id=1)
        validated_data['tipo'] = Tipo.objects.get(id=1)
        return super().create(validated_data)





class EgresosSerializer(serializers.ModelSerializer):
    subcategoria = serializers.PrimaryKeyRelatedField(
        queryset=Subcategoria.objects.all(),
        required=False,
        allow_null=True
    )
    nombreCatalogo = serializers.SerializerMethodField()
    nombreSubcatalogo = serializers.SerializerMethodField()

    class Meta:
        model = Egresos
        fields = [
            'id',
            'fecha',
            'categoria',
            'subcategoria',
            'monto',
            'descripcion',
            'anio',
            'mes',
            'activo',
            'nombreCatalogo',
            'nombreSubcatalogo'
        ]
        read_only_fields = ['activo', 'usuario']  # 'nombreCatalogo' y 'nombreSubcatalogo' no están aquí

    def get_nombreCatalogo(self, obj):
        return obj.categoria.nombre if obj.categoria else None

    def get_nombreSubcatalogo(self, obj):
        return obj.subcategoria.nombre if obj.subcategoria else None

    def create(self, validated_data):
        # Asignar automáticamente el tipo como 'egreso' (id=2)
        try:
            tipo_egreso = Tipo.objects.get(id=2)
        except Tipo.DoesNotExist:
            raise serializers.ValidationError({"error": "Tipo 'Egreso' no encontrado."})

        validated_data['tipo'] = tipo_egreso
        validated_data['usuario'] = self.context['request'].user  # Asignar el usuario automáticamente
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Asegurar que el tipo se mantenga como 'egreso'
        if 'tipo' not in validated_data:
            try:
                tipo_egreso = Tipo.objects.get(id=2)
            except Tipo.DoesNotExist:
                raise serializers.ValidationError({"error": "Tipo 'Egreso' no encontrado."})
            validated_data['tipo'] = tipo_egreso
        return super().update(instance, validated_data)


class FinanzasSummarySerializer(serializers.Serializer):
    sum_ingresos = serializers.DecimalField(max_digits=15, decimal_places=2)
    sum_egresos = serializers.DecimalField(max_digits=15, decimal_places=2)
    disponible = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaccion = serializers.IntegerField()