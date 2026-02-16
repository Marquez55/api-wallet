from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, Q, Count
from django.db.models.functions import Coalesce
from django.db import transaction
from datetime import date
from django.db import models
from app.financing.models import (
    Prestamo,
    PagosPrestamo,
    ConceptoPrestamo,
    CardCredito,
    ComprasTarjetaCredito,
    PagoTarjetaCredito,
)
from app.financing.services import recalc_saldo_tarjeta


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


# --- Tarjeta de crédito ---
class CardCreditoSerializer(serializers.ModelSerializer):
    total_pagado = serializers.SerializerMethodField()

    class Meta:
        model = CardCredito
        fields = ['id', 'nombre', 'limite', 'saldo', 'total_pagado', 'tasa_interes', 'fecha_corte', 'fecha_pago']
        extra_kwargs = {
            'saldo': {'read_only': True},   # el cliente no lo envía
        }

    def get_total_pagado(self, obj: CardCredito) -> float:
        total = obj.pagos.filter(activo=True).aggregate(total=Sum('monto'))['total'] or Decimal('0')
        return float(_q2(total))

    # ===== helpers =====
    @staticmethod
    def _q2(val) -> Decimal:
        return Decimal(val).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # ===== validación/normalización de ENTRADA =====
    def validate(self, attrs):
        # Normalice fechas recibidas a año canónico 2000 (si vienen en partial, respete las omitidas)
        for k in ('fecha_corte', 'fecha_pago'):
            d = attrs.get(k)
            if d:
                attrs[k] = date(2000, d.month, d.day)

        if 'nombre' in attrs and not (attrs['nombre'] or '').strip():
            raise ValidationError({'nombre': 'El nombre del banco es requerido.'})
        if 'limite' in attrs and Decimal(attrs['limite']) <= 0:
            raise ValidationError({'limite': 'La línea de crédito debe ser mayor a 0.'})
        if 'tasa_interes' in attrs and Decimal(attrs['tasa_interes']) < 0:
            raise ValidationError({'tasa_interes': 'La tasa no puede ser negativa.'})
        return attrs

    def create(self, validated_data):
        # Aquí ya existen fecha_corte/fecha_pago (porque ahora son campos writeable)
        if 'tasa_interes' in validated_data:
            validated_data['tasa_interes'] = self._q2(validated_data['tasa_interes'])
        validated_data['limite'] = self._q2(validated_data['limite'])
        validated_data['saldo']  = validated_data['limite']  # saldo inicial = límite
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance: CardCredito, validated_data):
        # validate() ya normalizó fechas si venían
        if 'tasa_interes' in validated_data:
            validated_data['tasa_interes'] = self._q2(validated_data['tasa_interes'])

        limite_cambia = 'limite' in validated_data
        if limite_cambia:
            validated_data['limite'] = self._q2(validated_data['limite'])

        instance = super().update(instance, validated_data)
        if limite_cambia:
            recalc_saldo_tarjeta(instance.id)  # mantiene saldo consistente
        return instance

    # ===== salida (to_representation): año actual para las fechas =====
    def to_representation(self, instance):
        data = super().to_representation(instance)
        today = date.today()
        data['fecha_corte'] = date(today.year, instance.fecha_corte.month, instance.fecha_corte.day).isoformat()
        data['fecha_pago']  = date(today.year, instance.fecha_pago.month,  instance.fecha_pago.day ).isoformat()
        return data


def _q2(v: Decimal) -> Decimal:
    return Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# --- Compras ---
class ComprasTarjetaCreditoSerializer(serializers.ModelSerializer):
    pagos_realizados = serializers.SerializerMethodField()
    meses_restantes = serializers.SerializerMethodField()
    cuota_mensual   = serializers.SerializerMethodField()
    liquidada       = serializers.SerializerMethodField()
    total_pagado    = serializers.SerializerMethodField()
    monto_restante  = serializers.SerializerMethodField()

    class Meta:
        model  = ComprasTarjetaCredito
        fields = [
            'id','tarjeta_credito','descripcion','monto','fecha_compra','meses','msi',
            'pagos_realizados','meses_restantes','cuota_mensual','liquidada',
            'total_pagado', 'monto_restante'
        ]

    # ---------- helpers ----------
    def _cuota(self, compra: ComprasTarjetaCredito) -> Decimal:
        meses = max(int(compra.meses or 1), 1)
        if compra.msi:
            return _q2(Decimal(compra.monto) / Decimal(meses))
        # con interés (anual→mensual) simplificado a anualidad
        tasa_anual = Decimal(compra.tarjeta_credito.tasa_interes or 0) / Decimal('100')
        r = tasa_anual / Decimal('12')
        if r <= 0:
            return _q2(Decimal(compra.monto) / Decimal(meses))
        num = Decimal(compra.monto) * r * (1 + r) ** meses
        den = (1 + r) ** meses - 1
        return _q2(num / den)

    # ---------- campos calculados ----------
    def get_pagos_realizados(self, obj: ComprasTarjetaCredito) -> int:
        # Si la vista anotó 'pagos_realizados', úselo para evitar N+1
        val = getattr(obj, 'pagos_realizados', None)
        if val is not None:
            return int(val)
        return obj.pagos_tarjeta.filter(activo=True).count()

    def get_meses_restantes(self, obj: ComprasTarjetaCredito) -> int:
        return max(int(obj.meses or 1) - self.get_pagos_realizados(obj), 0)

    def get_cuota_mensual(self, obj: ComprasTarjetaCredito) -> str:
        return str(self._cuota(obj))  # como string para no romper front que espera string/number

    def get_liquidada(self, obj: ComprasTarjetaCredito) -> bool:
        return self.get_meses_restantes(obj) == 0

    def get_total_pagado(self, obj: ComprasTarjetaCredito) -> float:
        pagos_count = self.get_pagos_realizados(obj)
        cuota = self._cuota(obj)
        total = Decimal(pagos_count) * cuota
        return float(_q2(total))

    def get_monto_restante(self, obj: ComprasTarjetaCredito) -> float:
        total_pagado = Decimal(str(self.get_total_pagado(obj)))
        restante = Decimal(obj.monto) - total_pagado
        return float(_q2(max(restante, Decimal('0'))))

    @transaction.atomic
    def create(self, validated_data):
        # si validas monto > 0, déjalo; aquí solo creamos y recalculamos
        compra = super().create(validated_data)
        recalc_saldo_tarjeta(compra.tarjeta_credito_id)
        return compra

    @transaction.atomic
    def update(self, instance, validated_data):
        old_tarjeta_id = instance.tarjeta_credito_id
        instance = super().update(instance, validated_data)
        # recálculo para la tarjeta destino
        recalc_saldo_tarjeta(instance.tarjeta_credito_id)
        # y si moviste la compra a otra tarjeta, recalcula la original
        if old_tarjeta_id != instance.tarjeta_credito_id:
            recalc_saldo_tarjeta(old_tarjeta_id)
        return instance



# --- Pagos ---
class PagoTarjetaCreditoSerializer(serializers.ModelSerializer):
    nombre_tarjeta = serializers.CharField(source='tarjeta_credito.nombre', read_only=True)
    # si el front quiere especificar, lo conserva:
    pago_compras = serializers.PrimaryKeyRelatedField(
        queryset=ComprasTarjetaCredito.objects.all(), many=True, required=False
    )

    class Meta:
        model  = PagoTarjetaCredito
        fields = ['id','tarjeta_credito','nombre_tarjeta','pago_compras','monto','fecha_pago']

    def _cuota(self, compra: ComprasTarjetaCredito) -> Decimal:
        meses = max(int(compra.meses or 1), 1)
        if compra.msi:
            return _q2(Decimal(compra.monto) / Decimal(meses))
        tasa_anual = Decimal(compra.tarjeta_credito.tasa_interes or 0) / Decimal('100')
        r = tasa_anual / Decimal('12')
        if r <= 0:
            return _q2(Decimal(compra.monto) / Decimal(meses))
        num = Decimal(compra.monto) * r * (1 + r) ** meses
        den = (1 + r) ** meses - 1
        return _q2(num / den)

    def _auto_aplicar(self, tarjeta, monto: Decimal) -> list[ComprasTarjetaCredito]:
        """
        Devuelve la lista de compras a las que se aplicará una CUOTA completa cada una.
        FIFO por fecha_compra.
        """
        restantes = monto
        seleccion = []

        compras = (ComprasTarjetaCredito.objects
                   .filter(tarjeta_credito=tarjeta, activo=True)
                   .annotate(pagos_realizados=Count('pagos_tarjeta', filter=Q(pagos_tarjeta__activo=True)))
                   .order_by('fecha_compra','id'))

        for c in compras:
            # si ya está liquidada (pagos_realizados >= meses), sáltela
            meses_restantes = max(int(c.meses or 1) - int(getattr(c,'pagos_realizados',0)), 0)
            if meses_restantes <= 0:
                continue

            cuota = self._cuota(c)
            if restantes + Decimal('0.005') >= cuota:  # tolerancia 0.01
                seleccion.append(c)
                restantes = _q2(restantes - cuota)
            else:
                break

        if not seleccion:
            raise ValidationError({'monto': 'El monto no alcanza para cubrir una cuota de ninguna compra.'})
        return seleccion  # el "sobrante" queda sin asignar (ver comentario en create)

    @transaction.atomic
    def create(self, validated_data):
        compras = validated_data.pop('pago_compras', None)
        tarjeta = validated_data['tarjeta_credito']
        monto   = _q2(Decimal(validated_data['monto']))
        if monto <= 0:
            raise ValidationError({'monto': 'El monto debe ser mayor a 0.'})

        # Si el front no especifica, hacemos reparto automático por cuotas
        if not compras:
            compras = self._auto_aplicar(tarjeta, monto)

        # Validar coherencia: que todas pertenezcan a la tarjeta y estén activas
        bad = [c for c in compras if (not c.activo) or (c.tarjeta_credito_id != tarjeta.id)]
        if bad:
            raise ValidationError({'pago_compras': 'Las compras deben pertenecer a la tarjeta y estar activas.'})

        pago = super().create(validated_data)
        if compras:
            pago.pago_compras.set(compras)

        # Nota: si el front manda un monto que cubre MÁS que la suma de cuotas seleccionadas,
        # aquí no podemos “sumar 2 cuotas” a una misma compra porque el M2M no almacena monto ni duplicados.
        # El saldo de la tarjeta sí subirá por el total del pago (recalc_saldo_tarjeta), y los “meses_restantes”
        # bajarán por cada compra en 'compras' (1 mes menos por compra).
        recalc_saldo_tarjeta(pago.tarjeta_credito_id)
        return pago

    @transaction.atomic
    def update(self, instance, validated_data):
        old_tarjeta_id = instance.tarjeta_credito_id
        compras = validated_data.pop('pago_compras', None)

        if 'monto' in validated_data:
            monto = _q2(Decimal(validated_data['monto']))
            if monto <= 0:
                raise ValidationError({'monto':'El monto debe ser mayor a 0.'})
            validated_data['monto'] = monto

        instance = super().update(instance, validated_data)
        if compras is not None:
            # misma validación de coherencia
            tarjeta = validated_data.get('tarjeta_credito', instance.tarjeta_credito)
            bad = [c for c in compras if (not c.activo) or (c.tarjeta_credito_id != tarjeta.id)]
            if bad:
                raise ValidationError({'pago_compras': 'Las compras deben pertenecer a la tarjeta y estar activas.'})
            instance.pago_compras.set(compras)

        recalc_saldo_tarjeta(instance.tarjeta_credito_id)
        if old_tarjeta_id != instance.tarjeta_credito_id:
            recalc_saldo_tarjeta(old_tarjeta_id)
        return instance
