from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.financing.models import Prestamo, PagosPrestamo
from app.financing.serializers import PrestamoSerializer, PagosPrestamoSerializer
from django.db import transaction
from django.db.models import Sum

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
        Listar pagos activos de un préstamo
        """
        try:
            prestamo = Prestamo.objects.get(pk=prestamo_id, usuario=request.user, activo=True)
        except Prestamo.DoesNotExist:
            return Response({"error": "Préstamo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        pagos = PagosPrestamo.objects.filter(prestamo=prestamo, activo=True)
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
