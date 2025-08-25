from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.financing.models import Prestamo, PagosPrestamo, ConceptoPrestamo, CardCredito, ComprasTarjetaCredito, PagoTarjetaCredito
from app.financing.serializers import PrestamoSerializer, PagosPrestamoSerializer, ConceptoPrestamoSerializer, CardCreditoSerializer, ComprasTarjetaCreditoSerializer, PagoTarjetaCreditoSerializer
from django.db import transaction
from django.db.models import Sum, Q, Count
from django.shortcuts import get_object_or_404
from datetime import date
from app.financing.services import recalc_saldo_tarjeta

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
        tarjeta = get_object_or_404(CardCredito, pk=pk, usuario=request.user, activo=True)
        # eliminar lógicamente compras y pagos asociados
        ComprasTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).update(activo=False)
        PagoTarjetaCredito.objects.filter(tarjeta_credito=tarjeta, activo=True).update(activo=False)
        tarjeta.eliminar_logicamente()
        return Response({"message": "Tarjeta y sus movimientos eliminados correctamente."}, status=status.HTTP_204_NO_CONTENT)


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
        compra = get_object_or_404(ComprasTarjetaCredito, pk=pk, activo=True)
        # Verificamos que la compra pertenezca a una tarjeta del usuario
        if compra.tarjeta_credito.usuario != request.user:
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ComprasTarjetaCreditoSerializer(compra, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        compra = get_object_or_404(ComprasTarjetaCredito, pk=pk, activo=True)
        if compra.tarjeta_credito.usuario != request.user:
            return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        compra.eliminar_logicamente()
        recalc_saldo_tarjeta(compra.tarjeta_credito_id)
        return Response({"message": "Compra eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)


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
        serializer = PagoTarjetaCreditoSerializer(pago, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # <- el serializer ya recalcula saldo en su update()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pago = get_object_or_404(PagoTarjetaCredito, pk=pk, usuario=request.user, activo=True)
        pago.eliminar_logicamente()
        recalc_saldo_tarjeta(pago.tarjeta_credito_id)
        return Response(status=status.HTTP_204_NO_CONTENT)  # 204 sin cuerpo es lo correcto
