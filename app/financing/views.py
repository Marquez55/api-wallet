from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.financing.models import Prestamo, PagosPrestamo, ConceptoPrestamo, CardCredito, ComprasTarjetaCredito, PagoTarjetaCredito
from app.financing.serializers import PrestamoSerializer, PagosPrestamoSerializer, ConceptoPrestamoSerializer, CardCreditoSerializer, ComprasTarjetaCreditoSerializer, PagoTarjetaCreditoSerializer
from django.db import transaction
from django.db.models import Sum, Q, Count
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from app.financing.services import recalc_saldo_tarjeta
from decimal import Decimal, ROUND_HALF_UP
from django.utils.dateparse import parse_date
from django.utils import timezone


def _q2(v) -> Decimal:
    return Decimal(v).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _money(v) -> float:
    return float(_q2(v or Decimal('0')))

class PrestamoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de préstamos activos del usuario autenticado
        """
        prestamos = Prestamo.objects.filter(usuario=request.user, activo=True)
        serializer = PrestamoSerializer(prestamos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creación de un nuevo préstamo
        """
        serializer = PrestamoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrestamoRetrieveAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, prestamo_id):
        """
        Recupera los datos individuales de un préstamo por su ID.
        Restringido al usuario autenticado dueño del préstamo.
        """
        try:
            prestamo = Prestamo.objects.get(id=prestamo_id, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response(
                {'error': 'Préstamo no encontrado o no tiene permisos para verlo'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PrestamoSerializer(prestamo)
        data = serializer.data

        # Agregar fecha actual
        data['fecha_actual'] = date.today()

        # Calcular estatus en base al total_restante
        total_restante = data.get('total_restante', 0)
        data['estatus'] = 'Pendiente' if total_restante != 0 else 'Liquidado'

        return Response(data, status=status.HTTP_200_OK)

class PrestamoUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        """
        Actualización de un préstamo existente
        """
        try:
            prestamo = Prestamo.objects.get(pk=pk, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response({"error": "Préstamo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PrestamoSerializer(prestamo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk):
        """
        Eliminación lógica del préstamo y de sus pagos asociados
        """
        try:
            prestamo = Prestamo.objects.get(pk=pk, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response({"error": "Préstamo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar pagos asociados lógicamente
        PagosPrestamo.objects.filter(prestamo=prestamo, activo=True).update(activo=False)

        # Eliminar préstamo lógicamente
        prestamo.eliminar_logicamente()

        return Response({"message": "Préstamo y sus pagos eliminados correctamente."}, status=status.HTTP_204_NO_CONTENT)


class PagosPrestamoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, prestamo_id):
        """
        Listar pagos activos de un préstamo en orden descendente por fecha
        """
        try:
            prestamo = Prestamo.objects.get(pk=prestamo_id, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response({"error": "Préstamo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        pagos = PagosPrestamo.objects.filter(prestamo=prestamo, activo=True).order_by('-fecha_pago')
        serializer = PagosPrestamoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, prestamo_id):
        """
        Crear un nuevo pago para un préstamo
        """
        try:
            prestamo = Prestamo.objects.get(pk=prestamo_id, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response({"error": "Préstamo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PagosPrestamoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user, prestamo=prestamo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PagosUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        """
        Actualización de un pago de préstamo
        """
        try:
            pago = PagosPrestamo.objects.get(pk=pk, usuario=request.user, activo=True)
        except PagosPrestamo.DoesNotExist:
            return Response({"error": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PagosPrestamoSerializer(pago, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        """
        Eliminación lógica de un pago
        """
        try:
            pago = PagosPrestamo.objects.get(pk=pk, usuario=request.user, activo=True)
        except PagosPrestamo.DoesNotExist:
            return Response({"error": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        pago.eliminar_logicamente()
        return Response({"message": "Pago eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)



class ResumenGeneralPrestamosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna el resumen general de préstamos y pagos del usuario autenticado
        """
        usuario = request.user

        total_prestamos = Prestamo.objects.filter(
            usuario=usuario,
            activo=True
        ).aggregate(total=Sum('monto'))['total'] or 0

        total_pagado = PagosPrestamo.objects.filter(
            usuario=usuario,
            activo=True,
            prestamo__activo=True
        ).aggregate(total=Sum('monto'))['total'] or 0

        total_restante = total_prestamos - total_pagado

        return Response({
            'total_prestamos': round(total_prestamos, 2),
            'total_pagado': round(total_pagado, 2),
            'total_restante': round(total_restante, 2)
        })


class DashboardFinancingSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        today = timezone.localdate()
        start_week = today - timedelta(days=today.weekday())
        week_days = [start_week + timedelta(days=i) for i in range(7)]

        weekly_series = []
        for day in week_days:
            compras_dia = ComprasTarjetaCredito.objects.filter(
                tarjeta_credito__usuario=usuario,
                activo=True,
                fecha_compra=day
            ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

            pagos_tarjeta_dia = PagoTarjetaCredito.objects.filter(
                usuario=usuario,
                activo=True,
                fecha_pago=day,
                tarjeta_credito__activo=True
            ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

            pagos_prestamo_dia = PagosPrestamo.objects.filter(
                usuario=usuario,
                activo=True,
                prestamo__activo=True,
                fecha_pago=day
            ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

            weekly_series.append(_money(compras_dia + pagos_tarjeta_dia + pagos_prestamo_dia))

        week_filter = {
            'fecha_pago__gte': start_week,
            'fecha_pago__lte': today,
        }
        purchase_week_filter = {
            'fecha_compra__gte': start_week,
            'fecha_compra__lte': today,
        }

        pagos_tarjeta_week = PagoTarjetaCredito.objects.filter(
            usuario=usuario,
            activo=True,
            tarjeta_credito__activo=True,
            **week_filter
        )
        pagos_prestamo_week = PagosPrestamo.objects.filter(
            usuario=usuario,
            activo=True,
            prestamo__activo=True,
            **week_filter
        )
        compras_week = ComprasTarjetaCredito.objects.filter(
            tarjeta_credito__usuario=usuario,
            tarjeta_credito__activo=True,
            activo=True,
            **purchase_week_filter
        )
        liquidaciones_week = pagos_tarjeta_week.filter(compras_liquidadas__isnull=False).distinct()

        total_pagos_tarjeta = pagos_tarjeta_week.aggregate(total=Sum('monto'))['total'] or Decimal('0')
        total_pagos_prestamo = pagos_prestamo_week.aggregate(total=Sum('monto'))['total'] or Decimal('0')
        total_compras = compras_week.aggregate(total=Sum('monto'))['total'] or Decimal('0')
        total_liquidado = liquidaciones_week.aggregate(total=Sum('monto'))['total'] or Decimal('0')
        total_movimiento = total_pagos_tarjeta + total_pagos_prestamo + total_compras
        dias_transcurridos = max((today - start_week).days + 1, 1)

        return Response({
            'weekly': {
                'title': 'Resumen semanal',
                'subtitle': 'Actividad promedio',
                'series': weekly_series,
                'total': _money(total_movimiento),
                'average_daily': _money(total_movimiento / Decimal(dias_transcurridos)),
                'stats': [
                    {
                        'id': 1,
                        'color': 'primary',
                        'icon': 'cash',
                        'title': 'Pagos realizados',
                        'subtitle': f"{pagos_tarjeta_week.count() + pagos_prestamo_week.count()} pagos esta semana",
                        'value': f"${_money(total_pagos_tarjeta + total_pagos_prestamo):,.2f}",
                    },
                    {
                        'id': 2,
                        'color': 'success',
                        'icon': 'credit-card',
                        'title': 'Compras financiadas',
                        'subtitle': f"{compras_week.count()} compras registradas",
                        'value': f"${_money(total_compras):,.2f}",
                    },
                    {
                        'id': 3,
                        'color': 'warning',
                        'icon': 'receipt-refund',
                        'title': 'Liquidaciones',
                        'subtitle': f"{liquidaciones_week.count()} compras liquidadas",
                        'value': f"${_money(total_liquidado):,.2f}",
                    },
                ],
            },
            'payment_gateways': {
                'title': 'Métodos de pago',
                'subtitle': 'Origen de movimientos',
                'items': [
                    {
                        'id': 1,
                        'color': 'primary',
                        'title': 'Tarjetas',
                        'subtitle': f"{pagos_tarjeta_week.count()} pagos de tarjeta",
                        'img': 'assets/images/svgs/icon-master-card.svg',
                        'amount': f"${_money(total_pagos_tarjeta):,.2f}",
                    },
                    {
                        'id': 2,
                        'color': 'success',
                        'title': 'Préstamos',
                        'subtitle': f"{pagos_prestamo_week.count()} pagos registrados",
                        'img': 'assets/images/svgs/icon-office-bag.svg',
                        'amount': f"${_money(total_pagos_prestamo):,.2f}",
                    },
                    {
                        'id': 3,
                        'color': 'warning',
                        'title': 'Compras',
                        'subtitle': f"{compras_week.count()} compras nuevas",
                        'img': 'assets/images/svgs/icon-paypal.svg',
                        'amount': f"${_money(total_compras):,.2f}",
                    },
                    {
                        'id': 4,
                        'color': 'error',
                        'title': 'Liquidaciones',
                        'subtitle': f"{liquidaciones_week.count()} pagos anticipados",
                        'img': 'assets/images/svgs/icon-pie.svg',
                        'amount': f"${_money(total_liquidado):,.2f}",
                    },
                ],
            }
        }, status=status.HTTP_200_OK)


class ConceptoPrestamoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prestamo_id = request.query_params.get('prestamo')
        if not prestamo_id:
            return Response(
                {'error': 'Debe proporcionar el parámetro ?prestamo=ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conceptos = ConceptoPrestamo.objects.filter(
            prestamo_id=prestamo_id,
            activo=True
        ).order_by('-fecha')

        serializer = ConceptoPrestamoSerializer(conceptos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConceptoPrestamoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        concepto = get_object_or_404(ConceptoPrestamo, pk=pk, activo=True)
        serializer = ConceptoPrestamoSerializer(concepto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        concepto = get_object_or_404(ConceptoPrestamo, pk=pk, activo=True)
        concepto.eliminar_logicamente()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------
# Servicios Tarjetas de Crédito
# ---------------------
class CardCreditoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tarjetas = CardCredito.objects.filter(usuario=request.user, activo=True)
        serializer = CardCreditoSerializer(tarjetas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CardCreditoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardCreditoRetrieveAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, id=tarjeta_id, usuario=request.user, activo=True)
        serializer = CardCreditoSerializer(tarjeta)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResumenTarjetaCreditoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, id=tarjeta_id, usuario=request.user, activo=True)
        # Totales
        total_compras = (ComprasTarjetaCredito.objects
                         .filter(tarjeta_credito=tarjeta, activo=True)
                         .aggregate(total=Sum('monto'))['total']) or 0
        total_pagos = (PagoTarjetaCredito.objects
                       .filter(tarjeta_credito=tarjeta, activo=True)
                       .aggregate(total=Sum('monto'))['total']) or 0
        saldo = float(total_compras) - float(total_pagos)

        # Reglas simples para mínimos/estimados (pueden ajustarse después)
        pago_minimo = round(max(saldo, 0) * 0.10, 2)
        pago_estimado = round(max(saldo, 0), 2)

        # Compras con meses y pagos restantes
        compras_qs = ComprasTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).order_by('-fecha_compra')
        compras = []
        for c in compras_qs:
            pagos_realizados = c.pagos_tarjeta.filter(activo=True, tarjeta_credito=tarjeta).count()
            meses = c.meses or 1
            faltantes = max(meses - pagos_realizados, 0)
            compras.append({
                'id': c.id,
                'descripcion': c.descripcion,
                'monto': float(c.monto),
                'fecha_compra': c.fecha_compra,
                'meses': meses,
                'msi': c.msi,
                'pagos_realizados': pagos_realizados,
                'pagos_faltantes': faltantes,
            })

        data = {
            'tarjeta': CardCreditoSerializer(tarjeta).data,
            'saldo': round(saldo, 2),
            'pago_minimo': pago_minimo,
            'pago_estimado': pago_estimado,
            'compras': compras,
        }
        return Response(data, status=status.HTTP_200_OK)


class CardCreditoUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        tarjeta = get_object_or_404(CardCredito, pk=pk, usuario=request.user, activo=True)
        serializer = CardCreditoSerializer(tarjeta, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk):
        tarjeta_qs = CardCredito.objects.filter(pk=pk, usuario=request.user)
        if not tarjeta_qs.exists():
            return Response({"detail": "No CardCredito matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        
        tarjeta = tarjeta_qs.first()
        if not tarjeta.activo:
            return Response({"message": "La tarjeta ya había sido eliminada anteriormente."}, status=status.HTTP_200_OK)

        # eliminar lógicamente compras y pagos asociados
        ComprasTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).update(activo=False)
        PagoTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).update(activo=False)
        tarjeta.eliminar_logicamente()
        return Response({"message": "Tarjeta y sus movimientos eliminados correctamente."}, status=status.HTTP_200_OK)


class ComprasTarjetaCreditoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, pk=tarjeta_id, usuario=request.user, activo=True)
        compras = (ComprasTarjetaCredito.objects
                   .filter(tarjeta_credito=tarjeta, activo=True)
                   .annotate(pagos_realizados=Count('pagos_tarjeta', filter=Q(pagos_tarjeta__activo=True)))
                   .order_by('monto', 'id'))  # como pidió: menor a mayor por monto
        serializer = ComprasTarjetaCreditoSerializer(compras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, pk=tarjeta_id, usuario=request.user, activo=True)
        data = request.data.copy()
        data['tarjeta_credito'] = tarjeta.id
        serializer = ComprasTarjetaCreditoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComprasTarjetaCreditoUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        compra = get_object_or_404(ComprasTarjetaCredito, pk=pk, tarjeta_credito__usuario=request.user, activo=True)
        serializer = ComprasTarjetaCreditoSerializer(compra, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Primero buscamos la compra sin el filtro de 'activo=True' para ver si existe
        compra_qs = ComprasTarjetaCredito.objects.filter(pk=pk, tarjeta_credito__usuario=request.user)
        if not compra_qs.exists():
            # Si ni siquiera existe para este usuario, 404 estándar
            return Response({"detail": "No ComprasTarjetaCredito matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        
        compra = compra_qs.first()
        if not compra.activo:
            # Si ya estaba inactiva, informamos que ya se eliminó previamente
            return Response({"message": "La compra ya había sido eliminada anteriormente."}, status=status.HTTP_200_OK)

        if compra.pago_liquidacion_id and compra.pago_liquidacion and compra.pago_liquidacion.activo:
            compra.pago_liquidacion.eliminar_logicamente()

        compra.eliminar_logicamente()
        recalc_saldo_tarjeta(compra.tarjeta_credito_id)
        return Response({"message": "Compra eliminada correctamente."}, status=status.HTTP_200_OK)


class LiquidarCompraTarjetaAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, pk):
        compra = get_object_or_404(
            ComprasTarjetaCredito,
            pk=pk,
            tarjeta_credito__usuario=request.user,
            activo=True
        )

        serializer = ComprasTarjetaCreditoSerializer()
        if serializer.get_liquidada(compra):
            return Response(
                {"error": "La compra ya se encuentra liquidada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        monto_restante = _q2(Decimal(str(serializer.get_monto_restante(compra))))
        if monto_restante <= 0:
            return Response(
                {"error": "La compra ya no tiene monto restante por liquidar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        fecha_pago_raw = request.data.get('fecha_pago') or date.today().isoformat()
        fecha_pago = parse_date(fecha_pago_raw)
        if not fecha_pago:
            return Response(
                {"error": "La fecha de pago no es válida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pago = PagoTarjetaCredito.objects.create(
            usuario=request.user,
            tarjeta_credito=compra.tarjeta_credito,
            monto=monto_restante,
            fecha_pago=fecha_pago,
        )
        pago.pago_compras.set([compra])

        compra.liquidada_manualmente = True
        compra.pago_liquidacion = pago
        compra.save(update_fields=['liquidada_manualmente', 'pago_liquidacion'])

        recalc_saldo_tarjeta(compra.tarjeta_credito_id)
        return Response(ComprasTarjetaCreditoSerializer(compra).data, status=status.HTTP_200_OK)


class PagoTarjetaCreditoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, pk=tarjeta_id, usuario=request.user, activo=True)
        pagos = PagoTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).order_by('-fecha_pago')
        serializer = PagoTarjetaCreditoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, tarjeta_id):
        tarjeta = get_object_or_404(CardCredito, pk=tarjeta_id, usuario=request.user, activo=True)
        data = request.data.copy()
        data['tarjeta_credito'] = tarjeta.id
        serializer = PagoTarjetaCreditoSerializer(data=data)
        if serializer.is_valid():
            pago = serializer.save(usuario=request.user)
            # devolvemos nuevamente serializado
            return Response(PagoTarjetaCreditoSerializer(pago).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoTarjetaCreditoUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        pago = get_object_or_404(PagoTarjetaCredito, pk=pk, usuario=request.user, activo=True)
        if pago.compras_liquidadas.filter(activo=True).exists():
            return Response(
                {"error": "Los pagos de liquidación no se pueden editar. Elimine la liquidación y vuelva a registrarla si necesita cambiarla."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PagoTarjetaCreditoSerializer(pago, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # <- el serializer ya recalcula saldo en su update()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pago_qs = PagoTarjetaCredito.objects.filter(pk=pk, usuario=request.user)
        if not pago_qs.exists():
            return Response({"detail": "No PagoTarjetaCredito matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        
        pago = pago_qs.first()
        if not pago.activo:
            return Response({"message": "El pago ya había sido eliminado anteriormente."}, status=status.HTTP_200_OK)

        pago.compras_liquidadas.filter(activo=True).update(
            liquidada_manualmente=False,
            pago_liquidacion=None
        )
        pago.eliminar_logicamente()
        recalc_saldo_tarjeta(pago.tarjeta_credito_id)
        return Response({"message": "Pago eliminado correctamente."}, status=status.HTTP_200_OK)


class AllComprasTarjetaCreditoListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de todas las compras de todas las tarjetas del usuario,
        ordenadas por fecha más reciente.
        """
        compras = (ComprasTarjetaCredito.objects
                   .filter(tarjeta_credito__usuario=request.user, activo=True)
                   .annotate(pagos_realizados=Count('pagos_tarjeta', filter=Q(pagos_tarjeta__activo=True)))
                   .order_by('-fecha_compra', '-id'))
        
        serializer = ComprasTarjetaCreditoSerializer(compras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllPagosTarjetaCreditoListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de todos los pagos realizados a todas las tarjetas del usuario,
        ordenados por fecha más reciente.
        """
        pagos = (PagoTarjetaCredito.objects
                 .select_related('tarjeta_credito')
                 .filter(tarjeta_credito__usuario=request.user, activo=True)
                 .order_by('-fecha_pago', '-id'))
        
        serializer = PagoTarjetaCreditoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
