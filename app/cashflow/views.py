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





class IngresosListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, anio_id, mes_id):
        """
        Lista los ingresos activos por año y mes.
        """
        ingresos = Ingresos.objects.filter(anio_id=anio_id, mes_id=mes_id, activo=True)
        serializer = IngresosSerializer(ingresos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        Lista los egresos activos por año y mes, ordenados por fecha.
        """
        egresos = Egresos.objects.filter(
            anio_id=anio_id,
            mes_id=mes_id,
            activo=True,
            usuario=request.user
        ).select_related('categoria', 'subcategoria').order_by('fecha')  # Ordenar por fecha ascendente

        serializer = EgresosSerializer(egresos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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

# control/views.py

class FinanzasSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, anio_id, mes_id):
        """
        Retorna la sumatoria de ingresos, egresos, el disponible y la cantidad total de transacciones
        para un usuario, año y mes específicos.
        """
        try:
            usuario = request.user

            # Verificar que el año y mes existan
            anio = AnioUsuario.objects.get(id=anio_id)
            mes = Mes.objects.get(id=mes_id)

            # Filtrar ingresos y egresos activos para el usuario, año y mes
            ingresos_qs = Ingresos.objects.filter(
                usuario=usuario,
                anio=anio,
                mes=mes,
                activo=True
            )
            egresos_qs = Egresos.objects.filter(
                usuario=usuario,
                anio=anio,
                mes=mes,
                activo=True
            )

            # Calcular las sumatorias
            sum_ingresos = ingresos_qs.aggregate(total=Sum('monto'))['total'] or 0
            sum_egresos = egresos_qs.aggregate(total=Sum('monto'))['total'] or 0
            disponible = sum_ingresos - sum_egresos

            # Calcular la cantidad de transacciones
            count_ingresos = ingresos_qs.count()
            count_egresos = egresos_qs.count()
            transaccion = count_ingresos + count_egresos

        except (AnioUsuario.DoesNotExist, Mes.DoesNotExist):
            # Si el año o mes no existen, establecer todos los campos en 0
            sum_ingresos = 0
            sum_egresos = 0
            disponible = 0
            transaccion = 0

        except Exception as e:
            # Manejar cualquier otro error inesperado
            print(f"Error en FinanzasSummaryAPIView: {e}")
            sum_ingresos = 0
            sum_egresos = 0
            disponible = 0
            transaccion = 0

        # Preparar los datos para el serializer
        data = {
            'sum_ingresos': sum_ingresos,
            'sum_egresos': sum_egresos,
            'disponible': disponible,
            'transaccion': transaccion
        }

        serializer = FinanzasSummarySerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
