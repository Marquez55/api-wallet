# apps/financing/services.py
from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

logger = logging.getLogger(__name__)

def _q2(v) -> Decimal:
    return Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@transaction.atomic
def recalc_saldo_tarjeta(tarjeta_id: Optional[int], *, debug: bool = False) -> Optional[Decimal]:
    """
    Recalcula: saldo = límite – (∑compras activas – ∑pagos activos).
    - Tolera tarjeta inexistente/None (devuelve None).
    - Bloquea la fila con select_for_update para evitar condiciones de carrera.
    """
    if not tarjeta_id:
        if debug:
            logger.warning("[recalc] tarjeta_id vacío/None")
        return None

    # Import local para evitar ciclos
    from .models import CardCredito, ComprasTarjetaCredito, PagoTarjetaCredito

    t_qs = CardCredito.objects.select_for_update().filter(pk=tarjeta_id)
    if not t_qs.exists():
        if debug:
            logger.warning("[recalc] tarjeta inexistente id=%s", tarjeta_id)
        return None

    t = t_qs.get()

    compras = ComprasTarjetaCredito.objects.filter(tarjeta_credito=t, activo=True) \
                 .aggregate(total=Coalesce(Sum('monto'), Decimal('0')))['total']
    pagos = PagoTarjetaCredito.objects.filter(tarjeta_credito=t, activo=True) \
               .aggregate(total=Coalesce(Sum('monto'), Decimal('0')))['total']

    utilizado = _q2(Decimal(compras) - Decimal(pagos))
    nuevo_saldo = _q2(Decimal(t.limite) - utilizado)  # puede ser negativo si bajó el límite

    if debug:
        logger.info(
            "[recalc] tarjeta=%s limite=%s sum_compras=%s sum_pagos=%s utilizado=%s nuevo_saldo=%s",
            t.id, t.limite, compras, pagos, utilizado, nuevo_saldo
        )

    t.saldo = nuevo_saldo
    t.save(update_fields=['saldo'])
    return nuevo_saldo

