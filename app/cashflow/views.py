from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.catalogos.models import AnioUsuario, Mes, Categoria, Subcategoria, Tipo
from django.contrib.auth.models import User
from app.cashflow.models import Ingresos, Egresos
from app.cashflow.serializers import IngresosSerializer, EgresosSerializer, FinanzasSummarySerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from app.utils.paginator import CustomPagination





class IngresosListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, anio_id, mes_id):
        """
        Lista los ingresos activos por año y mes con paginación.
        """
        ingresos = Ingresos.objects.filter(anio_id=anio_id, mes_id=mes_id, activo=True)
        serializer = IngresosSerializer(ingresos, many=True)

        # Aplicar paginación
        paginator = CustomPagination()
        paginated_response = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(paginated_response, "ingresos")


class IngresosCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Crea un nuevo ingreso.
        """
        data = request.data  # Datos enviados desde el frontend
        data['tipo'] = 1  # Asignar automáticamente el tipo como 'ingreso' (id=1)

        serializer = IngresosSerializer(data=data)
        if serializer.is_valid():
            # Guardar el objeto y asignar automáticamente el usuario autenticado
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngresosDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, ingreso_id):
        """
        Detalle de un ingreso específico.
        """
        try:
            ingreso = Ingresos.objects.get(id=ingreso_id, activo=True)
        except Ingresos.DoesNotExist:
            return Response({"error": "Ingreso no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = IngresosSerializer(ingreso)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngresosUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, ingreso_id):
        """
        Actualiza un ingreso existente.
        """
        try:
            ingreso = Ingresos.objects.get(id=ingreso_id, activo=True)
        except Ingresos.DoesNotExist:
            return Response({"error": "Ingreso no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = IngresosSerializer(ingreso, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngresosDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, ingreso_id):
        """
        Realiza un soft delete de un ingreso.
        """
        try:
            ingreso = Ingresos.objects.get(id=ingreso_id, activo=True)
        except Ingresos.DoesNotExist:
            return Response({"error": "Ingreso no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        ingreso.activo = False
        ingreso.save()
        return Response({"message": "Ingreso eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)



#Egresos Servicios

class EgresosListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, anio_id, mes_id):
        """
        Lista los egresos activos por año y mes, ordenados por fecha, con paginación.
        """
        egresos = Egresos.objects.filter(
            anio_id=anio_id,
            mes_id=mes_id,
            activo=True,
            usuario=request.user
        ).select_related('categoria', 'subcategoria').order_by('-fecha')  # Ordenar por fecha ascendente

        serializer = EgresosSerializer(egresos, many=True)

        # Aplicar paginación
        paginator = CustomPagination()
        paginated_response = paginator.paginate_queryset(serializer.data, request)
        return paginator.get_paginated_response(paginated_response, "egresos")



class EgresosCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Crea un nuevo egreso.
        """
        data = request.data.copy()  # Copia de los datos enviados desde el frontend

        # Asignar automáticamente el tipo como 'egreso' (id=2)
        tipo_egreso = Tipo.objects.filter(id=2).first()
        if not tipo_egreso:
            return Response({"error": "Tipo 'Egreso' no encontrado."}, status=status.HTTP_400_BAD_REQUEST)
        data['tipo'] = tipo_egreso.id

        # Pasar el contexto al serializador
        serializer = EgresosSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            # Guardar el objeto y asignar automáticamente el usuario autenticado
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EgresosDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, egreso_id):
        """
        Detalle de un egreso específico.
        """
        egreso = get_object_or_404(Egresos, id=egreso_id, activo=True, usuario=request.user)
        serializer = EgresosSerializer(egreso)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EgresosUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, egreso_id):
        """
        Actualiza un egreso existente.
        """
        # Obtener el objeto Egreso o retornar 404 si no existe
        egreso = get_object_or_404(Egresos, id=egreso_id, activo=True, usuario=request.user)

        # Serializar los datos entrantes
        serializer = EgresosSerializer(egreso, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            # Guardar los cambios
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Retornar errores de validación si los hay
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EgresosDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, egreso_id):
        """
        Realiza un soft delete de un egreso.
        """
        egreso = get_object_or_404(Egresos, id=egreso_id, activo=True, usuario=request.user)
        egreso.activo = False  # Soft delete
        egreso.save()
        return Response({"message": "Egreso eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)




#Logistica


class FinanzasSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, anio_id, mes_id):
        """
        Retorna los ingresos, egresos del mes específico, el disponible general acumulado
        (desde el inicio), y la cantidad total de transacciones hasta el mes actual para el usuario.
        """
        try:
            usuario = request.user

            # Verificar que el año y mes existan
            anio = AnioUsuario.objects.get(id=anio_id)
            mes_actual = Mes.objects.get(id=mes_id)

            # Filtrar ingresos y egresos SOLO del mes actual
            ingresos_mes_qs = Ingresos.objects.filter(
                usuario=usuario,
                anio=anio,
                mes=mes_actual,
                activo=True
            )
            egresos_mes_qs = Egresos.objects.filter(
                usuario=usuario,
                anio=anio,
                mes=mes_actual,
                activo=True
            )

            # 🔹 Obtener ingresos y egresos TOTALES (acumulados desde el inicio)
            total_ingresos = Ingresos.objects.filter(
                usuario=usuario,
                activo=True  # Sin filtrar por mes
            ).aggregate(total=Sum('monto'))['total'] or 0

            total_egresos = Egresos.objects.filter(
                usuario=usuario,
                activo=True  # Sin filtrar por mes
            ).aggregate(total=Sum('monto'))['total'] or 0

            # 🔹 Calcular el disponible GENERAL
            disponible = total_ingresos - total_egresos  # Siempre desde el inicio

            # 🔹 Calcular sumatorias SOLO del mes actual
            sum_ingresos = ingresos_mes_qs.aggregate(total=Sum('monto'))['total'] or 0
            sum_egresos = egresos_mes_qs.aggregate(total=Sum('monto'))['total'] or 0

            # 🔹 Calcular la cantidad de transacciones del mes actual
            count_ingresos = ingresos_mes_qs.count()
            count_egresos = egresos_mes_qs.count()
            transaccion = count_ingresos + count_egresos

            # 🔹 Obtener el nombre del mes actual
            mes_actual_valor = mes_actual.mes

        except (AnioUsuario.DoesNotExist, Mes.DoesNotExist):
            # Si el año o mes no existen, establecer valores en 0
            sum_ingresos = 0
            sum_egresos = 0
            disponible = 0
            transaccion = 0
            mes_actual_valor = "Desconocido"

        except Exception as e:
            # Manejo de errores generales
            print(f"Error en FinanzasSummaryAPIView: {e}")
            sum_ingresos = 0
            sum_egresos = 0
            disponible = 0
            transaccion = 0
            mes_actual_valor = "Error"

        # Preparar los datos para el serializer
        data = {
            'sum_ingresos': sum_ingresos,  # Solo del mes actual
            'sum_egresos': sum_egresos,    # Solo del mes actual
            'disponible': disponible,      # 🔹 General (ingresos - egresos desde el inicio)
            'transaccion': transaccion,    # Cantidad de transacciones del mes actual
            'mes_actual': mes_actual_valor  # Nombre del mes
        }

        serializer = FinanzasSummarySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)



