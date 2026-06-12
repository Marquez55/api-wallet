from rest_framework import serializers
from django.db.models import Sum
from app.cashflow.models import Ingresos, Tipo, Egresos, Subcategoria, BaulDisponible


class BaulDisponibleSerializer(serializers.ModelSerializer):
    saldo_actual = serializers.SerializerMethodField()
    ingresos_asignados = serializers.SerializerMethodField()
    egresos_asignados = serializers.SerializerMethodField()

    class Meta:
        model = BaulDisponible
        fields = [
            'id',
            'nombre',
            'tipo',
            'descripcion',
            'saldo_inicial',
            'saldo_actual',
            'ingresos_asignados',
            'egresos_asignados',
            'activo'
        ]
        read_only_fields = ['activo', 'usuario']

    def get_ingresos_asignados(self, obj):
        total = Ingresos.objects.filter(usuario=obj.usuario, baul=obj, activo=True).aggregate(total=Sum('monto'))['total'] or 0
        return total

    def get_egresos_asignados(self, obj):
        total = Egresos.objects.filter(usuario=obj.usuario, baul=obj, activo=True).aggregate(total=Sum('monto'))['total'] or 0
        return total

    def get_saldo_actual(self, obj):
        return (obj.saldo_inicial or 0) + self.get_ingresos_asignados(obj) - self.get_egresos_asignados(obj)


class IngresosSerializer(serializers.ModelSerializer):
    nombreBaul = serializers.SerializerMethodField()

    class Meta:
        model = Ingresos
        fields = ['id', 'fecha', 'tipoingreso', 'baul', 'monto', 'descripcion', 'anio', 'mes', 'activo', 'nombreBaul']
        read_only_fields = ['activo', 'usuario']

    def get_nombreBaul(self, obj):
        return obj.baul.nombre if obj.baul else None

    def validate_baul(self, value):
        request = self.context.get('request')

        if self.instance is None and value is None:
            raise serializers.ValidationError("Debes seleccionar un baúl.")

        if value is not None and request and value.usuario_id != request.user.id:
            raise serializers.ValidationError("El baúl seleccionado no pertenece al usuario actual.")

        return value

    def create(self, validated_data):
        validated_data['tipo'] = Tipo.objects.get(id=1)
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError({"error": "No se encontró el contexto de la solicitud."})
        validated_data['usuario'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'tipo' not in validated_data:
            validated_data['tipo'] = instance.tipo or Tipo.objects.get(id=1)
        return super().update(instance, validated_data)


class EgresosSerializer(serializers.ModelSerializer):
    subcategoria = serializers.PrimaryKeyRelatedField(
        queryset=Subcategoria.objects.all(),
        required=False,
        allow_null=True
    )
    nombreCatalogo = serializers.SerializerMethodField()
    nombreSubcatalogo = serializers.SerializerMethodField()
    nombreBaul = serializers.SerializerMethodField()

    class Meta:
        model = Egresos
        fields = [
            'id',
            'fecha',
            'categoria',
            'subcategoria',
            'baul',
            'monto',
            'descripcion',
            'anio',
            'mes',
            'activo',
            'nombreCatalogo',
            'nombreSubcatalogo',
            'nombreBaul'
        ]
        read_only_fields = ['activo', 'usuario']

    def get_nombreCatalogo(self, obj):
        return obj.categoria.nombre if obj.categoria else None

    def get_nombreSubcatalogo(self, obj):
        return obj.subcategoria.nombre if obj.subcategoria else None

    def get_nombreBaul(self, obj):
        return obj.baul.nombre if obj.baul else None

    def validate_baul(self, value):
        request = self.context.get('request')

        if self.instance is None and value is None:
            raise serializers.ValidationError("Debes seleccionar un baúl.")

        if value is not None and request and value.usuario_id != request.user.id:
            raise serializers.ValidationError("El baúl seleccionado no pertenece al usuario actual.")

        return value

    def create(self, validated_data):
        try:
            tipo_egreso = Tipo.objects.get(id=2)
        except Tipo.DoesNotExist:
            raise serializers.ValidationError({"error": "Tipo 'Egreso' no encontrado."})

        validated_data['tipo'] = tipo_egreso
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError({"error": "No se encontró el contexto de la solicitud."})
        validated_data['usuario'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
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
    mes_actual = serializers.CharField(max_length=20)
